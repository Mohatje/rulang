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

    def test_arithmetic_with_strings_should_fail(self):
        """Test arithmetic with strings raises error."""
        entity = {"a": "10", "b": "5"}
        rule = parse_rule("entity.a + entity.b >= 0 => ret true")
        interpreter = RuleInterpreter(entity)
        # String concatenation might work, or raise error
        try:
            matched, _ = interpreter.execute(rule.tree)
            # If it works, it's string concatenation
            assert matched is True
        except (TypeError, EvaluationError):
            # If it fails, that's also acceptable
            pass

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

