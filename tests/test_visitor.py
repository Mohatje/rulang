"""Tests for the rule visitor/interpreter."""

import pytest
from dataclasses import dataclass

from rule_interpreter.visitor import parse_rule, RuleInterpreter
from rule_interpreter.exceptions import PathResolutionError, WorkflowNotFoundError


class TestConditionEvaluation:
    """Test condition evaluation."""

    def test_equality(self):
        rule = parse_rule("entity.value == 10 => ret true")
        interpreter = RuleInterpreter({"value": 10})
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert result is True

        interpreter = RuleInterpreter({"value": 5})
        matched, result = interpreter.execute(rule.tree)
        assert matched is False

    def test_inequality(self):
        rule = parse_rule("entity.value != 10 => ret true")
        interpreter = RuleInterpreter({"value": 5})
        matched, result = interpreter.execute(rule.tree)
        assert matched is True

    def test_comparison_operators(self):
        entity = {"value": 15}

        rule = parse_rule("entity.value > 10 => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

        rule = parse_rule("entity.value >= 15 => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

        rule = parse_rule("entity.value < 20 => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

        rule = parse_rule("entity.value <= 15 => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

    def test_arithmetic_in_condition(self):
        entity = {"price": 10, "quantity": 5}
        rule = parse_rule("entity.price * entity.quantity >= 50 => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

    def test_logical_and(self):
        entity = {"a": 5, "b": 3}
        rule = parse_rule("entity.a > 0 and entity.b > 0 => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

        entity = {"a": 5, "b": -1}
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is False

    def test_logical_or(self):
        entity = {"a": -1, "b": 5}
        rule = parse_rule("entity.a > 0 or entity.b > 0 => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

    def test_logical_not(self):
        entity = {"disabled": False}
        rule = parse_rule("not entity.disabled => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

    def test_membership_in(self):
        entity = {"status": "active"}
        rule = parse_rule("entity.status in ['active', 'pending'] => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

        entity = {"status": "deleted"}
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is False

    def test_membership_not_in(self):
        entity = {"status": "active"}
        rule = parse_rule("entity.status not in ['deleted', 'archived'] => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True


class TestPathResolution:
    """Test path resolution for different entity types."""

    def test_dict_entity(self):
        entity = {"user": {"profile": {"name": "John"}}}
        rule = parse_rule("entity.user.profile.name == 'John' => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

    def test_object_entity(self):
        @dataclass
        class Profile:
            name: str

        @dataclass
        class User:
            profile: Profile

        @dataclass
        class Entity:
            user: User

        entity = Entity(user=User(profile=Profile(name="John")))
        rule = parse_rule("entity.user.profile.name == 'John' => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

    def test_list_index(self):
        entity = {"items": [{"value": 10}, {"value": 20}, {"value": 30}]}
        rule = parse_rule("entity.items[1].value == 20 => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

    def test_negative_index(self):
        entity = {"items": [{"value": 10}, {"value": 20}, {"value": 30}]}
        rule = parse_rule("entity.items[-1].value == 30 => ret true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True

    def test_missing_path_raises_error(self):
        entity = {"name": "test"}
        rule = parse_rule("entity.missing.path == 'value' => ret true")
        with pytest.raises(PathResolutionError):
            RuleInterpreter(entity).execute(rule.tree)


class TestAssignments:
    """Test assignment actions."""

    def test_simple_assignment(self):
        entity = {"status": "pending"}
        rule = parse_rule("entity.status == 'pending' => entity.status = 'processed'")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True
        assert entity["status"] == "processed"

    def test_nested_assignment(self):
        entity = {"user": {"active": False}}
        rule = parse_rule("entity.user.active == false => entity.user.active = true")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True
        assert entity["user"]["active"] is True

    def test_compound_addition(self):
        entity = {"counter": 10}
        rule = parse_rule("entity.counter > 0 => entity.counter += 5")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True
        assert entity["counter"] == 15

    def test_compound_subtraction(self):
        entity = {"counter": 10}
        rule = parse_rule("entity.counter > 0 => entity.counter -= 3")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert entity["counter"] == 7

    def test_compound_multiplication(self):
        entity = {"value": 5}
        rule = parse_rule("entity.value > 0 => entity.value *= 2")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert entity["value"] == 10

    def test_compound_division(self):
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => entity.value /= 2")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert entity["value"] == 5.0

    def test_assignment_with_expression(self):
        entity = {"price": 100, "discount": 0.1, "final_price": 0}
        rule = parse_rule("entity.price > 0 => entity.final_price = entity.price * (1 - entity.discount)")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert entity["final_price"] == 90.0


class TestReturnStatements:
    """Test return statements."""

    def test_return_literal(self):
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => ret 42")
        matched, result = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True
        assert result == 42

    def test_return_entity(self):
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => ret entity")
        matched, result = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True
        assert result == entity

    def test_return_expression(self):
        entity = {"a": 5, "b": 3}
        rule = parse_rule("entity.a > 0 => ret entity.a + entity.b")
        matched, result = RuleInterpreter(entity).execute(rule.tree)
        assert result == 8

    def test_return_string(self):
        entity = {"status": "ready"}
        rule = parse_rule("entity.status == 'ready' => ret 'processed'")
        matched, result = RuleInterpreter(entity).execute(rule.tree)
        assert result == "processed"

    def test_default_return_true(self):
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => entity.processed = true")
        matched, result = RuleInterpreter(entity).execute(rule.tree)
        assert matched is True
        assert result is True


class TestWorkflowCalls:
    """Test workflow function calls."""

    def test_simple_workflow(self):
        entity = {"value": 10, "processed": False}

        def process(e):
            e["processed"] = True

        rule = parse_rule("entity.value > 0 => workflow('process')")
        matched, _ = RuleInterpreter(entity, {"process": process}).execute(rule.tree)
        assert matched is True
        assert entity["processed"] is True

    def test_workflow_with_return_value(self):
        entity = {"value": 10}

        def calculate(e):
            return e["value"] * 2

        rule = parse_rule("entity.value > 0 => ret workflow('calculate')")
        matched, result = RuleInterpreter(entity, {"calculate": calculate}).execute(rule.tree)
        assert result == 20

    def test_workflow_not_found(self):
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => workflow('missing')")
        with pytest.raises(WorkflowNotFoundError):
            RuleInterpreter(entity).execute(rule.tree)


class TestMultipleActions:
    """Test multiple actions in a single rule."""

    def test_multiple_assignments(self):
        entity = {"a": 0, "b": 0, "c": 0, "ready": True}
        rule = parse_rule("entity.ready == true => entity.a = 1; entity.b = 2; entity.c = 3")
        matched, _ = RuleInterpreter(entity).execute(rule.tree)
        assert entity["a"] == 1
        assert entity["b"] == 2
        assert entity["c"] == 3

    def test_workflow_then_assignment(self):
        entity = {"value": 10, "processed": False, "status": "pending"}

        def process(e):
            e["processed"] = True

        rule = parse_rule("entity.value > 0 => workflow('process'); entity.status = 'done'")
        matched, _ = RuleInterpreter(entity, {"process": process}).execute(rule.tree)
        assert entity["processed"] is True
        assert entity["status"] == "done"

    def test_assignment_then_return(self):
        entity = {"value": 10, "status": "pending"}
        rule = parse_rule("entity.value > 0 => entity.status = 'done'; ret entity.status")
        matched, result = RuleInterpreter(entity).execute(rule.tree)
        assert entity["status"] == "done"
        assert result == "done"

