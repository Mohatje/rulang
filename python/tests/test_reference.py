"""Tests for the bundled grammar reference (proposal #7)."""

import re

import pytest

import rulang
from rulang import grammar_reference, parse


def test_grammar_reference_returns_non_empty_string():
    text = grammar_reference()
    assert isinstance(text, str)
    assert len(text) > 500


def test_grammar_reference_is_exposed_at_top_level():
    assert rulang.grammar_reference is grammar_reference


def test_grammar_reference_mentions_major_sections():
    text = grammar_reference()
    for heading in [
        "Rule structure",
        "Condition operators",
        "Path access",
        "Literals",
        "Built-in functions",
        "Assignment",
        "Workflow calls",
    ]:
        assert heading in text, f"missing section: {heading}"


def test_grammar_reference_lists_core_operators():
    text = grammar_reference()
    # Token shown in the doc's operator tables
    for op in ["==", "!=", "<=", ">=", "and", "or", "not", "in", "contains", "startswith",
               "endswith", "matches", "contains_any", "contains_all", "exists", "is_empty",
               "?.", "??"]:
        assert op in text, f"operator missing from reference: {op}"


def test_grammar_reference_lists_builtin_functions():
    text = grammar_reference()
    from rulang.visitor import BUILTIN_FUNCTIONS

    for name in BUILTIN_FUNCTIONS:
        # Be forgiving — the doc may present the function as `fn(x)` or as a group reference.
        assert name in text, f"builtin missing from reference: {name}"


def _extract_code_blocks(text: str) -> list[str]:
    return re.findall(r"```\n(.*?)\n```", text, flags=re.DOTALL)


def test_every_rule_example_in_the_reference_parses():
    text = grammar_reference()
    blocks = _extract_code_blocks(text)
    # Skip blocks that contain grammar placeholders like `<condition>`.
    rule_blocks = [b for b in blocks if "=>" in b and "<" not in b]
    assert len(rule_blocks) >= 5, "expected several rule examples in the reference"

    for block in rule_blocks:
        # Some blocks may show multiple rules separated by blank lines
        for rule_text in filter(None, (ln.strip() for ln in block.splitlines())):
            if "=>" not in rule_text:
                continue
            try:
                parse(rule_text)
            except Exception as exc:  # noqa: BLE001
                pytest.fail(f"example failed to parse: {rule_text!r}\n{exc}")


def test_grammar_reference_reflects_signature_example():
    # Smoke — the canonical signature pattern should appear literally.
    text = grammar_reference()
    assert "=> <action>" in text
