"""
Generic validation framework (proposal #4).

Rulang walks the AST and calls hooks on a user-supplied `Resolver`; the
resolver answers domain questions ("is this path valid? are these types
compatible?") and rulang collects the results into a list of
`Diagnostic`. `validate()` never raises — parse errors are surfaced as
diagnostics too, so callers have a single mental model.

Key design choices (see docs/proposals/04-validation-framework.md):

- `Resolver` is a Protocol. `BaseResolver` gives no-op defaults — consumers
  subclass it and override only the hooks they care about. Unimplemented
  hooks return `UNKNOWN` / `OK` and rulang emits no diagnostic for them.
- Hooks are semantic (check_path, check_assignment, check_comparison,
  check_workflow_call) and receive full expression ASTs — rulang is not a
  typechecker, so expression-level reasoning lives in the resolver.
- Parse errors appear as `rulang.syntax_error` diagnostics.
- Diagnostic codes are namespaced strings; `rulang.*` is rulang-owned,
  anything else is consumer-owned.
- Severities default per-code; `severity_overrides` lets callers adjust
  without changing the resolver.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Protocol, Union, runtime_checkable

from rulang.ast import (
    And,
    Binary,
    Compound,
    Comparison,
    ComparisonOp,
    Condition,
    Existence,
    Expr,
    FunctionCall,
    IndexSegment,
    Literal_,
    Not,
    NullCoalesce,
    Or,
    Path,
    PathRef,
    Return,
    Rule,
    Set_,
    Span,
    Unary,
    WorkflowCallAction,
    WorkflowCallExpr,
    parse,
)
from rulang.exceptions import RuleSyntaxError


Severity = str  # "error" | "warning" | "info"


# --- Sentinels ----------------------------------------------------------


class _Sentinel:
    def __init__(self, name: str):
        self._name = name

    def __repr__(self) -> str:
        return self._name

    def __bool__(self) -> bool:  # allow truthy checks
        return False


#: Sentinel: resolver returned no opinion; rulang emits no diagnostic.
UNKNOWN = _Sentinel("UNKNOWN")

#: Sentinel: hook ran successfully with no findings.
OK = _Sentinel("OK")


# --- PathInfo -----------------------------------------------------------


@dataclass(frozen=True)
class PathInfo:
    """
    What the resolver knows about a path.

    - `exists`: the path is valid in the schema
    - `writable`: the path can be assigned to
    - `type`: a loose string tag for the path's value type, or None if
      the resolver doesn't want to opine
    """

    exists: bool = True
    writable: bool = True
    type: str | None = None


# --- Diagnostic ---------------------------------------------------------


@dataclass(frozen=True)
class Diagnostic:
    """
    One finding from `validate()`.

    Resolvers can emit `Diagnostic` objects directly for anything they care
    about; they don't have to use one of rulang's built-in codes.
    """

    code: str
    message: str
    severity: Severity = "error"
    span: Span | None = None
    related: tuple["Diagnostic", ...] = ()


# --- Resolver protocol + base class -------------------------------------


@runtime_checkable
class Resolver(Protocol):
    """The interface `validate()` calls while walking the AST."""

    def check_path(self, path: Path) -> Union[PathInfo, _Sentinel]: ...

    def check_assignment(
        self, path: Path, value: Expr
    ) -> Union[_Sentinel, list[Diagnostic]]: ...

    def check_comparison(
        self, left: Expr, op: ComparisonOp, right: Expr
    ) -> Union[_Sentinel, list[Diagnostic]]: ...

    def check_workflow_call(
        self, name: str, args: list[Expr]
    ) -> Union[_Sentinel, list[Diagnostic]]: ...


class BaseResolver:
    """
    Resolver with no-op defaults. Subclass this and override only the hooks
    you want to act on; anything you don't override returns
    `UNKNOWN` / `OK` and rulang emits no diagnostic for it.
    """

    def check_path(self, path: Path) -> Union[PathInfo, _Sentinel]:  # noqa: ARG002
        return UNKNOWN

    def check_assignment(
        self, path: Path, value: Expr
    ) -> Union[_Sentinel, list[Diagnostic]]:  # noqa: ARG002
        return OK

    def check_comparison(
        self, left: Expr, op: ComparisonOp, right: Expr
    ) -> Union[_Sentinel, list[Diagnostic]]:  # noqa: ARG002
        return OK

    def check_workflow_call(
        self, name: str, args: list[Expr]
    ) -> Union[_Sentinel, list[Diagnostic]]:  # noqa: ARG002
        return OK


# --- Rulang-owned diagnostic codes --------------------------------------


DIAGNOSTIC_CODES: tuple[str, ...] = (
    "rulang.syntax_error",
    "rulang.unknown_path",
    "rulang.path_not_writable",
    "rulang.type_mismatch",
    "rulang.unknown_workflow",
    "rulang.workflow_arg_mismatch",
    "rulang.invalid_literal",
)

_DEFAULT_SEVERITIES: dict[str, Severity] = {
    "rulang.syntax_error": "error",
    "rulang.unknown_path": "error",
    "rulang.path_not_writable": "error",
    "rulang.type_mismatch": "error",
    "rulang.unknown_workflow": "error",
    "rulang.workflow_arg_mismatch": "error",
    "rulang.invalid_literal": "error",
}


# --- validate() ---------------------------------------------------------


def validate(
    rule_or_text: Union[str, Rule],
    resolver: BaseResolver,
    *,
    severity_overrides: dict[str, Severity] | None = None,
    entity_name: str = "entity",
) -> list[Diagnostic]:
    """
    Validate a rule against a resolver and return the list of diagnostics.

    Never raises for validation issues — even rule parse errors appear as
    `rulang.syntax_error` diagnostics, so callers have a single list to
    display. Programmer errors (e.g. resolver not implementing the
    protocol) may still raise.

    Args:
        rule_or_text: a rule as text or a public AST `Rule`.
        resolver: an object implementing the `Resolver` protocol. Typically
            a subclass of `BaseResolver`.
        severity_overrides: per-code severity overrides, applied last over
            default severities and any severities the resolver chose.
        entity_name: identifier used to prefix bare paths (only relevant
            when `rule_or_text` is a string).
    """
    overrides = severity_overrides or {}
    diagnostics: list[Diagnostic] = []

    if isinstance(rule_or_text, str):
        try:
            rule = parse(rule_or_text, entity_name=entity_name)
        except RuleSyntaxError as exc:
            span: Span | None = None
            if exc.line is not None and exc.column is not None:
                span = Span(start=0, end=len(rule_or_text), line=exc.line, column=exc.column + 1)
            _add(
                diagnostics,
                Diagnostic(
                    code="rulang.syntax_error",
                    message=exc.args[0] if exc.args else str(exc),
                    span=span,
                ),
                overrides,
            )
            return diagnostics
    else:
        rule = rule_or_text

    _validate_condition(rule.condition, resolver, diagnostics, overrides)
    for action in rule.actions:
        _validate_action(action, resolver, diagnostics, overrides)

    return diagnostics


# --- AST traversal ------------------------------------------------------


def _validate_condition(
    cond: Condition,
    resolver: BaseResolver,
    diagnostics: list[Diagnostic],
    overrides: dict[str, Severity],
) -> None:
    if isinstance(cond, (And, Or)):
        _validate_condition(cond.left, resolver, diagnostics, overrides)
        _validate_condition(cond.right, resolver, diagnostics, overrides)
        return
    if isinstance(cond, Not):
        _validate_condition(cond.inner, resolver, diagnostics, overrides)
        return
    if isinstance(cond, Comparison):
        _walk_expr_for_paths(cond.left, resolver, diagnostics, overrides)
        _walk_expr_for_paths(cond.right, resolver, diagnostics, overrides)
        _handle_hook(
            resolver.check_comparison(cond.left, cond.op, cond.right),
            diagnostics,
            overrides,
        )
        return
    if isinstance(cond, Existence):
        _walk_expr_for_paths(cond.expr, resolver, diagnostics, overrides)
        return


def _validate_action(
    action: Any,
    resolver: BaseResolver,
    diagnostics: list[Diagnostic],
    overrides: dict[str, Severity],
) -> None:
    if isinstance(action, (Set_, Compound)):
        info = resolver.check_path(action.path)
        if isinstance(info, PathInfo):
            if not info.exists:
                _add(
                    diagnostics,
                    Diagnostic(
                        code="rulang.unknown_path",
                        message=f"Unknown path: {action.path.to_string(normalize_entity=None)}",
                        span=action.path.span,
                    ),
                    overrides,
                )
            elif not info.writable:
                _add(
                    diagnostics,
                    Diagnostic(
                        code="rulang.path_not_writable",
                        message=f"Path is not writable: {action.path.to_string(normalize_entity=None)}",
                        span=action.path.span,
                    ),
                    overrides,
                )
        _walk_path_indices(action.path, resolver, diagnostics, overrides)
        _walk_expr_for_paths(action.value, resolver, diagnostics, overrides)
        _handle_hook(
            resolver.check_assignment(action.path, action.value),
            diagnostics,
            overrides,
        )
        return

    if isinstance(action, WorkflowCallAction):
        _handle_hook(
            resolver.check_workflow_call(action.name, list(action.args)),
            diagnostics,
            overrides,
        )
        for arg in action.args:
            _walk_expr_for_paths(arg, resolver, diagnostics, overrides)
        return

    if isinstance(action, Return):
        _walk_expr_for_paths(action.value, resolver, diagnostics, overrides)
        return


def _walk_expr_for_paths(
    expr: Expr,
    resolver: BaseResolver,
    diagnostics: list[Diagnostic],
    overrides: dict[str, Severity],
) -> None:
    if isinstance(expr, PathRef):
        info = resolver.check_path(expr.path)
        if isinstance(info, PathInfo) and not info.exists:
            _add(
                diagnostics,
                Diagnostic(
                    code="rulang.unknown_path",
                    message=f"Unknown path: {expr.path.to_string(normalize_entity=None)}",
                    span=expr.path.span,
                ),
                overrides,
            )
        _walk_path_indices(expr.path, resolver, diagnostics, overrides)
        return
    if isinstance(expr, FunctionCall):
        for a in expr.args:
            _walk_expr_for_paths(a, resolver, diagnostics, overrides)
        return
    if isinstance(expr, (Binary, NullCoalesce)):
        _walk_expr_for_paths(expr.left, resolver, diagnostics, overrides)
        _walk_expr_for_paths(expr.right, resolver, diagnostics, overrides)
        return
    if isinstance(expr, Unary):
        _walk_expr_for_paths(expr.expr, resolver, diagnostics, overrides)
        return
    if isinstance(expr, WorkflowCallExpr):
        _handle_hook(
            resolver.check_workflow_call(expr.name, list(expr.args)),
            diagnostics,
            overrides,
        )
        for a in expr.args:
            _walk_expr_for_paths(a, resolver, diagnostics, overrides)
        return
    if isinstance(expr, Literal_) and expr.type == "list":
        for item in expr.value:
            _walk_expr_for_paths(item, resolver, diagnostics, overrides)


def _walk_path_indices(
    path: Path,
    resolver: BaseResolver,
    diagnostics: list[Diagnostic],
    overrides: dict[str, Severity],
) -> None:
    for seg in path.segments:
        if isinstance(seg, IndexSegment):
            _walk_expr_for_paths(seg.expr, resolver, diagnostics, overrides)


# --- Diagnostic plumbing -----------------------------------------------


def _handle_hook(
    result: Any,
    diagnostics: list[Diagnostic],
    overrides: dict[str, Severity],
) -> None:
    if result is OK or result is UNKNOWN:
        return
    if isinstance(result, list):
        for d in result:
            _add(diagnostics, d, overrides)
        return
    if isinstance(result, Diagnostic):
        _add(diagnostics, result, overrides)


def _add(
    diagnostics: list[Diagnostic],
    diagnostic: Diagnostic,
    overrides: dict[str, Severity],
) -> None:
    default_sev = _DEFAULT_SEVERITIES.get(diagnostic.code, diagnostic.severity)
    severity = overrides.get(diagnostic.code, default_sev)
    diagnostics.append(replace(diagnostic, severity=severity))
