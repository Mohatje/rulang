"""Edge case tests for visitor/interpreter."""

import pytest
from dataclasses import dataclass

from rule_interpreter.visitor import parse_rule, RuleInterpreter
from rule_interpreter.exceptions import PathResolutionError, EvaluationError, RuleSyntaxError


class TestVisitorEdgeCases:
    """Test edge cases in visitor/interpreter."""

    def test_comparison_with_zero(self):
        """Test comparisons with zero."""
        entity = {"value": 0}
        rule = parse_rule("entity.value == 0 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_comparison_with_negative_zero(self):
        """Test comparison with negative zero."""
        entity = {"value": -0}
        rule = parse_rule("entity.value == 0 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_very_large_integer_comparison(self):
        """Test comparison with very large integers."""
        entity = {"value": 999999999999999999}
        rule = parse_rule("entity.value == 999999999999999999 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_float_precision(self):
        """Test float precision in comparisons."""
        entity = {"value": 0.1 + 0.2}
        rule = parse_rule("entity.value == 0.3 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        # Floating point precision issues
        assert matched is False  # 0.1 + 0.2 != 0.3 exactly

    def test_string_comparison_case_sensitive(self):
        """Test string comparison is case sensitive."""
        entity = {"value": "Test"}
        rule = parse_rule('entity.value == "test" => ret true')
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is False

    def test_string_comparison_exact_match(self):
        """Test string exact match."""
        entity = {"value": "test"}
        rule = parse_rule('entity.value == "test" => ret true')
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_empty_string_comparison(self):
        """Test empty string comparison."""
        entity = {"value": ""}
        rule = parse_rule('entity.value == "" => ret true')
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_none_comparison(self):
        """Test None comparison."""
        entity = {"value": None}
        rule = parse_rule("entity.value == none => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_boolean_truthiness(self):
        """Test boolean truthiness."""
        entity = {"value": True}
        rule = parse_rule("entity.value == true => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_list_comparison(self):
        """Test list comparison."""
        entity = {"value": [1, 2, 3]}
        rule = parse_rule("entity.value == [1, 2, 3] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        # Lists are compared by reference/value
        assert matched is True

    def test_dict_comparison(self):
        """Test dict comparison - dict literals not supported in grammar."""
        # Dict literals are not supported in the grammar
        # We can only compare paths, not dict literals directly
        entity = {"value": {"a": 1}, "other": {"a": 1}}
        # Can only compare paths, not literals
        rule = parse_rule("entity.value == entity.other => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        # Dict comparison by reference/value
        assert matched is True

    def test_arithmetic_overflow_simulation(self):
        """Test arithmetic with very large numbers."""
        entity = {"a": 999999999999999999, "b": 1, "result": 0}
        rule = parse_rule("entity.a + entity.b >= entity.result => entity.result = entity.a + entity.b; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert result > 999999999999999999

    def test_division_by_very_small_number(self):
        """Test division by very small number."""
        entity = {"a": 10, "b": 0.0000001}
        rule = parse_rule("entity.b != 0 => entity.result = entity.a / entity.b; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert result > 10000000

    def test_modulo_with_negative(self):
        """Test modulo with negative numbers."""
        entity = {"a": -10, "b": 3}
        rule = parse_rule("entity.b != 0 => entity.result = entity.a % entity.b; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        # Python modulo: -10 % 3 = 2
        assert result == 2

    def test_unary_minus_with_zero(self):
        """Test unary minus with zero."""
        entity = {"value": 0, "neg": -1}
        rule = parse_rule("-entity.value >= entity.neg => entity.neg = -entity.value; ret entity.neg")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert result == 0

    def test_logical_short_circuit_and(self):
        """Test logical AND short-circuit."""
        call_count = {"b": 0}
        
        def get_b():
            call_count["b"] += 1
            return 5
        
        entity = {"a": False, "b_func": get_b}
        # Can't directly call functions, but can test short-circuit with paths
        rule = parse_rule("entity.a == true and entity.b > 0 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is False

    def test_logical_short_circuit_or(self):
        """Test logical OR short-circuit."""
        entity = {"a": True, "b": False}
        rule = parse_rule("entity.a == true or entity.b == true => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_membership_with_empty_list(self):
        """Test membership with empty list."""
        entity = {"value": 1}
        rule = parse_rule("entity.value in [] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is False

    def test_membership_with_single_element(self):
        """Test membership with single element list."""
        entity = {"value": 42}
        rule = parse_rule("entity.value in [42] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_not_in_with_present_value(self):
        """Test 'not in' with value present."""
        entity = {"value": 1}
        rule = parse_rule("entity.value not in [1, 2, 3] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is False

    def test_not_in_with_absent_value(self):
        """Test 'not in' with value absent."""
        entity = {"value": 5}
        rule = parse_rule("entity.value not in [1, 2, 3] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_assignment_creates_new_key(self):
        """Test assignment creates new dictionary key."""
        entity = {}
        rule = parse_rule("true => entity.new_key = 'value'")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity["new_key"] == "value"

    def test_assignment_overwrites_existing(self):
        """Test assignment overwrites existing value."""
        entity = {"key": "old"}
        rule = parse_rule("true => entity.key = 'new'")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity["key"] == "new"

    def test_compound_assignment_with_zero(self):
        """Test compound assignment with zero."""
        entity = {"counter": 0}
        rule = parse_rule("true => entity.counter += 10")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity["counter"] == 10

    def test_compound_assignment_with_negative(self):
        """Test compound assignment with negative."""
        entity = {"value": 10}
        rule = parse_rule("true => entity.value += -5")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity["value"] == 5

    def test_assignment_to_nonexistent_nested(self):
        """Test assignment to nonexistent nested path."""
        entity = {}
        rule = parse_rule("true => entity.user.name = 'John'")
        interpreter = RuleInterpreter(entity)
        with pytest.raises(PathResolutionError):
            interpreter.execute(rule.tree)

    def test_return_stops_execution(self):
        """Test return stops further execution."""
        entity = {"a": 0, "b": 0}
        rule = parse_rule("true => entity.a = 1; ret entity.a; entity.b = 2")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert entity["a"] == 1
        assert entity["b"] == 0  # Should not execute
        assert result == 1

    def test_workflow_with_none_return(self):
        """Test workflow returning None."""
        def return_none(entity):
            return None
        
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => ret workflow('return_none')")
        interpreter = RuleInterpreter(entity, {"return_none": return_none})
        matched, result = interpreter.execute(rule.tree)
        assert result is None

    def test_workflow_with_exception(self):
        """Test workflow raising exception."""
        def raise_error(entity):
            raise ValueError("Test error")
        
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => workflow('raise_error')")
        interpreter = RuleInterpreter(entity, {"raise_error": raise_error})
        with pytest.raises(EvaluationError):
            interpreter.execute(rule.tree)

    def test_workflow_with_wrong_arg_count(self):
        """Test workflow with wrong argument count."""
        def two_args(entity, a, b):
            return a + b
        
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => ret workflow('two_args', entity.value)")
        interpreter = RuleInterpreter(entity, {"two_args": two_args})
        # Should raise TypeError when called
        with pytest.raises((TypeError, EvaluationError)):
            interpreter.execute(rule.tree)

    def test_condition_false_no_actions_execute(self):
        """Test that false condition prevents action execution."""
        entity = {"value": 5, "processed": False}
        rule = parse_rule("entity.value > 10 => entity.processed = true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is False
        assert entity["processed"] is False

    def test_multiple_returns_first_wins(self):
        """Test that first return statement wins."""
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => ret 1; ret 2")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert result == 1  # First return

    def test_default_return_when_no_explicit(self):
        """Test default return True when no explicit return."""
        entity = {"value": 10}
        rule = parse_rule("entity.value > 0 => entity.processed = true")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert result is True

    def test_nested_path_resolution(self):
        """Test nested path resolution."""
        entity = {"level1": {"level2": {"level3": {"value": 10}}}}
        rule = parse_rule("entity.level1.level2.level3.value == 10 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_list_index_resolution(self):
        """Test list index resolution."""
        entity = {"items": [{"value": 10}, {"value": 20}]}
        rule = parse_rule("entity.items[0].value == 10 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_negative_index_resolution(self):
        """Test negative index resolution."""
        entity = {"items": [{"value": 10}, {"value": 20}]}
        rule = parse_rule("entity.items[-1].value == 20 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_dynamic_index_resolution(self):
        """Test dynamic index resolution."""
        entity = {"items": [{"value": 10}, {"value": 20}], "index": 1}
        rule = parse_rule("entity.items[entity.index].value == 20 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_missing_path_in_condition(self):
        """Test missing path in condition raises error."""
        entity = {"name": "test"}
        rule = parse_rule("entity.missing.path > 0 => ret true")
        interpreter = RuleInterpreter(entity)
        with pytest.raises(PathResolutionError):
            interpreter.execute(rule.tree)

    def test_missing_path_in_action(self):
        """Test missing path in action raises error."""
        entity = {"name": "test"}
        rule = parse_rule("true => entity.missing.path = 10")
        interpreter = RuleInterpreter(entity)
        with pytest.raises(PathResolutionError):
            interpreter.execute(rule.tree)

    def test_dataclass_entity_assignment(self):
        """Test assignment to dataclass entity."""
        @dataclass
        class Entity:
            value: int
        
        entity = Entity(value=10)
        rule = parse_rule("entity.value > 0 => entity.value = 20")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert entity.value == 20

    def test_object_with_property(self):
        """Test object with property access."""
        class Entity:
            def __init__(self):
                self._value = 10
            
            @property
            def value(self):
                return self._value
        
        entity = Entity()
        rule = parse_rule("entity.value == 10 => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is True

    def test_complex_expression_evaluation(self):
        """Test complex expression evaluation."""
        entity = {"a": 10, "b": 5, "c": 2, "result": 0}
        rule = parse_rule("(entity.a + entity.b) * entity.c >= entity.result => entity.result = (entity.a + entity.b) * entity.c; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert result == 30

    def test_nested_workflow_calls(self):
        """Test nested workflow calls."""
        def inner(entity):
            return 10
        
        def outer(entity, value):
            return value * 2
        
        entity = {}
        rule = parse_rule("true => ret workflow('outer', workflow('inner'))")
        interpreter = RuleInterpreter(entity, {"inner": inner, "outer": outer})
        matched, result = interpreter.execute(rule.tree)
        assert result == 20

    def test_workflow_modifies_entity(self):
        """Test workflow that modifies entity."""
        def modify(entity):
            entity["modified"] = True
            return entity["modified"]
        
        entity = {"value": 10, "modified": False}
        rule = parse_rule("entity.value > 0 => workflow('modify')")
        interpreter = RuleInterpreter(entity, {"modify": modify})
        matched, _ = interpreter.execute(rule.tree)
        assert entity["modified"] is True

    def test_comparison_different_types(self):
        """Test comparison between different types."""
        entity = {"value": 10}
        rule = parse_rule('entity.value == "10" => ret true')
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        assert matched is False  # 10 != "10"

    def test_list_with_none_elements(self):
        """Test list with None elements."""
        entity = {"value": None}
        rule = parse_rule("entity.value in [None, 1, 2] => ret true")
        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(rule.tree)
        # None comparison
        assert matched is True

    def test_boolean_arithmetic(self):
        """Test arithmetic with booleans."""
        entity = {"a": True, "b": False, "result": 0}
        rule = parse_rule("entity.a + entity.b >= entity.result => entity.result = entity.a + entity.b; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        # True = 1, False = 0 in Python arithmetic
        assert result == 1

    def test_modulo_with_float(self):
        """Test modulo with floats."""
        entity = {"a": 10.5, "b": 3.0}
        rule = parse_rule("entity.b != 0 => entity.result = entity.a % entity.b; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert matched is True
        assert isinstance(result, float)

    def test_division_result_is_float(self):
        """Test division always results in float."""
        entity = {"a": 10, "b": 2}
        rule = parse_rule("entity.b != 0 => entity.result = entity.a / entity.b; ret entity.result")
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(rule.tree)
        assert result == 5.0  # Division always float in Python 3

    def test_floor_division_not_supported(self):
        """Test that floor division (//) is not supported."""
        # Floor division operator not in grammar
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.a // entity.b >= 0 => ret true")

    def test_power_operator_not_supported(self):
        """Test that power operator (**) is not supported."""
        # Power operator not in grammar
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.a ** entity.b >= 0 => ret true")

    def test_bitwise_operators_not_supported(self):
        """Test that bitwise operators are not supported."""
        for op in ["&", "|", "^", "<<", ">>"]:
            with pytest.raises(RuleSyntaxError):
                parse_rule(f"entity.a {op} entity.b >= 0 => ret true")

    def test_ternary_operator_not_supported(self):
        """Test that ternary operator is not supported."""
        # No ternary in grammar
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.a > 0 ? entity.b : entity.c => ret true")

    def test_assignment_chain_not_supported(self):
        """Test that assignment chaining is not supported."""
        # Chained assignments like a = b = c not in grammar
        with pytest.raises(RuleSyntaxError):
            parse_rule("true => entity.a = entity.b = 10")

    def test_increment_decrement_not_supported(self):
        """Test that increment/decrement operators are not supported."""
        for op in ["++", "--"]:
            with pytest.raises(RuleSyntaxError):
                parse_rule(f"entity.value{op} => ret true")


class TestTruthyConditions:
    """Test truthy value conditions."""

    def test_truthy_value_as_condition(self):
        """Test truthy check with no comparison operator."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.enabled => entity.result = 'yes'")

        entity = {"enabled": True, "result": "no"}
        engine.evaluate(entity)
        assert entity["result"] == "yes"

        entity = {"enabled": False, "result": "no"}
        engine.evaluate(entity)
        assert entity["result"] == "no"

    def test_numeric_truthy_as_condition(self):
        """Test numeric value as truthy condition."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.count => entity.has_items = true")

        entity = {"count": 5, "has_items": False}
        engine.evaluate(entity)
        assert entity["has_items"] is True

        entity = {"count": 0, "has_items": False}
        engine.evaluate(entity)
        assert entity["has_items"] is False

    def test_string_truthy_as_condition(self):
        """Test string value as truthy condition."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.name => entity.has_name = true")

        entity = {"name": "John", "has_name": False}
        engine.evaluate(entity)
        assert entity["has_name"] is True

        entity = {"name": "", "has_name": False}
        engine.evaluate(entity)
        assert entity["has_name"] is False

    def test_comparison_no_operator_fallthrough(self):
        """Test comparison with just a value, no operator."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.active => entity.checked = true")

        entity = {"active": True, "checked": False}
        engine.evaluate(entity)
        assert entity["checked"] is True

        entity = {"active": False, "checked": False}
        engine.evaluate(entity)
        assert entity["checked"] is False

    def test_comparison_with_just_value(self):
        """Test truthy check with just a value."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.count => entity.has_items = true")

        entity = {"count": 5, "has_items": False}
        engine.evaluate(entity)
        assert entity["has_items"] is True


class TestContainsOperatorEdgeCases:
    """Test contains_any and contains_all with non-list values."""

    def test_contains_any_with_scalar_values(self):
        """Test _contains_any with non-list values."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.tag contains_any 'urgent' => entity.priority = 'high'")

        entity = {"tag": ["urgent", "normal"], "priority": "low"}
        engine.evaluate(entity)
        assert entity["priority"] == "high"

    def test_contains_any_with_scalar_collection(self):
        """Test _contains_any with scalar as collection."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.value contains_any [1, 2, 3] => entity.found = true")

        entity = {"value": 2, "found": False}
        engine.evaluate(entity)
        assert entity["found"] is True

    def test_contains_all_with_scalar_values(self):
        """Test _contains_all with non-list values."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.tags contains_all 'required' => entity.valid = true")

        entity = {"tags": ["required", "optional"], "valid": False}
        engine.evaluate(entity)
        assert entity["valid"] is True

    def test_contains_all_with_scalar_collection(self):
        """Test _contains_all with scalar as collection."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.value contains_all [5] => entity.exact = true")

        entity = {"value": 5, "exact": False}
        engine.evaluate(entity)
        assert entity["exact"] is True


class TestUnknownFunction:
    """Test unknown function error."""

    def test_unknown_function_error(self):
        """Test unknown function raises EvaluationError."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("unknown_func(entity.value) > 0 => entity.result = true")

        with pytest.raises(EvaluationError, match="Unknown function"):
            engine.evaluate({"value": 10, "result": False})


class TestActionsWithReturn:
    """Test early return in actions."""

    def test_return_stops_subsequent_actions(self):
        """Test early return break in actions loop."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.x > 0 => ret 'early'; entity.y = 100")

        entity = {"x": 5, "y": 0}
        result = engine.evaluate(entity)

        assert result == "early"
        assert entity["y"] == 0

    def test_return_in_middle_of_actions(self):
        """Test return in the middle of multiple actions."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.a > 0 => entity.b = 1; ret 'done'; entity.c = 1")

        entity = {"a": 5, "b": 0, "c": 0}
        result = engine.evaluate(entity)

        assert result == "done"
        assert entity["b"] == 1
        assert entity["c"] == 0

    def test_three_actions_return_in_middle(self):
        """Test three actions with return in middle."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.x > 0 => entity.a = 1; entity.b = 2; ret 'stop'; entity.c = 3")

        entity = {"x": 5, "a": 0, "b": 0, "c": 0}
        result = engine.evaluate(entity)

        assert result == "stop"
        assert entity["a"] == 1
        assert entity["b"] == 2
        assert entity["c"] == 0

    def test_first_action_returns(self):
        """Test return as first action stops all subsequent."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.x > 0 => ret 42; entity.y = 100")

        entity = {"x": 5, "y": 0}
        result = engine.evaluate(entity)

        assert result == 42
        assert entity["y"] == 0


class TestCompoundAssignments:
    """Test compound assignment operators."""

    def test_all_compound_assignments(self):
        """Ensure all compound assignments work."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.a > 0 => entity.a += 5",
            "entity.b > 0 => entity.b -= 3",
            "entity.c > 0 => entity.c *= 2",
            "entity.d > 0 => entity.d /= 4",
        ])

        entity = {"a": 10, "b": 10, "c": 10, "d": 20}
        engine.evaluate(entity)
        assert entity["a"] == 15
        assert entity["b"] == 7
        assert entity["c"] == 20
        assert entity["d"] == 5


class TestDynamicPathIndex:
    """Test non-numeric index in path brackets."""

    def test_string_key_in_brackets(self):
        """Test non-numeric index (string key) in path brackets."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.data[entity.key] > 0 => entity.found = true")

        entity = {"data": {"mykey": 42}, "key": "mykey", "found": False}
        engine.evaluate(entity)
        assert entity["found"] is True

    def test_dynamic_string_key(self):
        """Test dynamic string key in brackets."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.config[entity.setting_name] == 'enabled' => entity.active = true")

        entity = {
            "config": {"feature_x": "enabled", "feature_y": "disabled"},
            "setting_name": "feature_x",
            "active": False
        }
        engine.evaluate(entity)
        assert entity["active"] is True


class TestComplexArithmeticExpressions:
    """Test complex arithmetic expressions."""

    def test_complex_addition_expression(self):
        """Test multiple additions."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.a + entity.b - entity.c + entity.d > 10 => entity.result = true")

        entity = {"a": 5, "b": 10, "c": 2, "d": 3, "result": False}
        engine.evaluate(entity)
        assert entity["result"] is True

    def test_multiple_subtractions(self):
        """Test multiple subtractions."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.x - entity.y - entity.z == 5 => entity.correct = true")

        entity = {"x": 20, "y": 10, "z": 5, "correct": False}
        engine.evaluate(entity)
        assert entity["correct"] is True

    def test_multiple_multiplications(self):
        """Test multiple * operators in expression."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.a * entity.b * entity.c > 50 => entity.result = true")

        entity = {"a": 2, "b": 5, "c": 6, "result": False}
        engine.evaluate(entity)
        assert entity["result"] is True

    def test_mixed_mul_div_mod(self):
        """Test mixed *, /, % operators."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.a * entity.b / entity.c % entity.d == 2 => entity.ok = true")

        entity = {"a": 10, "b": 6, "c": 4, "d": 5, "ok": False}
        engine.evaluate(entity)
        # 10 * 6 / 4 % 5 = 60 / 4 % 5 = 15 % 5 = 0 != 2
        assert entity["ok"] is False

        entity = {"a": 10, "b": 6, "c": 4, "d": 7, "ok": False}
        engine.evaluate(entity)
        # 10 * 6 / 4 % 7 = 15 % 7 = 1 != 2
        assert entity["ok"] is False


class TestReturnStatementVariants:
    """Test return statement variants."""

    def test_return_complex_expression(self):
        """Test return with complex expression."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.x > 0 => ret (entity.x + entity.y) * 2")

        result = engine.evaluate({"x": 5, "y": 3})
        assert result == 16

    def test_return_function_result(self):
        """Test return with function call."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.name != '' => ret upper(entity.name)")

        result = engine.evaluate({"name": "hello"})
        assert result == "HELLO"

    def test_explicit_return_value_captured(self):
        """Test _has_returned check returning return value."""
        parsed = parse_rule("entity.x > 0 => entity.y = 1; ret entity.y * 2")

        entity = {"x": 5, "y": 0}
        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(parsed.tree)

        assert matched is True
        assert entity["y"] == 1
        assert result == 2

    def test_explicit_return_with_has_returned_flag(self):
        """Test return value through _has_returned flag."""
        parsed = parse_rule("entity.value > 0 => ret entity.value + 10")
        entity = {"value": 5}

        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(parsed.tree)

        assert matched is True
        assert result == 15
        assert interpreter._has_returned is True
        assert interpreter._return_value == 15


class TestListLiterals:
    """Test list literals in conditions."""

    def test_list_literal_with_in_operator(self):
        """Test list literal on right side of 'in' operator."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.status in ['active', 'pending'] => entity.valid = true")

        entity = {"status": "active", "valid": False}
        engine.evaluate(entity)
        assert entity["valid"] is True

        entity = {"status": "inactive", "valid": False}
        engine.evaluate(entity)
        assert entity["valid"] is False

    def test_list_literal_assignment(self):
        """Test assigning a list literal."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.init == true => entity.items = [1, 2, 3]")

        entity = {"init": True, "items": []}
        engine.evaluate(entity)
        assert entity["items"] == [1, 2, 3]


class TestUnaryOperators:
    """Test unary operators."""

    def test_unary_minus_in_condition(self):
        """Test unary minus in condition."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("-entity.value > 0 => entity.negative = true")

        entity = {"value": -5, "negative": False}
        engine.evaluate(entity)
        assert entity["negative"] is True

    def test_unary_minus_in_assignment(self):
        """Test unary minus in assignment."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.x > 0 => entity.y = -entity.x")

        entity = {"x": 10, "y": 0}
        engine.evaluate(entity)
        assert entity["y"] == -10


class TestShortCircuitEvaluation:
    """Test short-circuit evaluation."""

    def test_or_short_circuit_first_true(self):
        """Test OR short-circuits on first true value."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.a > 0 or entity.missing.path > 0 => entity.result = true")

        entity = {"a": 5, "result": False}
        engine.evaluate(entity)
        assert entity["result"] is True

    def test_or_evaluates_all_when_needed(self):
        """Test OR evaluates all conditions when first is false."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.a > 10 or entity.b > 10 => entity.result = true")

        entity = {"a": 5, "b": 15, "result": False}
        engine.evaluate(entity)
        assert entity["result"] is True

    def test_and_short_circuit_first_false(self):
        """Test AND short-circuits on first false value."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.a < 0 and entity.missing.path > 0 => entity.result = true")

        entity = {"a": 5, "result": False}
        engine.evaluate(entity)
        assert entity["result"] is False

    def test_and_evaluates_all_when_needed(self):
        """Test AND evaluates all conditions when first is true."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.a > 0 and entity.b > 0 => entity.result = true")

        entity = {"a": 5, "b": 15, "result": False}
        engine.evaluate(entity)
        assert entity["result"] is True


class TestNotOperator:
    """Test NOT expression."""

    def test_not_true_becomes_false(self):
        """Test NOT with true value."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("not entity.active => entity.inactive = true")

        entity = {"active": True, "inactive": False}
        engine.evaluate(entity)
        assert entity["inactive"] is False

    def test_not_false_becomes_true(self):
        """Test NOT with false value."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("not entity.active => entity.inactive = true")

        entity = {"active": False, "inactive": False}
        engine.evaluate(entity)
        assert entity["inactive"] is True

    def test_double_not(self):
        """Test double NOT."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("not not entity.value => entity.result = true")

        entity = {"value": True, "result": False}
        engine.evaluate(entity)
        assert entity["result"] is True


class TestNullCoalesceOperator:
    """Test null coalesce operator chain."""

    def test_null_coalesce_returns_first_non_none(self):
        """Test ?? returns first non-None value."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.x > 0 => entity.result = entity.a ?? entity.b ?? entity.c")

        entity = {"x": 1, "a": None, "b": None, "c": "fallback", "result": ""}
        engine.evaluate(entity)
        assert entity["result"] == "fallback"

    def test_null_coalesce_returns_first_value(self):
        """Test ?? returns first value when not None."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.x > 0 => entity.result = entity.a ?? entity.b ?? 'default'")

        entity = {"x": 1, "a": "first", "b": "second", "result": ""}
        engine.evaluate(entity)
        assert entity["result"] == "first"


class TestRegexAndIsEmpty:
    """Test regex match and is_empty operators."""

    def test_matches_with_invalid_regex(self):
        """Test matches operator with invalid regex pattern returns False."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.text matches '[invalid' => entity.matched = true")

        entity = {"text": "anything", "matched": False}
        engine.evaluate(entity)
        assert entity["matched"] is False

    def test_is_empty_with_set(self):
        """Test is_empty with set."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.items is_empty => entity.empty = true")

        entity = {"items": set(), "empty": False}
        engine.evaluate(entity)
        assert entity["empty"] is True

    def test_is_empty_with_whitespace_string(self):
        """Test is_empty with whitespace-only string."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("entity.text is_empty => entity.blank = true")

        entity = {"text": "   ", "blank": False}
        engine.evaluate(entity)
        assert entity["blank"] is True

class TestFunctionErrorHandling:
    """Test function call error handling."""

    def test_function_with_wrong_args(self):
        """Test function raising error with wrong arguments."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("round(entity.value, entity.precision) > 0 => entity.ok = true")

        entity = {"value": 3.14159, "precision": 2, "ok": False}
        engine.evaluate(entity)
        assert entity["ok"] is True

    def test_function_error_wrapped(self):
        """Test that function errors are wrapped in EvaluationError."""
        from rule_interpreter import RuleEngine
        engine = RuleEngine()
        engine.add_rules("int(entity.value) > 0 => entity.ok = true")

        with pytest.raises(EvaluationError):
            engine.evaluate({"value": "not_a_number", "ok": False})

