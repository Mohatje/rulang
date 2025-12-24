"""Comprehensive expanded tests for dependency graph."""

import pytest
import warnings

from rule_interpreter.visitor import parse_rule
from rule_interpreter.dependency_graph import DependencyGraph
from rule_interpreter.workflows import Workflow
from rule_interpreter.exceptions import CyclicDependencyWarning


class TestDependencyDetectionExpanded:
    """Expanded tests for dependency detection."""

    def test_one_to_many_dependencies(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")  # writes b
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")  # reads b, writes c
        rule2 = parse_rule("entity.b > 0 => entity.d = 1")  # reads b, writes d
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.analyze()
        
        # Both rule1 and rule2 depend on rule0
        assert 1 in graph.edges.get(0, set())
        assert 2 in graph.edges.get(0, set())

    def test_many_to_one_dependency(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")  # writes b
        rule1 = parse_rule("entity.c > 0 => entity.b = 2")  # writes b
        rule2 = parse_rule("entity.b > 0 => entity.d = 1")  # reads b
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.analyze()
        
        # Rule2 depends on both rule0 and rule1
        assert 2 in graph.edges.get(0, set())
        assert 2 in graph.edges.get(1, set())

    def test_diamond_dependency(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")  # writes b
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")  # reads b, writes c
        rule2 = parse_rule("entity.b > 0 => entity.d = 1")  # reads b, writes d
        rule3 = parse_rule("entity.c > 0 and entity.d > 0 => entity.e = 1")  # reads c, d
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.add_rule(rule3)
        
        order = graph.get_execution_order()
        
        # Rule0 must come first
        assert order.index(0) < order.index(1)
        assert order.index(0) < order.index(2)
        # Rule1 and rule2 must come before rule3
        assert order.index(1) < order.index(3)
        assert order.index(2) < order.index(3)

    def test_indirect_dependency(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        rule2 = parse_rule("entity.c > 0 => entity.d = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        
        order = graph.get_execution_order()
        
        # Must be in order 0 -> 1 -> 2
        assert order.index(0) < order.index(1)
        assert order.index(1) < order.index(2)

    def test_no_dependencies_independent_rules(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.c > 0 => entity.d = 1")
        rule2 = parse_rule("entity.e > 0 => entity.f = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        
        graph.analyze()
        
        # No edges
        assert len(graph.edges) == 0

    def test_self_modification_not_cycle(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.a = entity.a + 1")  # reads and writes a
        
        graph.add_rule(rule0)
        
        cycles = graph.detect_cycles()
        # Self-modification (read+write same attribute) is not a cycle between rules
        # A cycle requires multiple rules
        assert len(cycles) == 0

    def test_multiple_independent_chains(self):
        graph = DependencyGraph()
        
        # Chain 1
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        
        # Chain 2
        rule2 = parse_rule("entity.x > 0 => entity.y = 1")
        rule3 = parse_rule("entity.y > 0 => entity.z = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.add_rule(rule3)
        
        order = graph.get_execution_order()
        
        # Each chain should be ordered correctly
        assert order.index(0) < order.index(1)
        assert order.index(2) < order.index(3)


class TestPathMatchingExpanded:
    """Expanded tests for path matching in dependencies."""

    def test_exact_path_match(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.user.name = 'test'")
        rule1 = parse_rule("entity.user.name == 'test' => entity.b = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.analyze()
        
        # Rule1 reads what rule0 writes
        assert 1 in graph.edges.get(0, set())

    def test_prefix_path_match(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.user = none")  # writes entity.user
        rule1 = parse_rule("entity.user.name == 'test' => entity.b = 1")  # reads entity.user.name
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.analyze()
        
        # Writing to parent affects child
        assert 1 in graph.edges.get(0, set())

    def test_wildcard_index_match(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.items[0].value = 1")  # writes items[*].value
        rule1 = parse_rule("entity.items[1].value > 0 => entity.b = 1")  # reads items[*].value
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.analyze()
        
        # Wildcard matching should detect dependency
        assert 1 in graph.edges.get(0, set())

    def test_nested_path_match(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.user.profile.name = 'test'")
        rule1 = parse_rule("entity.user.profile.name == 'test' => entity.b = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.analyze()
        
        assert 1 in graph.edges.get(0, set())

    def test_no_match_different_paths(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.x = 1")
        rule1 = parse_rule("entity.y > 0 => entity.z = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.analyze()
        
        # No dependency
        assert 1 not in graph.edges.get(0, set())
        assert 0 not in graph.edges.get(1, set())


class TestCycleDetectionExpanded:
    """Expanded tests for cycle detection."""

    def test_two_rule_cycle(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.a = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        
        cycles = graph.detect_cycles()
        assert len(cycles) > 0

    def test_three_rule_cycle(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        rule2 = parse_rule("entity.c > 0 => entity.a = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        
        cycles = graph.detect_cycles()
        assert len(cycles) > 0

    def test_four_rule_cycle(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        rule2 = parse_rule("entity.c > 0 => entity.d = 1")
        rule3 = parse_rule("entity.d > 0 => entity.a = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.add_rule(rule3)
        
        cycles = graph.detect_cycles()
        assert len(cycles) > 0

    def test_multiple_cycles(self):
        graph = DependencyGraph()
        
        # Cycle 1: 0 -> 1 -> 0
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.a = 1")
        
        # Cycle 2: 2 -> 3 -> 2
        rule2 = parse_rule("entity.c > 0 => entity.d = 1")
        rule3 = parse_rule("entity.d > 0 => entity.c = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.add_rule(rule3)
        
        cycles = graph.detect_cycles()
        assert len(cycles) >= 2

    def test_nested_cycles(self):
        graph = DependencyGraph()
        
        # Outer cycle: 0 -> 1 -> 2 -> 0
        # Inner cycle: 1 -> 3 -> 1
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        rule2 = parse_rule("entity.c > 0 => entity.a = 1")
        rule3 = parse_rule("entity.b > 0 => entity.b = 2")  # Self-modification
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.add_rule(rule3)
        
        cycles = graph.detect_cycles()
        assert len(cycles) > 0

    def test_cycle_with_branch(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        rule2 = parse_rule("entity.b > 0 => entity.d = 1")
        rule3 = parse_rule("entity.c > 0 and entity.d > 0 => entity.a = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.add_rule(rule3)
        
        cycles = graph.detect_cycles()
        assert len(cycles) > 0

    def test_cycle_breaking_warning(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.a = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            order = graph.get_execution_order()
            
            cycle_warnings = [x for x in w if issubclass(x.category, CyclicDependencyWarning)]
            assert len(cycle_warnings) > 0

    def test_cycle_breaking_deterministic(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.a = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        
        # Run multiple times - should break cycle consistently
        order1 = graph.get_execution_order()
        order2 = graph.get_execution_order()
        
        assert order1 == order2


class TestTopologicalSortExpanded:
    """Expanded tests for topological sorting."""

    def test_linear_chain(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        rule2 = parse_rule("entity.c > 0 => entity.d = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        
        order = graph.get_execution_order()
        
        assert order == [0, 1, 2]

    def test_multiple_roots(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.c > 0 => entity.d = 1")
        rule2 = parse_rule("entity.b > 0 and entity.d > 0 => entity.e = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        
        order = graph.get_execution_order()
        
        # Rule0 and rule1 are roots, rule2 depends on both
        assert order.index(0) < order.index(2)
        assert order.index(1) < order.index(2)

    def test_multiple_leaves(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        rule2 = parse_rule("entity.b > 0 => entity.d = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        
        order = graph.get_execution_order()
        
        # Rule0 first, then rule1 and rule2 (order between them doesn't matter)
        assert order.index(0) < order.index(1)
        assert order.index(0) < order.index(2)

    def test_complex_dag(self):
        graph = DependencyGraph()
        
        #     0
        #   /   \
        #  1     2
        #   \   /
        #     3
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        rule2 = parse_rule("entity.b > 0 => entity.d = 1")
        rule3 = parse_rule("entity.c > 0 and entity.d > 0 => entity.e = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        graph.add_rule(rule3)
        
        order = graph.get_execution_order()
        
        assert order.index(0) < order.index(1)
        assert order.index(0) < order.index(2)
        assert order.index(1) < order.index(3)
        assert order.index(2) < order.index(3)

    def test_deterministic_order(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.c > 0 => entity.d = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        
        # Multiple calls should produce same order
        order1 = graph.get_execution_order()
        order2 = graph.get_execution_order()
        
        assert order1 == order2

    def test_tie_breaking_lowest_index(self):
        graph = DependencyGraph()
        
        # Two independent rules - should preserve insertion order
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.c > 0 => entity.d = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        
        order = graph.get_execution_order()
        
        # Should be [0, 1] (lowest index first)
        assert order == [0, 1]

    def test_empty_graph(self):
        graph = DependencyGraph()
        
        order = graph.get_execution_order()
        
        assert order == []

    def test_single_node(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        graph.add_rule(rule0)
        
        order = graph.get_execution_order()
        
        assert order == [0]

    def test_all_nodes_independent(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.c > 0 => entity.d = 1")
        rule2 = parse_rule("entity.e > 0 => entity.f = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        
        order = graph.get_execution_order()
        
        # Should preserve order
        assert order == [0, 1, 2]


class TestWorkflowDependenciesExpanded:
    """Expanded tests for workflow dependencies."""

    def test_workflow_reads_creates_dependency(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.input = 1")
        rule1 = parse_rule("entity.ready == true => workflow('process')")
        
        workflows = {
            "process": Workflow(
                fn=lambda e: None,
                reads=["entity.input"],
                writes=[]
            )
        }
        
        graph.add_rule(rule0)
        graph.add_rule(rule1, workflows)
        graph.analyze()
        
        # Rule1's workflow reads input, rule0 writes input
        assert 1 in graph.edges.get(0, set())

    def test_workflow_writes_creates_dependency(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.ready == true => workflow('calculate')")
        rule1 = parse_rule("entity.result > 0 => entity.done = true")
        
        workflows = {
            "calculate": Workflow(
                fn=lambda e: None,
                reads=[],
                writes=["entity.result"]
            )
        }
        
        graph.add_rule(rule0, workflows)
        graph.add_rule(rule1)
        graph.analyze()
        
        # Rule0's workflow writes result, rule1 reads result
        assert 1 in graph.edges.get(0, set())

    def test_workflow_both_reads_writes(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.input = 1")
        rule1 = parse_rule("entity.ready == true => workflow('process')")
        rule2 = parse_rule("entity.output > 0 => entity.done = true")
        
        workflows = {
            "process": Workflow(
                fn=lambda e: None,
                reads=["entity.input"],
                writes=["entity.output"]
            )
        }
        
        graph.add_rule(rule0)
        graph.add_rule(rule1, workflows)
        graph.add_rule(rule2)
        
        order = graph.get_execution_order()
        
        # Rule0 -> Rule1 -> Rule2
        assert order.index(0) < order.index(1)
        assert order.index(1) < order.index(2)

    def test_multiple_workflows_same_rule(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.input = 1")
        rule1 = parse_rule("entity.ready == true => workflow('wf1'); workflow('wf2')")
        
        workflows = {
            "wf1": Workflow(fn=lambda e: None, reads=["entity.input"], writes=[]),
            "wf2": Workflow(fn=lambda e: None, reads=["entity.input"], writes=[]),
        }
        
        graph.add_rule(rule0)
        graph.add_rule(rule1, workflows)
        graph.analyze()
        
        # Both workflows read input
        assert 1 in graph.edges.get(0, set())

    def test_workflow_dependency_chain(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => workflow('step1')")
        rule1 = parse_rule("entity.b > 0 => workflow('step2')")
        rule2 = parse_rule("entity.c > 0 => workflow('step3')")
        
        workflows = {
            "step1": Workflow(fn=lambda e: None, reads=[], writes=["entity.b"]),
            "step2": Workflow(fn=lambda e: None, reads=["entity.b"], writes=["entity.c"]),
            "step3": Workflow(fn=lambda e: None, reads=["entity.c"], writes=["entity.d"]),
        }
        
        graph.add_rule(rule0, workflows)
        graph.add_rule(rule1, workflows)
        graph.add_rule(rule2, workflows)
        
        order = graph.get_execution_order()
        
        # Must be 0 -> 1 -> 2
        assert order.index(0) < order.index(1)
        assert order.index(1) < order.index(2)


class TestGraphAPIExpanded:
    """Expanded tests for graph API methods."""

    def test_get_dependencies(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        rule2 = parse_rule("entity.b > 0 => entity.d = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        
        deps1 = graph.get_dependencies(1)
        deps2 = graph.get_dependencies(2)
        
        assert 0 in deps1
        assert 0 in deps2
        assert len(deps1) == 1
        assert len(deps2) == 1

    def test_get_dependents(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        rule2 = parse_rule("entity.b > 0 => entity.d = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        graph.add_rule(rule2)
        
        dependents = graph.get_dependents(0)
        
        assert 1 in dependents
        assert 2 in dependents
        assert len(dependents) == 2

    def test_get_graph(self):
        graph = DependencyGraph()
        
        rule0 = parse_rule("entity.a > 0 => entity.b = 1")
        rule1 = parse_rule("entity.b > 0 => entity.c = 1")
        
        graph.add_rule(rule0)
        graph.add_rule(rule1)
        
        graph_dict = graph.get_graph()
        
        assert 1 in graph_dict.get(0, set())
        assert isinstance(graph_dict, dict)

    def test_len(self):
        graph = DependencyGraph()
        assert len(graph) == 0
        
        graph.add_rule(parse_rule("entity.a > 0 => entity.b = 1"))
        assert len(graph) == 1
        
        graph.add_rule(parse_rule("entity.c > 0 => entity.d = 1"))
        assert len(graph) == 2

