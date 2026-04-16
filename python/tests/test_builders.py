"""Tests for builder primitives (proposal #2)."""

import pytest

import rulang
from rulang import format, parse
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
    PathRef,
    Return,
    Rule,
    Set_,
    Unary,
    WorkflowCallAction,
    WorkflowCallExpr,
)
from rulang.builders import (
    and_,
    binary,
    compound,
    contains,
    contains_all,
    contains_any,
    endswith,
    eq,
    exists,
    fn,
    gt,
    gte,
    in_,
    is_empty,
    lit,
    lt,
    lte,
    matches,
    neq,
    not_,
    not_contains,
    not_in,
    null_coalesce,
    or_,
    path_of,
    pathref,
    ret,
    rule,
    set_,
    startswith,
    unary,
    workflow_call,
    workflow_expr,
)


# --- path_of -----------------------------------------------------------


def test_path_of_positional_parts():
    p = path_of("entity", "a", "b")
    assert p.root == "entity"
    names = [s.name for s in p.segments if isinstance(s, FieldSegment)]
    assert names == ["a", "b"]


def test_path_of_dotted_string():
    p = path_of("entity.a.b")
    assert p.root == "entity"
    assert [s.name for s in p.segments if isinstance(s, FieldSegment)] == ["a", "b"]


def test_path_of_int_index():
    p = path_of("entity", "items", 0, "name")
    idx = [s for s in p.segments if isinstance(s, IndexSegment)]
    assert len(idx) == 1
    assert idx[0].expr.value == 0


def test_path_of_null_safe_in_dotted():
    p = path_of("entity.a?.b")
    assert any(isinstance(s, NullSafeFieldSegment) for s in p.segments)


def test_path_of_null_safe_in_positional():
    p = path_of("entity", "?.a", "b")
    assert isinstance(p.segments[0], NullSafeFieldSegment)
    assert p.segments[0].name == "a"


# --- lit ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected_type"),
    [
        (None, "none"),
        (True, "bool"),
        (False, "bool"),
        (42, "int"),
        (3.14, "float"),
        ("hello", "string"),
    ],
)
def test_lit_infers_type(value, expected_type):
    assert lit(value).type == expected_type


def test_lit_list():
    result = lit([1, "two", True])
    assert result.type == "list"
    assert len(result.value) == 3
    assert result.value[0].type == "int"
    assert result.value[1].type == "string"
    assert result.value[2].type == "bool"


# --- pathref / fn / binary / unary / null_coalesce --------------------


def test_pathref_from_string():
    r = pathref("entity.a")
    assert isinstance(r, PathRef)
    assert r.path.root == "entity"


def test_fn_builds_function_call():
    r = fn("lower", pathref("entity.name"))
    assert isinstance(r, FunctionCall)
    assert r.name == "lower"
    assert len(r.args) == 1


def test_binary_and_unary():
    b = binary(pathref("entity.x"), "+", 1)
    assert isinstance(b, Binary)
    assert b.op == "+"
    u = unary(pathref("entity.x"))
    assert isinstance(u, Unary)


def test_binary_rejects_invalid_op():
    with pytest.raises(ValueError):
        binary(1, "**", 2)


def test_null_coalesce():
    n = null_coalesce(pathref("entity.a"), lit("default"))
    assert isinstance(n, NullCoalesce)


def test_workflow_expr():
    w = workflow_expr("score", pathref("entity.id"))
    assert isinstance(w, WorkflowCallExpr)
    assert w.name == "score"


# --- Comparisons -------------------------------------------------------


@pytest.mark.parametrize(
    ("fn_", "expected_op"),
    [
        (eq, "=="),
        (neq, "!="),
        (lt, "<"),
        (gt, ">"),
        (lte, "<="),
        (gte, ">="),
        (in_, "in"),
        (not_in, "not in"),
        (contains, "contains"),
        (not_contains, "not contains"),
        (startswith, "startswith"),
        (endswith, "endswith"),
        (matches, "matches"),
        (contains_any, "contains_any"),
        (contains_all, "contains_all"),
    ],
)
def test_comparison_builders(fn_, expected_op):
    c = fn_(pathref("entity.x"), lit(1))
    assert isinstance(c, Comparison)
    assert c.op == expected_op


def test_comparison_coerces_raw_values():
    c = eq("entity.x", 1)  # raw string + raw int
    # "entity.x" becomes a string literal (not a path) because lit() is applied
    assert isinstance(c.left, Literal_)


def test_comparison_with_pathref_shortcut():
    c = eq(pathref("entity.age"), 18)
    assert isinstance(c.left, PathRef)
    assert isinstance(c.right, Literal_)
    assert c.right.value == 18


# --- Existence ---------------------------------------------------------


def test_exists_builder():
    e = exists(pathref("entity.x"))
    assert isinstance(e, Existence)
    assert e.kind == "exists"


def test_is_empty_builder():
    e = is_empty(pathref("entity.x"))
    assert e.kind == "is_empty"


# --- Logical ----------------------------------------------------------


def test_and_two_args():
    c1 = eq(pathref("entity.a"), 1)
    c2 = eq(pathref("entity.b"), 2)
    combined = and_(c1, c2)
    assert isinstance(combined, And)


def test_and_three_args_is_left_associative():
    c1 = eq(pathref("entity.a"), 1)
    c2 = eq(pathref("entity.b"), 2)
    c3 = eq(pathref("entity.c"), 3)
    combined = and_(c1, c2, c3)
    assert isinstance(combined, And)
    assert isinstance(combined.left, And)
    assert combined.right is c3


def test_and_requires_two_or_more():
    with pytest.raises(ValueError):
        and_(eq(pathref("entity.a"), 1))


def test_or_and_not():
    c1 = eq(pathref("entity.a"), 1)
    c2 = eq(pathref("entity.b"), 2)
    assert isinstance(or_(c1, c2), Or)
    assert isinstance(not_(c1), Not)


# --- Actions ----------------------------------------------------------


def test_set_action():
    s = set_(pathref("entity.y").path, lit(42))
    assert isinstance(s, Set_)


def test_set_action_accepts_string_path():
    s = set_("entity.y", 42)
    assert isinstance(s, Set_)
    assert s.path.root == "entity"


def test_compound_action():
    c = compound("entity.count", "+=", 1)
    assert isinstance(c, Compound)
    assert c.op == "+="


def test_compound_rejects_invalid_op():
    with pytest.raises(ValueError):
        compound("entity.x", "**=", 1)


def test_workflow_call_action():
    w = workflow_call("notify", pathref("entity.email"))
    assert isinstance(w, WorkflowCallAction)
    assert w.name == "notify"


def test_ret_action():
    r = ret("done")
    assert isinstance(r, Return)


# --- Rule builder -----------------------------------------------------


def test_rule_builder_constructs_rule():
    r = rule(
        condition=eq(pathref("entity.age"), 18),
        actions=[set_("entity.adult", True)],
    )
    assert isinstance(r, Rule)
    assert isinstance(r.condition, Comparison)
    assert len(r.actions) == 1


def test_rule_builder_populates_reads_writes():
    r = rule(
        condition=and_(
            gte(pathref("entity.age"), 18),
            eq(pathref("entity.status"), "active"),
        ),
        actions=[set_("entity.adult", True)],
    )
    assert "entity.age" in r.reads
    assert "entity.status" in r.reads
    assert "entity.adult" in r.writes


def test_rule_builder_tracks_workflow_calls():
    r = rule(
        condition=eq(pathref("entity.x"), 1),
        actions=[workflow_call("notify", pathref("entity.email"))],
    )
    assert "notify" in r.workflow_calls


# --- Round-trip guarantees --------------------------------------------


def test_format_of_built_rule_parses_back():
    r = rule(
        condition=and_(
            gte(pathref("entity.age"), 18),
            eq(pathref("entity.status"), "active"),
        ),
        actions=[set_("entity.adult", True)],
    )
    text = format(r)
    reparsed = parse(text)
    assert text == format(reparsed)


def test_format_built_rule_produces_expected_text():
    r = rule(
        condition=eq(pathref("entity.age"), 18),
        actions=[set_("entity.adult", True)],
    )
    assert format(r) == "entity.age == 18 => entity.adult = true"


def test_format_idempotent_after_build():
    r = rule(
        condition=gt(binary(pathref("entity.x"), "+", 1), 5),
        actions=[ret(lit("hi"))],
    )
    once = format(r)
    twice = format(parse(once))
    assert once == twice


# --- Module namespace -------------------------------------------------


def test_builders_module_exposed():
    assert hasattr(rulang, "builders")
    assert rulang.builders.path_of is path_of
