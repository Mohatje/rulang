"""Tests for the RuleEngine."""

import pytest
import warnings
from dataclasses import dataclass

from rule_interpreter import RuleEngine, Workflow, workflow
from rule_interpreter.exceptions import (
    RuleSyntaxError,
    PathResolutionError,
    CyclicDependencyWarning,
)
from rule_interpreter.workflows import clear_workflow_registry


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear workflow registry before each test."""
    clear_workflow_registry()
    yield
    clear_workflow_registry()


class TestBasicUsage:
    """Test basic RuleEngine usage."""

    def test_single_rule(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 10 => ret true")

        result = engine.evaluate({"value": 15})
        assert result is True

        result = engine.evaluate({"value": 5})
        assert result is None

    def test_multiple_rules_as_list(self):
        engine = RuleEngine()
        engine.add_rules([
            "entity.value > 100 => ret 'high'",
            "entity.value > 50 => ret 'medium'",
            "entity.value > 0 => ret 'low'",
        ])

        # First match mode (default) - returns first matching rule
        result = engine.evaluate({"value": 150})
        assert result == "high"

    def test_rule_mutation(self):
        engine = RuleEngine()
        engine.add_rules("entity.status == 'pending' => entity.status = 'processed'")

        entity = {"status": "pending"}
        engine.evaluate(entity)
        assert entity["status"] == "processed"

    def test_no_match_returns_none(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 100 => ret true")

        result = engine.evaluate({"value": 50})
        assert result is None


class TestEvaluationModes:
    """Test different evaluation modes."""

    def test_first_match_mode(self):
        engine = RuleEngine(mode="first_match")
        engine.add_rules([
            "entity.value > 0 => entity.a = 1",
            "entity.value > 0 => entity.b = 2",
        ])

        entity = {"value": 10, "a": 0, "b": 0}
        engine.evaluate(entity)

        # In first_match mode, only first rule executes
        assert entity["a"] == 1
        assert entity["b"] == 0

    def test_all_match_mode(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.value > 0 => entity.a = 1",
            "entity.value > 0 => entity.b = 2",
        ])

        entity = {"value": 10, "a": 0, "b": 0}
        engine.evaluate(entity)

        # In all_match mode, all matching rules execute
        assert entity["a"] == 1
        assert entity["b"] == 2


class TestDependencyOrdering:
    """Test dependency-based execution ordering."""

    def test_dependent_rules_ordered_correctly(self):
        engine = RuleEngine(mode="all_match")

        # Add rules in "wrong" order - rule 2 depends on rule 1's write
        engine.add_rules([
            "entity.is_adult == true => entity.discount = 0.1",  # Rule 0: reads is_adult, writes discount
            "entity.age >= 18 => entity.is_adult = true",  # Rule 1: reads age, writes is_adult
        ])

        entity = {"age": 25, "is_adult": False, "discount": 0.0}
        engine.evaluate(entity)

        # Despite being added second, the age rule should execute first
        assert entity["is_adult"] is True
        assert entity["discount"] == 0.1

    def test_execution_order_api(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.b > 0 => entity.c = 1",  # Rule 0: reads b, writes c
            "entity.a > 0 => entity.b = 1",  # Rule 1: reads a, writes b
        ])

        order = engine.get_execution_order()
        # Rule 1 should come before Rule 0 (Rule 0 depends on Rule 1)
        assert order.index(1) < order.index(0)


class TestDependencyGraph:
    """Test dependency graph functionality."""

    def test_get_dependency_graph(self):
        engine = RuleEngine()
        engine.add_rules([
            "entity.a > 0 => entity.b = 1",
            "entity.b > 0 => entity.c = 1",
        ])

        graph = engine.get_dependency_graph()
        # Rule 0 writes b, Rule 1 reads b, so Rule 1 depends on Rule 0
        assert 1 in graph.get(0, set())

    def test_rule_analysis(self):
        engine = RuleEngine()
        engine.add_rules("entity.a > 0 and entity.b < 10 => entity.c = entity.a + entity.b")

        analysis = engine.get_rule_analysis(0)
        assert len(analysis["reads"]) > 0
        assert len(analysis["writes"]) > 0


class TestCyclicDependencies:
    """Test cyclic dependency detection and handling."""

    def test_cycle_warning(self):
        engine = RuleEngine(mode="all_match")

        # Create a cycle: A writes B, B writes A
        engine.add_rules([
            "entity.a > 0 => entity.b = 1",
            "entity.b > 0 => entity.a = 1",
        ])

        entity = {"a": 1, "b": 1}

        # Should warn about cycle but still execute
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            engine.evaluate(entity)
            # Check if CyclicDependencyWarning was issued
            cycle_warnings = [x for x in w if issubclass(x.category, CyclicDependencyWarning)]
            assert len(cycle_warnings) > 0


class TestWorkflows:
    """Test workflow integration."""

    def test_workflow_dict(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => workflow('double')")

        def double(e):
            e["value"] *= 2

        entity = {"value": 10}
        engine.evaluate(entity, workflows={"double": double})
        assert entity["value"] == 20

    def test_workflow_wrapper_class(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.ready == true => workflow('calculate')",
            "entity.result > 0 => entity.status = 'done'",
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

        # Workflow dependencies should ensure correct ordering
        assert entity["result"] == 20
        assert entity["status"] == "done"

    def test_workflow_decorator(self):
        @RuleEngine.workflow("process", reads=["entity.input"], writes=["entity.output"])
        def process_fn(entity):
            entity["output"] = entity["input"].upper()

        engine = RuleEngine()
        engine.add_rules("entity.input != '' => workflow('process')")

        entity = {"input": "hello", "output": ""}
        engine.evaluate(entity)
        assert entity["output"] == "HELLO"


class TestEntityTypes:
    """Test different entity types."""

    def test_dict_entity(self):
        engine = RuleEngine()
        engine.add_rules("entity.name == 'test' => entity.processed = true")

        entity = {"name": "test", "processed": False}
        engine.evaluate(entity)
        assert entity["processed"] is True

    def test_dataclass_entity(self):
        @dataclass
        class Entity:
            name: str
            processed: bool = False

        engine = RuleEngine()
        engine.add_rules("entity.name == 'test' => entity.processed = true")

        entity = Entity(name="test")
        engine.evaluate(entity)
        assert entity.processed is True

    def test_nested_dict(self):
        engine = RuleEngine()
        engine.add_rules("entity.user.age >= 18 => entity.user.is_adult = true")

        entity = {"user": {"age": 25, "is_adult": False}}
        engine.evaluate(entity)
        assert entity["user"]["is_adult"] is True


class TestErrorHandling:
    """Test error handling."""

    def test_syntax_error(self):
        engine = RuleEngine()
        with pytest.raises(RuleSyntaxError):
            engine.add_rules("invalid rule syntax")

    def test_path_resolution_error(self):
        engine = RuleEngine()
        engine.add_rules("entity.missing.path > 0 => ret true")

        with pytest.raises(PathResolutionError):
            engine.evaluate({"name": "test"})


class TestEngineManagement:
    """Test engine management methods."""

    def test_get_rules(self):
        engine = RuleEngine()
        rules = [
            "entity.a > 0 => ret true",
            "entity.b > 0 => ret false",
        ]
        engine.add_rules(rules)

        assert engine.get_rules() == rules

    def test_clear(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => ret true")
        assert len(engine) == 1

        engine.clear()
        assert len(engine) == 0

    def test_len(self):
        engine = RuleEngine()
        assert len(engine) == 0

        engine.add_rules([
            "entity.a > 0 => ret true",
            "entity.b > 0 => ret true",
        ])
        assert len(engine) == 2

