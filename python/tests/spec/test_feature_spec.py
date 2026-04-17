"""Cross-runtime spec for new features: format, conflicts, dry_run.

Each JSON file declares a `kind` and a `cases` array. Python and TypeScript
loaders share the same fixtures; divergence is caught by CI.
"""

import json
from pathlib import Path

import pytest

from rulang import (
    Conflict,
    RuleEngine,
    detect_conflicts,
    format,
)


FEATURE_DIR = Path(__file__).resolve().parents[3] / "spec" / "feature-cases"


def _load_bundle(name: str) -> list:
    data = json.loads((FEATURE_DIR / name).read_text())
    kind = data["kind"]
    return [pytest.param({**c, "kind": kind}, id=c["id"]) for c in data["cases"]]


# --- format -------------------------------------------------------------


@pytest.mark.parametrize("case", _load_bundle("format.json"))
def test_format_spec(case):
    assert case["kind"] == "format"
    assert format(case["input"]) == case["expected"]


# --- conflicts ----------------------------------------------------------


@pytest.mark.parametrize("case", _load_bundle("conflicts.json"))
def test_conflict_spec(case):
    assert case["kind"] == "conflicts"
    mode = case.get("mode", "all_match")
    result = detect_conflicts(case["rules"], mode=mode)

    assert len(result) == len(case["expected"])
    for got, want in zip(result, case["expected"]):
        assert got.kind == want["kind"]
        assert list(got.rule_indices) == want["rule_indices"]
        if "fields" in want:
            assert list(got.fields) == want["fields"]


# --- dry_run ------------------------------------------------------------


@pytest.mark.parametrize("case", _load_bundle("dry_run.json"))
def test_dry_run_spec(case):
    assert case["kind"] == "dry_run"
    engine = RuleEngine(case.get("mode", "first_match"))
    engine.add_rules(case["rules"])
    result = engine.dry_run(case["input"])

    expected = case["expected"]

    # matched
    got_matched = [
        {
            "index": m.index,
            "condition_result": m.condition_result,
            "executed": m.executed,
        }
        for m in result.matched_rules
    ]
    assert got_matched == expected["matched"]

    # diff
    # JSON doesn't preserve tuples; normalize both sides to lists.
    got_diff = {k: list(v) for k, v in result.diff.items()}
    assert got_diff == expected["diff"]

    # final entity
    assert result.final_entity == expected["final_entity"]

    # returned
    assert result.returned == expected["returned"]
