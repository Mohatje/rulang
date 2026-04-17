"""Tests for the dry-run diff API (proposal #8)."""

import pytest

import rulang
from rulang import (
    DryRunResult,
    ExecutedAction,
    MatchedRule,
    RuleEngine,
)


# --- Return shape -------------------------------------------------------


def test_dry_run_returns_dry_run_result():
    engine = RuleEngine()
    engine.add_rules("entity.x == 1 => entity.y = 2")
    result = engine.dry_run({"x": 1, "y": 0})
    assert isinstance(result, DryRunResult)


# --- Non-mutating by default -------------------------------------------


def test_dry_run_does_not_mutate_original_entity():
    engine = RuleEngine()
    engine.add_rules("entity.x == 1 => entity.y = 99")
    entity = {"x": 1, "y": 0}
    engine.dry_run(entity)
    assert entity == {"x": 1, "y": 0}  # unchanged


def test_dry_run_with_deep_copy_false_mutates_entity():
    engine = RuleEngine()
    engine.add_rules("entity.x == 1 => entity.y = 99")
    entity = {"x": 1, "y": 0}
    engine.dry_run(entity, deep_copy=False)
    assert entity["y"] == 99


# --- matched_rules ------------------------------------------------------


def test_matched_rules_report_condition_results_and_execution():
    engine = RuleEngine("all_match")
    engine.add_rules([
        "entity.x > 0 => entity.a = 1",
        "entity.x < 0 => entity.b = 1",
    ])
    result = engine.dry_run({"x": 1, "a": 0, "b": 0})

    assert len(result.matched_rules) == 2
    matched = {m.index: m for m in result.matched_rules}
    assert matched[0].condition_result is True
    assert matched[0].executed is True
    assert matched[1].condition_result is False
    assert matched[1].executed is False


def test_first_match_mode_executes_only_first_but_traces_all_considered():
    engine = RuleEngine("first_match")
    engine.add_rules([
        "entity.x > 0 => entity.a = 1",
        "entity.x > 0 => entity.b = 1",
    ])
    result = engine.dry_run({"x": 1, "a": 0, "b": 0})

    assert result.final_entity["a"] == 1
    assert result.final_entity["b"] == 0  # second rule didn't execute


# --- executed_actions ---------------------------------------------------


def test_executed_actions_records_kind_and_changes():
    engine = RuleEngine()
    engine.add_rules("entity.x == 1 => entity.y = 42")
    result = engine.dry_run({"x": 1, "y": 0})

    assert len(result.executed_actions) == 1
    action = result.executed_actions[0]
    assert action.rule_index == 0
    assert action.action_kind == "set"
    assert len(action.changes) == 1
    change = action.changes[0]
    assert change.before == 0
    assert change.after == 42


def test_executed_actions_for_compound():
    engine = RuleEngine()
    engine.add_rules("entity.x == 1 => entity.count += 5")
    result = engine.dry_run({"x": 1, "count": 10})

    action = result.executed_actions[0]
    assert action.action_kind == "compound"
    assert action.changes[0].before == 10
    assert action.changes[0].after == 15


def test_executed_actions_for_workflow_call():
    engine = RuleEngine()
    engine.add_rules('entity.x == 1 => workflow("bump", entity.id)')

    def bump(entity, _id):
        entity["bumped"] = True

    result = engine.dry_run({"x": 1, "id": 7, "bumped": False}, workflows={"bump": bump})
    action = result.executed_actions[0]
    assert action.action_kind == "workflow"
    assert any(c.path == "bumped" for c in action.changes)


def test_executed_actions_for_return():
    engine = RuleEngine()
    engine.add_rules("entity.x == 1 => ret 'matched'")
    result = engine.dry_run({"x": 1})
    action = result.executed_actions[0]
    assert action.action_kind == "return"
    assert action.returned == "matched"


def test_return_value_surfaces_on_result():
    engine = RuleEngine()
    engine.add_rules("entity.x == 1 => ret 'yes'")
    result = engine.dry_run({"x": 1})
    assert result.returned == "yes"


def test_no_match_returns_none():
    engine = RuleEngine()
    engine.add_rules("entity.x == 99 => ret 'no'")
    result = engine.dry_run({"x": 1})
    assert result.returned is None
    assert all(not m.executed for m in result.matched_rules)


# --- Diff ---------------------------------------------------------------


def test_aggregate_diff_covers_all_changed_paths():
    engine = RuleEngine("all_match")
    engine.add_rules([
        "entity.x == 1 => entity.a = 10",
        "entity.a == 10 => entity.b = 20",
    ])
    result = engine.dry_run({"x": 1, "a": 0, "b": 0})
    assert result.diff == {"a": (0, 10), "b": (0, 20)}


def test_multiple_writes_to_same_path_keep_original_before_and_latest_after():
    engine = RuleEngine("all_match")
    engine.add_rules([
        "entity.x == 1 => entity.a = 10",
        "entity.a == 10 => entity.a = 20",
    ])
    result = engine.dry_run({"x": 1, "a": 0})
    assert result.diff["a"] == (0, 20)


def test_diff_entry_drops_when_change_cancels_itself():
    engine = RuleEngine("all_match")
    engine.add_rules([
        "entity.x == 1 => entity.a = 10",
        "entity.a == 10 => entity.a = 0",
    ])
    result = engine.dry_run({"x": 1, "a": 0})
    assert "a" not in result.diff


# --- Final entity -------------------------------------------------------


def test_final_entity_reflects_run():
    engine = RuleEngine("all_match")
    engine.add_rules([
        "entity.a == 0 => entity.a = 1",
        "entity.a == 1 => entity.b = 2",
    ])
    result = engine.dry_run({"a": 0, "b": 0})
    assert result.final_entity == {"a": 1, "b": 2}


# --- Nested paths -------------------------------------------------------


def test_diff_handles_nested_paths():
    engine = RuleEngine()
    engine.add_rules("entity.user.name == 'alice' => entity.user.role = 'admin'")
    entity = {"user": {"name": "alice", "role": "guest"}}
    result = engine.dry_run(entity)
    assert result.diff == {"user.role": ("guest", "admin")}


def test_diff_handles_list_indices():
    engine = RuleEngine()
    engine.add_rules("entity.items[0].price == 10 => entity.items[0].price = 15")
    entity = {"items": [{"price": 10}, {"price": 20}]}
    result = engine.dry_run(entity)
    assert result.diff == {"items[0].price": (10, 15)}


# --- Multiple rules with first_match ret --------------------------------


def test_first_match_ret_stops_later_rules():
    engine = RuleEngine("first_match")
    engine.add_rules([
        "entity.x > 0 => ret 'positive'",
        "entity.x > 0 => entity.extra = 1",
    ])
    result = engine.dry_run({"x": 1, "extra": 0})
    assert result.returned == "positive"
    # Second rule should not be executed
    assert result.final_entity["extra"] == 0
    second = next(m for m in result.matched_rules if m.index == 1)
    assert second.executed is False


# --- Any-matched helper --------------------------------------------------


def test_any_matched_property():
    engine = RuleEngine()
    engine.add_rules("entity.x == 1 => entity.y = 1")
    assert engine.dry_run({"x": 1, "y": 0}).any_matched is True
    assert engine.dry_run({"x": 0, "y": 0}).any_matched is False


# --- Module-level reexport ---------------------------------------------


def test_dry_run_types_exposed_top_level():
    assert rulang.DryRunResult is DryRunResult
    assert rulang.MatchedRule is MatchedRule
    assert rulang.ExecutedAction is ExecutedAction
