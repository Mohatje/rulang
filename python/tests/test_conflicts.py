"""Tests for conflict detection (proposal #5)."""

import pytest

import rulang
from rulang import Conflict, detect_conflicts, parse


# --- Duplicate ---------------------------------------------------------


def test_duplicate_identical_rules():
    conflicts = detect_conflicts([
        "entity.x == 1 => entity.y = 2",
        "entity.x == 1 => entity.y = 2",
    ])
    assert len(conflicts) == 1
    assert conflicts[0].kind == "duplicate"
    assert conflicts[0].rule_indices == (0, 1)


def test_duplicate_detected_across_whitespace_variants():
    conflicts = detect_conflicts([
        "entity.x == 1 => entity.y = 2",
        "entity.x==1=>entity.y=2",
    ])
    assert len(conflicts) == 1
    assert conflicts[0].kind == "duplicate"


def test_duplicate_detected_across_quote_styles():
    conflicts = detect_conflicts([
        "entity.status == 'active' => entity.ok = true",
        'entity.status == "active" => entity.ok = true',
    ])
    assert len(conflicts) == 1
    assert conflicts[0].kind == "duplicate"


def test_duplicate_detected_across_alias_operators():
    conflicts = detect_conflicts([
        "entity.name starts_with 'A' => entity.y = 1",
        "entity.name startswith 'A' => entity.y = 1",
    ])
    assert len(conflicts) == 1
    assert conflicts[0].kind == "duplicate"


def test_non_duplicate_rules_produce_no_conflict():
    conflicts = detect_conflicts([
        "entity.x == 1 => entity.y = 2",
        "entity.x == 2 => entity.y = 3",
    ])
    assert conflicts == []


# --- Contradiction -----------------------------------------------------


def test_contradiction_same_condition_different_literal_values():
    conflicts = detect_conflicts([
        "entity.x == 1 => entity.y = 'a'",
        "entity.x == 1 => entity.y = 'b'",
    ])
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c.kind == "contradiction"
    assert c.rule_indices == (0, 1)
    assert "entity.y" in c.fields
    assert c.diff["entity.y"] == (("string", "a"), ("string", "b"))


def test_contradiction_reports_multiple_fields():
    conflicts = detect_conflicts([
        "entity.x == 1 => entity.a = 1; entity.b = 2",
        "entity.x == 1 => entity.a = 9; entity.b = 8",
    ])
    c = conflicts[0]
    assert c.kind == "contradiction"
    assert set(c.fields) == {"entity.a", "entity.b"}


def test_no_contradiction_when_writes_agree():
    conflicts = detect_conflicts([
        "entity.x == 1 => entity.y = 1; entity.a = 1",
        "entity.x == 1 => entity.y = 1; entity.b = 2",
    ])
    # Rules have identical condition but no conflicting literal writes on shared path
    # (they don't share a write path). So: no contradiction in all_match.
    assert all(c.kind != "contradiction" for c in conflicts)


def test_contradiction_ignores_non_literal_rhs():
    conflicts = detect_conflicts([
        "entity.x == 1 => entity.y = entity.a",
        "entity.x == 1 => entity.y = entity.b",
    ])
    # RHS are expressions, not literals — v1 does not compare those.
    assert all(c.kind != "contradiction" for c in conflicts)


# --- Shadowing (first_match) -------------------------------------------


def test_shadowing_first_match_identical_conditions():
    conflicts = detect_conflicts(
        [
            "entity.x == 1 => entity.a = 1",
            "entity.x == 1 => entity.b = 2",
        ],
        mode="first_match",
    )
    assert len(conflicts) == 1
    assert conflicts[0].kind == "shadowing"
    assert conflicts[0].rule_indices == (0, 1)


def test_no_shadowing_in_all_match_for_non_conflicting_writes():
    conflicts = detect_conflicts(
        [
            "entity.x == 1 => entity.a = 1",
            "entity.x == 1 => entity.b = 2",
        ],
        mode="all_match",
    )
    assert conflicts == []


def test_duplicate_supersedes_shadowing():
    conflicts = detect_conflicts(
        [
            "entity.x == 1 => entity.y = 2",
            "entity.x == 1 => entity.y = 2",
        ],
        mode="first_match",
    )
    assert len(conflicts) == 1
    assert conflicts[0].kind == "duplicate"


def test_duplicate_supersedes_contradiction_when_identical():
    conflicts = detect_conflicts(
        [
            "entity.x == 1 => entity.y = 1; entity.z = 1",
            "entity.x == 1 => entity.y = 1; entity.z = 1",
        ],
    )
    assert len(conflicts) == 1
    assert conflicts[0].kind == "duplicate"


# --- Accept AST directly ------------------------------------------------


def test_accepts_rule_ast_inputs():
    a = parse("entity.x == 1 => entity.y = 2")
    b = parse("entity.x == 1 => entity.y = 2")
    conflicts = detect_conflicts([a, b])
    assert len(conflicts) == 1
    assert conflicts[0].kind == "duplicate"


def test_mixed_string_and_ast_inputs():
    ast = parse("entity.x == 1 => entity.y = 2")
    conflicts = detect_conflicts([ast, "entity.x == 1 => entity.y = 2"])
    assert len(conflicts) == 1
    assert conflicts[0].kind == "duplicate"


# --- No false positives -------------------------------------------------


def test_different_conditions_do_not_conflict():
    conflicts = detect_conflicts([
        "entity.x == 1 => entity.y = 1",
        "entity.x == 2 => entity.y = 2",
    ])
    assert conflicts == []


def test_semantically_equivalent_but_not_syntactically_ok_reports_no_conflict():
    # v1 is syntactic — `a == b` and `b == a` aren't flagged.
    conflicts = detect_conflicts([
        "entity.a == 1 => entity.x = 1",
        "1 == entity.a => entity.x = 2",
    ])
    assert conflicts == []


# --- Pairwise ordering --------------------------------------------------


def test_reports_all_pairs_for_triple_duplicates():
    conflicts = detect_conflicts([
        "entity.x == 1 => entity.y = 2",
        "entity.x == 1 => entity.y = 2",
        "entity.x == 1 => entity.y = 2",
    ])
    indices = {c.rule_indices for c in conflicts}
    assert indices == {(0, 1), (0, 2), (1, 2)}


# --- Module-level exposure ---------------------------------------------


def test_detect_conflicts_exposed_top_level():
    assert rulang.detect_conflicts is detect_conflicts
    assert rulang.Conflict is Conflict
