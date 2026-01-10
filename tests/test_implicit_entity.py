"""Comprehensive tests for implicit entity syntax.

Tests that rules can use shorter paths like 'age' instead of 'entity.age'.
Both explicit ('entity.age') and implicit ('age') syntax should work.
"""

import pytest
import warnings
from dataclasses import dataclass

from rulang import RuleEngine, Workflow
from rulang.path_resolver import PathResolver
from rulang.visitor import parse_rule, RuleInterpreter
from rulang.exceptions import CyclicDependencyWarning
from rulang.workflows import clear_workflow_registry


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear workflow registry before each test."""
    clear_workflow_registry()
    yield
    clear_workflow_registry()


class TestPathResolverImplicitEntity:
    """Test PathResolver with implicit entity prefix."""

    def test_normalize_path_adds_entity_prefix(self):
        entity = {"name": "test", "age": 25}
        resolver = PathResolver(entity)

        # Should normalize ["age"] to ["entity", "age"]
        normalized = resolver.normalize_path(["age"])
        assert normalized == ["entity", "age"]

    def test_normalize_path_keeps_existing_prefix(self):
        entity = {"name": "test"}
        resolver = PathResolver(entity)

        # Should not change ["entity", "name"]
        normalized = resolver.normalize_path(["entity", "name"])
        assert normalized == ["entity", "name"]

    def test_normalize_path_with_custom_entity_name(self):
        entity = {"name": "test"}
        resolver = PathResolver(entity, entity_name="user")

        # Should normalize to custom entity name
        normalized = resolver.normalize_path(["name"])
        assert normalized == ["user", "name"]

    def test_resolve_implicit_simple_path(self):
        entity = {"name": "John", "age": 30}
        resolver = PathResolver(entity)

        # Implicit entity access
        assert resolver.resolve(["name"]) == "John"
        assert resolver.resolve(["age"]) == 30

    def test_resolve_implicit_nested_path(self):
        entity = {"user": {"profile": {"name": "John"}}}
        resolver = PathResolver(entity)

        # Implicit entity access with nested path
        assert resolver.resolve(["user", "profile", "name"]) == "John"

    def test_resolve_implicit_with_list_index(self):
        entity = {"items": [{"value": 10}, {"value": 20}]}
        resolver = PathResolver(entity)

        # Implicit entity access with list indexing
        assert resolver.resolve(["items", 0, "value"]) == 10
        assert resolver.resolve(["items", 1, "value"]) == 20

    def test_resolve_explicit_still_works(self):
        entity = {"name": "John"}
        resolver = PathResolver(entity)

        # Explicit entity access should still work
        assert resolver.resolve(["entity", "name"]) == "John"

    def test_assign_implicit_path(self):
        entity = {"value": 10}
        resolver = PathResolver(entity)

        # Implicit assignment
        resolver.assign(["value"], 20)
        assert entity["value"] == 20

    def test_assign_implicit_nested_path(self):
        entity = {"user": {"name": "John"}}
        resolver = PathResolver(entity)

        # Implicit nested assignment
        resolver.assign(["user", "name"], "Jane")
        assert entity["user"]["name"] == "Jane"

    def test_assign_explicit_still_works(self):
        entity = {"value": 10}
        resolver = PathResolver(entity)

        # Explicit assignment should still work
        resolver.assign(["entity", "value"], 30)
        assert entity["value"] == 30

    def test_context_variables_take_precedence(self):
        entity = {"name": "entity_name"}
        resolver = PathResolver(entity)

        # Add another variable to context
        resolver.add_to_context("other", {"name": "other_name"})

        # "other" should resolve from context, not entity
        assert resolver.resolve(["other", "name"]) == "other_name"
        # "name" should still resolve from entity (implicit)
        assert resolver.resolve(["name"]) == "entity_name"


class TestRuleAnalyzerImplicitEntity:
    """Test RuleAnalyzer normalizes paths correctly."""

    def test_implicit_path_normalized_in_reads(self):
        parsed = parse_rule("age >= 18 => is_adult = true")

        # Both implicit paths should be normalized to include 'entity'
        assert "entity.age" in parsed.reads
        assert "entity.is_adult" in parsed.writes

    def test_explicit_path_unchanged_in_reads(self):
        parsed = parse_rule("entity.age >= 18 => entity.is_adult = true")

        # Explicit paths should remain the same
        assert "entity.age" in parsed.reads
        assert "entity.is_adult" in parsed.writes

    def test_mixed_implicit_explicit_paths(self):
        parsed = parse_rule("entity.age >= 18 and status == 'active' => discount = 0.1")

        # Both should be normalized consistently
        assert "entity.age" in parsed.reads
        assert "entity.status" in parsed.reads
        assert "entity.discount" in parsed.writes

    def test_nested_implicit_path(self):
        parsed = parse_rule("user.profile.age >= 18 => user.is_adult = true")

        # Nested implicit paths should be normalized
        assert "entity.user.profile.age" in parsed.reads
        assert "entity.user.is_adult" in parsed.writes

    def test_custom_entity_name_normalization(self):
        parsed = parse_rule("age >= 18 => is_adult = true", entity_name="customer")

        # Should normalize to custom entity name
        assert "customer.age" in parsed.reads
        assert "customer.is_adult" in parsed.writes


class TestRuleInterpreterImplicitEntity:
    """Test RuleInterpreter with implicit entity syntax."""

    def test_simple_implicit_condition(self):
        entity = {"age": 25, "is_adult": False}
        parsed = parse_rule("age >= 18 => is_adult = true")

        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(parsed.tree)

        assert matched is True
        assert entity["is_adult"] is True

    def test_implicit_condition_not_matched(self):
        entity = {"age": 15, "is_adult": False}
        parsed = parse_rule("age >= 18 => is_adult = true")

        interpreter = RuleInterpreter(entity)
        matched, _ = interpreter.execute(parsed.tree)

        assert matched is False
        assert entity["is_adult"] is False

    def test_implicit_compound_assignment(self):
        entity = {"value": 10}
        parsed = parse_rule("value > 0 => value += 5")

        interpreter = RuleInterpreter(entity)
        interpreter.execute(parsed.tree)

        assert entity["value"] == 15

    def test_implicit_nested_path(self):
        entity = {"user": {"age": 25, "status": "pending"}}
        parsed = parse_rule("user.age >= 18 => user.status = 'adult'")

        interpreter = RuleInterpreter(entity)
        interpreter.execute(parsed.tree)

        assert entity["user"]["status"] == "adult"

    def test_implicit_with_return(self):
        entity = {"value": 100}
        parsed = parse_rule("value > 50 => ret 'high'")

        interpreter = RuleInterpreter(entity)
        matched, result = interpreter.execute(parsed.tree)

        assert matched is True
        assert result == "high"

    def test_implicit_with_list_access(self):
        entity = {"items": [{"price": 100}, {"price": 200}]}
        parsed = parse_rule("items[0].price > 50 => items[0].discounted = true")

        interpreter = RuleInterpreter(entity)
        interpreter.execute(parsed.tree)

        assert entity["items"][0]["discounted"] is True

    def test_mixed_implicit_explicit(self):
        entity = {"a": 10, "b": 20, "result": 0}
        parsed = parse_rule("a > 5 and entity.b > 10 => entity.result = a + b")

        interpreter = RuleInterpreter(entity)
        interpreter.execute(parsed.tree)

        assert entity["result"] == 30


class TestRuleEngineImplicitEntity:
    """Test RuleEngine with implicit entity syntax."""

    def test_basic_implicit_rule(self):
        engine = RuleEngine()
        engine.add_rules("value > 10 => ret true")

        result = engine.evaluate({"value": 15})
        assert result is True

        result = engine.evaluate({"value": 5})
        assert result is None

    def test_implicit_mutation(self):
        engine = RuleEngine()
        engine.add_rules("status == 'pending' => status = 'processed'")

        entity = {"status": "pending"}
        engine.evaluate(entity)
        assert entity["status"] == "processed"

    def test_implicit_multiple_rules(self):
        engine = RuleEngine()
        engine.add_rules([
            "value > 100 => ret 'high'",
            "value > 50 => ret 'medium'",
            "value > 0 => ret 'low'",
        ])

        assert engine.evaluate({"value": 150}) == "high"
        assert engine.evaluate({"value": 75}) == "medium"
        assert engine.evaluate({"value": 25}) == "low"

    def test_implicit_all_match_mode(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "value > 0 => count = 1",
            "value > 0 => total = value * 2",
        ])

        entity = {"value": 10, "count": 0, "total": 0}
        engine.evaluate(entity)

        assert entity["count"] == 1
        assert entity["total"] == 20

    def test_implicit_dependency_ordering(self):
        engine = RuleEngine(mode="all_match")

        # Add rules in "wrong" order - dependency should fix it
        engine.add_rules([
            "is_adult == true => discount = 0.1",  # Depends on is_adult
            "age >= 18 => is_adult = true",  # Must run first
        ])

        entity = {"age": 25, "is_adult": False, "discount": 0.0}
        engine.evaluate(entity)

        # Despite order, age rule should execute first
        assert entity["is_adult"] is True
        assert entity["discount"] == 0.1

    def test_implicit_with_explicit_mixed(self):
        engine = RuleEngine(mode="all_match")

        # Mix implicit and explicit syntax
        engine.add_rules([
            "entity.age >= 18 => is_adult = true",
            "is_adult == true => entity.discount = 0.1",
        ])

        entity = {"age": 25, "is_adult": False, "discount": 0.0}
        engine.evaluate(entity)

        assert entity["is_adult"] is True
        assert entity["discount"] == 0.1

    def test_implicit_nested_entity(self):
        engine = RuleEngine()
        engine.add_rules("user.profile.age >= 18 => user.is_adult = true")

        entity = {"user": {"profile": {"age": 25}, "is_adult": False}}
        engine.evaluate(entity)
        assert entity["user"]["is_adult"] is True

    def test_implicit_with_dataclass(self):
        @dataclass
        class Entity:
            name: str
            processed: bool = False

        engine = RuleEngine()
        engine.add_rules("name == 'test' => processed = true")

        entity = Entity(name="test")
        engine.evaluate(entity)
        assert entity.processed is True

    def test_implicit_with_functions(self):
        engine = RuleEngine()
        engine.add_rules("len(items) > 0 => has_items = true")

        entity = {"items": [1, 2, 3], "has_items": False}
        engine.evaluate(entity)
        assert entity["has_items"] is True

    def test_implicit_with_string_operators(self):
        engine = RuleEngine()
        engine.add_rules("name contains 'test' => matched = true")

        entity = {"name": "this is a test string", "matched": False}
        engine.evaluate(entity)
        assert entity["matched"] is True

    def test_implicit_with_list_operators(self):
        engine = RuleEngine()
        engine.add_rules("tags contains_any ['urgent', 'priority'] => is_important = true")

        entity = {"tags": ["urgent", "normal"], "is_important": False}
        engine.evaluate(entity)
        assert entity["is_important"] is True

    def test_implicit_with_null_safe(self):
        engine = RuleEngine()
        engine.add_rules("user?.name != none => has_name = true")

        entity = {"user": {"name": "John"}, "has_name": False}
        engine.evaluate(entity)
        assert entity["has_name"] is True

        # Test with None user
        entity = {"user": None, "has_name": False}
        engine.evaluate(entity)
        assert entity["has_name"] is False

    def test_implicit_with_null_coalesce(self):
        engine = RuleEngine()
        engine.add_rules("true => result = value ?? 'default'")

        entity = {"value": None, "result": ""}
        engine.evaluate(entity)
        assert entity["result"] == "default"

        entity = {"value": "custom", "result": ""}
        engine.evaluate(entity)
        assert entity["result"] == "custom"


class TestImplicitEntityWorkflows:
    """Test implicit entity syntax with workflows."""

    def test_implicit_with_workflow(self):
        engine = RuleEngine()
        engine.add_rules("value > 0 => workflow('double')")

        def double(e):
            e["value"] *= 2

        entity = {"value": 10}
        engine.evaluate(entity, workflows={"double": double})
        assert entity["value"] == 20

    def test_implicit_workflow_dependencies(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "ready == true => workflow('calculate')",
            "result > 0 => status = 'done'",
        ])

        def calculate(e):
            e["result"] = e["value"] * 2

        workflows = {
            "calculate": Workflow(
                fn=calculate,
                reads=["entity.value"],
                writes=["entity.result"],
            )
        }

        entity = {"ready": True, "value": 10, "result": 0, "status": "pending"}
        engine.evaluate(entity, workflows=workflows)

        assert entity["result"] == 20
        assert entity["status"] == "done"


class TestImplicitEntityDependencyGraph:
    """Test that dependency graph works correctly with implicit entity."""

    def test_dependency_graph_with_implicit_paths(self):
        engine = RuleEngine()
        engine.add_rules([
            "a > 0 => b = 1",  # writes b
            "b > 0 => c = 1",  # reads b, writes c
        ])

        graph = engine.get_dependency_graph()
        # Rule 0 writes b, Rule 1 reads b, so Rule 1 depends on Rule 0
        assert 1 in graph.get(0, set())

    def test_execution_order_with_implicit_paths(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "b > 0 => c = 1",  # Rule 0: reads b
            "a > 0 => b = 1",  # Rule 1: writes b
        ])

        order = engine.get_execution_order()
        # Rule 1 should come before Rule 0
        assert order.index(1) < order.index(0)

    def test_rule_analysis_with_implicit_paths(self):
        engine = RuleEngine()
        engine.add_rules("a > 0 and b < 10 => c = a + b")

        analysis = engine.get_rule_analysis(0)
        # All paths should be normalized to include entity
        assert "entity.a" in analysis["reads"]
        assert "entity.b" in analysis["reads"]
        assert "entity.c" in analysis["writes"]

    def test_cyclic_dependency_detection_with_implicit(self):
        engine = RuleEngine(mode="all_match")

        # Create a cycle with implicit paths
        engine.add_rules([
            "a > 0 => b = 1",
            "b > 0 => a = 1",
        ])

        entity = {"a": 1, "b": 1}

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            engine.evaluate(entity)
            cycle_warnings = [x for x in w if issubclass(x.category, CyclicDependencyWarning)]
            assert len(cycle_warnings) > 0


class TestBackwardCompatibility:
    """Test that explicit entity syntax still works correctly."""

    def test_explicit_entity_still_works(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 10 => entity.result = true")

        entity = {"value": 15, "result": False}
        engine.evaluate(entity)
        assert entity["result"] is True

    def test_mixed_explicit_implicit_same_engine(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.a > 0 => b = 1",  # explicit condition, implicit action
            "b > 0 => entity.c = 1",  # implicit condition, explicit action
        ])

        entity = {"a": 1, "b": 0, "c": 0}
        engine.evaluate(entity)

        assert entity["b"] == 1
        assert entity["c"] == 1

    def test_all_explicit_entity_rules(self):
        # Rules using all explicit entity syntax should work exactly as before
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.is_adult == true => entity.discount = 0.1",
            "entity.age >= 18 => entity.is_adult = true",
        ])

        entity = {"age": 25, "is_adult": False, "discount": 0.0}
        engine.evaluate(entity)

        assert entity["is_adult"] is True
        assert entity["discount"] == 0.1


class TestEdgeCases:
    """Test edge cases for implicit entity syntax."""

    def test_empty_entity(self):
        engine = RuleEngine()
        engine.add_rules("name == none => ret 'no_name'")

        # Should handle missing attributes gracefully
        # Note: This will raise PathResolutionError if 'name' doesn't exist
        entity = {"name": None}
        result = engine.evaluate(entity)
        assert result == "no_name"

    def test_implicit_with_negative_indices(self):
        engine = RuleEngine()
        engine.add_rules("items[-1].value > 0 => last_positive = true")

        entity = {"items": [{"value": -1}, {"value": 10}], "last_positive": False}
        engine.evaluate(entity)
        assert entity["last_positive"] is True

    def test_implicit_with_computed_index(self):
        engine = RuleEngine()
        engine.add_rules("items[len(items) - 1].value > 0 => result = true")

        entity = {"items": [{"value": 1}, {"value": 2}], "result": False}
        engine.evaluate(entity)
        assert entity["result"] is True

    def test_implicit_boolean_expressions(self):
        engine = RuleEngine()
        engine.add_rules("active and premium => tier = 'gold'")

        entity = {"active": True, "premium": True, "tier": "basic"}
        engine.evaluate(entity)
        assert entity["tier"] == "gold"

    def test_implicit_arithmetic_expressions(self):
        engine = RuleEngine()
        engine.add_rules("price * quantity > 100 => bulk_order = true")

        entity = {"price": 25, "quantity": 5, "bulk_order": False}
        engine.evaluate(entity)
        assert entity["bulk_order"] is True

    def test_implicit_with_existence_operators(self):
        engine = RuleEngine()
        engine.add_rules("name exists => has_name = true")

        entity = {"name": "John", "has_name": False}
        engine.evaluate(entity)
        assert entity["has_name"] is True

    def test_implicit_with_is_empty(self):
        engine = RuleEngine()
        engine.add_rules("items is_empty => empty_cart = true")

        entity = {"items": [], "empty_cart": False}
        engine.evaluate(entity)
        assert entity["empty_cart"] is True

    def test_single_letter_attributes(self):
        engine = RuleEngine()
        engine.add_rules("x > 0 and y > 0 => z = x + y")

        entity = {"x": 5, "y": 3, "z": 0}
        engine.evaluate(entity)
        assert entity["z"] == 8

    def test_attributes_with_underscores(self):
        engine = RuleEngine()
        engine.add_rules("first_name != '' => full_name = first_name")

        entity = {"first_name": "John", "full_name": ""}
        engine.evaluate(entity)
        assert entity["full_name"] == "John"
