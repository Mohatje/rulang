"""Tests for existence operators: exists, is_empty."""

import pytest

from rule_interpreter import RuleEngine


class TestExistsOperator:
    """Tests for the 'exists' operator."""

    def test_exists_with_value(self):
        """Test exists with a non-None value."""
        engine = RuleEngine()
        engine.add_rules(["entity.customer_id exists => ret true"])
        assert engine.evaluate({"customer_id": "C123"}) is True
        assert engine.evaluate({"customer_id": 123}) is True
        assert engine.evaluate({"customer_id": 0}) is True
        assert engine.evaluate({"customer_id": ""}) is True

    def test_exists_with_none(self):
        """Test exists with None value."""
        engine = RuleEngine()
        engine.add_rules(["entity.customer_id exists => ret true"])
        assert engine.evaluate({"customer_id": None}) is None

    def test_exists_with_false(self):
        """Test exists with boolean False (exists should return True)."""
        engine = RuleEngine()
        engine.add_rules(["entity.flag exists => ret true"])
        assert engine.evaluate({"flag": False}) is True

    def test_exists_with_zero(self):
        """Test exists with zero (exists should return True)."""
        engine = RuleEngine()
        engine.add_rules(["entity.count exists => ret true"])
        assert engine.evaluate({"count": 0}) is True

    def test_exists_with_empty_string(self):
        """Test exists with empty string (exists should return True)."""
        engine = RuleEngine()
        engine.add_rules(["entity.name exists => ret true"])
        assert engine.evaluate({"name": ""}) is True

    def test_exists_with_empty_list(self):
        """Test exists with empty list (exists should return True)."""
        engine = RuleEngine()
        engine.add_rules(["entity.items exists => ret true"])
        assert engine.evaluate({"items": []}) is True

    def test_not_exists(self):
        """Test not exists (checking for None)."""
        engine = RuleEngine()
        engine.add_rules(["not entity.customer_id exists => ret true"])
        assert engine.evaluate({"customer_id": None}) is True
        assert engine.evaluate({"customer_id": "C123"}) is None

    def test_exists_nested_path(self):
        """Test exists with nested path."""
        engine = RuleEngine()
        engine.add_rules(["entity.user.profile.name exists => ret true"])
        assert engine.evaluate({"user": {"profile": {"name": "John"}}}) is True


class TestIsEmptyOperator:
    """Tests for the 'is_empty' operator."""

    def test_is_empty_with_none(self):
        """Test is_empty with None value."""
        engine = RuleEngine()
        engine.add_rules(["entity.notes is_empty => ret true"])
        assert engine.evaluate({"notes": None}) is True

    def test_is_empty_with_empty_string(self):
        """Test is_empty with empty string."""
        engine = RuleEngine()
        engine.add_rules(["entity.notes is_empty => ret true"])
        assert engine.evaluate({"notes": ""}) is True

    def test_is_empty_with_whitespace_only(self):
        """Test is_empty with whitespace-only string."""
        engine = RuleEngine()
        engine.add_rules(["entity.notes is_empty => ret true"])
        assert engine.evaluate({"notes": "   "}) is True
        assert engine.evaluate({"notes": "\t\n"}) is True

    def test_is_empty_with_empty_list(self):
        """Test is_empty with empty list."""
        engine = RuleEngine()
        engine.add_rules(["entity.items is_empty => ret true"])
        assert engine.evaluate({"items": []}) is True

    def test_is_empty_with_empty_dict(self):
        """Test is_empty with empty dict."""
        engine = RuleEngine()
        engine.add_rules(["entity.metadata is_empty => ret true"])
        assert engine.evaluate({"metadata": {}}) is True

    def test_is_empty_with_content(self):
        """Test is_empty with non-empty values."""
        engine = RuleEngine()
        engine.add_rules(["entity.notes is_empty => ret true"])
        assert engine.evaluate({"notes": "Some content"}) is None
        assert engine.evaluate({"notes": [1, 2, 3]}) is None
        assert engine.evaluate({"notes": {"key": "value"}}) is None

    def test_isempty_alias(self):
        """Test isempty alias (without underscore)."""
        engine = RuleEngine()
        engine.add_rules(["entity.notes isempty => ret true"])
        assert engine.evaluate({"notes": ""}) is True
        assert engine.evaluate({"notes": None}) is True

    def test_not_is_empty(self):
        """Test not is_empty (checking for content)."""
        engine = RuleEngine()
        engine.add_rules(["not entity.notes is_empty => ret true"])
        assert engine.evaluate({"notes": "Has content"}) is True
        assert engine.evaluate({"notes": ""}) is None
        assert engine.evaluate({"notes": None}) is None

    def test_is_empty_with_zero(self):
        """Test is_empty with zero (should NOT be empty)."""
        engine = RuleEngine()
        engine.add_rules(["entity.count is_empty => ret true"])
        assert engine.evaluate({"count": 0}) is None

    def test_is_empty_with_false(self):
        """Test is_empty with False (should NOT be empty)."""
        engine = RuleEngine()
        engine.add_rules(["entity.flag is_empty => ret true"])
        assert engine.evaluate({"flag": False}) is None


class TestCombinedExistenceOperators:
    """Tests for combining existence operators with other conditions."""

    def test_exists_and_not_empty(self):
        """Test checking that a value exists AND has content."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.name exists and not entity.name is_empty => ret true"
        ])
        assert engine.evaluate({"name": "John"}) is True
        assert engine.evaluate({"name": ""}) is None
        assert engine.evaluate({"name": None}) is None

    def test_exists_or_default(self):
        """Test exists in condition with assignment."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.status exists => entity.has_status = true",
            "not entity.status exists => entity.has_status = false"
        ])
        entity1 = {"status": "active", "has_status": None}
        engine.evaluate(entity1)
        assert entity1["has_status"] is True

        entity2 = {"status": None, "has_status": None}
        engine.evaluate(entity2)
        assert entity2["has_status"] is False

    def test_multiple_existence_checks(self):
        """Test multiple existence checks in one rule."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.a exists and entity.b exists and not entity.c exists => ret true"
        ])
        assert engine.evaluate({"a": 1, "b": 2, "c": None}) is True
        assert engine.evaluate({"a": 1, "b": None, "c": None}) is None
        assert engine.evaluate({"a": 1, "b": 2, "c": 3}) is None

    def test_is_empty_with_len_comparison(self):
        """Test comparing is_empty with len() function."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.items is_empty => entity.count = 0",
            "not entity.items is_empty => entity.count = len(entity.items)"
        ])
        entity1 = {"items": [], "count": None}
        engine.evaluate(entity1)
        assert entity1["count"] == 0

        entity2 = {"items": [1, 2, 3], "count": None}
        engine.evaluate(entity2)
        assert entity2["count"] == 3
