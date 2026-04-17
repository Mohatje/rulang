"""Targeted tests to cover edge cases in the new modules.

These fill coverage gaps around error handling, object-with-__dict__
diffing, workflow arg walking, etc.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from rulang import (
    BaseResolver,
    PathInfo,
    RuleEngine,
    format,
    parse,
    validate,
)
from rulang.ast import Binary, FunctionCall, Literal_, Path, Unary
from rulang.builders import (
    binary,
    compound,
    eq,
    fn,
    int_lit,
    float_lit,
    lit,
    path_of,
    pathref,
    set_,
    unary,
    workflow_call,
    workflow_expr,
)
from rulang.dry_run import _diff_entities, _same


# --- dry_run: _diff_entities edge cases --------------------------------


def test_diff_entities_same_returns_empty():
    assert _diff_entities({"a": 1}, {"a": 1}) == {}


def test_diff_entities_type_mismatch_records_whole_node():
    assert _diff_entities({"a": 1}, [1]) == {"<root>": ({"a": 1}, [1])}


def test_diff_entities_list_length_mismatch():
    diff = _diff_entities([1, 2], [1, 2, 3])
    assert "<root>" in diff


def test_diff_entities_dict_key_added():
    diff = _diff_entities({"a": 1}, {"a": 1, "b": 2})
    assert diff == {"b": (None, 2)}


def test_diff_entities_dict_key_removed():
    diff = _diff_entities({"a": 1, "b": 2}, {"a": 1})
    assert diff == {"b": (2, None)}


def test_diff_entities_object_dict():
    @dataclass
    class E:
        x: int = 0

    before = E(1)
    after = E(2)
    diff = _diff_entities(before, after)
    assert diff == {"x": (1, 2)}


def test_same_handles_incompatible_types():
    class WeirdEq:
        def __eq__(self, other):
            raise TypeError("no")

    a = WeirdEq()
    b = WeirdEq()
    # Falls back to identity
    assert _same(a, a) is True
    assert _same(a, b) is False


def test_dry_run_against_object_entity_diffs_attrs():
    @dataclass
    class E:
        x: int = 1
        y: int = 0

    engine = RuleEngine()
    engine.add_rules("entity.x == 1 => entity.y = 42")
    result = engine.dry_run(E(1, 0))
    assert result.diff == {"y": (0, 42)}
    assert result.final_entity.y == 42


# --- validation: walking into NullCoalesce / Binary / Unary ------------


class _UnknownResolver(BaseResolver):
    def check_path(self, path: Path) -> PathInfo:
        return PathInfo(exists=False)


def test_validation_walks_into_null_coalesce():
    result = validate("entity.x ?? entity.fallback == 5 => entity.y = 1", _UnknownResolver())
    assert any(d.code == "rulang.unknown_path" for d in result)


def test_validation_walks_into_binary():
    result = validate("entity.x + entity.y == 5 => entity.z = 1", _UnknownResolver())
    assert sum(1 for d in result if d.code == "rulang.unknown_path") >= 2


def test_validation_walks_into_unary():
    result = validate("entity.x == -entity.y => entity.z = 1", _UnknownResolver())
    assert any(d.code == "rulang.unknown_path" for d in result)


def test_validation_walks_into_workflow_args():
    result = validate(
        'entity.x == 1 => workflow("notify", entity.missing)',
        _UnknownResolver(),
    )
    assert any(d.code == "rulang.unknown_path" for d in result)


def test_validation_walks_into_return_expression():
    result = validate("entity.x == 1 => ret entity.missing", _UnknownResolver())
    assert any(d.code == "rulang.unknown_path" for d in result)


# --- builders: parity helpers + edge cases -----------------------------


def test_int_lit_truncates_floats():
    assert int_lit(3.9).value == 3


def test_float_lit_preserves_whole_numbers_as_float():
    out = float_lit(3)
    assert out.type == "float"
    assert out.value == 3.0


def test_path_of_requires_at_least_one_part():
    with pytest.raises(ValueError):
        path_of()


def test_path_of_rejects_non_string_root():
    with pytest.raises(TypeError):
        path_of(123)  # type: ignore[arg-type]


def test_path_of_accepts_expression_index():
    # Pass an Expr in an index position
    expr = binary(lit(1), "+", lit(2))
    p = path_of("entity", "items", expr)
    assert p.segments[-1].__class__.__name__ == "IndexSegment"


def test_null_coalesce_round_trips_through_format():
    from rulang.builders import null_coalesce
    r = set_("entity.y", null_coalesce(pathref("entity.a"), lit("default")))
    from rulang.builders import rule
    built = rule(eq(pathref("entity.x"), 1), [r])
    text = format(built)
    assert format(parse(text)) == text


def test_workflow_expr_in_expression_position():
    from rulang.builders import rule
    r = rule(eq(workflow_expr("lookup", lit(1)), lit(True)), [set_("entity.y", 1)])
    text = format(r)
    assert "workflow(" in text


# --- formatter: edge cases --------------------------------------------


def test_formatter_rejects_unknown_expr_type():
    # Ensure a Binary with an invalid op surfaces a clear error
    from rulang.formatter import _format_expr, _P_OR

    class _Fake:
        pass

    with pytest.raises(RuntimeError):
        _format_expr(_Fake(), _P_OR)  # type: ignore[arg-type]


def test_format_string_escapes_backslash_then_quote():
    rule_text = "entity.x == 'a\\\\b' => entity.y = 1"
    assert "'a\\\\b'" in format(rule_text)


def test_format_single_operand_comparison_becomes_eq_true():
    # A bare path in condition position has its == true wrapper applied
    text = format("entity.flag => entity.y = 1")
    assert "entity.flag == true" in text


# --- AST extra coverage -----------------------------------------------


def test_literals_helper_returns_all_literal_nodes():
    rule = parse("entity.x == 1 and entity.y == 'foo' => entity.z = 99")
    lits = rule.literals
    values = [l.value for l in lits]
    assert 1 in values
    assert "foo" in values
    assert 99 in values


def test_path_to_string_with_indices_preserved():
    rule = parse("entity.items[0].name == 'x' => entity.y = 1")
    path = rule.condition.left.path
    s = path.to_string(normalize_entity="entity", include_indices=True)
    assert "[0]" in s


def test_walk_visits_all_major_node_types():
    """One comprehensive rule that touches every AST variant."""
    from rulang import walk

    text = (
        "(entity.a == 1 or entity.b != 2) "
        "and not entity.c "
        "and entity.d exists "
        "and entity.e is_empty "
        "and lower(entity.name) contains 'x' "
        "and entity.items[0] == 1 "
        "and entity.fallback ?? 'x' == 'x' "
        "and -entity.n + 1 > 0 "
        "and workflow(\"w\", entity.q) == true "
        "=> entity.x = 1; entity.y += 2; workflow(\"k\"); ret 'done'"
    )
    rule = parse(text)
    types_seen = set()

    def _v(node):
        types_seen.add(type(node).__name__)

    walk(rule, _v)

    # Confirm every node-kind was visited at least once
    for name in [
        "And",
        "Or",
        "Not",
        "Comparison",
        "Existence",
        "Set_",
        "Compound",
        "WorkflowCallAction",
        "Return",
        "PathRef",
        "FunctionCall",
        "Binary",
        "NullCoalesce",
        "Unary",
        "WorkflowCallExpr",
        "Path",
        "Literal_",
    ]:
        assert name in types_seen, f"walk did not visit any {name}"


def test_path_to_string_renders_pathref_inside_index():
    # Exercise the "PathRef inside IndexSegment" branch of the path renderer.
    rule = parse("entity.items[entity.idx].name == 'x' => entity.y = 1")
    path = rule.condition.left.path
    s = path.to_string(normalize_entity="entity", include_indices=True)
    # When indices are preserved, the nested PathRef should render as entity.idx
    assert "[entity.idx]" in s
