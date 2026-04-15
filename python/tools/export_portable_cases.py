from __future__ import annotations

import argparse
import ast
import copy
import json
from pathlib import Path
from typing import Any

from rulang import RuleEngine
from rulang.visitor import parse_rule


ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "python" / "tests"
OUTPUT_PATH = ROOT / "spec" / "generated" / "python-portable-cases.json"
TARGET_FILES = [
    "test_builtin_functions.py",
    "test_engine.py",
    "test_engine_edge_cases.py",
    "test_existence_operators.py",
    "test_implicit_entity.py",
    "test_list_operators.py",
    "test_null_safe.py",
    "test_parser.py",
    "test_parser_edge_cases.py",
    "test_parser_expanded.py",
    "test_string_operators.py",
]


EVAL_GLOBALS = {
    "__builtins__": {},
    "False": False,
    "None": None,
    "True": True,
    "range": range,
    "str": str,
}


def eval_expr(node: ast.AST, env: dict[str, Any]) -> Any:
    locals_env = {key: copy.deepcopy(value) for key, value in env.items()}
    return eval(compile(ast.Expression(node), "<extractor>", "eval"), EVAL_GLOBALS, locals_env)


def literal_value(node: ast.AST, env: dict[str, Any]) -> Any:
    return copy.deepcopy(eval_expr(node, env))


def is_call(node: ast.AST, obj_name: str | None, func_name: str) -> bool:
    if not isinstance(node, ast.Call):
        return False

    func = node.func
    if isinstance(func, ast.Name):
        return obj_name is None and func.id == func_name
    if isinstance(func, ast.Attribute):
        parts = [func.attr]
        current = func.value
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
            dotted = ".".join(reversed(parts))
            if obj_name is None:
                return dotted == func_name
            return dotted == f"{obj_name}.{func_name}"
    return False


def root_name_and_path(node: ast.AST) -> tuple[str, list[Any]] | None:
    path: list[Any] = []
    current = node

    while True:
        if isinstance(current, ast.Subscript):
            key_node = current.slice
            if isinstance(key_node, ast.Constant):
                key = key_node.value
            else:
                try:
                    key = ast.literal_eval(key_node)
                except Exception:
                    return None
            path.insert(0, key)
            current = current.value
            continue

        if isinstance(current, ast.Attribute):
            path.insert(0, current.attr)
            current = current.value
            continue

        if isinstance(current, ast.Name):
            return current.id, path

        return None


def set_path(target: dict[str, Any] | list[Any], path: list[Any], value: Any) -> None:
    current: Any = target
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value


def extract_result_expectation(assert_stmt: ast.Assert, result_name: str, env: dict[str, Any]) -> Any | None:
    test = assert_stmt.test
    if not isinstance(test, ast.Compare) or len(test.ops) != 1 or len(test.comparators) != 1:
        return None
    if not isinstance(test.left, ast.Name) or test.left.id != result_name:
        return None

    op = test.ops[0]
    if not isinstance(op, (ast.Is, ast.Eq)):
        return None

    try:
        return literal_value(test.comparators[0], env)
    except Exception:
        return None


def apply_entity_expectation(assert_stmt: ast.Assert, entity_name: str, expected_entity: Any, env: dict[str, Any]) -> bool:
    test = assert_stmt.test
    if not isinstance(test, ast.Compare) or len(test.ops) != 1 or len(test.comparators) != 1:
        return False

    root_and_path = root_name_and_path(test.left)
    if root_and_path is None:
        return False

    root, path = root_and_path
    if root != entity_name:
        return False

    op = test.ops[0]
    if not isinstance(op, (ast.Is, ast.Eq)):
        return False

    try:
        expected = literal_value(test.comparators[0], env)
    except Exception:
        return False

    if path:
        set_path(expected_entity, path, expected)
    else:
        if not isinstance(expected, (dict, list)):
            return False
        if isinstance(expected_entity, dict) and isinstance(expected, dict):
            expected_entity.clear()
            expected_entity.update(expected)
        elif isinstance(expected_entity, list) and isinstance(expected, list):
            expected_entity[:] = expected
        else:
            return False
    return True


def make_parse_case(
    case_id: str,
    rule_text: str,
    entity_name: str | None,
) -> dict[str, Any]:
    parsed = parse_rule(rule_text, entity_name=entity_name or "entity")
    return {
        "id": case_id,
        "kind": "parse",
        "rule": rule_text,
        "entity_name": entity_name,
        "expected": {
            "reads": sorted(parsed.reads),
            "writes": sorted(parsed.writes),
            "workflow_calls": sorted(parsed.workflow_calls),
        },
    }


def is_portable_evaluate_call(call: ast.Call, rules: list[str]) -> bool:
    if call.keywords:
        return False
    return all("workflow(" not in rule for rule in rules)


def make_evaluate_case(
    case_id: str,
    mode: str,
    rules: list[str],
    input_value: Any,
) -> dict[str, Any]:
    engine = RuleEngine(mode=mode)
    engine.add_rules(copy.deepcopy(rules))
    entity = copy.deepcopy(input_value)
    result = engine.evaluate(entity)

    case = {
        "id": case_id,
        "kind": "evaluate",
        "mode": mode,
        "rules": copy.deepcopy(rules),
        "input": copy.deepcopy(input_value),
        "expected_result": copy.deepcopy(result),
    }

    if isinstance(entity, (dict, list)):
        case["expected_entity"] = entity

    return case


def extract_parse_error(with_stmt: ast.With, case_id: str, env: dict[str, Any]) -> dict[str, Any] | None:
    if len(with_stmt.items) != 1 or len(with_stmt.body) != 1:
        return None

    context = with_stmt.items[0].context_expr
    if not is_call(context, "pytest", "raises"):
        return None
    if not context.args or not isinstance(context.args[0], ast.Name):
        return None

    body_stmt = with_stmt.body[0]
    if not isinstance(body_stmt, ast.Expr) or not is_call(body_stmt.value, None, "parse_rule"):
        return None

    call = body_stmt.value
    try:
        rule_text = literal_value(call.args[0], env)
    except Exception:
        return None

    entity_name = None
    for keyword in call.keywords:
        if keyword.arg == "entity_name":
            entity_name = literal_value(keyword.value, env)

    return {
        "id": case_id,
        "kind": "parse_error",
        "rule": rule_text,
        "entity_name": entity_name,
        "expected_error": context.args[0].id,
    }
def extract_parametrized_envs(function: ast.FunctionDef) -> list[dict[str, Any]]:
    envs = [{}]
    for decorator in function.decorator_list:
        if not is_call(decorator, "pytest.mark", "parametrize"):
            continue
        if len(decorator.args) < 2:
            continue

        names_node = decorator.args[0]
        if not isinstance(names_node, ast.Constant) or not isinstance(names_node.value, str):
            continue

        names = [name.strip() for name in names_node.value.split(",") if name.strip()]

        try:
            values = eval_expr(decorator.args[1], {})
        except Exception:
            continue

        expanded_envs: list[dict[str, Any]] = []
        for base_env in envs:
            for value in values:
                next_env = copy.deepcopy(base_env)
                if len(names) == 1:
                    next_env[names[0]] = copy.deepcopy(value)
                else:
                    for name, part in zip(names, value, strict=False):
                        next_env[name] = copy.deepcopy(part)
                expanded_envs.append(next_env)
        envs = expanded_envs
    return envs


def extract_cases_from_statements(
    path: Path,
    body: list[ast.stmt],
    class_stack: list[str],
    function_name: str,
    env: dict[str, Any],
    mode: str,
    rules: list[str] | None,
    case_index: int,
    cases: list[dict[str, Any]],
) -> tuple[dict[str, Any], str, list[str] | None, int]:
    index = 0

    while index < len(body):
        stmt = body[index]

        if isinstance(stmt, ast.For) and isinstance(stmt.target, ast.Name):
            try:
                items = list(eval_expr(stmt.iter, env))
            except Exception:
                index += 1
                continue

            for item in items:
                env[stmt.target.id] = copy.deepcopy(item)
                env, mode, rules, case_index = extract_cases_from_statements(
                    path=path,
                    body=stmt.body,
                    class_stack=class_stack,
                    function_name=function_name,
                    env=env,
                    mode=mode,
                    rules=rules,
                    case_index=case_index,
                    cases=cases,
                )
            index += 1
            continue

        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            target_name = stmt.targets[0].id

            if is_call(stmt.value, None, "RuleEngine"):
                call = stmt.value
                mode = "first_match"
                for keyword in call.keywords:
                    if keyword.arg == "mode":
                        mode = literal_value(keyword.value, env)
                index += 1
                continue

            if is_call(stmt.value, "engine", "evaluate") and rules:
                call = stmt.value
                try:
                    input_value = literal_value(call.args[0], env)
                except Exception:
                    index += 1
                    continue

                consumed = False
                next_index = index + 1

                while next_index < len(body) and isinstance(body[next_index], ast.Assert):
                    assert_stmt = body[next_index]
                    if extract_result_expectation(assert_stmt, target_name, env) is not None:
                        consumed = True
                        next_index += 1
                        continue
                    entity_name = call.args[0].id if isinstance(call.args[0], ast.Name) else None
                    if entity_name and isinstance(input_value, (dict, list)) and apply_entity_expectation(
                        assert_stmt,
                        entity_name,
                        copy.deepcopy(input_value),
                        env,
                    ):
                        consumed = True
                        next_index += 1
                        continue
                    break

                if consumed and is_portable_evaluate_call(call, rules):
                    case_index += 1
                    cases.append(make_evaluate_case(
                        f"{path.stem}::{'.'.join(class_stack + [function_name])}::{case_index}",
                        mode,
                        rules,
                        input_value,
                    ))

                index = next_index
                continue

            if is_call(stmt.value, None, "parse_rule"):
                call = stmt.value
                try:
                    rule_text = literal_value(call.args[0], env)
                except Exception:
                    index += 1
                    continue

                entity_name = None
                for keyword in call.keywords:
                    if keyword.arg == "entity_name":
                        entity_name = literal_value(keyword.value, env)

                consumed = False
                next_index = index + 1
                while next_index < len(body) and isinstance(body[next_index], ast.Assert):
                    consumed = True
                    next_index += 1

                if consumed or target_name == "rule":
                    case_index += 1
                    cases.append(make_parse_case(
                        f"{path.stem}::{'.'.join(class_stack + [function_name])}::{case_index}",
                        rule_text,
                        entity_name,
                    ))

                index = next_index
                continue

            try:
                env[target_name] = literal_value(stmt.value, env)
            except Exception:
                pass

            index += 1
            continue

        if isinstance(stmt, ast.Expr) and is_call(stmt.value, "engine", "add_rules"):
            try:
                rules_value = literal_value(stmt.value.args[0], env)
                new_rules = [rules_value] if isinstance(rules_value, str) else list(rules_value)
                rules = [*(rules or []), *new_rules]
            except Exception:
                pass
            index += 1
            continue

        if (
            isinstance(stmt, ast.Assert)
            and isinstance(stmt.test, ast.Compare)
            and is_call(stmt.test.left, "engine", "evaluate")
            and rules
        ):
            try:
                input_value = literal_value(stmt.test.left.args[0], env)
                expected_result = literal_value(stmt.test.comparators[0], env)
            except Exception:
                index += 1
                continue

            if not isinstance(stmt.test.ops[0], (ast.Is, ast.Eq)):
                index += 1
                continue

            if is_portable_evaluate_call(stmt.test.left, rules):
                case_index += 1
                cases.append(make_evaluate_case(
                    f"{path.stem}::{'.'.join(class_stack + [function_name])}::{case_index}",
                    mode,
                    rules,
                    input_value,
                ))
            index += 1
            continue

        if isinstance(stmt, ast.With):
            case_index += 1
            error_case = extract_parse_error(
                stmt,
                f"{path.stem}::{'.'.join(class_stack + [function_name])}::{case_index}",
                env,
            )
            if error_case:
                cases.append(error_case)
            index += 1
            continue

        index += 1

    return env, mode, rules, case_index


def walk_tests(path: Path, node: ast.AST, class_stack: list[str]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for child in getattr(node, "body", []):
        if isinstance(child, ast.ClassDef):
            cases.extend(walk_tests(path, child, [*class_stack, child.name]))
        elif isinstance(child, ast.FunctionDef) and child.name.startswith("test_"):
            case_index = 0
            parametrized_envs = extract_parametrized_envs(child)
            for env in parametrized_envs:
                _, _, _, case_index = extract_cases_from_statements(
                    path=path,
                    body=child.body,
                    class_stack=class_stack,
                    function_name=child.name,
                    env=copy.deepcopy(env),
                    mode="first_match",
                    rules=None,
                    case_index=case_index,
                    cases=cases,
                )
    return cases


def build_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for filename in TARGET_FILES:
        path = TEST_DIR / filename
        module = ast.parse(path.read_text(), filename=str(path))
        cases.extend(walk_tests(path, module, []))
    return sorted(cases, key=lambda case: case["id"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    cases = build_cases()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(cases, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {len(cases)} portable cases to {args.output}")


if __name__ == "__main__":
    main()
