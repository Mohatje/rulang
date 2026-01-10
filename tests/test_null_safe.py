"""Tests for null-safe access (?.) and null coalescing (??) operators."""

import pytest

from rulang import RuleEngine


class TestNullSafeAccess:
    """Tests for the null-safe access operator (?.)."""

    def test_null_safe_with_value(self):
        """Test ?. when value exists."""
        engine = RuleEngine()
        engine.add_rules(["entity.user?.name == 'John' => ret true"])
        assert engine.evaluate({"user": {"name": "John"}}) is True

    def test_null_safe_with_none_parent(self):
        """Test ?. when parent is None."""
        engine = RuleEngine()
        engine.add_rules(["entity.user?.name == none => ret true"])
        assert engine.evaluate({"user": None}) is True

    def test_null_safe_chain(self):
        """Test chained null-safe access."""
        engine = RuleEngine()
        engine.add_rules(["entity.user?.profile?.name == 'John' => ret true"])
        assert engine.evaluate({
            "user": {"profile": {"name": "John"}}
        }) is True
        assert engine.evaluate({
            "user": {"profile": None}
        }) is None
        assert engine.evaluate({
            "user": None
        }) is None

    def test_null_safe_chain_returns_none(self):
        """Test null-safe chain returns None when any part is None."""
        engine = RuleEngine()
        engine.add_rules(["entity.a?.b?.c?.d == none => ret true"])
        assert engine.evaluate({"a": None}) is True
        assert engine.evaluate({"a": {"b": None}}) is True
        assert engine.evaluate({"a": {"b": {"c": None}}}) is True

    def test_null_safe_mixed_with_regular(self):
        """Test mixing null-safe and regular access."""
        engine = RuleEngine()
        engine.add_rules(["entity.config?.settings.timeout == 30 => ret true"])
        assert engine.evaluate({
            "config": {"settings": {"timeout": 30}}
        }) is True

    def test_null_safe_with_exists(self):
        """Test null-safe access with exists operator."""
        engine = RuleEngine()
        engine.add_rules(["entity.user?.email exists => ret true"])
        assert engine.evaluate({"user": {"email": "test@example.com"}}) is True
        assert engine.evaluate({"user": {"email": None}}) is None
        assert engine.evaluate({"user": None}) is None

    def test_null_safe_in_condition(self):
        """Test null-safe access in complex condition."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.order?.status == 'shipped' and entity.order?.tracking exists => ret true"
        ])
        assert engine.evaluate({
            "order": {"status": "shipped", "tracking": "ABC123"}
        }) is True
        assert engine.evaluate({
            "order": {"status": "shipped", "tracking": None}
        }) is None
        assert engine.evaluate({
            "order": None
        }) is None


class TestNullCoalescing:
    """Tests for the null coalescing operator (??)."""

    def test_null_coalesce_with_value(self):
        """Test ?? when value is not None."""
        engine = RuleEngine()
        engine.add_rules(["entity.name ?? 'Unknown' == 'John' => ret true"])
        assert engine.evaluate({"name": "John"}) is True

    def test_null_coalesce_with_none(self):
        """Test ?? when value is None."""
        engine = RuleEngine()
        engine.add_rules(["entity.name ?? 'Unknown' == 'Unknown' => ret true"])
        assert engine.evaluate({"name": None}) is True

    def test_null_coalesce_with_zero(self):
        """Test ?? with zero (should NOT use default)."""
        engine = RuleEngine()
        engine.add_rules(["entity.count ?? 10 == 0 => ret true"])
        assert engine.evaluate({"count": 0}) is True

    def test_null_coalesce_with_empty_string(self):
        """Test ?? with empty string (should NOT use default)."""
        engine = RuleEngine()
        engine.add_rules(["entity.name ?? 'Unknown' == '' => ret true"])
        assert engine.evaluate({"name": ""}) is True

    def test_null_coalesce_with_false(self):
        """Test ?? with False (should NOT use default)."""
        engine = RuleEngine()
        engine.add_rules(["entity.flag ?? true == false => ret true"])
        assert engine.evaluate({"flag": False}) is True

    def test_null_coalesce_chain(self):
        """Test chained null coalescing."""
        engine = RuleEngine()
        engine.add_rules(["entity.a ?? entity.b ?? entity.c ?? 'default' == 'found' => ret true"])
        assert engine.evaluate({"a": "found", "b": None, "c": None}) is True
        assert engine.evaluate({"a": None, "b": "found", "c": None}) is True
        assert engine.evaluate({"a": None, "b": None, "c": "found"}) is True

    def test_null_coalesce_chain_default(self):
        """Test chained null coalescing falls back to default."""
        engine = RuleEngine()
        engine.add_rules(["entity.a ?? entity.b ?? 'default' == 'default' => ret true"])
        assert engine.evaluate({"a": None, "b": None}) is True

    def test_null_coalesce_in_assignment(self):
        """Test ?? in assignment expression."""
        engine = RuleEngine()
        engine.add_rules(["true => entity.result = entity.name ?? 'Anonymous'"])
        entity1 = {"name": "John", "result": None}
        engine.evaluate(entity1)
        assert entity1["result"] == "John"

        entity2 = {"name": None, "result": None}
        engine.evaluate(entity2)
        assert entity2["result"] == "Anonymous"

    def test_null_coalesce_with_arithmetic(self):
        """Test ?? in arithmetic expression."""
        engine = RuleEngine()
        engine.add_rules(["(entity.bonus ?? 0) + entity.salary == 1100 => ret true"])
        assert engine.evaluate({"bonus": 100, "salary": 1000}) is True
        assert engine.evaluate({"bonus": None, "salary": 1100}) is True


class TestCombinedNullSafeAndCoalescing:
    """Tests for combining ?. and ?? operators."""

    def test_null_safe_with_coalescing(self):
        """Test ?. combined with ?? for safe access with default."""
        engine = RuleEngine()
        engine.add_rules(["entity.user?.name ?? 'Unknown' == 'John' => ret true"])
        assert engine.evaluate({"user": {"name": "John"}}) is True

    def test_null_safe_with_coalescing_fallback(self):
        """Test ?. with ?? falling back to default."""
        engine = RuleEngine()
        engine.add_rules(["entity.user?.name ?? 'Unknown' == 'Unknown' => ret true"])
        assert engine.evaluate({"user": None}) is True
        assert engine.evaluate({"user": {"name": None}}) is True

    def test_deep_null_safe_with_coalescing(self):
        """Test deep null-safe access with coalescing."""
        engine = RuleEngine()
        engine.add_rules([
            "entity.config?.database?.timeout ?? 30 == 30 => ret true"
        ])
        assert engine.evaluate({"config": None}) is True
        assert engine.evaluate({"config": {"database": None}}) is True
        assert engine.evaluate({"config": {"database": {"timeout": None}}}) is True
        assert engine.evaluate({"config": {"database": {"timeout": 60}}}) is None

    def test_null_safe_with_function(self):
        """Test null-safe access with function call."""
        engine = RuleEngine()
        engine.add_rules([
            "lower(entity.user?.name ?? 'unknown') == 'john' => ret true"
        ])
        assert engine.evaluate({"user": {"name": "JOHN"}}) is True
        assert engine.evaluate({"user": None}) is None  # 'unknown' != 'john'

    def test_complex_null_safe_expression(self):
        """Test complex expression with multiple null-safe operators."""
        engine = RuleEngine()
        engine.add_rules([
            "(entity.order?.total ?? 0) + (entity.order?.shipping ?? 5) > 100 => ret true"
        ])
        assert engine.evaluate({"order": {"total": 100, "shipping": 10}}) is True
        assert engine.evaluate({"order": {"total": 100, "shipping": None}}) is True  # 100 + 5 > 100
        assert engine.evaluate({"order": None}) is None  # 0 + 5 = 5, not > 100


class TestNullSafeEdgeCases:
    """Edge cases for null-safe operations."""

    def test_null_safe_preserves_false(self):
        """Test that ?. doesn't treat False as None."""
        engine = RuleEngine()
        engine.add_rules(["entity.user?.active == false => ret true"])
        assert engine.evaluate({"user": {"active": False}}) is True

    def test_null_safe_preserves_zero(self):
        """Test that ?. doesn't treat 0 as None."""
        engine = RuleEngine()
        engine.add_rules(["entity.user?.count == 0 => ret true"])
        assert engine.evaluate({"user": {"count": 0}}) is True

    def test_null_safe_preserves_empty_string(self):
        """Test that ?. doesn't treat '' as None."""
        engine = RuleEngine()
        engine.add_rules(["entity.user?.name == '' => ret true"])
        assert engine.evaluate({"user": {"name": ""}}) is True

    def test_null_coalesce_only_for_none(self):
        """Test that ?? only triggers for None, not other falsy values."""
        engine = RuleEngine()
        engine.add_rules(["entity.value ?? 'default' == entity.value => ret true"])
        assert engine.evaluate({"value": 0}) is True
        assert engine.evaluate({"value": ""}) is True
        assert engine.evaluate({"value": False}) is True
        assert engine.evaluate({"value": []}) is True

    def test_null_safe_with_list_access(self):
        """Test null-safe access followed by list index."""
        engine = RuleEngine()
        engine.add_rules(["entity.user?.items[0] == 'first' => ret true"])
        assert engine.evaluate({"user": {"items": ["first", "second"]}}) is True

    def test_double_question_mark_is_coalesce_not_safe_safe(self):
        """Test that ?? is null coalesce, not double null-safe."""
        engine = RuleEngine()
        engine.add_rules(["entity.a ?? entity.b == 'b_value' => ret true"])
        assert engine.evaluate({"a": None, "b": "b_value"}) is True
