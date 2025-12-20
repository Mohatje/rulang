"""Tests for the dependency graph."""

import pytest
import warnings

from rule_interpreter.visitor import parse_rule
from rule_interpreter.dependency_graph import DependencyGraph
from rule_interpreter.workflows import Workflow
from rule_interpreter.exceptions import CyclicDependencyWarning


class TestDependencyDetection:
    """Test dependency detection between rules."""

    def test_no_dependencies(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.a > 0 => entity.b = 1")
        rule2 = parse_rule("entity.c > 0 => entity.d = 1")

        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.analyze()

        # No overlap between reads and writes
        assert len(graph.edges) == 0

    def test_simple_dependency(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.a > 0 => entity.b = 1")  # writes b
        rule2 = parse_rule("entity.b > 0 => entity.c = 1")  # reads b

        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.analyze()

        # Rule 1 writes b, Rule 2 reads b
        # So Rule 2 depends on Rule 1 (edge from 0 to 1)
        assert 1 in graph.edges.get(0, set())

    def test_chain_dependency(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.a > 0 => entity.b = 1")
        rule2 = parse_rule("entity.b > 0 => entity.c = 1")
        rule3 = parse_rule("entity.c > 0 => entity.d = 1")

        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.add_rule(rule3)

        order = graph.get_execution_order()

        # Order should be 0 -> 1 -> 2
        assert order.index(0) < order.index(1)
        assert order.index(1) < order.index(2)

    def test_multiple_dependencies(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.x > 0 => entity.a = 1")  # writes a
        rule2 = parse_rule("entity.y > 0 => entity.b = 1")  # writes b
        rule3 = parse_rule("entity.a > 0 and entity.b > 0 => entity.c = 1")  # reads a and b

        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.add_rule(rule3)

        order = graph.get_execution_order()

        # Rule 3 depends on both Rule 1 and Rule 2
        assert order.index(0) < order.index(2)
        assert order.index(1) < order.index(2)


class TestWorkflowDependencies:
    """Test workflow dependency merging."""

    def test_workflow_reads_merged(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.x > 0 => entity.input = 1")  # writes input
        rule2 = parse_rule("entity.ready == true => workflow('process')")  # calls process

        # Process workflow reads entity.input
        workflows = {
            "process": Workflow(fn=lambda e: None, reads=["entity.input"], writes=[])
        }

        graph.add_rule(rule1)
        graph.add_rule(rule2, workflows)
        graph.analyze()

        # Rule 2's workflow reads input, Rule 1 writes input
        # So Rule 2 depends on Rule 1
        assert 1 in graph.edges.get(0, set())

    def test_workflow_writes_merged(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.ready == true => workflow('calculate')")  # calls calculate
        rule2 = parse_rule("entity.result > 0 => entity.done = true")  # reads result

        # Calculate workflow writes entity.result
        workflows = {
            "calculate": Workflow(fn=lambda e: None, reads=[], writes=["entity.result"])
        }

        graph.add_rule(rule1, workflows)
        graph.add_rule(rule2)
        graph.analyze()

        # Rule 1's workflow writes result, Rule 2 reads result
        # So Rule 2 depends on Rule 1
        assert 1 in graph.edges.get(0, set())


class TestCycleDetection:
    """Test cycle detection and handling."""

    def test_simple_cycle_detected(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.a > 0 => entity.b = 1")  # reads a, writes b
        rule2 = parse_rule("entity.b > 0 => entity.a = 1")  # reads b, writes a

        graph.add_rule(rule1)
        graph.add_rule(rule2)

        cycles = graph.detect_cycles()
        assert len(cycles) > 0

    def test_cycle_broken_with_warning(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.a > 0 => entity.b = 1")
        rule2 = parse_rule("entity.b > 0 => entity.a = 1")

        graph.add_rule(rule1)
        graph.add_rule(rule2)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            order = graph.get_execution_order()

            # Should have warned about cycle
            cycle_warnings = [x for x in w if issubclass(x.category, CyclicDependencyWarning)]
            assert len(cycle_warnings) > 0

        # Should still return a valid order
        assert len(order) == 2
        assert set(order) == {0, 1}

    def test_no_cycle_no_warning(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.a > 0 => entity.b = 1")
        rule2 = parse_rule("entity.b > 0 => entity.c = 1")

        graph.add_rule(rule1)
        graph.add_rule(rule2)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            graph.get_execution_order()

            cycle_warnings = [x for x in w if issubclass(x.category, CyclicDependencyWarning)]
            assert len(cycle_warnings) == 0


class TestExecutionOrder:
    """Test topological sort for execution order."""

    def test_independent_rules_preserve_order(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.a > 0 => entity.x = 1")
        rule2 = parse_rule("entity.b > 0 => entity.y = 1")
        rule3 = parse_rule("entity.c > 0 => entity.z = 1")

        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.add_rule(rule3)

        order = graph.get_execution_order()

        # No dependencies, so original order should be preserved (0, 1, 2)
        assert order == [0, 1, 2]

    def test_reverse_dependency_order(self):
        graph = DependencyGraph()

        # Add rules in reverse dependency order
        rule1 = parse_rule("entity.c > 0 => entity.d = 1")  # depends on c
        rule2 = parse_rule("entity.b > 0 => entity.c = 1")  # depends on b, writes c
        rule3 = parse_rule("entity.a > 0 => entity.b = 1")  # writes b

        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.add_rule(rule3)

        order = graph.get_execution_order()

        # Execution order should be 2 -> 1 -> 0
        assert order.index(2) < order.index(1)
        assert order.index(1) < order.index(0)


class TestPathMatching:
    """Test path matching for dependency detection."""

    def test_exact_path_match(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.a > 0 => entity.user.name = 'test'")
        rule2 = parse_rule("entity.user.name == 'test' => entity.b = 1")

        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.analyze()

        # Rule 2 reads user.name, Rule 1 writes user.name
        assert 1 in graph.edges.get(0, set())

    def test_prefix_path_match(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.a > 0 => entity.user = none")  # writes entity.user
        rule2 = parse_rule("entity.user.name == 'test' => entity.b = 1")  # reads entity.user.name

        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.analyze()

        # Writing to entity.user affects entity.user.name
        assert 1 in graph.edges.get(0, set())


class TestGraphAPI:
    """Test dependency graph API methods."""

    def test_get_dependencies(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.a > 0 => entity.b = 1")
        rule2 = parse_rule("entity.b > 0 => entity.c = 1")

        graph.add_rule(rule1)
        graph.add_rule(rule2)

        deps = graph.get_dependencies(1)
        assert 0 in deps

    def test_get_dependents(self):
        graph = DependencyGraph()

        rule1 = parse_rule("entity.a > 0 => entity.b = 1")
        rule2 = parse_rule("entity.b > 0 => entity.c = 1")

        graph.add_rule(rule1)
        graph.add_rule(rule2)

        dependents = graph.get_dependents(0)
        assert 1 in dependents

    def test_len(self):
        graph = DependencyGraph()
        assert len(graph) == 0

        graph.add_rule(parse_rule("entity.a > 0 => entity.b = 1"))
        assert len(graph) == 1

        graph.add_rule(parse_rule("entity.c > 0 => entity.d = 1"))
        assert len(graph) == 2

