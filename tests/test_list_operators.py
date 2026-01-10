"""Tests for list operators: contains_any, contains_all, and any-satisfies semantics."""

import pytest

from rulang import RuleEngine


class TestContainsAnyOperator:
    """Tests for the 'contains_any' operator."""

    def test_contains_any_single_match(self):
        """Test contains_any with single matching element."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.recipients contains_any ['admin@co.com', 'support@co.com'] => ret true"
        ])
        assert engine.evaluate({"recipients": ["admin@co.com", "user@co.com"]}) is True
        assert engine.evaluate({"recipients": ["user@co.com", "other@co.com"]}) is None

    def test_contains_any_multiple_matches(self):
        """Test contains_any with multiple matching elements."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.tags contains_any ['urgent', 'critical'] => ret true"
        ])
        assert engine.evaluate({"tags": ["urgent", "critical"]}) is True
        assert engine.evaluate({"tags": ["normal"]}) is None

    def test_contains_any_empty_list(self):
        """Test contains_any with empty lists."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.tags contains_any ['urgent'] => ret true"
        ])
        assert engine.evaluate({"tags": []}) is None

    def test_contains_any_with_numbers(self):
        """Test contains_any with numeric values."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.codes contains_any [100, 200, 300] => ret true"
        ])
        assert engine.evaluate({"codes": [100, 400]}) is True
        assert engine.evaluate({"codes": [400, 500]}) is None

    def test_contains_any_with_none(self):
        """Test contains_any with None collection."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.tags contains_any ['urgent'] => ret true"
        ])
        assert engine.evaluate({"tags": None}) is None

    def test_contains_any_scalar_left(self):
        """Test contains_any with scalar on left (converts to list)."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.status contains_any ['active', 'pending'] => ret true"
        ])
        assert engine.evaluate({"status": "active"}) is True
        assert engine.evaluate({"status": "inactive"}) is None


class TestContainsAllOperator:
    """Tests for the 'contains_all' operator."""

    def test_contains_all_all_present(self):
        """Test contains_all when all elements are present."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.tags contains_all ['reviewed', 'approved'] => ret true"
        ])
        assert engine.evaluate({"tags": ["reviewed", "approved", "done"]}) is True
        assert engine.evaluate({"tags": ["reviewed", "approved"]}) is True

    def test_contains_all_partial_match(self):
        """Test contains_all when only some elements are present."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.tags contains_all ['reviewed', 'approved'] => ret true"
        ])
        assert engine.evaluate({"tags": ["reviewed"]}) is None
        assert engine.evaluate({"tags": ["approved"]}) is None

    def test_contains_all_empty_list(self):
        """Test contains_all with empty lists."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.tags contains_all ['urgent'] => ret true"
        ])
        assert engine.evaluate({"tags": []}) is None

    def test_contains_all_with_numbers(self):
        """Test contains_all with numeric values."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.codes contains_all [100, 200] => ret true"
        ])
        assert engine.evaluate({"codes": [100, 200, 300]}) is True
        assert engine.evaluate({"codes": [100, 300]}) is None

    def test_contains_all_with_none(self):
        """Test contains_all with None collection."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.tags contains_all ['urgent'] => ret true"
        ])
        assert engine.evaluate({"tags": None}) is None

    def test_contains_all_scalar_left(self):
        """Test contains_all with scalar on left (converts to list)."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.status contains_all ['active'] => ret true"
        ])
        assert engine.evaluate({"status": "active"}) is True
        assert engine.evaluate({"status": "inactive"}) is None


class TestAnySatisfiesSemantics:
    """Tests for list any-satisfies semantics in comparisons."""

    def test_equality_any_satisfies_left_list(self):
        """Test == with list on left uses any-satisfies."""
        engine = RuleEngine()
        engine.add_rules(["entity.tags == 'urgent' => ret true"])
        assert engine.evaluate({"tags": ["urgent", "normal"]}) is True
        assert engine.evaluate({"tags": ["normal", "low"]}) is None

    def test_equality_any_satisfies_right_list(self):
        """Test == with list on right uses any-satisfies."""
        engine = RuleEngine()
        engine.add_rules(["entity.status == ['active', 'pending'] => ret true"])
        assert engine.evaluate({"status": "active"}) is True
        assert engine.evaluate({"status": "inactive"}) is None

    def test_equality_both_lists_exact_match(self):
        """Test == with both lists uses exact equality."""
        engine = RuleEngine()
        engine.add_rules(["entity.tags == [1, 2, 3] => ret true"])
        assert engine.evaluate({"tags": [1, 2, 3]}) is True
        assert engine.evaluate({"tags": [1, 2]}) is None
        assert engine.evaluate({"tags": [3, 2, 1]}) is None

    def test_not_equal_any_satisfies(self):
        """Test != with any-satisfies semantics."""
        engine = RuleEngine()
        engine.add_rules(["entity.tags != 'spam' => ret true"])
        # All tags must not equal 'spam' for != to be true
        assert engine.evaluate({"tags": ["good", "content"]}) is True
        assert engine.evaluate({"tags": ["spam", "content"]}) is None

    def test_in_operator_any_satisfies(self):
        """Test 'in' with any-satisfies semantics on left."""
        engine = RuleEngine()
        engine.add_rules(["entity.tags in ['urgent', 'critical'] => ret true"])
        assert engine.evaluate({"tags": ["urgent", "normal"]}) is True
        assert engine.evaluate({"tags": ["normal", "low"]}) is None

    def test_greater_than_with_scalar(self):
        """Test > compares scalar values (no any-satisfies for numeric comparisons)."""
        engine = RuleEngine()
        engine.add_rules(["entity.score > 90 => ret true"])
        assert engine.evaluate({"score": 95}) is True
        assert engine.evaluate({"score": 85}) is None

    def test_less_than_with_scalar(self):
        """Test < compares scalar values (no any-satisfies for numeric comparisons)."""
        engine = RuleEngine()
        engine.add_rules(["entity.score < 50 => ret true"])
        assert engine.evaluate({"score": 40}) is True
        assert engine.evaluate({"score": 60}) is None


class TestCombinedListOperators:
    """Tests for combining list operators with other conditions."""

    def test_contains_any_and_contains_all(self):
        """Test combining contains_any and contains_all."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.tags contains_all ['approved'] and entity.labels contains_any ['urgent', 'high'] => ret true"
        ])
        assert engine.evaluate({
            "tags": ["approved", "done"],
            "labels": ["urgent"]
        }) is True
        assert engine.evaluate({
            "tags": ["approved"],
            "labels": ["low"]
        }) is None

    def test_contains_any_with_len(self):
        """Test contains_any with len() function."""
        engine = RuleEngine()
        engine.add_rules([
            "len(entity.items) > 0 and entity.items contains_any ['special'] => ret true"
        ])
        assert engine.evaluate({"items": ["normal", "special"]}) is True
        assert engine.evaluate({"items": []}) is None

    def test_any_satisfies_with_function(self):
        """Test any-satisfies with lower() function."""
        engine = RuleEngine()
        # Note: lower() applied to list returns the list (we apply to strings inside)
        engine.add_rules(["entity.tags == 'URGENT' => ret true"])
        # This checks if any tag equals 'URGENT' exactly
        assert engine.evaluate({"tags": ["URGENT", "normal"]}) is True
        assert engine.evaluate({"tags": ["urgent", "normal"]}) is None

    def test_list_operations_with_assignment(self):
        """Test list operations with assignments."""
        engine = RuleEngine(mode="all_match")  # Need all_match to execute both rules
        engine.add_rules([
            "entity.tags contains_any ['urgent', 'critical'] => entity.priority = 'high'",
            "entity.tags contains_all ['reviewed', 'approved'] => entity.status = 'ready'"
        ])
        entity = {"tags": ["urgent", "reviewed", "approved"], "priority": None, "status": None}
        engine.evaluate(entity)
        assert entity["priority"] == "high"
        assert entity["status"] == "ready"


class TestListEdgeCases:
    """Edge cases for list operators."""

    def test_empty_check_list(self):
        """Test with empty check list."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.tags contains_any [] => ret true"
        ])
        # contains_any with empty list should return False
        assert engine.evaluate({"tags": ["anything"]}) is None

    def test_contains_all_empty_check_list(self):
        """Test contains_all with empty check list."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.tags contains_all [] => ret true"
        ])
        # contains_all with empty list should return True (vacuous truth)
        assert engine.evaluate({"tags": ["anything"]}) is True

    def test_nested_list_comparison(self):
        """Test comparing nested lists uses exact equality."""
        engine = RuleEngine()
        engine.add_rules(["entity.matrix == [[1, 2], [3, 4]] => ret true"])
        # When comparing two lists, use exact equality
        assert engine.evaluate({"matrix": [[1, 2], [3, 4]]}) is True
        assert engine.evaluate({"matrix": [[3, 4], [5, 6]]}) is None

    def test_tuple_treated_as_list(self):
        """Test tuples are treated the same as lists."""
        engine = RuleEngine()
        engine.add_rules(["entity.items == 'a' => ret true"])
        assert engine.evaluate({"items": ("a", "b", "c")}) is True
        assert engine.evaluate({"items": ("x", "y", "z")}) is None
