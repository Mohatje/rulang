"""
Builder primitives for rulang (proposal #2).

Ergonomic constructors so consumers (visual builders, rule generators, LLM
agents) can assemble ASTs programmatically without regex-splitting rule
strings. Combine with `format()` to go from structured input to canonical
text; use `parse()` for the reverse.

Round-trip guarantees (enforced by tests):

    parse(format(rule)) structurally equals rule
    format(parse(text)) is canonical

Example:

    from rulang.builders import rule, eq, path_of, lit, set_
    r = rule(
        condition=eq(path_of("entity.age"), lit(18)),
        actions=[set_(path_of("entity.adult"), lit(True))],
    )
    rulang.format(r)   # "entity.age == 18 => entity.adult = true"
"""

from __future__ import annotations

from typing import Any, Iterable, Union

from rulang.ast import (
    Action,
    And,
    Binary,
    BinaryOp,
    Comparison,
    ComparisonOp,
    Compound,
    CompoundOp,
    Condition,
    Existence,
    ExistenceKind,
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
    PathSegment,
    Return,
    Rule,
    Set_,
    Unary,
    WorkflowCallAction,
    WorkflowCallExpr,
    _extract_reads_writes,
)


# --- Paths --------------------------------------------------------------


def path_of(*parts: Union[str, int, Expr]) -> Path:
    """
    Build a `Path` from convenient inputs.

    Accepts a dotted string (`"entity.a.b"`) as a single argument, or a
    mixed sequence of parts:

        path_of("entity", "a", "b")
        path_of("entity.a.b")
        path_of("entity", "items", 0, "name")   # literal int index
        path_of("entity", "items", lit(0))      # expression index

    Null-safe segments are written with a leading `?` in the dotted form,
    e.g. `path_of("entity.a?.b")`.
    """
    if len(parts) == 1 and isinstance(parts[0], str) and ("." in parts[0] or "?." in parts[0]):
        return _parse_dotted(parts[0])

    if not parts:
        raise ValueError("path_of() requires at least one part")

    root = parts[0]
    if not isinstance(root, str):
        raise TypeError(f"path root must be a string, got {type(root).__name__}")

    segments: list[PathSegment] = []
    for part in parts[1:]:
        if isinstance(part, int):
            segments.append(IndexSegment(expr=Literal_(value=part, type="int", span=None)))
        elif isinstance(part, str):
            if part.startswith("?."):
                segments.append(NullSafeFieldSegment(name=part[2:]))
            else:
                segments.append(FieldSegment(name=part))
        else:
            # Assume Expr
            segments.append(IndexSegment(expr=part))
    return Path(root=root, segments=tuple(segments), span=None)


def _parse_dotted(text: str) -> Path:
    """Parse a dotted path string including null-safe segments."""
    # Split on `.` and `?.` while preserving which is which
    segments: list[PathSegment] = []
    i = 0
    root_end = None
    while i < len(text):
        if text[i] == ".":
            root_end = i
            break
        if i + 1 < len(text) and text[i : i + 2] == "?.":
            root_end = i
            break
        i += 1
    if root_end is None:
        return Path(root=text, segments=(), span=None)
    root = text[:root_end]
    i = root_end
    while i < len(text):
        if text[i : i + 2] == "?.":
            i += 2
            j = i
            while j < len(text) and text[j] not in (".", "?"):
                j += 1
            segments.append(NullSafeFieldSegment(name=text[i:j]))
            i = j
        elif text[i] == ".":
            i += 1
            j = i
            while j < len(text) and text[j] not in (".", "?"):
                j += 1
            segments.append(FieldSegment(name=text[i:j]))
            i = j
        else:
            # Shouldn't happen given the grammar of what we accept here
            break
    return Path(root=root, segments=tuple(segments), span=None)


# --- Literals / expressions --------------------------------------------


def float_lit(value: float) -> Literal_:
    """Explicit float literal. Use when you want a float representation regardless
    of whether the input value is a whole number.

    TypeScript can't distinguish `3.0` from `3` at runtime; Python can. Use
    `float_lit(3)` when you want float semantics and need cross-runtime parity.
    """
    return Literal_(value=float(value), type="float", span=None)


def int_lit(value: int) -> Literal_:
    """Explicit int literal."""
    return Literal_(value=int(value), type="int", span=None)


def lit(value: Any) -> Literal_:
    """
    Build a `Literal_` with the type inferred from the Python value.

    Supports None, bool, int, float, str, and list (of literals or Exprs).
    Use `float_lit()` / `int_lit()` for explicit control when the Python
    value is ambiguous or when you need strict cross-runtime type parity.
    """
    if value is None:
        return Literal_(value=None, type="none", span=None)
    if isinstance(value, bool):
        return Literal_(value=value, type="bool", span=None)
    if isinstance(value, int):
        return Literal_(value=value, type="int", span=None)
    if isinstance(value, float):
        return Literal_(value=value, type="float", span=None)
    if isinstance(value, str):
        return Literal_(value=value, type="string", span=None)
    if isinstance(value, (list, tuple)):
        # Inside a list literal, context is unambiguous (all elements are
        # literals), so strings can be auto-wrapped. AST nodes pass through.
        items = tuple(
            v if isinstance(v, (Literal_, PathRef, FunctionCall, Binary, NullCoalesce, Unary, WorkflowCallExpr)) else lit(v)
            for v in value
        )
        return Literal_(value=items, type="list", span=None)
    raise TypeError(f"lit() does not accept values of type {type(value).__name__}")


def _as_expr(value: Any) -> Expr:
    """Coerce raw Python values to an Expr via `lit()`; pass through AST nodes.

    Raw strings are rejected because they're ambiguous: the caller might mean
    either a string literal or a path. Use `lit('hello')` for literals and
    `pathref('entity.name')` for paths.
    """
    if isinstance(value, (Literal_, PathRef, FunctionCall, Binary, NullCoalesce, Unary, WorkflowCallExpr)):
        return value
    if isinstance(value, Path):
        return PathRef(path=value, span=None)
    if isinstance(value, str):
        raise TypeError(
            "Raw strings in expression position are ambiguous — they could "
            "mean a path or a string literal. Use lit(%r) for a string "
            "literal or pathref(%r) for a path." % (value, value)
        )
    return lit(value)


def pathref(path: Union[str, Path]) -> PathRef:
    """Wrap a path in a `PathRef` for use as an expression."""
    if isinstance(path, str):
        path = path_of(path)
    return PathRef(path=path, span=None)


def fn(name: str, *args: Any) -> FunctionCall:
    """Build a built-in function call: `fn("lower", pathref("entity.x"))`."""
    return FunctionCall(name=name, args=tuple(_as_expr(a) for a in args), span=None)


def binary(left: Any, op: BinaryOp, right: Any) -> Binary:
    """Build a `Binary` (arithmetic) node."""
    if op not in ("+", "-", "*", "/", "%"):
        raise ValueError(f"invalid binary op: {op!r}")
    return Binary(left=_as_expr(left), op=op, right=_as_expr(right), span=None)


def unary(inner: Any) -> Unary:
    """Build a `Unary(-)` node."""
    return Unary(op="-", expr=_as_expr(inner), span=None)


def null_coalesce(left: Any, right: Any) -> NullCoalesce:
    """Build a null-coalesce `left ?? right`."""
    return NullCoalesce(left=_as_expr(left), right=_as_expr(right), span=None)


def workflow_expr(name: str, *args: Any) -> WorkflowCallExpr:
    """Build a `workflow("name", ...)` in expression position."""
    return WorkflowCallExpr(name=name, args=tuple(_as_expr(a) for a in args), span=None)


# --- Conditions --------------------------------------------------------


def _cmp(op: ComparisonOp, left: Any, right: Any) -> Comparison:
    return Comparison(left=_as_expr(left), op=op, right=_as_expr(right), span=None)


def eq(left: Any, right: Any) -> Comparison:
    return _cmp("==", left, right)


def neq(left: Any, right: Any) -> Comparison:
    return _cmp("!=", left, right)


def lt(left: Any, right: Any) -> Comparison:
    return _cmp("<", left, right)


def gt(left: Any, right: Any) -> Comparison:
    return _cmp(">", left, right)


def lte(left: Any, right: Any) -> Comparison:
    return _cmp("<=", left, right)


def gte(left: Any, right: Any) -> Comparison:
    return _cmp(">=", left, right)


def in_(left: Any, right: Any) -> Comparison:
    return _cmp("in", left, right)


def not_in(left: Any, right: Any) -> Comparison:
    return _cmp("not in", left, right)


def contains(left: Any, right: Any) -> Comparison:
    return _cmp("contains", left, right)


def not_contains(left: Any, right: Any) -> Comparison:
    return _cmp("not contains", left, right)


def startswith(left: Any, right: Any) -> Comparison:
    return _cmp("startswith", left, right)


def endswith(left: Any, right: Any) -> Comparison:
    return _cmp("endswith", left, right)


def matches(left: Any, right: Any) -> Comparison:
    return _cmp("matches", left, right)


def contains_any(left: Any, right: Any) -> Comparison:
    return _cmp("contains_any", left, right)


def contains_all(left: Any, right: Any) -> Comparison:
    return _cmp("contains_all", left, right)


def exists(expr: Any) -> Existence:
    """`x exists` — true if x is non-null."""
    return Existence(expr=_as_expr(expr), kind="exists", span=None)


def is_empty(expr: Any) -> Existence:
    """`x is_empty` — true if x is null, empty string, or empty collection."""
    return Existence(expr=_as_expr(expr), kind="is_empty", span=None)


def and_(*conditions: Condition) -> Condition:
    """Left-associative `and` of two or more conditions."""
    if len(conditions) < 2:
        raise ValueError("and_() requires at least two conditions")
    result = conditions[0]
    for c in conditions[1:]:
        result = And(left=result, right=c, span=None)
    return result


def or_(*conditions: Condition) -> Condition:
    """Left-associative `or` of two or more conditions."""
    if len(conditions) < 2:
        raise ValueError("or_() requires at least two conditions")
    result = conditions[0]
    for c in conditions[1:]:
        result = Or(left=result, right=c, span=None)
    return result


def not_(condition: Condition) -> Not:
    return Not(inner=condition, span=None)


# --- Actions -----------------------------------------------------------


def set_(path: Union[str, Path], value: Any) -> Set_:
    """`path = value` — a Set action."""
    return Set_(path=_as_path(path), value=_as_expr(value), span=None)


def compound(path: Union[str, Path], op: CompoundOp, value: Any) -> Compound:
    """Compound assignment (`+=`, `-=`, `*=`, `/=`)."""
    if op not in ("+=", "-=", "*=", "/="):
        raise ValueError(f"invalid compound op: {op!r}")
    return Compound(path=_as_path(path), op=op, value=_as_expr(value), span=None)


def workflow_call(name: str, *args: Any) -> WorkflowCallAction:
    """`workflow("name", ...)` as an action."""
    return WorkflowCallAction(name=name, args=tuple(_as_expr(a) for a in args), span=None)


def ret(value: Any) -> Return:
    """`ret value` — return from the rule."""
    return Return(value=_as_expr(value), span=None)


def _as_path(p: Union[str, Path]) -> Path:
    if isinstance(p, str):
        return path_of(p)
    return p


# --- Rule --------------------------------------------------------------


def rule(
    condition: Condition,
    actions: Iterable[Action],
    *,
    entity_name: str = "entity",
) -> Rule:
    """
    Build a `Rule` from a condition and a sequence of actions.

    Reads/writes/workflow_calls are computed automatically from the AST so
    the resulting Rule is indistinguishable from one produced by `parse()`
    (modulo spans and `source`, which will be None / ""). Round-trip with
    `format()` produces a canonical string that re-parses to the same AST.
    """
    action_tuple = tuple(actions)
    reads, writes, workflow_calls = _extract_reads_writes(condition, action_tuple, entity_name)
    return Rule(
        condition=condition,
        actions=action_tuple,
        source="",
        entity_name=entity_name,
        span=None,
        reads=frozenset(reads),
        writes=frozenset(writes),
        workflow_calls=frozenset(workflow_calls),
    )
