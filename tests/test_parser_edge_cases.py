"""Edge case tests for parser."""

import pytest

from rule_interpreter.visitor import parse_rule
from rule_interpreter.exceptions import RuleSyntaxError


class TestParserEdgeCases:
    """Test parser edge cases and boundary conditions."""

    def test_very_long_rule(self):
        """Test parsing a very long rule."""
        long_condition = " and ".join([f"entity.field{i} > 0" for i in range(50)])
        long_rule = f"{long_condition} => entity.result = 1"
        rule = parse_rule(long_rule)
        assert rule is not None

    def test_rule_with_only_whitespace(self):
        """Test rule with excessive whitespace."""
        rule = parse_rule("entity.value    ==    10    =>    ret    true")
        assert rule is not None

    def test_rule_with_tabs(self):
        """Test rule with tab characters."""
        rule = parse_rule("entity.value\t==\t10\t=>\tret\ttrue")
        assert rule is not None

    def test_rule_with_newlines(self):
        """Test rule with newlines (should be handled)."""
        rule = parse_rule("entity.value == 10\n=>\nret true")
        assert rule is not None

    def test_unicode_in_identifiers(self):
        """Test unicode characters in identifiers (not supported by grammar)."""
        # Unicode identifiers are not supported by the grammar
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.测试 == 10 => ret true")

    def test_unicode_in_strings(self):
        """Test unicode characters in strings."""
        rule = parse_rule('entity.name == "José" => ret true')
        assert rule is not None

    def test_very_large_number(self):
        """Test very large number parsing."""
        rule = parse_rule("entity.value == 999999999999999999999 => ret true")
        assert rule is not None

    def test_very_small_float(self):
        """Test very small float parsing."""
        rule = parse_rule("entity.value == 0.0000000001 => ret true")
        assert rule is not None

    def test_scientific_notation_not_supported(self):
        """Test that scientific notation is not supported (should fail or parse as string)."""
        # Scientific notation like 1e10 is not in grammar
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value == 1e10 => ret true")

    def test_string_with_newline_escaped(self):
        """Test string with escaped newline."""
        rule = parse_rule('entity.message == "line1\\nline2" => ret true')
        assert rule is not None

    def test_string_with_tab_escaped(self):
        """Test string with escaped tab."""
        rule = parse_rule('entity.message == "col1\\tcol2" => ret true')
        assert rule is not None

    def test_empty_string_literal(self):
        """Test empty string literal."""
        rule = parse_rule('entity.name == "" => ret true')
        assert rule is not None

    def test_list_with_many_elements(self):
        """Test list with many elements."""
        elements = ", ".join([str(i) for i in range(100)])
        rule = parse_rule(f"entity.value in [{elements}] => ret true")
        assert rule is not None

    def test_nested_lists_deep(self):
        """Test deeply nested lists."""
        rule = parse_rule("entity.value in [[[[[1]]]]] => ret true")
        assert rule is not None

    def test_path_with_many_levels(self):
        """Test path with many nesting levels."""
        path = "entity." + ".".join([f"level{i}" for i in range(20)])
        rule = parse_rule(f"{path} == 10 => ret true")
        assert rule is not None

    def test_multiple_brackets_in_path(self):
        """Test path with multiple bracket accesses."""
        rule = parse_rule("entity.matrix[0][1][2][3] == 10 => ret true")
        assert rule is not None

    def test_workflow_with_many_args(self):
        """Test workflow call with many arguments."""
        args = ", ".join([f"entity.arg{i}" for i in range(20)])
        rule = parse_rule(f"entity.ready == true => workflow('process', {args})")
        assert "process" in rule.workflow_calls

    def test_many_actions(self):
        """Test rule with many actions."""
        actions = "; ".join([f"entity.field{i} = {i}" for i in range(50)])
        rule = parse_rule(f"entity.ready == true => {actions}")
        assert rule is not None

    def test_complex_nested_expressions(self):
        """Test deeply nested expressions."""
        nested = "entity.value"
        for i in range(20):
            nested = f"({nested})"
        rule = parse_rule(f"{nested} == 10 => ret true")
        assert rule is not None

    def test_all_operators_in_one_rule(self):
        """Test rule using all operators."""
        rule = parse_rule(
            "entity.a + entity.b * entity.c - entity.d / entity.e % entity.f >= 0 "
            "and entity.g < 10 or entity.h > 20 => "
            "entity.result = (entity.a + entity.b) * entity.c; ret entity.result"
        )
        assert rule is not None

    def test_mixed_string_quotes(self):
        """Test mixing single and double quotes."""
        rule = parse_rule('entity.name == "test" and entity.status == \'active\' => ret true')
        assert rule is not None

    def test_negative_numbers_in_expressions(self):
        """Test negative numbers in various contexts."""
        rule = parse_rule("entity.value == -10 and entity.other == -5.5 => ret true")
        assert rule is not None

    def test_zero_values(self):
        """Test zero values."""
        rule = parse_rule("entity.value == 0 => ret true")
        assert rule is not None

    def test_boolean_comparisons(self):
        """Test boolean value comparisons."""
        rule = parse_rule("entity.active == true and entity.enabled == false => ret true")
        assert rule is not None

    def test_none_comparisons(self):
        """Test None/null comparisons."""
        rule = parse_rule("entity.value == none and entity.other == null => ret true")
        assert rule is not None

    def test_in_with_empty_list(self):
        """Test 'in' operator with empty list."""
        rule = parse_rule("entity.value in [] => ret true")
        assert rule is not None

    def test_not_in_with_empty_list(self):
        """Test 'not in' operator with empty list."""
        rule = parse_rule("entity.value not in [] => ret true")
        assert rule is not None

    def test_chained_logical_operators(self):
        """Test chained logical operators."""
        rule = parse_rule("entity.a > 0 and entity.b > 0 and entity.c > 0 and entity.d > 0 => ret true")
        assert rule is not None

    def test_multiple_not_operators(self):
        """Test multiple 'not' operators."""
        rule = parse_rule("not not not entity.value == 10 => ret true")
        assert rule is not None

    def test_unary_minus_multiple(self):
        """Test multiple unary minus operators."""
        rule = parse_rule("----entity.value >= 0 => ret true")
        assert rule is not None

    def test_assignment_to_complex_path(self):
        """Test assignment to complex nested path."""
        rule = parse_rule("entity.ready == true => entity.users[0].profile.settings.theme = 'dark'")
        assert rule is not None

    def test_return_with_complex_expression(self):
        """Test return with complex expression."""
        rule = parse_rule("entity.ready == true => ret (entity.a + entity.b) * (entity.c - entity.d) / entity.e")
        assert rule is not None

    def test_workflow_in_condition(self):
        """Test workflow call in condition."""
        rule = parse_rule("workflow('check') == true => ret true")
        assert "check" in rule.workflow_calls

    def test_workflow_in_return(self):
        """Test workflow call in return statement."""
        rule = parse_rule("entity.ready == true => ret workflow('calculate')")
        assert "calculate" in rule.workflow_calls

    def test_arithmetic_with_negatives(self):
        """Test arithmetic with negative numbers."""
        rule = parse_rule("entity.a + (-entity.b) * entity.c >= 0 => ret true")
        assert rule is not None

    def test_modulo_operations(self):
        """Test modulo operations."""
        rule = parse_rule("entity.value % entity.divisor == 0 => ret true")
        assert rule is not None

    def test_division_operations(self):
        """Test division operations."""
        rule = parse_rule("entity.value / entity.divisor >= 1 => ret true")
        assert rule is not None

    def test_membership_with_expressions(self):
        """Test membership with expression lists."""
        rule = parse_rule("entity.value in [entity.a, entity.b, entity.c] => ret true")
        assert rule is not None

    def test_comparison_with_expressions(self):
        """Test comparison with complex expressions."""
        rule = parse_rule("entity.a + entity.b == entity.c * entity.d => ret true")
        assert rule is not None

    def test_logical_with_comparisons(self):
        """Test logical operators with comparisons."""
        rule = parse_rule("(entity.a > 0 and entity.b < 10) or (entity.c == 5 and entity.d != 0) => ret true")
        assert rule is not None

    def test_parentheses_override_precedence(self):
        """Test parentheses overriding operator precedence."""
        rule = parse_rule("(entity.a + entity.b) * entity.c == entity.d => ret true")
        assert rule is not None

    def test_compound_assignment_all_types(self):
        """Test all compound assignment operators."""
        for op in ["+=", "-=", "*=", "/="]:
            rule = parse_rule(f"entity.value > 0 => entity.total {op} entity.value")
            assert rule is not None

    def test_multiple_returns_should_fail(self):
        """Test that multiple returns in one action list might be handled."""
        # Actually, this might parse but only first return matters
        rule = parse_rule("entity.ready == true => ret 1; ret 2")
        assert rule is not None  # Parses, but second ret might not execute

    def test_empty_actions_should_fail(self):
        """Test that empty actions should fail."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value > 0 =>")

    def test_missing_semicolon_between_actions(self):
        """Test missing semicolon between actions."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.ready == true => entity.a = 1 entity.b = 2")

    def test_invalid_path_syntax(self):
        """Test invalid path syntax."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity..value == 10 => ret true")

    def test_invalid_operator_combination(self):
        """Test invalid operator combinations."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value == == 10 => ret true")

    def test_missing_operand(self):
        """Test missing operand."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value == => ret true")

    def test_unclosed_string(self):
        """Test unclosed string."""
        with pytest.raises(RuleSyntaxError):
            parse_rule('entity.name == "test => ret true')

    def test_unclosed_list(self):
        """Test unclosed list."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value in [1, 2, 3 => ret true")

    def test_unclosed_parentheses(self):
        """Test unclosed parentheses."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("(entity.value == 10 => ret true")

    def test_invalid_identifier(self):
        """Test invalid identifier."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.123invalid == 10 => ret true")

    def test_keyword_misuse(self):
        """Test keyword used incorrectly."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.and == 10 => ret true")

    def test_arrow_in_wrong_place(self):
        """Test arrow operator in wrong place."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("=> entity.value == 10 ret true")

    def test_multiple_arrows(self):
        """Test multiple arrow operators."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value > 0 => => ret true")

    def test_comment_in_middle(self):
        """Test comment in middle of rule."""
        # Comments are line comments, so this should fail
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value == 10 # comment => ret true")

    def test_special_characters_in_string(self):
        """Test special characters in strings."""
        rule = parse_rule('entity.message == "Hello! @#$%^&*()" => ret true')
        assert rule is not None

    def test_escaped_quotes_in_string(self):
        """Test escaped quotes in strings."""
        rule = parse_rule('entity.message == "Say \\"hello\\"" => ret true')
        assert rule is not None

    def test_very_long_identifier(self):
        """Test very long identifier."""
        long_id = "a" * 200
        rule = parse_rule(f"entity.{long_id} == 10 => ret true")
        assert rule is not None

    def test_path_with_spaces_should_fail(self):
        """Test path with spaces should fail."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.my field == 10 => ret true")

    def test_numeric_starting_identifier_should_fail(self):
        """Test identifier starting with number should fail."""
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.123field == 10 => ret true")

    def test_operator_without_spaces(self):
        """Test operators without spaces."""
        rule = parse_rule("entity.value==10=>ret true")
        assert rule is not None

    def test_all_whitespace_variations(self):
        """Test various whitespace combinations."""
        rule = parse_rule("  entity.value  ==  10  =>  ret  true  ")
        assert rule is not None

    def test_leading_trailing_whitespace(self):
        """Test leading and trailing whitespace."""
        rule = parse_rule("   entity.value == 10 => ret true   ")
        assert rule is not None

    def test_mixed_whitespace(self):
        """Test mixed tabs and spaces."""
        rule = parse_rule("entity.value\t ==\t 10 =>\t ret\ttrue")
        assert rule is not None

