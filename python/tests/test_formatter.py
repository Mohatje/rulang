"""Tests for the canonical formatter (proposal #3)."""

import pytest

import rulang
from rulang import format, format_ast, parse
from rulang.ast import (
    And,
    Comparison,
    Literal_,
    Or,
    PathRef,
    Set_,
)


# --- Basic formatting ---------------------------------------------------


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        # whitespace normalization
        ("entity.x==1=>entity.y=2", "entity.x == 1 => entity.y = 2"),
        ("entity.x   ==   1  =>  entity.y   =  2", "entity.x == 1 => entity.y = 2"),
        # action separator
        (
            "entity.x == 1 => entity.a=1;entity.b=2",
            "entity.x == 1 => entity.a = 1; entity.b = 2",
        ),
        # double-quoted string becomes single-quoted
        ('entity.x == "hi" => entity.y = 1', "entity.x == 'hi' => entity.y = 1"),
        # boolean / none lowercase
        ("entity.x == True => entity.y = False", "entity.x == true => entity.y = false"),
        ("entity.x == null => entity.y = None", "entity.x == none => entity.y = none"),
        # alias operators collapse to canonical
        ("entity.x starts_with 'a' => entity.y = 1", "entity.x startswith 'a' => entity.y = 1"),
        ("entity.x ends_with 'a' => entity.y = 1", "entity.x endswith 'a' => entity.y = 1"),
    ],
)
def test_canonical_form(input_text, expected):
    assert format(input_text) == expected


# --- Idempotence and round-trip ----------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "entity.x == 1 => entity.y = 2",
        "entity.a and entity.b => entity.c = 'hi'",
        "entity.x == 1 or entity.y == 2 => entity.z = true",
        "not entity.x == 1 => entity.y = 2",
        "entity.x >= 18 and entity.s == 'ok' => entity.r = true",
        "entity.items[0].name == 'foo' => entity.hit = true",
        "entity.x + 1 * 2 == 3 => entity.y = 1",
        "(entity.x + 1) * 2 == 4 => entity.y = 1",
        "entity.x ?? 0 == 5 => entity.y = 1",
        "lower(entity.name) == 'bob' => entity.y = 1",
        'workflow("log", entity.id) => entity.y = 1',
        "entity.x in [1, 2, 3] => entity.y = 1",
        "entity.x not in [1, 2] => entity.y = 1",
        "entity.x exists => entity.y = 1",
        "entity.x is_empty => entity.y = 1",
        "entity.x == 1 => entity.count += 1",
        "entity.x == 1 => ret 'done'",
    ],
)
def test_format_is_idempotent(text):
    once = format(text)
    twice = format(once)
    assert once == twice


@pytest.mark.parametrize(
    "text",
    [
        "entity.age >= 18 => entity.adult = true",
        "entity.x == 1 or entity.y == 2 and entity.z == 3 => entity.r = 'hit'",
        "not (entity.a or entity.b) => entity.x = 1",
        "(entity.a or entity.b) and entity.c => entity.x = 1",
        "entity.items[-1].price == 20 => ret true",
        "entity.x ?? 'default' == 'default' => entity.y = 1",
        "entity.a?.b?.c exists => entity.r = 1",
    ],
)
def test_format_round_trip_preserves_ast(text):
    original = parse(text)
    formatted = format(text)
    reparsed = parse(formatted)
    assert _strip_spans(original) == _strip_spans(reparsed)


# --- Parentheses only where needed --------------------------------------


def test_and_binds_tighter_than_or():
    # a or b and c — `b and c` groups; parens would be redundant
    out = format("entity.a or entity.b and entity.c => entity.r = 1")
    assert out == "entity.a == true or entity.b == true and entity.c == true => entity.r = 1"


def test_parens_preserved_for_or_under_and():
    out = format("(entity.a or entity.b) and entity.c => entity.r = 1")
    assert "(entity.a == true or entity.b == true) and" in out


def test_mul_binds_tighter_than_add():
    out = format("entity.x == entity.a + entity.b * 2 => entity.y = 1")
    assert out == "entity.x == entity.a + entity.b * 2 => entity.y = 1"


def test_parens_preserved_for_add_under_mul():
    out = format("entity.x == (entity.a + entity.b) * 2 => entity.y = 1")
    assert "(entity.a + entity.b) * 2" in out


def test_not_wraps_and_in_parens():
    out = format("not (entity.a and entity.b) => entity.r = 1")
    assert "not (entity.a == true and entity.b == true)" in out


# --- String escaping ----------------------------------------------------


def test_string_with_embedded_single_quote_is_escaped():
    rule = parse("entity.x == \"it's\" => entity.y = 1")
    assert format(rule) == "entity.x == 'it\\'s' => entity.y = 1"


def test_string_with_backslash_is_escaped():
    rule = parse(r"entity.x == 'a\\b' => entity.y = 1")
    # The original has 'a\\b' — the AST value is 'a\b' (one backslash)
    out = format(rule)
    assert "'a\\\\b'" in out


def test_string_with_newline_escaped_back():
    # Build an AST programmatically with a newline value
    rule = parse("entity.x == 'hi\\nworld' => entity.y = 1")
    out = format(rule)
    assert "'hi\\nworld'" in out


# --- Numeric formatting -------------------------------------------------


def test_int_no_trailing_zero():
    assert format("entity.x == 5 => entity.y = 1") == "entity.x == 5 => entity.y = 1"


def test_float_has_decimal():
    out = format("entity.x == 3.14 => entity.y = 1")
    assert "3.14" in out


# --- format accepts AST or string ---------------------------------------


def test_format_accepts_ast():
    rule = parse("entity.x == 1 => entity.y = 2")
    assert format(rule) == "entity.x == 1 => entity.y = 2"


def test_format_ast_is_alias():
    rule = parse("entity.x == 1 => entity.y = 2")
    assert format_ast(rule) == format(rule)


def test_format_propagates_syntax_errors():
    with pytest.raises(rulang.RuleSyntaxError):
        format("entity.x ===")


# --- Custom entity name is preserved -----------------------------------


def test_custom_entity_name():
    out = format("shipment.weight > 100 => shipment.heavy = true", entity_name="shipment")
    assert out == "shipment.weight > 100 => shipment.heavy = true"


# --- Helper: strip spans for structural equality -----------------------


def _strip_spans(node):
    """Return a span-free representation for structural equality."""
    if isinstance(node, tuple):
        return tuple(_strip_spans(x) for x in node)
    if isinstance(node, list):
        return [_strip_spans(x) for x in node]
    if isinstance(node, frozenset):
        return node
    if isinstance(node, set):
        return node
    if hasattr(node, "__dataclass_fields__"):
        cls = type(node)
        out = {}
        for f in node.__dataclass_fields__.values():
            if f.name in ("span", "source"):
                continue
            out[f.name] = _strip_spans(getattr(node, f.name))
        return (cls.__name__, out)
    return node
