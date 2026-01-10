"""Comprehensive expanded tests for the rule visitor/interpreter."""

import pytest
from dataclasses import dataclass
from math import inf, nan

from rulang.visitor import parse_rule, RuleInterpreter
from rulang.exceptions import PathResolutionError, WorkflowNotFoundError, EvaluationError


class TestComparisonEvaluation:
    """Test comparison operator evaluation with all types."""

    @pytest.mark.parametrize("left,right,expected", [
        (10, 10, True), (10, 5, False), (5, 10, False),
        (10.0, 10, True), (10, 10.0, True), (10.5, 10.5, True),
        (-10, -10, True), (0, 0, True), (-0, 0, True),
    ])
    def test_equality_numbers(self, left, right, expected):
        entity = {"value": left}
        rule = parse_rule(f"entity.value == {right} => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched == expected

    @pytest.mark.parametrize("left,right,expected", [
        ("test", "test", True), ("test", "other", False),
        ("", "", True), ("a", "b", False),
    ])
    def test_equality_strings(self, left, right, expected):
        entity = {"value": left}
        rule = parse_rule(f'entity.value == "{right}" => ret true')
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched == expected

    @pytest.mark.parametrize("left,right,expected", [
        (True, True, True), (False, False, True),
        (True, False, False), (False, True, False),
    ])
    def test_equality_booleans(self, left, right, expected):
        entity = {"value": left}
        rule = parse_rule(f"entity.value == {str(right).lower()} => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched == expected

    def test_equality_none(self):
        entity = {"value": None}
        rule = parse_rule("entity.value == none => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_inequality_numbers(self):
        entity = {"value": 10}
        rule = parse_rule("entity.value != 5 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    @pytest.mark.parametrize("left,right,op,expected", [
        (10, 5, "<", False), (5, 10, "<", True), (10, 10, "<", False),
        (10, 5, ">", True), (5, 10, ">", False), (10, 10, ">", False),
        (10, 5, "<=", False), (5, 10, "<=", True), (10, 10, "<=", True),
        (10, 5, ">=", True), (5, 10, ">=", False), (10, 10, ">=", True),
    ])
    def test_comparison_operators_numbers(self, left, right, op, expected):
        entity = {"value": left}
        rule = parse_rule(f"entity.value {op} {right} => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched == expected

    def test_comparison_strings_lexicographic(self):
        entity = {"value": "apple"}
        rule = parse_rule('entity.value < "banana" => ret true')
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_comparison_mixed_types_error(self):
        entity = {"value": 10}
        rule = parse_rule('entity.value == "test" => ret true')
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        # Should not match (10 != "test")
        assert matched is False

    def test_comparison_very_large_numbers(self):
        entity = {"value": 999999999999999999}
        rule = parse_rule("entity.value == 999999999999999999 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_comparison_very_small_numbers(self):
        entity = {"value": 0.0000001}
        rule = parse_rule("entity.value == 0.0000001 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True


class TestArithmeticEvaluation:
    """Test arithmetic operation evaluation."""

    @pytest.mark.parametrize("a,b,expected", [
        (10, 5, 15), (0, 0, 0), (-10, 5, -5), (10, -5, 5),
        (10.5, 5.5, 16.0), (10, 5.5, 15.5),
    ])
    def test_addition(self, a, b, expected):
        entity = {"a": a, "b": b, "result": 0}
        rule = parse_rule("true => entity.result = entity.a + entity.b; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert abs(result - expected) < 0.0001

    @pytest.mark.parametrize("a,b,expected", [
        (10, 5, 5), (0, 0, 0), (-10, 5, -15), (10, -5, 15),
        (10.5, 5.5, 5.0), (10, 5.5, 4.5),
    ])
    def test_subtraction(self, a, b, expected):
        entity = {"a": a, "b": b, "result": 0}
        rule = parse_rule("entity.a - entity.b >= -100 => entity.result = entity.a - entity.b; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert abs(result - expected) < 0.0001

    @pytest.mark.parametrize("a,b,expected", [
        (10, 5, 50), (0, 5, 0), (-10, 5, -50), (10, -5, -50),
        (10.5, 2, 21.0), (10, 0.5, 5.0),
    ])
    def test_multiplication(self, a, b, expected):
        entity = {"a": a, "b": b, "result": 0}
        rule = parse_rule("entity.a * entity.b >= -100 => entity.result = entity.a * entity.b; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert abs(result - expected) < 0.0001

    @pytest.mark.parametrize("a,b,expected", [
        (10, 5, 2.0), (10, 2, 5.0), (10, -5, -2.0), (-10, 5, -2.0),
        (10.5, 2, 5.25), (10, 0.5, 20.0),
    ])
    def test_division(self, a, b, expected):
        entity = {"a": a, "b": b, "result": 0}
        rule = parse_rule("entity.b != 0 => entity.result = entity.a / entity.b; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert abs(result - expected) < 0.0001

    def test_division_by_zero(self):
        entity = {"a": 10, "b": 0}
        rule = parse_rule("entity.a / entity.b >= 0 => ret true")
        interpreter = RuleInterpreter(entity)
        with pytest.raises((ZeroDivisionError, EvaluationError)):
            interpreter.execute(rule.tree)

    @pytest.mark.parametrize("a,b,expected", [
        (10, 3, 1), (10, 5, 0), (10, 7, 3), (-10, 3, 2),  # Python modulo: -10 % 3 = 2
    ])
    def test_modulo(self, a, b, expected):
        entity = {"a": a, "b": b, "result": 0}
        rule = parse_rule("entity.b != 0 => entity.result = entity.a % entity.b; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert result == expected

    def test_modulo_by_zero(self):
        entity = {"a": 10, "b": 0}
        rule = parse_rule("entity.a % entity.b >= 0 => ret true")
        interpreter = RuleInterpreter(entity)
        with pytest.raises((ZeroDivisionError, EvaluationError)):
            interpreter.execute(rule.tree)

    def test_unary_minus(self):
        entity = {"value": 10, "neg": 0}
        rule = parse_rule("entity.value > 0 => entity.neg = -entity.value; ret entity.neg")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert result == -10

    def test_complex_arithmetic_expression(self):
        entity = {"a": 10, "b": 5, "c": 2, "result": 0}
        rule = parse_rule("entity.a + entity.b * entity.c >= 0 => entity.result = entity.a + entity.b * entity.c; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert result == 20  # 10 + 5 * 2 = 20


class TestLogicalEvaluation:
    """Test logical operator evaluation."""

    @pytest.mark.parametrize("a,b,expected", [
        (True, True, True), (True, False, False),
        (False, True, False), (False, False, False),
    ])
    def test_and_booleans(self, a, b, expected):
        entity = {"a": a, "b": b}
        rule = parse_rule("entity.a == true and entity.b == true => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched == expected

    def test_and_short_circuit(self):
        entity = {"a": False, "b": True}
        # If short-circuit works, entity.b should not be evaluated
        rule = parse_rule("entity.a == true and entity.b == true => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is False

    @pytest.mark.parametrize("a,b,expected", [
        (True, True, True), (True, False, True),
        (False, True, True), (False, False, False),
    ])
    def test_or_booleans(self, a, b, expected):
        entity = {"a": a, "b": b}
        rule = parse_rule("entity.a == true or entity.b == true => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched == expected

    def test_or_short_circuit(self):
        entity = {"a": True, "b": False}
        rule = parse_rule("entity.a == true or entity.b == true => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_not_boolean(self):
        entity = {"value": True}
        rule = parse_rule("not entity.value == true => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is False

    def test_not_false(self):
        entity = {"value": False}
        rule = parse_rule("not entity.value == true => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_truthiness_numbers(self):
        entity = {"zero": 0, "one": 1, "negative": -1}
        rule1 = parse_rule("entity.zero == 0 => ret true")
        rule2 = parse_rule("entity.one > 0 => ret true")
        rule3 = parse_rule("entity.negative < 0 => ret true")
        
        interpreter1 = RuleInterpreter(entity)
        interpreter2 = RuleInterpreter(entity)
        interpreter3 = RuleInterpreter(entity)
        
        matched1, _ = interpreter1.execute(rule1.tree)
        matched2, _ = interpreter2.execute(rule2.tree)
        matched3, _ = interpreter3.execute(rule3.tree)
        
        assert matched1 is True
        assert matched2 is True
        assert matched3 is True

    def test_truthiness_strings(self):
        entity = {"empty": "", "nonempty": "test"}
        rule1 = parse_rule('entity.empty == "" => ret true')
        rule2 = parse_rule('entity.nonempty != "" => ret true')
        
        interpreter1 = RuleInterpreter(entity)
        interpreter2 = RuleInterpreter(entity)
        
        matched1, _ = interpreter1.execute(rule1.tree)
        matched2, _ = interpreter2.execute(rule2.tree)
        
        assert matched1 is True
        assert matched2 is True

    def test_truthiness_none(self):
        entity = {"value": None}
        rule = parse_rule("entity.value == none => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_complex_logical_expression(self):
        entity = {"a": 5, "b": 3, "c": 10}
        rule = parse_rule("entity.a > 0 and entity.b > 0 or entity.c > 100 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True


class TestMembershipEvaluation:
    """Test membership operator evaluation."""

    def test_in_with_list_numbers(self):
        entity = {"value": 2}
        rule = parse_rule("entity.value in [1, 2, 3] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_in_with_list_not_present(self):
        entity = {"value": 5}
        rule = parse_rule("entity.value in [1, 2, 3] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is False

    def test_in_with_list_strings(self):
        entity = {"status": "active"}
        rule = parse_rule("entity.status in ['active', 'pending'] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_in_with_empty_list(self):
        entity = {"value": 1}
        rule = parse_rule("entity.value in [] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is False

    def test_not_in_with_list(self):
        entity = {"status": "deleted"}
        rule = parse_rule("entity.status not in ['active', 'pending'] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_not_in_with_list_present(self):
        entity = {"status": "active"}
        rule = parse_rule("entity.status not in ['active', 'pending'] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is False

    def test_in_with_mixed_types(self):
        entity = {"value": "test"}
        rule = parse_rule("entity.value in [1, 'test', 3.0] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True


class TestAssignmentExecution:
    """Test assignment action execution."""

    @pytest.mark.parametrize("value", [10, 10.5, "test", True, False, None])
    def test_simple_assignment_all_types(self, value):
        entity = {"target": None}
        if isinstance(value, str):
            rule = parse_rule(f'entity.target == none => entity.target = "{value}"')
        elif isinstance(value, bool):
            rule = parse_rule(f"entity.target == none => entity.target = {str(value).lower()}")
        elif value is None:
            rule = parse_rule("entity.target == none => entity.target = none")
        else:
            rule = parse_rule(f"entity.target == none => entity.target = {value}")
        
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True
        assert entity["target"] == value

    def test_compound_addition(self):
        entity = {"counter": 10}
        rule = parse_rule("entity.counter > 0 => entity.counter += 5")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True
        assert entity["counter"] == 15

    def test_compound_subtraction(self):
        entity = {"counter": 10}
        rule = parse_rule("entity.counter > 0 => entity.counter -= 3")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity["counter"] == 7

    def test_compound_multiplication(self):
        entity = {"value": 5}
        rule = parse_rule("entity.value > 0 => entity.value *= 2")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity["value"] == 10

    def test_compound_division(self):
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => entity.value /= 2")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity["value"] == 5.0

    def test_compound_with_expression(self):
        entity = {"total": 10, "add": 5}
        rule = parse_rule("entity.total > 0 => entity.total += entity.add")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity["total"] == 15

    def test_nested_assignment(self):
        entity = {"user": {"profile": {"score": 0}}}
        rule = parse_rule("entity.user.profile.score == 0 => entity.user.profile.score = 100")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity["user"]["profile"]["score"] == 100

    def test_list_index_assignment(self):
        entity = {"items": [{"value": 10}, {"value": 20}]}
        rule = parse_rule("entity.items[0].value == 10 => entity.items[0].value = 100")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity["items"][0]["value"] == 100

    def test_assignment_with_complex_expression(self):
        entity = {"price": 100, "quantity": 2, "discount": 0.1, "total": 0}
        rule = parse_rule("entity.price > 0 => entity.total = entity.price * entity.quantity * (1 - entity.discount)")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert abs(entity["total"] - 180.0) < 0.01


class TestReturnStatements:
    """Test return statement execution."""

    @pytest.mark.parametrize("value,expected", [
        (42, 42), (3.14, 3.14), ("test", "test"),
        (True, True), (False, False), (None, None),
    ])
    def test_return_literals(self, value, expected):
        entity = {"ready": True}
        if isinstance(value, str):
            rule = parse_rule(f'entity.ready == true => ret "{value}"')
        elif isinstance(value, bool):
            rule = parse_rule(f"entity.ready == true => ret {str(value).lower()}")
        elif value is None:
            rule = parse_rule("entity.ready == true => ret none")
        else:
            rule = parse_rule(f"entity.ready == true => ret {value}")
        
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert result == expected

    def test_return_entity(self):
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => ret entity")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert result == entity

    def test_return_expression(self):
        entity = {"a": 5, "b": 3}
        rule = parse_rule("entity.a > 0 => ret entity.a + entity.b")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert result == 8

    def test_return_nested_path(self):
        entity = {"user": {"profile": {"name": "John"}}}
        rule = parse_rule("entity.user.profile.name != '' => ret entity.user.profile.name")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert result == "John"

    def test_return_workflow_result(self):
        def calculate(e):
            return e["value"] * 2
        
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => ret workflow('calculate')")
        interpreter = RuleInterpreter(entity, {"calculate": calculate})
        matched, result = interpreter.execute(rule.tree)
        assert result == 20

    def test_default_return_true(self):
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => entity.processed = true")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert result is True

    def test_no_return_no_match(self):
        entity = {"value": -1}
        rule = parse_rule("entity.value > 0 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is False
        assert result is None


class TestWorkflowExecution:
    """Test workflow function execution."""

    def test_workflow_no_arguments(self):
        called = []
        def process(e):
            called.append(True)
            e["processed"] = True

        entity = {"value": 10, "processed": False}
        rule = parse_rule("entity.value > 0 => workflow('process')")
        interpreter = RuleInterpreter(entity, {"process": process})
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True
        assert entity["processed"] is True
        assert len(called) == 1

    def test_workflow_single_argument(self):
        def double(e, value):
            return value * 2

        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => ret workflow('double', entity.value)")
        interpreter = RuleInterpreter(entity, {"double": double})
        matched, result = interpreter.execute(rule.tree)
        assert result == 20

    def test_workflow_multiple_arguments(self):
        def multiply(e, a, b, c):
            return a * b * c

        entity = {"a": 2, "b": 3, "c": 4}
        rule = parse_rule("entity.a > 0 => ret workflow('multiply', entity.a, entity.b, entity.c)")
        interpreter = RuleInterpreter(entity, {"multiply": multiply})
        matched, result = interpreter.execute(rule.tree)
        assert result == 24

    def test_workflow_with_literal_arguments(self):
        def add(e, a, b):
            return a + b

        entity = {}
        rule = parse_rule("true => ret workflow('add', 10, 20)")
        interpreter = RuleInterpreter(entity, {"add": add})
        matched, result = interpreter.execute(rule.tree)
        assert result == 30

    def test_workflow_with_expression_arguments(self):
        def add(e, a, b):
            return a + b

        entity = {"x": 5, "y": 3}
        rule = parse_rule("true => ret workflow('add', entity.x + 5, entity.y * 2)")
        interpreter = RuleInterpreter(entity, {"add": add})
        matched, result = interpreter.execute(rule.tree)
        assert result == 16

    def test_workflow_nested_call(self):
        def inner(e):
            return 10
        def outer(e, value):
            return value * 2

        entity = {}
        rule = parse_rule("true => ret workflow('outer', workflow('inner'))")
        interpreter = RuleInterpreter(entity, {"inner": inner, "outer": outer})
        matched, result = interpreter.execute(rule.tree)
        assert result == 20

    def test_workflow_not_found_error(self):
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => workflow('missing')")
        interpreter = RuleInterpreter(entity)
        with pytest.raises(WorkflowNotFoundError):
            interpreter.execute(rule.tree)

    def test_workflow_with_wrapper_class(self):
        from rulang.workflows import Workflow
        
        def process(e):
            e["processed"] = True

        workflow_obj = Workflow(fn=process, reads=["entity.value"], writes=["entity.processed"])
        entity = {"value": 10, "processed": False}
        rule = parse_rule("entity.value > 0 => workflow('process')")
        interpreter = RuleInterpreter(entity, {"process": workflow_obj})
        matched, _ = interpreter.execute(rule.tree)
        assert entity["processed"] is True


class TestMultipleActions:
    """Test multiple action execution."""

    def test_multiple_assignments(self):
        entity = {"a": 0, "b": 0, "c": 0, "ready": True}
        rule = parse_rule("entity.ready == true => entity.a = 1; entity.b = 2; entity.c = 3")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity["a"] == 1
        assert entity["b"] == 2
        assert entity["c"] == 3

    def test_mixed_actions(self):
        called = []
        def process(e):
            called.append(True)

        entity = {"value": 10, "status": "pending"}
        rule = parse_rule("entity.value > 0 => workflow('process'); entity.status = 'done'; ret entity.status")
        interpreter = RuleInterpreter(entity, {"process": process})
        matched, result = interpreter.execute(rule.tree)
        assert len(called) == 1
        assert entity["status"] == "done"
        assert result == "done"

    def test_return_stops_execution(self):
        entity = {"a": 0, "b": 0}
        rule = parse_rule("true => entity.a = 1; ret entity.a; entity.b = 2")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert entity["a"] == 1
        assert entity["b"] == 0  # Should not execute after return
        assert result == 1

