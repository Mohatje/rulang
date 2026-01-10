"""Tests for the rule parser."""

import pytest

from rulang.visitor import parse_rule
from rulang.exceptions import RuleSyntaxError


class TestBasicParsing:
    """Test basic rule parsing."""

    def test_simple_condition_with_literal_return(self):
        rule = parse_rule("entity.age >= 18 => ret true")
        assert rule.rule_text == "entity.age >= 18 => ret true"
        assert "entity.age" in rule.reads or "entity.[*].age" in rule.reads or any("age" in r for r in rule.reads)

    def test_simple_comparison_operators(self):
        operators = ["==", "!=", "<", ">", "<=", ">="]
        for op in operators:
            rule = parse_rule(f"entity.value {op} 10 => ret true")
            assert rule is not None

    def test_arithmetic_in_condition(self):
        rule = parse_rule("entity.price * entity.quantity >= 100 => ret true")
        assert rule is not None

    def test_logical_operators(self):
        rule = parse_rule("entity.a > 0 and entity.b < 10 => ret true")
        assert rule is not None

        rule = parse_rule("entity.a > 0 or entity.b < 10 => ret true")
        assert rule is not None

        rule = parse_rule("not entity.disabled => ret true")
        assert rule is not None

    def test_membership_operators(self):
        rule = parse_rule("entity.status in ['active', 'pending'] => ret true")
        assert rule is not None

        rule = parse_rule("entity.status not in ['deleted'] => ret true")
        assert rule is not None


class TestPathParsing:
    """Test path expression parsing."""

    def test_simple_path(self):
        rule = parse_rule("entity.name == 'test' => ret true")
        assert rule is not None

    def test_nested_path(self):
        rule = parse_rule("entity.user.profile.name == 'test' => ret true")
        assert rule is not None

    def test_list_index(self):
        rule = parse_rule("entity.items[0].value > 10 => ret true")
        assert rule is not None

    def test_negative_index(self):
        rule = parse_rule("entity.items[-1].value > 10 => ret true")
        assert rule is not None

    def test_dynamic_index(self):
        rule = parse_rule("entity.items[entity.index].value > 10 => ret true")
        assert rule is not None


class TestActionParsing:
    """Test action parsing."""

    def test_simple_assignment(self):
        rule = parse_rule("entity.ready == true => entity.status = 'processed'")
        assert "entity.status" in rule.writes or any("status" in w for w in rule.writes)

    def test_compound_assignments(self):
        rule = parse_rule("entity.value > 0 => entity.total += entity.value")
        assert rule is not None

        rule = parse_rule("entity.value > 0 => entity.total -= 10")
        assert rule is not None

        rule = parse_rule("entity.value > 0 => entity.total *= 2")
        assert rule is not None

        rule = parse_rule("entity.value > 0 => entity.total /= 2")
        assert rule is not None

    def test_multiple_actions(self):
        rule = parse_rule("entity.ready == true => entity.a = 1; entity.b = 2; entity.c = 3")
        assert rule is not None

    def test_return_statement(self):
        rule = parse_rule("entity.ready == true => entity.status = 'done'; ret entity")
        assert rule is not None

    def test_workflow_call(self):
        rule = parse_rule("entity.ready == true => workflow('process')")
        assert "process" in rule.workflow_calls


class TestLiteralParsing:
    """Test literal value parsing."""

    def test_integer(self):
        rule = parse_rule("entity.value == 42 => ret true")
        assert rule is not None

    def test_negative_integer(self):
        rule = parse_rule("entity.value == -42 => ret true")
        assert rule is not None

    def test_float(self):
        rule = parse_rule("entity.value == 3.14 => ret true")
        assert rule is not None

    def test_string_double_quotes(self):
        rule = parse_rule('entity.name == "test" => ret true')
        assert rule is not None

    def test_string_single_quotes(self):
        rule = parse_rule("entity.name == 'test' => ret true")
        assert rule is not None

    def test_boolean_true(self):
        rule = parse_rule("entity.active == true => ret true")
        assert rule is not None

        rule = parse_rule("entity.active == True => ret true")
        assert rule is not None

    def test_boolean_false(self):
        rule = parse_rule("entity.active == false => ret false")
        assert rule is not None

    def test_none_null(self):
        rule = parse_rule("entity.value == none => ret true")
        assert rule is not None

        rule = parse_rule("entity.value == null => ret true")
        assert rule is not None

    def test_list_literal(self):
        rule = parse_rule("entity.status in [1, 2, 3] => ret true")
        assert rule is not None


class TestSyntaxErrors:
    """Test syntax error handling."""

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


class TestReadWriteAnalysis:
    """Test read/write set extraction."""

    def test_reads_from_condition(self):
        rule = parse_rule("entity.user.age >= 18 => ret true")
        # Should have reads for entity.user.age
        assert len(rule.reads) > 0

    def test_writes_from_assignment(self):
        rule = parse_rule("entity.ready == true => entity.status = 'done'")
        assert len(rule.writes) > 0

    def test_compound_assignment_reads_and_writes(self):
        rule = parse_rule("entity.ready == true => entity.counter += 1")
        # counter should be in both reads and writes
        assert len(rule.writes) > 0
        # For compound assignment, the target is also read
        assert len(rule.reads) > 0

    def test_workflow_calls_tracked(self):
        rule = parse_rule("entity.ready == true => workflow('process'); workflow('notify')")
        assert "process" in rule.workflow_calls
        assert "notify" in rule.workflow_calls

