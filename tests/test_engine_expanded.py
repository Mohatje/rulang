"""Comprehensive expanded tests for the RuleEngine."""

import pytest
import warnings
from dataclasses import dataclass

from rule_interpreter import RuleEngine, Workflow
from rule_interpreter.exceptions import (
    RuleSyntaxError,
    PathResolutionError,
    WorkflowNotFoundError,
)
from rule_interpreter.workflows import clear_workflow_registry


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear workflow registry before each test."""
    clear_workflow_registry()
    yield
    clear_workflow_registry()


class TestRuleManagementExpanded:
    """Expanded tests for rule management."""

    def test_add_single_rule(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => ret true")
        assert len(engine) == 1

    def test_add_multiple_rules_list(self):
        engine = RuleEngine()
        engine.add_rules([
            "entity.a > 0 => ret true",
            "entity.b > 0 => ret true",
            "entity.c > 0 => ret true",
        ])
        assert len(engine) == 3

    def test_add_empty_list(self):
        engine = RuleEngine()
        engine.add_rules([])
        assert len(engine) == 0

    def test_add_duplicate_rules(self):
        engine = RuleEngine()
        rule = "entity.value > 0 => ret true"
        engine.add_rules(rule)
        engine.add_rules(rule)
        assert len(engine) == 2  # Duplicates are allowed

    def test_add_rules_same_condition(self):
        engine = RuleEngine()
        engine.add_rules([
            "entity.value > 0 => entity.a = 1",
            "entity.value > 0 => entity.b = 2",
        ])
        assert len(engine) == 2

    def test_get_all_rules(self):
        engine = RuleEngine()
        rules = [
            "entity.a > 0 => ret true",
            "entity.b > 0 => ret false",
        ]
        engine.add_rules(rules)
        assert engine.get_rules() == rules

    def test_get_rule_analysis(self):
        engine = RuleEngine()
        engine.add_rules("entity.a > 0 and entity.b < 10 => entity.c = entity.a + entity.b")
        
        analysis = engine.get_rule_analysis(0)
        assert "rule" in analysis
        assert "reads" in analysis
        assert "writes" in analysis
        assert "workflow_calls" in analysis

    def test_get_rule_analysis_invalid_index(self):
        engine = RuleEngine()
        engine.add_rules("entity.a > 0 => ret true")
        
        with pytest.raises(IndexError):
            engine.get_rule_analysis(10)

    def test_clear_all_rules(self):
        engine = RuleEngine()
        engine.add_rules([
            "entity.a > 0 => ret true",
            "entity.b > 0 => ret true",
        ])
        assert len(engine) == 2
        
        engine.clear()
        assert len(engine) == 0

    def test_clear_empty_engine(self):
        engine = RuleEngine()
        engine.clear()
        assert len(engine) == 0

    def test_clear_and_readd(self):
        engine = RuleEngine()
        engine.add_rules("entity.a > 0 => ret true")
        engine.clear()
        engine.add_rules("entity.b > 0 => ret true")
        assert len(engine) == 1


class TestEvaluationModesExpanded:
    """Expanded tests for evaluation modes."""

    @pytest.mark.parametrize("mode", ["first_match", "all_match"])
    def test_evaluation_modes(self, mode):
        engine = RuleEngine(mode=mode)
        engine.add_rules([
            "entity.value > 0 => entity.a = 1",
            "entity.value > 0 => entity.b = 2",
        ])
        
        entity = {"value": 10, "a": 0, "b": 0}
        engine.evaluate(entity)
        
        if mode == "first_match":
            assert entity["a"] == 1
            assert entity["b"] == 0
        else:
            assert entity["a"] == 1
            assert entity["b"] == 2

    def test_first_match_stops_after_first(self):
        engine = RuleEngine(mode="first_match")
        engine.add_rules([
            "entity.value > 100 => ret 'high'",
            "entity.value > 50 => ret 'medium'",
            "entity.value > 0 => ret 'low'",
        ])
        
        result = engine.evaluate({"value": 150})
        assert result == "high"

    def test_all_match_executes_all(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.value > 0 => entity.a = 1",
            "entity.value > 0 => entity.b = 2",
            "entity.value > 0 => entity.c = 3",
        ])
        
        entity = {"value": 10, "a": 0, "b": 0, "c": 0}
        engine.evaluate(entity)
        
        assert entity["a"] == 1
        assert entity["b"] == 2
        assert entity["c"] == 3

    def test_all_match_some_rules_match(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.value > 100 => entity.a = 1",
            "entity.value > 50 => entity.b = 2",
            "entity.value > 0 => entity.c = 3",
        ])
        
        entity = {"value": 75, "a": 0, "b": 0, "c": 0}
        engine.evaluate(entity)
        
        assert entity["a"] == 0  # Doesn't match
        assert entity["b"] == 2  # Matches
        assert entity["c"] == 3  # Matches

    def test_all_match_no_rules_match(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.value > 100 => entity.a = 1",
            "entity.value > 50 => entity.b = 2",
        ])
        
        entity = {"value": 10, "a": 0, "b": 0}
        result = engine.evaluate(entity)
        
        assert entity["a"] == 0
        assert entity["b"] == 0
        assert result is None

    def test_mode_affects_execution_order(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.b > 0 => entity.c = 1",  # Depends on b
            "entity.a > 0 => entity.b = 1",  # Writes b
        ])
        
        entity = {"a": 10, "b": 0, "c": 0}
        engine.evaluate(entity)
        
        # Should execute in dependency order regardless of mode
        assert entity["b"] == 1
        assert entity["c"] == 1


class TestEntityEvaluationExpanded:
    """Expanded tests for entity evaluation."""

    def test_dict_entity_simple(self):
        engine = RuleEngine()
        engine.add_rules("entity.name == 'test' => entity.processed = true")
        
        entity = {"name": "test", "processed": False}
        engine.evaluate(entity)
        assert entity["processed"] is True

    def test_dict_entity_nested(self):
        engine = RuleEngine()
        engine.add_rules("entity.user.age >= 18 => entity.user.is_adult = true")
        
        entity = {"user": {"age": 25, "is_adult": False}}
        engine.evaluate(entity)
        assert entity["user"]["is_adult"] is True

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

    def test_custom_class_entity(self):
        class Entity:
            def __init__(self):
                self.name = "test"
                self.processed = False
        
        engine = RuleEngine()
        engine.add_rules("entity.name == 'test' => entity.processed = true")
        
        entity = Entity()
        engine.evaluate(entity)
        assert entity.processed is True

    def test_single_mutation(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => entity.result = entity.value * 2")
        
        entity = {"value": 10, "result": 0}
        engine.evaluate(entity)
        assert entity["result"] == 20

    def test_multiple_mutations(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.value > 0 => entity.a = 1",
            "entity.value > 0 => entity.b = 2",
            "entity.value > 0 => entity.c = 3",
        ])
        
        entity = {"value": 10, "a": 0, "b": 0, "c": 0}
        engine.evaluate(entity)
        
        assert entity["a"] == 1
        assert entity["b"] == 2
        assert entity["c"] == 3

    def test_nested_mutations(self):
        engine = RuleEngine()
        engine.add_rules("entity.ready == true => entity.user.profile.status = 'active'")
        
        entity = {"ready": True, "user": {"profile": {"status": "inactive"}}}
        engine.evaluate(entity)
        assert entity["user"]["profile"]["status"] == "active"

    def test_mutations_in_dependency_order(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.b > 0 => entity.c = 1",  # Depends on b
            "entity.a > 0 => entity.b = 1",  # Writes b
        ])
        
        entity = {"a": 10, "b": 0, "c": 0}
        engine.evaluate(entity)
        
        # Should execute in correct order
        assert entity["b"] == 1
        assert entity["c"] == 1

    def test_explicit_return_value(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => ret entity.value * 2")
        
        result = engine.evaluate({"value": 10})
        assert result == 20

    def test_default_return_true(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => entity.processed = true")
        
        result = engine.evaluate({"value": 10})
        assert result is True

    def test_no_match_returns_none(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 100 => ret true")
        
        result = engine.evaluate({"value": 50})
        assert result is None

    def test_all_match_last_return(self):
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.value > 0 => entity.a = 1; ret 'first'",
            "entity.value > 0 => entity.b = 2; ret 'second'",
        ])
        
        result = engine.evaluate({"value": 10, "a": 0, "b": 0})
        assert result == "second"  # Last return value

    def test_path_error_propagates(self):
        engine = RuleEngine()
        engine.add_rules("entity.missing.path > 0 => ret true")
        
        with pytest.raises(PathResolutionError):
            engine.evaluate({"name": "test"})

    def test_workflow_error_propagates(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => workflow('missing')")
        
        with pytest.raises(WorkflowNotFoundError):
            engine.evaluate({"value": 10})


class TestWorkflowIntegrationExpanded:
    """Expanded tests for workflow integration."""

    def test_dict_workflows(self):
        def process(e):
            e["processed"] = True
        
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => workflow('process')")
        
        entity = {"value": 10, "processed": False}
        engine.evaluate(entity, workflows={"process": process})
        assert entity["processed"] is True

    def test_workflow_wrapper_class(self):
        def calculate(e):
            e["result"] = e["value"] * 2
        
        workflows = {
            "calculate": Workflow(
                fn=calculate,
                reads=["entity.value"],
                writes=["entity.result"]
            )
        }
        
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => workflow('calculate')")
        
        entity = {"value": 10, "result": 0}
        engine.evaluate(entity, workflows=workflows)
        assert entity["result"] == 20

    def test_mixed_workflow_types(self):
        def process1(e):
            e["a"] = 1
        
        def process2(e):
            e["b"] = 2
        
        workflows = {
            "process1": process1,
            "process2": Workflow(fn=process2, reads=[], writes=["entity.b"]),
        }
        
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.ready == true => workflow('process1')",
            "entity.ready == true => workflow('process2')",
        ])
        
        entity = {"ready": True, "a": 0, "b": 0}
        engine.evaluate(entity, workflows=workflows)
        assert entity["a"] == 1
        assert entity["b"] == 2

    def test_empty_workflows_dict(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => entity.processed = true")
        
        entity = {"value": 10, "processed": False}
        engine.evaluate(entity, workflows={})
        assert entity["processed"] is True

    def test_workflow_execution_order(self):
        called_order = []
        
        def step1(e):
            called_order.append(1)
            e["step1"] = True
        
        def step2(e):
            called_order.append(2)
            e["step2"] = True
        
        workflows = {
            "step1": Workflow(fn=step1, reads=[], writes=["entity.step1"]),
            "step2": Workflow(fn=step2, reads=["entity.step1"], writes=["entity.step2"]),
        }
        
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.ready == true => workflow('step2')",
            "entity.ready == true => workflow('step1')",
        ])
        
        entity = {"ready": True, "step1": False, "step2": False}
        engine.evaluate(entity, workflows=workflows)
        
        # step1 should execute before step2 due to dependencies
        assert called_order == [1, 2]
        assert entity["step1"] is True
        assert entity["step2"] is True

    def test_workflow_dependencies_affect_order(self):
        def calculate(e):
            e["result"] = e["input"] * 2
        
        def use_result(e):
            e["final"] = e["result"] + 10
        
        workflows = {
            "calculate": Workflow(fn=calculate, reads=["entity.input"], writes=["entity.result"]),
            "use_result": Workflow(fn=use_result, reads=["entity.result"], writes=["entity.final"]),
        }
        
        engine = RuleEngine(mode="all_match")
        engine.add_rules([
            "entity.ready == true => workflow('use_result')",
            "entity.ready == true => workflow('calculate')",
        ])
        
        entity = {"ready": True, "input": 10, "result": 0, "final": 0}
        engine.evaluate(entity, workflows=workflows)
        
        # calculate should execute before use_result
        assert entity["result"] == 20
        assert entity["final"] == 30


class TestDependencyGraphAPIExpanded:
    """Expanded tests for dependency graph API."""

    def test_get_dependency_graph(self):
        engine = RuleEngine()
        engine.add_rules([
            "entity.a > 0 => entity.b = 1",
            "entity.b > 0 => entity.c = 1",
        ])
        
        graph = engine.get_dependency_graph()
        
        # Rule 1 depends on Rule 0
        assert 1 in graph.get(0, set())

    def test_get_execution_order(self):
        engine = RuleEngine()
        engine.add_rules([
            "entity.b > 0 => entity.c = 1",
            "entity.a > 0 => entity.b = 1",
        ])
        
        order = engine.get_execution_order()
        
        # Rule 1 should come before Rule 0
        assert order.index(1) < order.index(0)

    def test_execution_order_respects_dependencies(self):
        engine = RuleEngine()
        engine.add_rules([
            "entity.c > 0 => entity.d = 1",  # Depends on c
            "entity.b > 0 => entity.c = 1",  # Depends on b
            "entity.a > 0 => entity.b = 1",  # Writes b
        ])
        
        order = engine.get_execution_order()
        
        assert order.index(2) < order.index(1)
        assert order.index(1) < order.index(0)


class TestEdgeCasesExpanded:
    """Expanded tests for edge cases."""

    def test_empty_engine(self):
        engine = RuleEngine()
        result = engine.evaluate({"value": 10})
        assert result is None

    def test_very_large_rule_set(self):
        engine = RuleEngine()
        rules = [f"entity.field{i} > 0 => entity.result{i} = 1" for i in range(50)]
        engine.add_rules(rules)
        assert len(engine) == 50

    def test_very_complex_rule(self):
        engine = RuleEngine()
        complex_rule = (
            "entity.a > 0 and entity.b > 0 and entity.c > 0 and entity.d > 0 => "
            "entity.result = (entity.a + entity.b) * (entity.c - entity.d) / entity.e; "
            "ret entity.result"
        )
        engine.add_rules(complex_rule)
        
        entity = {"a": 10, "b": 5, "c": 8, "d": 3, "e": 2, "result": 0}
        result = engine.evaluate(entity)
        assert result == 37.5

    def test_entity_with_none_values(self):
        engine = RuleEngine()
        engine.add_rules("entity.value == none => entity.processed = true")
        
        entity = {"value": None, "processed": False}
        engine.evaluate(entity)
        assert entity["processed"] is True

    def test_entity_with_empty_dict(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => entity.result = 1")
        
        entity = {}
        # Should fail because value doesn't exist
        with pytest.raises(PathResolutionError):
            engine.evaluate(entity)

    def test_multiple_evaluations_same_engine(self):
        engine = RuleEngine()
        engine.add_rules("entity.value > 0 => entity.processed = true")
        
        entity1 = {"value": 10, "processed": False}
        entity2 = {"value": 20, "processed": False}
        
        engine.evaluate(entity1)
        engine.evaluate(entity2)
        
        assert entity1["processed"] is True
        assert entity2["processed"] is True

    def test_entity_name_custom(self):
        engine = RuleEngine()
        engine.add_rules("obj.value > 0 => obj.processed = true")
        
        entity = {"value": 10, "processed": False}
        engine.evaluate(entity, entity_name="obj")
        assert entity["processed"] is True

