"""Tests for the public AST (proposal #1)."""

import pytest

import rulang
from rulang.ast import (
    And,
    Binary,
    Compound,
    Comparison,
    Existence,
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
    Span,
    Unary,
    WorkflowCallAction,
    WorkflowCallExpr,
    parse,
    walk,
)
from rulang.exceptions import RuleSyntaxError


# --- parse() returns a Rule ---------------------------------------------


def test_parse_simple_rule_returns_rule_with_condition_and_actions():
    rule = parse("entity.age >= 18 => entity.is_adult = true")
    assert isinstance(rule, Rule)
    assert isinstance(rule.condition, Comparison)
    assert rule.condition.op == ">="
    assert len(rule.actions) == 1
    assert isinstance(rule.actions[0], Set_)


def test_parse_raises_rule_syntax_error_on_bad_rule():
    with pytest.raises(RuleSyntaxError):
        parse("entity.x ===")


# --- Spans are populated ------------------------------------------------


def test_every_node_has_a_span_from_source():
    rule = parse("entity.age >= 18 => entity.adult = true")
    spans_seen: list[Span] = []

    def _collect(node):
        span = getattr(node, "span", None)
        if span is not None:
            spans_seen.append(span)

    walk(rule, _collect)
    assert len(spans_seen) > 0
    for span in spans_seen:
        assert span.start >= 0
        assert span.end >= span.start
        assert span.line >= 1
        assert span.column >= 1


def test_span_points_into_source_text():
    source = "entity.age >= 18 => entity.adult = true"
    rule = parse(source)
    # Rule span should cover at least 'entity.age' to 'true'
    assert rule.span is not None
    assert source[rule.span.start:rule.span.end].startswith("entity.age")


# --- Condition tree: and, or, not ---------------------------------------


def test_parse_and_or_not_condition_tree():
    rule = parse("not (entity.x == 1 and (entity.y == 2 or entity.z == 3)) => entity.out = 1")
    assert isinstance(rule.condition, Not)
    inner = rule.condition.inner
    assert isinstance(inner, And)
    assert isinstance(inner.left, Comparison)
    assert isinstance(inner.right, Or)


# --- Comparison operators -----------------------------------------------


@pytest.mark.parametrize(
    ("rule_text", "expected_op"),
    [
        ("entity.x == 1 => entity.y = 1", "=="),
        ("entity.x != 1 => entity.y = 1", "!="),
        ("entity.x < 1 => entity.y = 1", "<"),
        ("entity.x > 1 => entity.y = 1", ">"),
        ("entity.x <= 1 => entity.y = 1", "<="),
        ("entity.x >= 1 => entity.y = 1", ">="),
        ("entity.x in [1, 2] => entity.y = 1", "in"),
        ("entity.x not in [1, 2] => entity.y = 1", "not in"),
        ("entity.x contains 'a' => entity.y = 1", "contains"),
        ("entity.x not contains 'a' => entity.y = 1", "not contains"),
        ("entity.x startswith 'a' => entity.y = 1", "startswith"),
        ("entity.x endswith 'a' => entity.y = 1", "endswith"),
        ("entity.x matches 'a' => entity.y = 1", "matches"),
        ("entity.x contains_any [1] => entity.y = 1", "contains_any"),
        ("entity.x contains_all [1] => entity.y = 1", "contains_all"),
    ],
)
def test_comparison_op_is_captured(rule_text, expected_op):
    rule = parse(rule_text)
    assert isinstance(rule.condition, Comparison)
    assert rule.condition.op == expected_op


# --- Existence ----------------------------------------------------------


def test_exists_condition():
    rule = parse("entity.x exists => entity.y = 1")
    assert isinstance(rule.condition, Existence)
    assert rule.condition.kind == "exists"


def test_is_empty_condition():
    rule = parse("entity.x is_empty => entity.y = 1")
    assert isinstance(rule.condition, Existence)
    assert rule.condition.kind == "is_empty"


# --- Literal types ------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected_type", "expected_value"),
    [
        ("entity.x == 42 => entity.y = 1", "int", 42),
        ("entity.x == 3.14 => entity.y = 1", "float", 3.14),
        ("entity.x == 'hello' => entity.y = 1", "string", "hello"),
        ("entity.x == true => entity.y = 1", "bool", True),
        ("entity.x == false => entity.y = 1", "bool", False),
        ("entity.x == none => entity.y = 1", "none", None),
    ],
)
def test_literal_type_inference(text, expected_type, expected_value):
    rule = parse(text)
    lit = rule.condition.right
    assert isinstance(lit, Literal_)
    assert lit.type == expected_type
    assert lit.value == expected_value


def test_list_literal():
    rule = parse("entity.x in [1, 'two', true] => entity.y = 1")
    lit = rule.condition.right
    assert isinstance(lit, Literal_)
    assert lit.type == "list"
    items = lit.value
    assert len(items) == 3
    assert items[0].type == "int"
    assert items[1].type == "string"
    assert items[2].type == "bool"


# --- Paths --------------------------------------------------------------


def test_path_with_plain_fields():
    rule = parse("entity.a.b.c == 1 => entity.x = 1")
    left = rule.condition.left
    assert isinstance(left, PathRef)
    assert left.path.root == "entity"
    assert [s.name for s in left.path.segments if isinstance(s, FieldSegment)] == ["a", "b", "c"]


def test_path_with_null_safe_segment():
    rule = parse("entity.a?.b == 1 => entity.x = 1")
    path = rule.condition.left.path
    assert isinstance(path.segments[0], FieldSegment)
    assert path.segments[0].name == "a"
    assert isinstance(path.segments[1], NullSafeFieldSegment)
    assert path.segments[1].name == "b"


def test_path_with_index_segment():
    rule = parse("entity.items[0].name == 'foo' => entity.x = 1")
    path = rule.condition.left.path
    index_seg = path.segments[1]
    assert isinstance(index_seg, IndexSegment)
    assert isinstance(index_seg.expr, Literal_)
    assert index_seg.expr.value == 0


# --- Actions ------------------------------------------------------------


def test_set_action():
    rule = parse("entity.x == 1 => entity.y = 2")
    assert isinstance(rule.actions[0], Set_)


def test_compound_action_operators():
    for op_text, op in [("+=", "+="), ("-=", "-="), ("*=", "*="), ("/=", "/=")]:
        rule = parse(f"entity.x == 1 => entity.y {op_text} 2")
        action = rule.actions[0]
        assert isinstance(action, Compound)
        assert action.op == op


def test_workflow_call_action():
    rule = parse('entity.x == 1 => workflow("doit", entity.a)')
    action = rule.actions[0]
    assert isinstance(action, WorkflowCallAction)
    assert action.name == "doit"
    assert len(action.args) == 1


def test_return_action():
    rule = parse("entity.x == 1 => ret 'hit'")
    action = rule.actions[0]
    assert isinstance(action, Return)
    assert action.value.value == "hit"


def test_multiple_actions():
    rule = parse("entity.x == 1 => entity.a = 1; entity.b = 2; ret 'done'")
    assert len(rule.actions) == 3
    assert isinstance(rule.actions[0], Set_)
    assert isinstance(rule.actions[1], Set_)
    assert isinstance(rule.actions[2], Return)


# --- Expressions --------------------------------------------------------


def test_function_call_expression():
    rule = parse("lower(entity.name) == 'abc' => entity.y = 1")
    left = rule.condition.left
    assert isinstance(left, FunctionCall)
    assert left.name == "lower"
    assert len(left.args) == 1


def test_binary_arithmetic_expression():
    rule = parse("entity.x + 1 == 10 => entity.y = 1")
    left = rule.condition.left
    assert isinstance(left, Binary)
    assert left.op == "+"


def test_null_coalesce_expression():
    rule = parse("entity.x ?? 0 == 5 => entity.y = 1")
    left = rule.condition.left
    assert isinstance(left, NullCoalesce)


def test_unary_minus_expression():
    # `-5` literal gets lexed as a signed number; use a path to force UnaryExpr.
    rule = parse("entity.x == -entity.y => entity.z = 1")
    right = rule.condition.right
    assert isinstance(right, Unary)
    assert right.op == "-"
    assert isinstance(right.expr, PathRef)


def test_workflow_call_in_expression():
    rule = parse('entity.x == workflow("get_x", entity.id) => entity.y = 1')
    right = rule.condition.right
    assert isinstance(right, WorkflowCallExpr)
    assert right.name == "get_x"


# --- Extractors: reads / writes / workflow_calls ------------------------


def test_reads_writes_extraction():
    rule = parse("entity.age >= 18 and entity.status == 'active' => entity.adult = true")
    assert rule.reads == frozenset({"entity.age", "entity.status"})
    assert rule.writes == frozenset({"entity.adult"})
    assert rule.workflow_calls == frozenset()


def test_compound_action_reads_target():
    rule = parse("entity.x == 1 => entity.count += 1")
    assert "entity.count" in rule.reads  # compound reads before writing
    assert "entity.count" in rule.writes


def test_workflow_call_extraction():
    rule = parse('entity.x == 1 => workflow("notify", entity.email); workflow("log")')
    assert rule.workflow_calls == frozenset({"notify", "log"})


def test_workflow_call_in_expression_position_is_tracked():
    rule = parse('workflow("fetch", entity.id) == true => entity.y = 1')
    assert "fetch" in rule.workflow_calls


def test_path_normalization_with_entity_prefix():
    # Rules written without the explicit `entity.` prefix should normalize
    rule = parse("age >= 18 => adult = true", entity_name="entity")
    assert "entity.age" in rule.reads
    assert "entity.adult" in rule.writes


def test_custom_entity_name():
    rule = parse("shipment.weight > 100 => shipment.heavy = true", entity_name="shipment")
    assert "shipment.weight" in rule.reads
    assert "shipment.heavy" in rule.writes


# --- Literals helper ----------------------------------------------------


def test_rule_literals_returns_all_literals():
    rule = parse("entity.x == 1 and entity.y == 'foo' => entity.z = true")
    lits = rule.literals
    values = [l.value for l in lits]
    assert 1 in values
    assert "foo" in values
    assert True in values


# --- walk() -------------------------------------------------------------


def test_walk_visits_every_node_once():
    rule = parse("entity.x + 1 > 5 => entity.y = 'hi'")
    count = [0]

    def _v(_):
        count[0] += 1

    walk(rule, _v)
    # Rough sanity: should visit condition, left Binary, PathRef, Path, Literal, right Literal, action, path, literal
    assert count[0] >= 6


def test_walk_does_not_recurse_into_literal_scalars():
    rule = parse("entity.x == 42 => entity.y = 1")
    types = []

    def _v(node):
        types.append(type(node).__name__)

    walk(rule, _v)
    # Int literal should appear; there should be no "int" type in the walk output
    assert "Literal_" in types
    assert "int" not in types


# --- Path.to_string rendering -------------------------------------------


def test_path_to_string_basic():
    rule = parse("entity.a.b.c == 1 => entity.x = 1")
    path = rule.condition.left.path
    assert path.to_string(normalize_entity="entity") == "entity.a.b.c"


def test_path_to_string_adds_entity_prefix_if_missing():
    rule = parse("a.b == 1 => x = 1", entity_name="entity")
    path = rule.condition.left.path
    assert path.to_string(normalize_entity="entity") == "entity.a.b"


def test_path_to_string_no_normalize():
    rule = parse("entity.a == 1 => x = 1", entity_name="entity")
    path = rule.condition.left.path
    assert path.to_string(normalize_entity=None) == "entity.a"


def test_path_to_string_indices_star():
    rule = parse("entity.items[0].name == 'x' => entity.y = 1")
    path = rule.condition.left.path
    s = path.to_string(normalize_entity="entity", include_indices=False)
    assert "[*]" in s


# --- Module-level re-exports --------------------------------------------


def test_rulang_top_level_exposes_parse_and_walk():
    assert rulang.parse is parse
    assert rulang.walk is walk


def test_rulang_top_level_exposes_ast_types():
    # Quick sanity — not exhaustive
    assert rulang.Rule is Rule
    assert rulang.Span is Span
    assert rulang.Path is Path
