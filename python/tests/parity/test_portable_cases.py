import json
from pathlib import Path

import pytest

from rulang import RuleEngine
from rulang.exceptions import RuleSyntaxError
from rulang.workflows import Workflow
from rulang.visitor import parse_rule


CASES_PATH = Path(__file__).resolve().parents[3] / "spec" / "generated" / "python-portable-cases.json"
WORKFLOW_CASES_PATH = Path(__file__).resolve().parents[3] / "spec" / "portable" / "workflow-portable-cases.json"
CASES = json.loads(CASES_PATH.read_text()) + json.loads(WORKFLOW_CASES_PATH.read_text())


def _get_path(entity, path: str):
    current = entity
    for segment in path.split("."):
        current = current[segment]
    return current


def _set_path(entity, path: str, value):
    parts = path.split(".")
    current = entity
    for segment in parts[:-1]:
        current = current[segment]
    current[parts[-1]] = value


def _eval_workflow_expr(expr, entity, args):
    expr_type = expr["type"]
    if expr_type == "literal":
        return expr["value"]
    if expr_type == "entity_path":
        return _get_path(entity, expr["path"])
    if expr_type == "arg":
        return args[expr["index"]]
    if expr_type == "binary":
        left = _eval_workflow_expr(expr["left"], entity, args)
        right = _eval_workflow_expr(expr["right"], entity, args)
        op = expr["op"]
        if op == "add":
            return left + right
        if op == "sub":
            return left - right
        if op == "mul":
            return left * right
        if op == "div":
            return left / right
        if op == "mod":
            return left % right
    if expr_type == "call":
        arg = _eval_workflow_expr(expr["arg"], entity, args)
        if expr["fn"] == "upper":
            return arg.upper()
    raise AssertionError(f"Unsupported workflow expression: {expr}")


def _build_workflows(case):
    workflows = {}
    for spec in case.get("workflows", []):
        def make_fn(spec):
            def fn(entity, *args):
                result = None
                for step in spec["steps"]:
                    if step["type"] == "set":
                        _set_path(entity, step["path"], _eval_workflow_expr(step["value"], entity, args))
                    elif step["type"] == "return":
                        result = _eval_workflow_expr(step["value"], entity, args)
                        return result
                    else:
                        raise AssertionError(f"Unsupported workflow step: {step}")
                return result

            return fn

        fn = make_fn(spec)
        if "reads" in spec or "writes" in spec:
            workflows[spec["name"]] = Workflow(fn=fn, reads=spec.get("reads", []), writes=spec.get("writes", []))
        else:
            workflows[spec["name"]] = fn
    return workflows or None


@pytest.mark.parametrize("case", [pytest.param(case, id=case["id"]) for case in CASES])
def test_portable_cases(case):
    kind = case["kind"]

    if kind == "evaluate":
        engine = RuleEngine(mode=case["mode"])
        engine.add_rules(case["rules"])
        entity = case["input"]
        result = engine.evaluate(entity, workflows=_build_workflows(case))
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
