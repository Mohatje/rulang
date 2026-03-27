import json
from pathlib import Path

import pytest

from rulang import RuleEngine
from rulang import exceptions as rulang_exceptions
from rulang.visitor import parse_rule


SPEC_DIR = Path(__file__).resolve().parents[3] / "spec" / "cases"


def _load_cases():
    cases = []
    for path in sorted(SPEC_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        cases.append(pytest.param(data, id=data["id"]))
    return cases


@pytest.mark.parametrize("case", _load_cases())
def test_shared_spec(case):
    if case.get("parse_only"):
        rule_text = case["rule"]
        expected = case["expected"]

        if "error_type" in expected:
            error_cls = getattr(rulang_exceptions, expected["error_type"])
            with pytest.raises(error_cls):
                parse_rule(rule_text)
            return

        parsed = parse_rule(rule_text)
        assert sorted(parsed.reads) == expected.get("reads", [])
        assert sorted(parsed.writes) == expected.get("writes", [])
        assert sorted(parsed.workflow_calls) == expected.get("workflow_calls", [])
        return

    engine = RuleEngine(mode=case.get("mode", "first_match"))
    engine.add_rules(case["rules"])
    entity = case["input"]
    result = engine.evaluate(entity)

    expected = case["expected"]
    assert result == expected["result"]
    assert entity == expected["entity"]

    if "execution_order" in expected:
        assert engine.get_execution_order() == expected["execution_order"]
