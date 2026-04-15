"""Expanded comprehensive tests for the rule parser."""

import pytest

from rulang.visitor import parse_rule
from rulang.exceptions import RuleSyntaxError


class TestLexerTokens:
    """Test lexer token recognition."""

    @pytest.mark.parametrize("keyword", ["true", "True", "false", "False", "none", "None", "null"])
    def test_boolean_none_keywords(self, keyword):
        rule = parse_rule(f"entity.value == {keyword} => ret true")
        assert rule is not None

    @pytest.mark.parametrize("op", ["==", "!=", "<", ">", "<=", ">=", "+", "-", "*", "/", "%"])
    def test_operator_tokens(self, op):
        rule = parse_rule(f"entity.value {op} 10 => ret true")
        assert rule is not None

    def test_string_empty_double_quotes(self):
        rule = parse_rule('entity.name == "" => ret true')
        assert rule is not None

    def test_string_empty_single_quotes(self):
        rule = parse_rule("entity.name == '' => ret true")
        assert rule is not None

    def test_string_escaped_quotes_double(self):
        rule = parse_rule('entity.message == "say \\"hello\\"" => ret true')
        assert rule is not None

    def test_string_escaped_quotes_single(self):
        rule = parse_rule("entity.message == 'say \\'hello\\'' => ret true")
        assert rule is not None

    def test_string_escaped_backslash(self):
        rule = parse_rule('entity.path == "path\\\\to\\\\file" => ret true')
        assert rule is not None

    def test_string_unicode_characters(self):
        rule = parse_rule('entity.name == "José" => ret true')
        assert rule is not None

    def test_number_very_large_integer(self):
        rule = parse_rule("entity.value == 999999999999999999 => ret true")
        assert rule is not None

    def test_number_very_small_float(self):
        rule = parse_rule("entity.value == 0.0000001 => ret true")
        assert rule is not None

    def test_number_leading_zeros(self):
        rule = parse_rule("entity.value == 007 => ret true")
        assert rule is not None

    def test_number_trailing_zeros(self):
        rule = parse_rule("entity.value == 10.00 => ret true")
        assert rule is not None

    def test_number_negative_zero(self):
        rule = parse_rule("entity.value == -0 => ret true")
        assert rule is not None

    def test_identifier_underscore_start(self):
        rule = parse_rule("entity._private == 10 => ret true")
        assert rule is not None

    def test_identifier_underscore_middle(self):
        rule = parse_rule("entity.my_value == 10 => ret true")
        assert rule is not None

    def test_identifier_very_long(self):
        long_name = "a" * 100
        rule = parse_rule(f"entity.{long_name} == 10 => ret true")
        assert rule is not None

    def test_whitespace_tabs(self):
        rule = parse_rule("entity.value\t==\t10 => ret true")
        assert rule is not None

    def test_whitespace_multiple_spaces(self):
        rule = parse_rule("entity.value    ==    10 => ret true")
        assert rule is not None

    def test_comment_end_of_line(self):
        rule = parse_rule("entity.value == 10 => ret true # comment")
        assert rule is not None

    def test_comment_before_arrow(self):
        # Comments are skipped by lexer, so "=>" after comment is invalid syntax
        # The comment removes everything after #, so we get "entity.value == 10 => ret true"
        # But actually, comments are line comments, so this should fail
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value == 10 # comment => ret true")


class TestOperatorPrecedence:
    """Test operator precedence parsing."""

    def test_arithmetic_precedence_multiplication_before_addition(self):
        rule = parse_rule("entity.a + entity.b * entity.c >= 10 => ret true")
        assert rule is not None

    def test_arithmetic_precedence_division_before_subtraction(self):
        rule = parse_rule("entity.a - entity.b / entity.c >= 10 => ret true")
        assert rule is not None

    def test_comparison_precedence_before_logical(self):
        rule = parse_rule("entity.a == 1 and entity.b == 2 => ret true")
        assert rule is not None

    def test_logical_precedence_and_before_or(self):
        rule = parse_rule("entity.a == 1 or entity.b == 2 and entity.c == 3 => ret true")
        assert rule is not None

    def test_unary_precedence_before_binary(self):
        rule = parse_rule("-entity.value * 2 >= 10 => ret true")
        assert rule is not None

    def test_complex_precedence(self):
        rule = parse_rule("entity.a + entity.b * entity.c == entity.d / entity.e => ret true")
        assert rule is not None


class TestAssociativity:
    """Test operator associativity."""

    def test_left_associative_subtraction(self):
        rule = parse_rule("entity.a - entity.b - entity.c >= 0 => ret true")
        assert rule is not None

    def test_left_associative_division(self):
        rule = parse_rule("entity.a / entity.b / entity.c >= 0 => ret true")
        assert rule is not None

    def test_left_associative_modulo(self):
        rule = parse_rule("entity.a % entity.b % entity.c >= 0 => ret true")
        assert rule is not None

    def test_left_associative_and(self):
        rule = parse_rule("entity.a > 0 and entity.b > 0 and entity.c > 0 => ret true")
        assert rule is not None

    def test_left_associative_or(self):
        rule = parse_rule("entity.a > 0 or entity.b > 0 or entity.c > 0 => ret true")
        assert rule is not None


class TestNestedExpressions:
    """Test nested expression parsing."""

    def test_deep_nesting_10_levels(self):
        # Create deeply nested expression
        expr = "entity.value"
        for i in range(10):
            expr = f"({expr})"
        rule = parse_rule(f"{expr} == 10 => ret true")
        assert rule is not None

    def test_mixed_nesting_arithmetic_logical(self):
        rule = parse_rule("(entity.a + entity.b) > 0 and (entity.c - entity.d) < 10 => ret true")
        assert rule is not None

    def test_nested_comparisons(self):
        rule = parse_rule("(entity.a == 1) == true => ret true")
        assert rule is not None

    def test_nested_logical(self):
        rule = parse_rule("(entity.a > 0 and entity.b > 0) or (entity.c > 0 and entity.d > 0) => ret true")
        assert rule is not None

    def test_nested_arithmetic(self):
        rule = parse_rule("(entity.a + entity.b) * (entity.c - entity.d) >= 10 => ret true")
        assert rule is not None


class TestParentheses:
    """Test parenthesized expressions."""

    def test_single_parentheses(self):
        rule = parse_rule("(entity.value) == 10 => ret true")
        assert rule is not None

    def test_nested_parentheses(self):
        rule = parse_rule("((entity.value)) == 10 => ret true")
        assert rule is not None

    def test_deep_nested_parentheses(self):
        # Fix: match opening and closing parentheses
        rule = parse_rule("((((entity.value)))) == 10 => ret true")
        assert rule is not None

    def test_unbalanced_parentheses_left(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("(entity.value == 10 => ret true")

    def test_unbalanced_parentheses_right(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value) == 10 => ret true")

    def test_parentheses_override_precedence(self):
        rule = parse_rule("(entity.a + entity.b) * entity.c >= 10 => ret true")
        assert rule is not None


class TestComparisonOperators:
    """Test comparison operator parsing."""

    @pytest.mark.parametrize("op", ["==", "!=", "<", ">", "<=", ">="])
    def test_comparison_with_numbers(self, op):
        rule = parse_rule(f"entity.value {op} 10 => ret true")
        assert rule is not None

    @pytest.mark.parametrize("op", ["==", "!=", "<", ">", "<=", ">="])
    def test_comparison_with_strings(self, op):
        rule = parse_rule(f'entity.name {op} "test" => ret true')
        assert rule is not None

    @pytest.mark.parametrize("op", ["==", "!="])
    def test_comparison_with_booleans(self, op):
        rule = parse_rule(f"entity.active {op} true => ret true")
        assert rule is not None

    def test_chained_comparison_should_fail(self):
        # Chained comparisons like a < b < c are not supported
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.a < entity.b < entity.c => ret true")


class TestLogicalOperators:
    """Test logical operator parsing."""

    def test_multiple_and_chain(self):
        rule = parse_rule("entity.a > 0 and entity.b > 0 and entity.c > 0 and entity.d > 0 => ret true")
        assert rule is not None

    def test_multiple_or_chain(self):
        rule = parse_rule("entity.a > 0 or entity.b > 0 or entity.c > 0 or entity.d > 0 => ret true")
        assert rule is not None

    def test_mixed_and_or(self):
        rule = parse_rule("entity.a > 0 and entity.b > 0 or entity.c > 0 => ret true")
        assert rule is not None

    def test_not_with_comparison(self):
        rule = parse_rule("not entity.value == 10 => ret true")
        assert rule is not None

    def test_not_with_logical(self):
        rule = parse_rule("not (entity.a > 0 and entity.b > 0) => ret true")
        assert rule is not None

    def test_multiple_not(self):
        rule = parse_rule("not not entity.value == 10 => ret true")
        assert rule is not None

    def test_not_with_arithmetic(self):
        rule = parse_rule("not entity.value + 10 > 0 => ret true")
        assert rule is not None


class TestArithmeticOperators:
    """Test arithmetic operator parsing."""

    def test_all_additions(self):
        rule = parse_rule("entity.a + entity.b + entity.c + entity.d >= 10 => ret true")
        assert rule is not None

    def test_all_subtractions(self):
        rule = parse_rule("entity.a - entity.b - entity.c - entity.d >= 0 => ret true")
        assert rule is not None

    def test_all_multiplications(self):
        rule = parse_rule("entity.a * entity.b * entity.c * entity.d >= 10 => ret true")
        assert rule is not None

    def test_all_divisions(self):
        rule = parse_rule("entity.a / entity.b / entity.c / entity.d >= 0 => ret true")
        assert rule is not None

    def test_all_modulo(self):
        rule = parse_rule("entity.a % entity.b % entity.c >= 0 => ret true")
        assert rule is not None

    def test_mixed_arithmetic(self):
        rule = parse_rule("entity.a + entity.b * entity.c - entity.d / entity.e >= 10 => ret true")
        assert rule is not None

    def test_unary_minus_simple(self):
        rule = parse_rule("-entity.value >= -10 => ret true")
        assert rule is not None

    def test_unary_minus_with_parentheses(self):
        rule = parse_rule("-(entity.value + 10) >= -20 => ret true")
        assert rule is not None

    def test_unary_minus_multiple(self):
        rule = parse_rule("--entity.value >= 0 => ret true")
        assert rule is not None


class TestMembershipOperators:
    """Test membership operator parsing."""

    def test_in_with_list(self):
        rule = parse_rule("entity.status in [1, 2, 3] => ret true")
        assert rule is not None

    def test_in_with_string_list(self):
        rule = parse_rule("entity.status in ['active', 'pending'] => ret true")
        assert rule is not None

    def test_in_with_mixed_list(self):
        rule = parse_rule("entity.value in [1, 'two', 3.0] => ret true")
        assert rule is not None

    def test_not_in_with_list(self):
        rule = parse_rule("entity.status not in ['deleted', 'archived'] => ret true")
        assert rule is not None

    def test_in_with_empty_list(self):
        rule = parse_rule("entity.value in [] => ret true")
        assert rule is not None

    def test_in_with_single_element_list(self):
        rule = parse_rule("entity.value in [42] => ret true")
        assert rule is not None

    def test_in_with_nested_expressions(self):
        rule = parse_rule("entity.value in [entity.a, entity.b, entity.c] => ret true")
        assert rule is not None


class TestPathExpressions:
    """Test path expression parsing."""

    def test_deep_nesting_10_levels(self):
        path = "entity." + ".".join([f"level{i}" for i in range(10)])
        rule = parse_rule(f"{path} == 10 => ret true")
        assert rule is not None

    def test_mixed_dot_bracket(self):
        rule = parse_rule("entity.users[0].profile.name == 'test' => ret true")
        assert rule is not None

    def test_multiple_consecutive_brackets(self):
        rule = parse_rule("entity.matrix[0][1][2] == 10 => ret true")
        assert rule is not None

    def test_bracket_with_expression(self):
        rule = parse_rule("entity.items[entity.index] == 10 => ret true")
        assert rule is not None

    def test_bracket_with_negative_index(self):
        rule = parse_rule("entity.items[-1] == 10 => ret true")
        assert rule is not None

    def test_bracket_with_arithmetic(self):
        rule = parse_rule("entity.items[entity.index + 1] == 10 => ret true")
        assert rule is not None

    def test_path_starting_with_different_identifier(self):
        rule = parse_rule("other.value == 10 => ret true")
        assert rule is not None


class TestListLiterals:
    """Test list literal parsing."""

    def test_empty_list(self):
        rule = parse_rule("entity.value in [] => ret true")
        assert rule is not None

    def test_single_element_list(self):
        rule = parse_rule("entity.value in [42] => ret true")
        assert rule is not None

    def test_multiple_elements_list(self):
        rule = parse_rule("entity.value in [1, 2, 3, 4, 5] => ret true")
        assert rule is not None

    def test_nested_lists(self):
        rule = parse_rule("entity.value in [[1, 2], [3, 4]] => ret true")
        assert rule is not None

    def test_list_with_mixed_types(self):
        rule = parse_rule("entity.value in [1, 'two', 3.0, true, false] => ret true")
        assert rule is not None

    def test_list_with_expressions(self):
        rule = parse_rule("entity.value in [entity.a, entity.b, entity.c] => ret true")
        assert rule is not None

    def test_list_with_arithmetic(self):
        rule = parse_rule("entity.value in [entity.a + 1, entity.b * 2] => ret true")
        assert rule is not None


class TestAssignmentParsing:
    """Test assignment action parsing."""

    def test_simple_assignment(self):
        rule = parse_rule("entity.value == 10 => entity.result = 20")
        assert rule is not None

    def test_all_compound_assignments(self):
        for op in ["+=", "-=", "*=", "/="]:
            rule = parse_rule(f"entity.value > 0 => entity.total {op} entity.value")
            assert rule is not None

    def test_assignment_to_nested_path(self):
        rule = parse_rule("entity.ready == true => entity.user.profile.name = 'John'")
        assert rule is not None

    def test_assignment_to_indexed_path(self):
        rule = parse_rule("entity.ready == true => entity.items[0].value = 100")
        assert rule is not None

    def test_assignment_with_complex_expression(self):
        rule = parse_rule("entity.ready == true => entity.total = entity.price * entity.quantity * (1 - entity.discount)")
        assert rule is not None

    def test_assignment_with_arithmetic_expression(self):
        rule = parse_rule("entity.ready == true => entity.result = entity.a + entity.b * entity.c")
        assert rule is not None

    def test_assignment_with_function_call(self):
        rule = parse_rule("entity.ready == true => entity.result = workflow('calculate')")
        assert rule is not None


class TestWorkflowCallParsing:
    """Test workflow call parsing."""

    def test_workflow_no_arguments(self):
        rule = parse_rule("entity.ready == true => workflow('process')")
        assert "process" in rule.workflow_calls

    def test_workflow_single_argument(self):
        rule = parse_rule("entity.ready == true => workflow('process', entity.value)")
        assert "process" in rule.workflow_calls

    def test_workflow_multiple_arguments(self):
        rule = parse_rule("entity.ready == true => workflow('process', entity.a, entity.b, entity.c)")
        assert "process" in rule.workflow_calls

    def test_workflow_with_literal_arguments(self):
        rule = parse_rule("entity.ready == true => workflow('process', 10, 'test', true)")
        assert "process" in rule.workflow_calls

    def test_workflow_with_expression_arguments(self):
        rule = parse_rule("entity.ready == true => workflow('process', entity.a + entity.b, entity.c * 2)")
        assert "process" in rule.workflow_calls

    def test_workflow_nested_call(self):
        rule = parse_rule("entity.ready == true => workflow('process', workflow('helper'))")
        assert "process" in rule.workflow_calls

    def test_workflow_name_with_quotes(self):
        rule = parse_rule('entity.ready == true => workflow("process")')
        assert "process" in rule.workflow_calls

    def test_workflow_name_unicode(self):
        rule = parse_rule("entity.ready == true => workflow('procesș')")
        assert "procesș" in rule.workflow_calls


class TestReturnStatementParsing:
    """Test return statement parsing."""

    def test_return_with_literal(self):
        rule = parse_rule("entity.value > 0 => ret 42")
        assert rule is not None

    def test_return_with_expression(self):
        rule = parse_rule("entity.value > 0 => ret entity.a + entity.b")
        assert rule is not None

    def test_return_with_path(self):
        rule = parse_rule("entity.value > 0 => ret entity.result")
        assert rule is not None

    def test_return_with_workflow_call(self):
        rule = parse_rule("entity.value > 0 => ret workflow('calculate')")
        assert rule is not None

    def test_return_with_string(self):
        rule = parse_rule("entity.value > 0 => ret 'success'")
        assert rule is not None

    def test_return_with_boolean(self):
        rule = parse_rule("entity.value > 0 => ret true")
        assert rule is not None

    def test_return_with_none(self):
        rule = parse_rule("entity.value > 0 => ret none")
        assert rule is not None


class TestMultipleActions:
    """Test multiple action parsing."""

    def test_two_actions(self):
        rule = parse_rule("entity.ready == true => entity.a = 1; entity.b = 2")
        assert rule is not None

    def test_many_actions_10(self):
        actions = "; ".join([f"entity.field{i} = {i}" for i in range(10)])
        rule = parse_rule(f"entity.ready == true => {actions}")
        assert rule is not None

    def test_mixed_action_types(self):
        rule = parse_rule("entity.ready == true => entity.a = 1; workflow('process'); entity.b = 2; ret entity.b")
        assert rule is not None

    def test_actions_with_different_separators(self):
        # Multiple semicolons create empty action which is invalid
        # This should fail because empty action is not allowed
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.ready == true => entity.a = 1;; entity.b = 2")


class TestRuleStructure:
    """Test complete rule structure parsing."""

    def test_minimal_rule(self):
        rule = parse_rule("true => ret true")
        assert rule is not None

    def test_complex_condition(self):
        rule = parse_rule("entity.a > 0 and entity.b < 10 or entity.c == 5 => ret true")
        assert rule is not None

    def test_multiple_actions(self):
        rule = parse_rule("entity.ready == true => entity.a = 1; entity.b = 2; entity.c = 3")
        assert rule is not None

    def test_with_return_statement(self):
        rule = parse_rule("entity.ready == true => entity.status = 'done'; ret entity.status")
        assert rule is not None

    def test_without_return_statement(self):
        rule = parse_rule("entity.ready == true => entity.status = 'done'")
        assert rule is not None

    def test_arrow_spacing(self):
        rule = parse_rule("entity.value==10=>ret true")
        assert rule is not None

    def test_arrow_with_spaces(self):
        rule = parse_rule("entity.value == 10 => ret true")
        assert rule is not None


class TestSyntaxErrors:
    """Test syntax error cases."""

    def test_missing_arrow(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value > 10 ret true")

    def test_missing_condition(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("=> ret true")

    def test_missing_action(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value > 10 =>")

    def test_invalid_operator(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value <> 10 => ret true")

    def test_invalid_characters(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value @ 10 => ret true")

    def test_malformed_string_unclosed_double(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule('entity.name == "test => ret true')

    def test_malformed_string_unclosed_single(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.name == 'test => ret true")

    def test_invalid_number_format(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value == 10. => ret true")

    def test_invalid_path_syntax(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity..value == 10 => ret true")

    def test_missing_comma_in_list(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value in [1 2 3] => ret true")

    def test_missing_closing_bracket(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value in [1, 2, 3 => ret true")

    def test_missing_closing_paren(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.value == (10 => ret true")

    def test_invalid_identifier_start(self):
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.123value == 10 => ret true")

    def test_keyword_as_identifier(self):
        # Keywords should not be used as identifiers without proper context
        with pytest.raises(RuleSyntaxError):
            parse_rule("entity.and == 10 => ret true")

