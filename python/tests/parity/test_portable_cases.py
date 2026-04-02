import copy
import json
from pathlib import Path

import pytest

from rulang import RuleEngine
from rulang.dependency_graph import DependencyGraph
from rulang.exceptions import EvaluationError, PathResolutionError, RuleSyntaxError, WorkflowNotFoundError
from rulang.path_resolver import PathResolver
from rulang.workflows import Workflow
from rulang.visitor import parse_rule


CASES_PATH = Path(__file__).resolve().parents[3] / "spec" / "generated" / "python-portable-cases.json"
PORTABLE_CASES_DIR = Path(__file__).resolve().parents[3] / "spec" / "portable"


def _load_cases():
    cases = json.loads(CASES_PATH.read_text())
    for path in sorted(PORTABLE_CASES_DIR.glob("*.json")):
        cases.extend(json.loads(path.read_text()))
    return cases


CASES = _load_cases()


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


def _normalize_graph(graph: dict[int, set[int]]) -> dict[str, list[int]]:
    return {
        str(index): sorted(dependents)
        for index, dependents in sorted(graph.items())
    }


def _get_error_class(name: str):
    mapping = {
        "RuleSyntaxError": RuleSyntaxError,
        "PathResolutionError": PathResolutionError,
        "WorkflowNotFoundError": WorkflowNotFoundError,
        "EvaluationError": EvaluationError,
    }
    if name not in mapping:
        raise AssertionError(f"Unsupported error type: {name}")
    return mapping[name]


def _run_engine_step(engine: RuleEngine, step: dict):
    op = step["op"]

    if op == "get_execution_order":
        assert engine.get_execution_order() == step["expected"]
        return

    if op == "evaluate":
        entity = copy.deepcopy(step["input"])
        result = engine.evaluate(entity, workflows=_build_workflows(step))
        assert result == step.get("expected_result")
        if "expected_entity" in step:
            assert entity == step["expected_entity"]
        return

    raise AssertionError(f"Unsupported engine step: {op}")


@pytest.mark.parametrize("case", [pytest.param(case, id=case["id"]) for case in CASES])
def test_portable_cases(case):
    kind = case["kind"]

    if kind == "evaluate":
        engine = RuleEngine(mode=case["mode"])
        engine.add_rules(case["rules"])
        entity = copy.deepcopy(case["input"])
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

    if kind == "resolve":
        resolver = PathResolver(copy.deepcopy(case["input"]), entity_name=case.get("entity_name") or "entity")
        expected = case["expected"]

        if "error_type" in expected:
            with pytest.raises(_get_error_class(expected["error_type"])):
                resolver.resolve(case["path"], set(case.get("null_safe_indices", [])))
            return

        assert resolver.resolve(case["path"], set(case.get("null_safe_indices", []))) == expected["value"]
        return

    if kind == "assign":
        entity = copy.deepcopy(case["input"])
        resolver = PathResolver(entity, entity_name=case.get("entity_name") or "entity")
        expected = case["expected"]

        if "error_type" in expected:
            with pytest.raises(_get_error_class(expected["error_type"])):
                resolver.assign(case["path"], copy.deepcopy(case["value"]))
            return

        resolver.assign(case["path"], copy.deepcopy(case["value"]))
        assert entity == expected["entity"]
        return

    if kind == "dependency_graph":
        graph = DependencyGraph()
        workflows = _build_workflows(case)

        for rule_text in case["rules"]:
            graph.add_rule(parse_rule(rule_text, entity_name=case.get("entity_name") or "entity"), workflows)

        expected = case["expected"]
        if "graph" in expected:
            assert _normalize_graph(graph.get_graph()) == expected["graph"]
        if "execution_order" in expected:
            assert graph.get_execution_order() == expected["execution_order"]
        return

    if kind == "evaluate_error":
        engine = RuleEngine(mode=case["mode"])
        engine.add_rules(case["rules"])
        entity = copy.deepcopy(case["input"])

        with pytest.raises(_get_error_class(case["expected_error"])):
            engine.evaluate(entity, workflows=_build_workflows(case))
        return

    if kind == "engine_sequence":
        engine = RuleEngine(mode=case["mode"])
        engine.add_rules(case["rules"])
        for step in case["steps"]:
            _run_engine_step(engine, step)
        return

    raise AssertionError(f"Unknown portable case kind: {kind}")
