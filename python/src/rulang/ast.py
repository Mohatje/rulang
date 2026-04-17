"""
Public AST for rulang rules.

Rulang's public AST is a pure-data tree (frozen dataclasses) produced from the
ANTLR parse tree. It is the primary extension point for downstream features:
validation, conflict detection, formatting, and rule-builder tooling.

The AST includes source spans on every node so diagnostics can point back into
source text.

Usage:

    import rulang
    rule = rulang.parse("entity.age >= 18 => entity.is_adult = true")
    rule.reads           # {"entity.age"}
    rule.writes          # {"entity.is_adult"}
    rule.condition       # Comparison(...)
    rule.actions         # [Set(...)]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Literal, Union

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from rulang.exceptions import RuleSyntaxError
from rulang.grammar.generated.BusinessRulesLexer import BusinessRulesLexer
from rulang.grammar.generated.BusinessRulesParser import BusinessRulesParser


# --- Spans ---------------------------------------------------------------


@dataclass(frozen=True)
class Span:
    """Source position for an AST node. May be None for programmatically built ASTs."""

    start: int  # character offset, inclusive
    end: int  # character offset, exclusive
    line: int  # 1-based
    column: int  # 1-based, at start

    def __repr__(self) -> str:
        return f"Span({self.line}:{self.column}, {self.start}..{self.end})"


# --- Literal types -------------------------------------------------------


LiteralType = Literal["string", "int", "float", "bool", "none", "list"]


# --- Path ----------------------------------------------------------------


@dataclass(frozen=True)
class FieldSegment:
    """A plain dotted field: `.name`."""

    name: str


@dataclass(frozen=True)
class NullSafeFieldSegment:
    """A null-safe dotted field: `?.name`."""

    name: str


@dataclass(frozen=True)
class IndexSegment:
    """A bracketed index access: `[expr]`."""

    expr: "Expr"


PathSegment = Union[FieldSegment, NullSafeFieldSegment, IndexSegment]


@dataclass(frozen=True)
class Path:
    """A dotted path with optional null-safe segments and index expressions."""

    root: str  # the IDENTIFIER at the start of the path
    segments: tuple[PathSegment, ...] = ()
    span: Span | None = None

    def to_string(self, *, normalize_entity: str | None = "entity", include_indices: bool = False) -> str:
        """
        Render the path to a dotted string.

        Args:
            normalize_entity: If given, ensure the rendered path starts with this root.
                              Used for dependency tracking where rules can omit the
                              entity prefix.
            include_indices: If True, render `[i]` segments as `[<value>]`. If False,
                             render them as `[*]` (the form used by the dependency
                             analyzer for normalization).
        """
        parts: list[str] = [self.root]
        for seg in self.segments:
            if isinstance(seg, FieldSegment):
                parts.append(seg.name)
            elif isinstance(seg, NullSafeFieldSegment):
                parts.append(seg.name)
            elif isinstance(seg, IndexSegment):
                if include_indices:
                    # Best-effort render of the index expression as a string
                    parts.append(f"[{_render_expr_for_path(seg.expr)}]")
                else:
                    parts.append("[*]")
        if normalize_entity is not None and parts[0] != normalize_entity:
            parts = [normalize_entity, *parts]
        return ".".join(parts)


def _render_expr_for_path(expr: "Expr") -> str:
    """Best-effort rendering of an index expression for path display."""
    if isinstance(expr, Literal_):
        if expr.type == "string":
            return f"'{expr.value}'"
        return str(expr.value)
    if isinstance(expr, PathRef):
        return expr.path.to_string(normalize_entity=None, include_indices=True)
    return "?"


# --- Expressions ---------------------------------------------------------


@dataclass(frozen=True)
class Literal_:
    """A literal value (string, number, boolean, null, list)."""

    value: Any
    type: LiteralType
    span: Span | None = None


@dataclass(frozen=True)
class PathRef:
    """A reference to a path in an expression position."""

    path: Path
    span: Span | None = None


@dataclass(frozen=True)
class FunctionCall:
    """A built-in function call like `lower(x)`, `len(y)`."""

    name: str
    args: tuple["Expr", ...]
    span: Span | None = None


BinaryOp = Literal["+", "-", "*", "/", "%"]


@dataclass(frozen=True)
class Binary:
    """An arithmetic binary operation."""

    left: "Expr"
    op: BinaryOp
    right: "Expr"
    span: Span | None = None


@dataclass(frozen=True)
class NullCoalesce:
    """A null-coalescing expression: `a ?? b`."""

    left: "Expr"
    right: "Expr"
    span: Span | None = None


@dataclass(frozen=True)
class Unary:
    """A unary negation: `-x`."""

    op: Literal["-"]
    expr: "Expr"
    span: Span | None = None


@dataclass(frozen=True)
class WorkflowCallExpr:
    """A `workflow("name", ...)` used in expression position."""

    name: str
    args: tuple["Expr", ...]
    span: Span | None = None


Expr = Union[Literal_, PathRef, FunctionCall, Binary, NullCoalesce, Unary, WorkflowCallExpr]


# --- Conditions ----------------------------------------------------------


ComparisonOp = Literal[
    "==",
    "!=",
    "<",
    ">",
    "<=",
    ">=",
    "in",
    "not in",
    "contains",
    "not contains",
    "startswith",
    "endswith",
    "matches",
    "contains_any",
    "contains_all",
]


@dataclass(frozen=True)
class Comparison:
    """A binary comparison between two expressions using one of the comparison ops."""

    left: Expr
    op: ComparisonOp
    right: Expr
    span: Span | None = None


ExistenceKind = Literal["exists", "is_empty"]


@dataclass(frozen=True)
class Existence:
    """A postfix existence check: `x exists` or `x is_empty`."""

    expr: Expr
    kind: ExistenceKind
    span: Span | None = None


@dataclass(frozen=True)
class And:
    left: "Condition"
    right: "Condition"
    span: Span | None = None


@dataclass(frozen=True)
class Or:
    left: "Condition"
    right: "Condition"
    span: Span | None = None


@dataclass(frozen=True)
class Not:
    inner: "Condition"
    span: Span | None = None


Condition = Union[And, Or, Not, Comparison, Existence]


# --- Actions -------------------------------------------------------------


@dataclass(frozen=True)
class Set_:
    """A plain assignment: `path = expr`."""

    path: Path
    value: Expr
    span: Span | None = None


CompoundOp = Literal["+=", "-=", "*=", "/="]


@dataclass(frozen=True)
class Compound:
    """A compound assignment: `path += expr` etc."""

    path: Path
    op: CompoundOp
    value: Expr
    span: Span | None = None


@dataclass(frozen=True)
class WorkflowCallAction:
    """A standalone `workflow("name", ...)` as an action."""

    name: str
    args: tuple[Expr, ...]
    span: Span | None = None


@dataclass(frozen=True)
class Return:
    """A `ret expr` action."""

    value: Expr
    span: Span | None = None


Action = Union[Set_, Compound, WorkflowCallAction, Return]


# --- Rule ----------------------------------------------------------------


@dataclass(frozen=True)
class Rule:
    """
    The root of a parsed rule AST.

    Provides the public API for introspection. Downstream code should always
    walk the AST (via the fields, helpers, or the walk() function) rather than
    regex-parse the source text.
    """

    condition: Condition
    actions: tuple[Action, ...]
    source: str
    entity_name: str = "entity"
    span: Span | None = None
    # The three extractors exposed by the public API
    reads: frozenset[str] = field(default_factory=frozenset)
    writes: frozenset[str] = field(default_factory=frozenset)
    workflow_calls: frozenset[str] = field(default_factory=frozenset)

    @property
    def literals(self) -> list[Literal_]:
        """Return every Literal_ in the rule, in source order."""
        out: list[Literal_] = []

        def _visit(node: Any) -> None:
            if isinstance(node, Literal_):
                out.append(node)

        walk(self, _visit)
        return out


# --- Walker --------------------------------------------------------------


def walk(node: Any, visitor: Callable[[Any], None]) -> None:
    """
    Depth-first pre-order traversal over the public AST.

    Calls `visitor(node)` for every AST node encountered. Does not descend into
    None fields or non-AST values (strings, numbers, etc.).
    """
    for child in _iter_ast(node):
        visitor(child)
        walk(child, visitor)


def _iter_ast(node: Any) -> Iterator[Any]:
    """Yield direct child AST nodes of `node` (excluding scalar fields)."""
    if isinstance(node, Rule):
        yield node.condition
        for action in node.actions:
            yield action
        return
    if isinstance(node, (And, Or)):
        yield node.left
        yield node.right
        return
    if isinstance(node, Not):
        yield node.inner
        return
    if isinstance(node, Comparison):
        yield node.left
        yield node.right
        return
    if isinstance(node, Existence):
        yield node.expr
        return
    if isinstance(node, Set_):
        yield node.path
        yield node.value
        return
    if isinstance(node, Compound):
        yield node.path
        yield node.value
        return
    if isinstance(node, WorkflowCallAction):
        for arg in node.args:
            yield arg
        return
    if isinstance(node, Return):
        yield node.value
        return
    if isinstance(node, PathRef):
        yield node.path
        return
    if isinstance(node, FunctionCall):
        for arg in node.args:
            yield arg
        return
    if isinstance(node, Binary):
        yield node.left
        yield node.right
        return
    if isinstance(node, NullCoalesce):
        yield node.left
        yield node.right
        return
    if isinstance(node, Unary):
        yield node.expr
        return
    if isinstance(node, WorkflowCallExpr):
        for arg in node.args:
            yield arg
        return
    if isinstance(node, Path):
        for seg in node.segments:
            if isinstance(seg, IndexSegment):
                yield seg.expr
        return
    # Literal_, FieldSegment, NullSafeFieldSegment: no AST children.


# --- Builder: ANTLR tree -> public AST -----------------------------------


class _SyntaxErrorListener(ErrorListener):
    def __init__(self, source: str):
        self.source = source
        self.errors: list[tuple[int, int, str]] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):  # noqa: N802
        self.errors.append((line, column, msg))


def _span_of(ctx: Any) -> Span | None:
    start = getattr(ctx, "start", None)
    stop = getattr(ctx, "stop", None)
    if start is None or stop is None:
        return None
    start_idx = start.start
    end_idx = stop.stop + 1 if stop.stop is not None else start_idx
    return Span(start=start_idx, end=end_idx, line=start.line, column=start.column + 1)


def parse(source: str, entity_name: str = "entity") -> Rule:
    """
    Parse a rulang rule string and return the public AST.

    Args:
        source: rule text, e.g. `"entity.age >= 18 => entity.is_adult = true"`.
        entity_name: the identifier used to refer to the root entity. Paths that
                     don't start with this identifier get it prepended when
                     computing `reads`/`writes`.

    Returns:
        A `Rule` AST with spans populated from the source.

    Raises:
        RuleSyntaxError: if the source fails to parse.
    """
    input_stream = InputStream(source)
    lexer = BusinessRulesLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = BusinessRulesParser(token_stream)

    listener = _SyntaxErrorListener(source)
    parser.removeErrorListeners()
    parser.addErrorListener(listener)

    tree = parser.rule_()

    if listener.errors:
        line, column, msg = listener.errors[0]
        raise RuleSyntaxError(source, msg, line, column)

    return _build_rule(tree, source, entity_name)


def _build_rule(ctx: Any, source: str, entity_name: str) -> Rule:
    condition = _as_condition(_build_condition(ctx.condition()))
    actions = tuple(_build_action(a) for a in ctx.actions().action())

    reads, writes, workflow_calls = _extract_reads_writes(condition, actions, entity_name)

    return Rule(
        condition=condition,
        actions=actions,
        source=source,
        entity_name=entity_name,
        span=_span_of(ctx),
        reads=frozenset(reads),
        writes=frozenset(writes),
        workflow_calls=frozenset(workflow_calls),
    )


def _as_condition(node: Any) -> Condition:
    """Coerce a node to a Condition. Expressions are wrapped as `expr == true`."""
    if isinstance(node, (And, Or, Not, Comparison, Existence)):
        return node
    return Comparison(
        left=node,
        op="==",
        right=Literal_(value=True, type="bool", span=None),
        span=getattr(node, "span", None),
    )


def _as_expr(node: Any) -> Expr:
    """Coerce a node to an Expr. If it's a wrapped-expression Comparison, unwrap."""
    if isinstance(node, Comparison):
        if (
            node.op == "=="
            and isinstance(node.right, Literal_)
            and node.right.type == "bool"
            and node.right.value is True
            and node.right.span is None
        ):
            return node.left
    return node  # type: ignore[return-value]


def _build_condition(ctx: Any) -> Any:
    return _build_or(ctx.orExpr())


def _build_or(ctx: Any) -> Any:
    children = ctx.andExpr()
    if len(children) == 1:
        return _build_and(children[0])
    result = _as_condition(_build_and(children[0]))
    for i in range(1, len(children)):
        right = _as_condition(_build_and(children[i]))
        result = Or(left=result, right=right, span=_span_of(ctx))
    return result


def _build_and(ctx: Any) -> Any:
    children = ctx.notExpr()
    if len(children) == 1:
        return _build_not(children[0])
    result = _as_condition(_build_not(children[0]))
    for i in range(1, len(children)):
        right = _as_condition(_build_not(children[i]))
        result = And(left=result, right=right, span=_span_of(ctx))
    return result


def _build_not(ctx: Any) -> Any:
    if ctx.NOT():
        inner = _as_condition(_build_not(ctx.notExpr()))
        return Not(inner=inner, span=_span_of(ctx))
    return _build_comparison(ctx.comparison())


_COMP_OP_TOKENS: list[tuple[str, str]] = [
    ("EQ", "=="),
    ("NEQ", "!="),
    ("LTE", "<="),
    ("GTE", ">="),
    ("LT", "<"),
    ("GT", ">"),
    ("NOT_IN", "not in"),
    ("IN", "in"),
    ("NOT_CONTAINS", "not contains"),
    ("CONTAINS_ANY", "contains_any"),
    ("CONTAINS_ALL", "contains_all"),
    ("CONTAINS", "contains"),
    ("STARTS_WITH", "startswith"),
    ("ENDS_WITH", "endswith"),
    ("MATCHES", "matches"),
]


def _build_comparison(ctx: Any) -> Any:
    operands = ctx.nullCoalesce()
    left = _build_expr_from_null_coalesce(operands[0])

    if ctx.IS_EMPTY():
        return Existence(expr=_as_expr(left), kind="is_empty", span=_span_of(ctx))
    if ctx.EXISTS():
        return Existence(expr=_as_expr(left), kind="exists", span=_span_of(ctx))

    if len(operands) == 1:
        # Pass through — caller decides whether to coerce to Condition or Expr.
        return left

    right = _build_expr_from_null_coalesce(operands[1])
    op = _comparison_op(ctx)
    return Comparison(left=_as_expr(left), op=op, right=_as_expr(right), span=_span_of(ctx))


def _comparison_op(ctx: Any) -> ComparisonOp:
    for token_name, op_str in _COMP_OP_TOKENS:
        token_fn = getattr(ctx, token_name, None)
        if token_fn is not None and token_fn():
            return op_str  # type: ignore[return-value]
    # Default — shouldn't reach here for valid parses
    return "=="


def _build_expr_from_null_coalesce(ctx: Any) -> Any:
    operands = ctx.addExpr()
    if len(operands) == 1:
        return _build_add_expr(operands[0])
    result = _as_expr(_build_add_expr(operands[0]))
    for i in range(1, len(operands)):
        right = _as_expr(_build_add_expr(operands[i]))
        result = NullCoalesce(left=result, right=right, span=_span_of(ctx))
    return result


def _build_add_expr(ctx: Any) -> Any:
    operands = ctx.mulExpr()
    if len(operands) == 1:
        return _build_mul_expr(operands[0])

    children = list(ctx.getChildren())
    result = _as_expr(_build_mul_expr(operands[0]))
    op_idx = 1
    for i in range(1, len(operands)):
        while op_idx < len(children):
            child = children[op_idx]
            token = getattr(child, "symbol", None)
            if token and token.type in (BusinessRulesParser.PLUS, BusinessRulesParser.MINUS):
                break
            op_idx += 1
        op_token = children[op_idx]
        op_idx += 1
        right = _as_expr(_build_mul_expr(operands[i]))
        op: BinaryOp = "+" if op_token.symbol.type == BusinessRulesParser.PLUS else "-"
        result = Binary(left=result, op=op, right=right, span=_span_of(ctx))
    return result


def _build_mul_expr(ctx: Any) -> Any:
    operands = ctx.unaryExpr()
    if len(operands) == 1:
        return _build_unary(operands[0])

    children = list(ctx.getChildren())
    result = _as_expr(_build_unary(operands[0]))
    op_idx = 1
    for i in range(1, len(operands)):
        while op_idx < len(children):
            child = children[op_idx]
            token = getattr(child, "symbol", None)
            if token and token.type in (
                BusinessRulesParser.STAR,
                BusinessRulesParser.SLASH,
                BusinessRulesParser.MOD,
            ):
                break
            op_idx += 1
        op_token = children[op_idx]
        op_idx += 1
        right = _as_expr(_build_unary(operands[i]))
        if op_token.symbol.type == BusinessRulesParser.STAR:
            op: BinaryOp = "*"
        elif op_token.symbol.type == BusinessRulesParser.SLASH:
            op = "/"
        else:
            op = "%"
        result = Binary(left=result, op=op, right=right, span=_span_of(ctx))
    return result


def _build_unary(ctx: Any) -> Any:
    if ctx.MINUS():
        inner = _as_expr(_build_unary(ctx.unaryExpr()))
        return Unary(op="-", expr=inner, span=_span_of(ctx))
    return _build_primary(ctx.primary())


def _build_primary(ctx: Any) -> Any:
    if ctx.LPAREN():
        # Parens can contain either a condition or an expression; return as-is.
        # Callers that need one or the other will coerce.
        return _build_or(ctx.orExpr())
    if ctx.literal():
        return _build_literal(ctx.literal())
    if ctx.functionCall():
        return _build_function_call(ctx.functionCall())
    if ctx.path():
        return PathRef(path=_build_path(ctx.path()), span=_span_of(ctx))
    if ctx.workflowCall():
        return _build_workflow_expr(ctx.workflowCall())
    raise RuntimeError("unexpected primary context")


def _build_literal(ctx: Any) -> Any:
    if ctx.NUMBER():
        text = ctx.NUMBER().getText()
        if "." in text:
            return Literal_(value=float(text), type="float", span=_span_of(ctx))
        return Literal_(value=int(text), type="int", span=_span_of(ctx))
    if ctx.STRING():
        text = ctx.STRING().getText()
        value = (
            text[1:-1]
            .replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace('\\"', '"')
            .replace("\\'", "'")
            .replace("\\\\", "\\")
        )
        return Literal_(value=value, type="string", span=_span_of(ctx))
    if ctx.TRUE():
        return Literal_(value=True, type="bool", span=_span_of(ctx))
    if ctx.FALSE():
        return Literal_(value=False, type="bool", span=_span_of(ctx))
    if ctx.NONE():
        return Literal_(value=None, type="none", span=_span_of(ctx))
    if ctx.list_():
        items = tuple(_build_expr_from_or(e) for e in ctx.list_().orExpr())
        return Literal_(value=items, type="list", span=_span_of(ctx))
    raise RuntimeError("unexpected literal")


def _build_expr_from_or(ctx: Any) -> Expr:
    return _as_expr(_build_or(ctx))


def _build_function_call(ctx: Any) -> Any:
    name = ctx.IDENTIFIER().getText()
    args = tuple(_build_expr_from_or(e) for e in ctx.orExpr())
    return FunctionCall(name=name, args=args, span=_span_of(ctx))


def _build_workflow_expr(ctx: Any) -> Any:
    name_raw = ctx.STRING().getText()
    name = name_raw[1:-1]
    args = tuple(_build_expr_from_or(e) for e in ctx.orExpr())
    return WorkflowCallExpr(name=name, args=args, span=_span_of(ctx))


def _build_path(ctx: Any) -> Path:
    root = ctx.IDENTIFIER().getText()
    segments: list[PathSegment] = []
    for seg in ctx.pathSegment():
        if seg.DOT():
            segments.append(FieldSegment(name=seg.IDENTIFIER().getText()))
        elif seg.NULL_SAFE_DOT():
            segments.append(NullSafeFieldSegment(name=seg.IDENTIFIER().getText()))
        elif seg.LBRACKET():
            expr = _build_expr_from_or(seg.orExpr())
            segments.append(IndexSegment(expr=expr))
    return Path(root=root, segments=tuple(segments), span=_span_of(ctx))


def _build_action(ctx: Any) -> Action:
    if ctx.returnStmt():
        value = _build_expr_from_or(ctx.returnStmt().orExpr())
        return Return(value=value, span=_span_of(ctx))
    if ctx.assignment():
        path = _build_path(ctx.assignment().path())
        value = _build_expr_from_or(ctx.assignment().orExpr())
        assign_op = ctx.assignment().assignOp()
        if assign_op.ASSIGN():
            return Set_(path=path, value=value, span=_span_of(ctx))
        op: CompoundOp
        if assign_op.PLUS_ASSIGN():
            op = "+="
        elif assign_op.MINUS_ASSIGN():
            op = "-="
        elif assign_op.STAR_ASSIGN():
            op = "*="
        elif assign_op.SLASH_ASSIGN():
            op = "/="
        else:
            op = "+="
        return Compound(path=path, op=op, value=value, span=_span_of(ctx))
    if ctx.workflowCall():
        wf_ctx = ctx.workflowCall()
        name = wf_ctx.STRING().getText()[1:-1]
        args = tuple(_build_expr_from_or(e) for e in wf_ctx.orExpr())
        return WorkflowCallAction(name=name, args=args, span=_span_of(ctx))
    raise RuntimeError("unexpected action")


# --- Reads/writes/workflow extraction from the public AST ----------------


def _extract_reads_writes(
    condition: Condition,
    actions: tuple[Action, ...],
    entity_name: str,
) -> tuple[set[str], set[str], set[str]]:
    reads: set[str] = set()
    writes: set[str] = set()
    workflow_calls: set[str] = set()

    def _path_str(p: Path) -> str:
        return p.to_string(normalize_entity=entity_name, include_indices=False)

    def _collect_reads(expr: Any) -> None:
        if isinstance(expr, PathRef):
            reads.add(_path_str(expr.path))
            # Recurse into index expressions
            for seg in expr.path.segments:
                if isinstance(seg, IndexSegment):
                    _collect_reads(seg.expr)
            return
        if isinstance(expr, FunctionCall):
            for a in expr.args:
                _collect_reads(a)
            return
        if isinstance(expr, (Binary, NullCoalesce)):
            _collect_reads(expr.left)
            _collect_reads(expr.right)
            return
        if isinstance(expr, Unary):
            _collect_reads(expr.expr)
            return
        if isinstance(expr, WorkflowCallExpr):
            workflow_calls.add(expr.name)
            for a in expr.args:
                _collect_reads(a)
            return
        if isinstance(expr, Literal_):
            if expr.type == "list":
                for item in expr.value:
                    _collect_reads(item)
            return

    def _walk_condition(c: Condition) -> None:
        if isinstance(c, (And, Or)):
            _walk_condition(c.left)
            _walk_condition(c.right)
            return
        if isinstance(c, Not):
            _walk_condition(c.inner)
            return
        if isinstance(c, Comparison):
            _collect_reads(c.left)
            _collect_reads(c.right)
            return
        if isinstance(c, Existence):
            _collect_reads(c.expr)
            return

    _walk_condition(condition)

    for action in actions:
        if isinstance(action, Set_):
            writes.add(_path_str(action.path))
            _collect_reads(action.value)
            # Also count index expressions on the target path as reads
            for seg in action.path.segments:
                if isinstance(seg, IndexSegment):
                    _collect_reads(seg.expr)
        elif isinstance(action, Compound):
            path_str = _path_str(action.path)
            writes.add(path_str)
            reads.add(path_str)  # compound reads the target before writing
            _collect_reads(action.value)
            for seg in action.path.segments:
                if isinstance(seg, IndexSegment):
                    _collect_reads(seg.expr)
        elif isinstance(action, WorkflowCallAction):
            workflow_calls.add(action.name)
            for a in action.args:
                _collect_reads(a)
        elif isinstance(action, Return):
            _collect_reads(action.value)

    return reads, writes, workflow_calls
