import json
from pathlib import Path

import pytest

from rulang import RuleEngine
from rulang.exceptions import RuleSyntaxError
from rulang.visitor import parse_rule


CASES_PATH = Path(__file__).resolve().parents[3] / "spec" / "generated" / "python-portable-cases.json"
CASES = json.loads(CASES_PATH.read_text())


@pytest.mark.parametrize("case", [pytest.param(case, id=case["id"]) for case in CASES])
def test_portable_cases(case):
    kind = case["kind"]

    if kind == "evaluate":
        engine = RuleEngine(mode=case["mode"])
        engine.add_rules(case["rules"])
        entity = case["input"]
        result = engine.evaluate(entity)
        assert result == case.get("expected_result")
        if "expected_entity" in case:
            assert entity == case["expected_entity"]
        return

    if kind == "parse":
        parsed = parse_rule(case["rule"], entity_name=case.get("entity_name") or "entity")
        assert sorted(parsed.reads) == case["expected"]["reads"]
        assert sorted(parsed.writes) == case["expected"]["writes"]
        assert sorted(parsed.workflow_calls) == case["expected"]["workflow_calls"]
        return

    if kind == "parse_error":
        with pytest.raises(RuleSyntaxError):
            parse_rule(case["rule"], entity_name=case.get("entity_name") or "entity")
        return

    raise AssertionError(f"Unknown portable case kind: {kind}")
