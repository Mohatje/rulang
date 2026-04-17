"""
Canonical pretty-printer for rulang rules.

`rulang.format(rule)` produces a single canonical string form for a rule.
Idempotent and round-trips with `parse()`:

    parse(format(rule)) structurally equals rule
    format(parse(text)) is canonical text
    format(format(x)) == format(x)

Canonical choices (v1, not configurable):
- single spaces around operators, one space after commas
- strings single-quoted; embedded single quotes escaped as \\'
- booleans / null lowercase (`true`, `false`, `none`)
- integers without trailing `.0`; floats use Python's default repr
- `!=` preferred over `<>`, `startswith` over `starts_with`, etc.
- parens only where precedence requires
- action separator `; `, arrow `=>` with single spaces
"""

from __future__ import annotations

from typing import Union

from rulang.ast import (
    Action,
    And,
    Binary,
    Compound,
    Comparison,
    Condition,
    Existence,
    Expr,
    FieldSegment,
    FunctionCall,
    IndexSegment,
    Literal_,
    Not,
    NullCoalesce,
    NullSafeFieldSegment,
    Or,
    Path,
    PathRef,
    Return,
    Rule,
    Set_,
    Unary,
    WorkflowCallAction,
    WorkflowCallExpr,
    parse,
)

# Precedence levels — higher binds tighter. Used to decide when to add parens.
_P_OR = 10
_P_AND = 20
_P_NOT = 30
_P_COMP = 40
_P_NULL_COALESCE = 50
_P_ADD = 60
_P_MUL = 70
_P_UNARY = 80
_P_PRIMARY = 90


def format(rule: Union[str, Rule], entity_name: str = "entity") -> str:
    """
    Format a rule to its canonical string form.

    Accepts either the rule source text or a public-AST `Rule`. When given
    source, it's parsed first (so syntax errors propagate as
    `RuleSyntaxError`).
    """
    if isinstance(rule, str):
        rule = parse(rule, entity_name=entity_name)
    return _format_rule(rule)


def format_ast(rule: Rule) -> str:
    """Format a `Rule` AST node to canonical string form (alias of `format` for ASTs)."""
    return _format_rule(rule)


def format_condition(condition: "Condition") -> str:
    """Format a condition subtree to canonical string form (no surrounding rule)."""
    return _format_condition(condition, _P_OR)


def format_action(action: "Action") -> str:
    """Format a single action to canonical string form."""
    return _format_action(action)


def format_path(path: "Path") -> str:
    """Format a path in canonical form (no entity-prefix normalization)."""
    return _format_path(path)


def format_expr(expr: "Expr") -> str:
    """Format an expression to canonical string form."""
    return _format_expr(expr, _P_OR)


def _format_rule(rule: Rule) -> str:
    cond = _format_condition(rule.condition, _P_OR)
    actions = "; ".join(_format_action(a) for a in rule.actions)
    return f"{cond} => {actions}"


# --- Conditions ---------------------------------------------------------


def _format_condition(cond: Condition, min_precedence: int) -> str:
    if isinstance(cond, Or):
        s = f"{_format_condition(cond.left, _P_OR)} or {_format_condition(cond.right, _P_AND)}"
        if min_precedence > _P_OR:
            return f"({s})"
        return s
    if isinstance(cond, And):
        s = f"{_format_condition(cond.left, _P_AND)} and {_format_condition(cond.right, _P_NOT)}"
        if min_precedence > _P_AND:
            return f"({s})"
        return s
    if isinstance(cond, Not):
        inner = _format_condition(cond.inner, _P_NOT)
        # `not` prefixes its operand; if the inner is an and/or, parens are required
        if isinstance(cond.inner, (And, Or)):
            inner = f"({_format_condition(cond.inner, _P_OR)})"
        return f"not {inner}"
    if isinstance(cond, Existence):
        inner = _format_expr(cond.expr, _P_COMP)
        return f"{inner} {cond.kind}"
    if isinstance(cond, Comparison):
        left = _format_expr(cond.left, _P_COMP)
        right = _format_expr(cond.right, _P_COMP)
        return f"{left} {cond.op} {right}"
    raise RuntimeError(f"unknown condition type: {type(cond)}")


# --- Expressions --------------------------------------------------------


def _format_expr(expr: Expr, min_precedence: int) -> str:
    if isinstance(expr, Literal_):
        return _format_literal(expr)
    if isinstance(expr, PathRef):
        return _format_path(expr.path)
    if isinstance(expr, FunctionCall):
        args = ", ".join(_format_expr(a, _P_OR) for a in expr.args)
        return f"{expr.name}({args})"
    if isinstance(expr, WorkflowCallExpr):
        return _format_workflow_call(expr.name, expr.args)
    if isinstance(expr, Unary):
        inner = _format_expr(expr.expr, _P_UNARY)
        return f"-{inner}"
    if isinstance(expr, Binary):
        return _format_binary(expr, min_precedence)
    if isinstance(expr, NullCoalesce):
        left = _format_expr(expr.left, _P_NULL_COALESCE)
        right = _format_expr(expr.right, _P_ADD)
        s = f"{left} ?? {right}"
        if min_precedence > _P_NULL_COALESCE:
            return f"({s})"
        return s
    # Comparison / existence can appear inside expressions only when wrapped in parens
    # (via grammar's LPAREN orExpr RPAREN). We format them as a parenthesized condition.
    if isinstance(expr, (And, Or, Not, Comparison, Existence)):
        return f"({_format_condition(expr, _P_OR)})"
    raise RuntimeError(f"unknown expr type: {type(expr)}")


def _format_binary(expr: Binary, min_precedence: int) -> str:
    if expr.op in ("+", "-"):
        my_prec = _P_ADD
        left = _format_expr(expr.left, _P_ADD)
        right = _format_expr(expr.right, _P_MUL)
    else:  # * / %
        my_prec = _P_MUL
        left = _format_expr(expr.left, _P_MUL)
        right = _format_expr(expr.right, _P_UNARY)
    s = f"{left} {expr.op} {right}"
    if min_precedence > my_prec:
        return f"({s})"
    return s


# --- Literals / paths / workflows ---------------------------------------


def _format_literal(lit: Literal_) -> str:
    if lit.type == "string":
        return _format_string(lit.value)
    if lit.type == "bool":
        return "true" if lit.value else "false"
    if lit.type == "none":
        return "none"
    if lit.type == "int":
        return str(int(lit.value))
    if lit.type == "float":
        return _format_float(lit.value)
    if lit.type == "list":
        items = ", ".join(_format_expr(item, _P_OR) for item in lit.value)
        return f"[{items}]"
    raise RuntimeError(f"unknown literal type: {lit.type}")


def _format_float(value: float) -> str:
    text = repr(value)
    # repr gives '3.14' already. Ensure it has a decimal or 'e'.
    if "." in text or "e" in text or "E" in text or "inf" in text or "nan" in text:
        return text
    return text + ".0"


def _format_string(value: str) -> str:
    # Single-quoted. Escape backslash, then single-quote.
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    # Also escape newlines / tabs back to their literal forms so the output is on one line
    escaped = escaped.replace("\n", "\\n").replace("\t", "\\t")
    return f"'{escaped}'"


def _format_path(path: Path) -> str:
    out = path.root
    for seg in path.segments:
        if isinstance(seg, FieldSegment):
            out += f".{seg.name}"
        elif isinstance(seg, NullSafeFieldSegment):
            out += f"?.{seg.name}"
        elif isinstance(seg, IndexSegment):
            idx = _format_expr(seg.expr, _P_OR)
            out += f"[{idx}]"
    return out


def _format_workflow_call(name: str, args: tuple[Expr, ...]) -> str:
    name_str = _format_string(name)
    if args:
        arg_strs = ", ".join(_format_expr(a, _P_OR) for a in args)
        return f"workflow({name_str}, {arg_strs})"
    return f"workflow({name_str})"


# --- Actions ------------------------------------------------------------


def _format_action(action: Action) -> str:
    if isinstance(action, Set_):
        return f"{_format_path(action.path)} = {_format_expr(action.value, _P_OR)}"
    if isinstance(action, Compound):
        return f"{_format_path(action.path)} {action.op} {_format_expr(action.value, _P_OR)}"
    if isinstance(action, WorkflowCallAction):
        return _format_workflow_call(action.name, action.args)
    if isinstance(action, Return):
        return f"ret {_format_expr(action.value, _P_OR)}"
    raise RuntimeError(f"unknown action type: {type(action)}")
