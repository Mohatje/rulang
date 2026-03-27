from __future__ import annotations

import argparse
import ast
import copy
import json
from pathlib import Path
from typing import Any

from rulang.visitor import parse_rule


ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = ROOT / "python" / "tests"
OUTPUT_PATH = ROOT / "spec" / "generated" / "python-portable-cases.json"
TARGET_FILES = [
    "test_builtin_functions.py",
    "test_existence_operators.py",
    "test_implicit_entity.py",
    "test_list_operators.py",
    "test_null_safe.py",
    "test_parser.py",
    "test_string_operators.py",
]


def literal_value(node: ast.AST, env: dict[str, Any]) -> Any:
    if isinstance(node, ast.Name) and node.id in env:
        return copy.deepcopy(env[node.id])
    return ast.literal_eval(node)


def is_call(node: ast.AST, obj_name: str | None, func_name: str) -> bool:
    if not isinstance(node, ast.Call):
        return False

    func = node.func
    if isinstance(func, ast.Name):
        return obj_name is None and func.id == func_name
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id == obj_name and func.attr == func_name
    return False


def parse_compare_literal(node: ast.Assert) -> tuple[str, Any] | None:
    test = node.test
    if not isinstance(test, ast.Compare) or len(test.ops) != 1 or len(test.comparators) != 1:
        return None

    op = test.ops[0]
    comparator = test.comparators[0]
    if not isinstance(op, (ast.Is, ast.Eq)):
        return None

    try:
        expected = ast.literal_eval(comparator)
    except Exception:
        return None

    return ("value", expected)


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


def extract_result_expectation(assert_stmt: ast.Assert, result_name: str) -> Any | None:
    test = assert_stmt.test
    if not isinstance(test, ast.Compare) or len(test.ops) != 1 or len(test.comparators) != 1:
        return None
    if not isinstance(test.left, ast.Name) or test.left.id != result_name:
        return None

    op = test.ops[0]
    if not isinstance(op, (ast.Is, ast.Eq)):
        return None

    try:
        return ast.literal_eval(test.comparators[0])
    except Exception:
        return None


def apply_entity_expectation(assert_stmt: ast.Assert, entity_name: str, expected_entity: Any) -> bool:
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
        expected = ast.literal_eval(test.comparators[0])
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


def extract_parse_error(with_stmt: ast.With, case_id: str) -> dict[str, Any] | None:
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
        rule_text = literal_value(call.args[0], {})
    except Exception:
        return None

    entity_name = None
    for keyword in call.keywords:
        if keyword.arg == "entity_name":
            entity_name = ast.literal_eval(keyword.value)

    return {
        "id": case_id,
        "kind": "parse_error",
        "rule": rule_text,
        "entity_name": entity_name,
        "expected_error": context.args[0].id,
    }


def extract_function_cases(path: Path, function: ast.FunctionDef, class_stack: list[str]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    env: dict[str, Any] = {}
    mode = "first_match"
    rules: list[str] | None = None
    case_index = 0
    body = function.body
    index = 0

    while index < len(body):
        stmt = body[index]

        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            target_name = stmt.targets[0].id

            if is_call(stmt.value, None, "RuleEngine"):
                call = stmt.value
                mode = "first_match"
                for keyword in call.keywords:
                    if keyword.arg == "mode":
                        mode = ast.literal_eval(keyword.value)
                index += 1
                continue

            if is_call(stmt.value, "engine", "evaluate") and rules:
                call = stmt.value
                try:
                    input_value = literal_value(call.args[0], env)
                except Exception:
                    index += 1
                    continue

                expected_result = None
                expected_entity = copy.deepcopy(input_value) if isinstance(input_value, (dict, list)) else None
                entity_name = call.args[0].id if isinstance(call.args[0], ast.Name) else None
                consumed = False
                next_index = index + 1

                while next_index < len(body) and isinstance(body[next_index], ast.Assert):
                    assert_stmt = body[next_index]
                    result_expectation = extract_result_expectation(assert_stmt, target_name)
                    if result_expectation is not None:
                        expected_result = result_expectation
                        consumed = True
                        next_index += 1
                        continue
                    if entity_name and expected_entity is not None and apply_entity_expectation(assert_stmt, entity_name, expected_entity):
                        consumed = True
                        next_index += 1
                        continue
                    break

                if consumed:
                    case_index += 1
                    cases.append({
                        "id": f"{path.stem}::{'.'.join(class_stack + [function.name])}::{case_index}",
                        "kind": "evaluate",
                        "mode": mode,
                        "rules": copy.deepcopy(rules),
                        "input": input_value,
                        "expected_result": expected_result,
                        "expected_entity": expected_entity,
                    })

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
                        entity_name = ast.literal_eval(keyword.value)

                consumed = False
                next_index = index + 1
                while next_index < len(body) and isinstance(body[next_index], ast.Assert):
                    consumed = True
                    next_index += 1

                if consumed or target_name == "rule":
                    case_index += 1
                    cases.append(make_parse_case(
                        f"{path.stem}::{'.'.join(class_stack + [function.name])}::{case_index}",
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
                rules = [rules_value] if isinstance(rules_value, str) else list(rules_value)
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
                expected_result = ast.literal_eval(stmt.test.comparators[0])
            except Exception:
                index += 1
                continue

            if not isinstance(stmt.test.ops[0], (ast.Is, ast.Eq)):
                index += 1
                continue

            case_index += 1
            cases.append({
                "id": f"{path.stem}::{'.'.join(class_stack + [function.name])}::{case_index}",
                "kind": "evaluate",
                "mode": mode,
                "rules": copy.deepcopy(rules),
                "input": input_value,
                "expected_result": expected_result,
            })
            index += 1
            continue

        if isinstance(stmt, ast.With):
            case_index += 1
            error_case = extract_parse_error(stmt, f"{path.stem}::{'.'.join(class_stack + [function.name])}::{case_index}")
            if error_case:
                cases.append(error_case)
            index += 1
            continue

        index += 1

    return cases


def walk_tests(path: Path, node: ast.AST, class_stack: list[str]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for child in getattr(node, "body", []):
        if isinstance(child, ast.ClassDef):
            cases.extend(walk_tests(path, child, [*class_stack, child.name]))
        elif isinstance(child, ast.FunctionDef) and child.name.startswith("test_"):
            cases.extend(extract_function_cases(path, child, class_stack))
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
