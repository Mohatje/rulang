"""Edge case tests for RuleEngine."""

import pytest
from rule_interpreter import RuleEngine
from rule_interpreter.exceptions import RuleSyntaxError, PathResolutionError, WorkflowNotFoundError, EvaluationError


class TestEngineEdgeCases:
    """Test edge cases in RuleEngine."""

    def test_empty_rule_list(self):
        """Test engine with empty rule list."""
        engine = RuleEngine()
        engine.add_rules([])
        result = engine.evaluate({"value": 10})
        assert result is None

    def test_single_rule_no_match(self):
        """Test single rule that doesn't match."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 100 => ret true"])
        result = engine.evaluate({"value": 10})
        assert result is None

    def test_multiple_rules_all_no_match(self):
        """Test multiple rules where none match."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.value > 100 => ret true",
            "entity.value < 0 => ret false",
            "entity.value == 50 => ret 'middle'"
        ])
        result = engine.evaluate({"value": 10})
        assert result is None

    def test_rule_with_empty_string(self):
        """Test rule with empty string value."""
        engine = RuleEngine()
        engine.add_rules(['entity.value == "" => ret true'])
        result = engine.evaluate({"value": ""})
        assert result is True

    def test_rule_with_none_value(self):
        """Test rule with None value."""
        engine = RuleEngine()
        engine.add_rules(["entity.value == none => ret true"])
        result = engine.evaluate({"value": None})
        assert result is True

    def test_rule_with_boolean_true(self):
        """Test rule with boolean True."""
        engine = RuleEngine()
        engine.add_rules(["entity.value == true => ret true"])
        result = engine.evaluate({"value": True})
        assert result is True

    def test_rule_with_boolean_false(self):
        """Test rule with boolean False."""
        engine = RuleEngine()
        engine.add_rules(["entity.value == false => ret true"])
        result = engine.evaluate({"value": False})
        assert result is True

    def test_rule_with_zero(self):
        """Test rule with zero value."""
        engine = RuleEngine()
        engine.add_rules(["entity.value == 0 => ret true"])
        result = engine.evaluate({"value": 0})
        assert result is True

    def test_rule_with_negative_zero(self):
        """Test rule with negative zero."""
        engine = RuleEngine()
        engine.add_rules(["entity.value == 0 => ret true"])
        result = engine.evaluate({"value": -0})
        assert result is True

    def test_rule_with_very_large_number(self):
        """Test rule with very large number."""
        engine = RuleEngine()
        large_num = 999999999999999999
        engine.add_rules([f"entity.value == {large_num} => ret true"])
        result = engine.evaluate({"value": large_num})
        assert result is True

    def test_rule_with_float(self):
        """Test rule with float value."""
        engine = RuleEngine()
        engine.add_rules(["entity.value == 3.14 => ret true"])
        result = engine.evaluate({"value": 3.14})
        assert result is True

    def test_rule_with_negative_float(self):
        """Test rule with negative float."""
        engine = RuleEngine()
        engine.add_rules(["entity.value == -3.14 => ret true"])
        result = engine.evaluate({"value": -3.14})
        assert result is True

    def test_rule_with_list(self):
        """Test rule with list value."""
        engine = RuleEngine()
        engine.add_rules(["entity.value == [1, 2, 3] => ret true"])
        result = engine.evaluate({"value": [1, 2, 3]})
        assert result is True

    def test_rule_with_empty_list(self):
        """Test rule with empty list."""
        engine = RuleEngine()
        engine.add_rules(["entity.value == [] => ret true"])
        result = engine.evaluate({"value": []})
        assert result is True

    def test_rule_with_nested_list(self):
        """Test rule with nested list."""
        engine = RuleEngine()
        engine.add_rules(["entity.value == [[1, 2], [3, 4]] => ret true"])
        result = engine.evaluate({"value": [[1, 2], [3, 4]]})
        assert result is True

    def test_first_match_mode_stops_after_first(self):
        """Test first_match mode stops after first match."""
        engine = RuleEngine(mode="first_match")
        engine.add_rules([
            "entity.value > 0 => entity.counter = 1; ret 1",
            "entity.value > 0 => entity.counter = 2; ret 2",
            "entity.value > 0 => entity.counter = 3; ret 3"
        ])
        entity = {"value": 10, "counter": 0}
        result = engine.evaluate(entity)
        assert result == 1
        assert entity["counter"] == 1  # Only first rule executed

    def test_all_match_mode_executes_all(self):
        """Test all_match mode executes all matching rules."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.value > 0 => entity.counter += 1",
            "entity.value > 0 => entity.counter += 1",
            "entity.value > 0 => entity.counter += 1"
        ])
        entity = {"value": 10, "counter": 0}
        result = engine.evaluate(entity)
        assert result is True  # Last return value
        assert entity["counter"] == 3  # All rules executed

    def test_all_match_mode_returns_last_value(self):
        """Test all_match mode returns last return value."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.value > 0 => ret 1",
            "entity.value > 0 => ret 2",
            "entity.value > 0 => ret 3"
        ])
        entity = {"value": 10}
        result = engine.evaluate(entity)
        assert result == 3  # Last return value

    def test_rule_with_workflow_not_provided(self):
        """Test rule calling workflow that's not provided."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => workflow('missing')"])
        with pytest.raises(WorkflowNotFoundError):
            engine.evaluate({"value": 10})

    def test_rule_with_workflow_provided(self):
        """Test rule calling workflow that is provided."""
        def test_workflow(entity):
            return "worked"
        
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => ret workflow('test_workflow')"])
        result = engine.evaluate({"value": 10}, workflows={"test_workflow": test_workflow})
        assert result == "worked"

    def test_rule_with_multiple_workflows(self):
        """Test rule calling multiple workflows."""
        def wf1(entity):
            return 1
        
        def wf2(entity, val):
            return val * 2
        
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => ret workflow('wf2', workflow('wf1'))"])
        result = engine.evaluate({"value": 10}, workflows={"wf1": wf1, "wf2": wf2})
        assert result == 2

    def test_rule_with_syntax_error(self):
        """Test rule with syntax error."""
        engine = RuleEngine()
        with pytest.raises(RuleSyntaxError):
            engine.add_rules(["invalid syntax => ret true"])

    def test_rule_with_path_error_in_condition(self):
        """Test rule with path error in condition."""
        engine = RuleEngine()
        engine.add_rules(["entity.missing.path > 0 => ret true"])
        with pytest.raises(PathResolutionError):
            engine.evaluate({"value": 10})

    def test_rule_with_path_error_in_action(self):
        """Test rule with path error in action."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => entity.missing.path = 10"])
        with pytest.raises(PathResolutionError):
            engine.evaluate({"value": 10})

    def test_rule_with_evaluation_error(self):
        """Test rule with evaluation error."""
        def error_workflow(entity):
            raise ValueError("Test error")
        
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => workflow('error_workflow')"])
        with pytest.raises(EvaluationError):
            engine.evaluate({"value": 10}, workflows={"error_workflow": error_workflow})

    def test_rule_replacement(self):
        """Test adding rules (they append, not replace)."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => ret 1"])
        result1 = engine.evaluate({"value": 10})
        assert result1 == 1
        
        engine.add_rules(["entity.value > 0 => ret 2"])
        result2 = engine.evaluate({"value": 10})
        # Rules append, so first match wins
        assert result2 == 1

    def test_rule_with_dependency_chain(self):
        """Test rules with dependency chain."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.a > 0 => entity.b = 10",
            "entity.b > 5 => entity.c = 20",
            "entity.c > 15 => ret true"
        ])
        entity = {"a": 10, "b": 0, "c": 0}
        result = engine.evaluate(entity)
        assert result is True
        assert entity["b"] == 10
        assert entity["c"] == 20

    def test_rule_with_cycle_detection(self):
        """Test rules with cycle detection."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.a > 0 => entity.b = 10",
            "entity.b > 0 => entity.a = 20"
        ])
        entity = {"a": 10, "b": 0}
        # Should detect cycle and warn, but still execute
        result = engine.evaluate(entity)
        assert result is True

    def test_rule_with_complex_dependencies(self):
        """Test rules with complex dependencies."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.x > 0 => entity.y = 10",
            "entity.y > 0 => entity.z = 20",
            "entity.z > 0 => entity.w = 30",
            "entity.w > 0 => ret true"
        ])
        entity = {"x": 10, "y": 0, "z": 0, "w": 0}
        result = engine.evaluate(entity)
        assert result is True
        assert entity["w"] == 30

    def test_rule_with_no_dependencies(self):
        """Test rules with no dependencies."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.a > 0 => ret 1",
            "entity.b > 0 => ret 2",
            "entity.c > 0 => ret 3"
        ])
        entity = {"a": 10, "b": 20, "c": 30}
        result = engine.evaluate(entity)
        assert result == 1  # First match

    def test_rule_with_mixed_dependencies(self):
        """Test rules with mixed dependencies."""
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.a > 0 => entity.b = 10",
            "entity.c > 0 => ret 2",
            "entity.b > 0 => entity.d = 20; ret 3"
        ])
        entity = {"a": 10, "b": 0, "c": 20, "d": 0}
        result = engine.evaluate(entity)
        assert result == 3  # Last return value
        assert entity["b"] == 10
        assert entity["d"] == 20

    def test_rule_with_workflow_dependencies(self):
        """Test rules with workflow dependencies."""
        from rule_interpreter.workflows import Workflow
        
        def modify_a(entity):
            entity["a"] = 100
        
        workflow_obj = Workflow(modify_a, reads=[], writes=["a"])
        
        engine = RuleEngine()
        engine.add_rules([
            "entity.x > 0 => workflow('modify_a')",
            "entity.a > 50 => ret true"
        ])
        entity = {"x": 10, "a": 0}
        result = engine.evaluate(entity, workflows={"modify_a": workflow_obj})
        assert result is True
        assert entity["a"] == 100

    def test_rule_with_nested_paths(self):
        """Test rules with nested paths."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.level1.level2.value > 0 => entity.level1.level2.result = 10; ret true"
        ])
        entity = {"level1": {"level2": {"value": 10, "result": 0}}}
        result = engine.evaluate(entity)
        assert result is True
        assert entity["level1"]["level2"]["result"] == 10

    def test_rule_with_list_indexing(self):
        """Test rules with list indexing."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.items[0] > 0 => entity.items[0] = 100; ret true"
        ])
        entity = {"items": [10, 20, 30]}
        result = engine.evaluate(entity)
        assert result is True
        assert entity["items"][0] == 100

    def test_rule_with_negative_index(self):
        """Test rules with negative index."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.items[-1] > 0 => entity.items[-1] = 100; ret true"
        ])
        entity = {"items": [10, 20, 30]}
        result = engine.evaluate(entity)
        assert result is True
        assert entity["items"][-1] == 100

    def test_rule_with_dynamic_index(self):
        """Test rules with dynamic index."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.items[entity.index] > 0 => entity.items[entity.index] = 100; ret true"
        ])
        entity = {"items": [10, 20, 30], "index": 1}
        result = engine.evaluate(entity)
        assert result is True
        assert entity["items"][1] == 100

    def test_rule_with_string_comparison(self):
        """Test rules with string comparison."""
        engine = RuleEngine()
        engine.add_rules(['entity.name == "test" => ret true'])
        result = engine.evaluate({"name": "test"})
        assert result is True

    def test_rule_with_string_inequality(self):
        """Test rules with string inequality."""
        engine = RuleEngine()
        engine.add_rules(['entity.name != "test" => ret true'])
        result = engine.evaluate({"name": "other"})
        assert result is True

    def test_rule_with_string_less_than(self):
        """Test rules with string less than."""
        engine = RuleEngine()
        engine.add_rules(['entity.name < "z" => ret true'])
        result = engine.evaluate({"name": "a"})
        assert result is True

    def test_rule_with_string_greater_than(self):
        """Test rules with string greater than."""
        engine = RuleEngine()
        engine.add_rules(['entity.name > "a" => ret true'])
        result = engine.evaluate({"name": "z"})
        assert result is True

    def test_rule_with_membership_in(self):
        """Test rules with membership 'in'."""
        engine = RuleEngine()
        engine.add_rules(["entity.value in [1, 2, 3] => ret true"])
        result = engine.evaluate({"value": 2})
        assert result is True

    def test_rule_with_membership_not_in(self):
        """Test rules with membership 'not in'."""
        engine = RuleEngine()
        engine.add_rules(["entity.value not in [1, 2, 3] => ret true"])
        result = engine.evaluate({"value": 5})
        assert result is True

    def test_rule_with_logical_and(self):
        """Test rules with logical AND."""
        engine = RuleEngine()
        engine.add_rules(["entity.a > 0 and entity.b > 0 => ret true"])
        result = engine.evaluate({"a": 10, "b": 20})
        assert result is True

    def test_rule_with_logical_or(self):
        """Test rules with logical OR."""
        engine = RuleEngine()
        engine.add_rules(["entity.a > 0 or entity.b > 0 => ret true"])
        result = engine.evaluate({"a": 10, "b": 0})
        assert result is True

    def test_rule_with_logical_not(self):
        """Test rules with logical NOT."""
        engine = RuleEngine()
        engine.add_rules(["not entity.value > 0 => ret true"])
        result = engine.evaluate({"value": -10})
        assert result is True

    def test_rule_with_arithmetic_addition(self):
        """Test rules with arithmetic addition."""
        engine = RuleEngine()
        engine.add_rules(["entity.a + entity.b >= 10 => ret true"])
        result = engine.evaluate({"a": 5, "b": 5})
        assert result is True

    def test_rule_with_arithmetic_subtraction(self):
        """Test rules with arithmetic subtraction."""
        engine = RuleEngine()
        engine.add_rules(["entity.a - entity.b >= 0 => ret true"])
        result = engine.evaluate({"a": 10, "b": 5})
        assert result is True

    def test_rule_with_arithmetic_multiplication(self):
        """Test rules with arithmetic multiplication."""
        engine = RuleEngine()
        engine.add_rules(["entity.a * entity.b >= 20 => ret true"])
        result = engine.evaluate({"a": 5, "b": 4})
        assert result is True

    def test_rule_with_arithmetic_division(self):
        """Test rules with arithmetic division."""
        engine = RuleEngine()
        engine.add_rules(["entity.a / entity.b >= 2 => ret true"])
        result = engine.evaluate({"a": 10, "b": 5})
        assert result is True

    def test_rule_with_arithmetic_modulo(self):
        """Test rules with arithmetic modulo."""
        engine = RuleEngine()
        engine.add_rules(["entity.a % entity.b == 0 => ret true"])
        result = engine.evaluate({"a": 10, "b": 5})
        assert result is True

    def test_rule_with_unary_minus(self):
        """Test rules with unary minus."""
        engine = RuleEngine()
        engine.add_rules(["-entity.value >= 0 => ret true"])
        result = engine.evaluate({"value": -10})
        assert result is True

    def test_rule_with_compound_assignment_add(self):
        """Test rules with compound assignment +=."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => entity.counter += 10"])
        entity = {"value": 10, "counter": 5}
        engine.evaluate(entity)
        assert entity["counter"] == 15

    def test_rule_with_compound_assignment_sub(self):
        """Test rules with compound assignment -=."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => entity.counter -= 5"])
        entity = {"value": 10, "counter": 20}
        engine.evaluate(entity)
        assert entity["counter"] == 15

    def test_rule_with_compound_assignment_mul(self):
        """Test rules with compound assignment *=."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => entity.counter *= 2"])
        entity = {"value": 10, "counter": 5}
        engine.evaluate(entity)
        assert entity["counter"] == 10

    def test_rule_with_compound_assignment_div(self):
        """Test rules with compound assignment /=."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => entity.counter /= 2"])
        entity = {"value": 10, "counter": 20}
        engine.evaluate(entity)
        assert entity["counter"] == 10.0

    def test_rule_with_compound_assignment_mod(self):
        """Test rules with compound assignment %= (not supported)."""
        engine = RuleEngine()
        # Modulo assignment not supported in grammar
        with pytest.raises(RuleSyntaxError):
            engine.add_rules(["entity.value > 0 => entity.counter %= 3"])

    def test_rule_with_return_entity(self):
        """Test rules with return entity."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => ret entity"])
        entity = {"value": 10}
        result = engine.evaluate(entity)
        assert result is entity

    def test_rule_with_return_literal(self):
        """Test rules with return literal."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => ret 42"])
        result = engine.evaluate({"value": 10})
        assert result == 42

    def test_rule_with_return_string(self):
        """Test rules with return string."""
        engine = RuleEngine()
        engine.add_rules(['entity.value > 0 => ret "success"'])
        result = engine.evaluate({"value": 10})
        assert result == "success"

    def test_rule_with_return_boolean(self):
        """Test rules with return boolean."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => ret false"])
        result = engine.evaluate({"value": 10})
        assert result is False

    def test_rule_with_return_none(self):
        """Test rules with return None."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => ret none"])
        result = engine.evaluate({"value": 10})
        assert result is None

    def test_rule_with_multiple_actions(self):
        """Test rules with multiple actions."""
        engine = RuleEngine()
        engine.add_rules(["entity.value > 0 => entity.a = 1; entity.b = 2; entity.c = 3"])
        entity = {"value": 10, "a": 0, "b": 0, "c": 0}
        engine.evaluate(entity)
        assert entity["a"] == 1
        assert entity["b"] == 2
        assert entity["c"] == 3

    def test_rule_with_comment(self):
        """Test rules with comment (comments after actions not supported)."""
        engine = RuleEngine()
        # Comments after actions not supported in grammar
        with pytest.raises(RuleSyntaxError):
            engine.add_rules(["entity.value > 0 => ret true  // This is a comment"])

    def test_rule_with_whitespace(self):
        """Test rules with extra whitespace."""
        engine = RuleEngine()
        engine.add_rules(["  entity.value  >  0  =>  ret  true  "])
        result = engine.evaluate({"value": 10})
        assert result is True

    def test_rule_with_parentheses(self):
        """Test rules with parentheses."""
        engine = RuleEngine()
        engine.add_rules(["((entity.a + entity.b) * entity.c) > 0 => ret true"])
        result = engine.evaluate({"a": 1, "b": 2, "c": 3})
        assert result is True

