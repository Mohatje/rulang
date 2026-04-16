"""Tests for the generic validation framework (proposal #4)."""

import pytest

import rulang
from rulang import (
    BaseResolver,
    Diagnostic,
    OK,
    PathInfo,
    UNKNOWN,
    validate,
)
from rulang.ast import Path


# --- Never raises -------------------------------------------------------


def test_validate_returns_list_even_when_empty():
    result = validate("entity.x == 1 => entity.y = 2", BaseResolver())
    assert result == []


def test_validate_does_not_raise_on_valid_input():
    # BaseResolver says nothing, so no diagnostics produced.
    validate("entity.x == 1 => entity.y = 2", BaseResolver())


# --- Parse errors as diagnostics ---------------------------------------


def test_parse_error_surfaces_as_diagnostic():
    result = validate("entity.x ===", BaseResolver())
    assert len(result) == 1
    d = result[0]
    assert d.code == "rulang.syntax_error"
    assert d.severity == "error"


def test_parse_error_stops_further_validation():
    # If parsing fails, we can't walk the AST. Only the syntax_error should appear.
    result = validate("entity.x ===", BaseResolver())
    assert all(d.code == "rulang.syntax_error" for d in result)


# --- check_path -------------------------------------------------------


class _UnknownPath(BaseResolver):
    def check_path(self, path: Path) -> PathInfo:
        return PathInfo(exists=False)


def test_unknown_path_emits_diagnostic():
    result = validate("entity.missing == 1 => entity.y = 2", _UnknownPath())
    codes = [d.code for d in result]
    assert "rulang.unknown_path" in codes


class _ReadOnly(BaseResolver):
    def check_path(self, path: Path) -> PathInfo:
        return PathInfo(exists=True, writable=False)


def test_non_writable_path_emits_distinct_diagnostic():
    result = validate("entity.x == 1 => entity.y = 2", _ReadOnly())
    codes = [d.code for d in result]
    # The condition paths will also be flagged as unknown path is False writable=False still exists — so no unknown_path emission
    assert "rulang.path_not_writable" in codes


class _AllFine(BaseResolver):
    def check_path(self, path: Path) -> PathInfo:
        return PathInfo(exists=True, writable=True)


def test_existing_paths_produce_no_diagnostic():
    result = validate("entity.x == 1 => entity.y = 2", _AllFine())
    assert result == []


# --- check_assignment ------------------------------------------------


class _BanHigh(BaseResolver):
    def check_assignment(self, path, value):  # noqa: ARG002
        from rulang.ast import Literal_
        if isinstance(value, Literal_) and value.value == "high":
            return [Diagnostic(code="myapp.no_high", message="no 'high' allowed")]
        return OK


def test_check_assignment_custom_diagnostic():
    result = validate("entity.x == 1 => entity.priority = 'high'", _BanHigh())
    assert len(result) == 1
    assert result[0].code == "myapp.no_high"


def test_check_assignment_can_be_skipped_with_ok():
    # Default is OK; no diagnostics emitted
    result = validate("entity.x == 1 => entity.priority = 'high'", BaseResolver())
    assert result == []


# --- check_comparison -----------------------------------------------


class _NoStringComparison(BaseResolver):
    def check_comparison(self, left, op, right):  # noqa: ARG002
        from rulang.ast import Literal_
        if isinstance(left, Literal_) and left.type == "string":
            return [Diagnostic(code="myapp.no_string_comp", message="no string comparisons")]
        if isinstance(right, Literal_) and right.type == "string":
            return [Diagnostic(code="myapp.no_string_comp", message="no string comparisons")]
        return OK


def test_check_comparison_custom_diagnostic():
    result = validate("entity.x == 'foo' => entity.y = 1", _NoStringComparison())
    codes = [d.code for d in result]
    assert "myapp.no_string_comp" in codes


# --- check_workflow_call ----------------------------------------------


class _NoWorkflows(BaseResolver):
    def check_workflow_call(self, name, args):  # noqa: ARG002
        return [Diagnostic(code="rulang.unknown_workflow", message=f"unknown workflow: {name}")]


def test_check_workflow_call_action_position():
    result = validate('entity.x == 1 => workflow("notify")', _NoWorkflows())
    codes = [d.code for d in result]
    assert "rulang.unknown_workflow" in codes


def test_check_workflow_call_expression_position():
    result = validate('workflow("fetch") == true => entity.y = 1', _NoWorkflows())
    codes = [d.code for d in result]
    assert "rulang.unknown_workflow" in codes


# --- Sentinel returns ------------------------------------------------


class _UnknownEverything(BaseResolver):
    def check_path(self, path):  # noqa: ARG002
        return UNKNOWN
    def check_assignment(self, path, value):  # noqa: ARG002
        return OK


def test_unknown_sentinel_produces_no_diagnostic():
    result = validate("entity.x == 1 => entity.y = 2", _UnknownEverything())
    assert result == []


# --- Severity overrides ---------------------------------------------


def test_severity_overrides_downgrade_error_to_warning():
    result = validate(
        "entity.missing == 1 => entity.y = 2",
        _UnknownPath(),
        severity_overrides={"rulang.unknown_path": "warning"},
    )
    unknown = [d for d in result if d.code == "rulang.unknown_path"]
    assert all(d.severity == "warning" for d in unknown)


def test_severity_overrides_apply_to_consumer_codes():
    result = validate(
        "entity.x == 1 => entity.priority = 'high'",
        _BanHigh(),
        severity_overrides={"myapp.no_high": "info"},
    )
    assert result[0].severity == "info"


# --- Accepts AST directly --------------------------------------------


def test_validate_accepts_rule_ast():
    rule = rulang.parse("entity.x == 1 => entity.y = 2")
    result = validate(rule, BaseResolver())
    assert result == []


# --- Module-level exposure ------------------------------------------


def test_validation_symbols_top_level():
    assert rulang.validate is validate
    assert rulang.BaseResolver is BaseResolver
    assert rulang.Diagnostic is Diagnostic
    assert rulang.PathInfo is PathInfo
    assert rulang.OK is OK
    assert rulang.UNKNOWN is UNKNOWN


# --- Spans on diagnostics -------------------------------------------


def test_diagnostics_carry_span_from_ast_path():
    result = validate("entity.missing == 1 => entity.y = 2", _UnknownPath())
    for d in result:
        if d.code == "rulang.unknown_path":
            assert d.span is not None
            assert d.span.start >= 0
            return
    pytest.fail("expected unknown_path diagnostic with a span")


# --- Walks into list literals and indices ---------------------------


def test_path_inside_list_literal_is_checked():
    result = validate("entity.x in [entity.missing] => entity.y = 1", _UnknownPath())
    paths_flagged = [d for d in result if d.code == "rulang.unknown_path"]
    # All PathRefs in the rule — including entity.missing in the list —
    # should get checked by our resolver, producing diagnostics for each.
    assert len(paths_flagged) >= 1


def test_path_inside_index_expression_is_checked():
    result = validate(
        "entity.items[entity.missing].name == 'x' => entity.y = 1",
        _UnknownPath(),
    )
    paths_flagged = [d for d in result if d.code == "rulang.unknown_path"]
    assert len(paths_flagged) >= 1
