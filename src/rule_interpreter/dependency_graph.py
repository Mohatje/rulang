"""
Dependency graph builder with cycle detection for business rules.

Analyzes read/write sets of rules to determine execution order.
"""

import warnings
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from rule_interpreter.exceptions import CyclicDependencyWarning

if TYPE_CHECKING:
    from rule_interpreter.visitor import ParsedRule
    from rule_interpreter.workflows import Workflow


@dataclass
class RuleNode:
    """Represents a rule in the dependency graph."""

    index: int
    rule: "ParsedRule"
    reads: set[str] = field(default_factory=set)
    writes: set[str] = field(default_factory=set)


class DependencyGraph:
    """
    Builds and manages a dependency graph for business rules.

    Dependencies are determined by read/write analysis:
    - Rule B depends on Rule A if B reads an attribute that A writes

    Supports cycle detection and topological sorting for execution order.
    """

    def __init__(self):
        self.nodes: list[RuleNode] = []
        self.edges: dict[int, set[int]] = defaultdict(set)  # from -> set of to
        self.reverse_edges: dict[int, set[int]] = defaultdict(set)  # to -> set of from
        self._analyzed = False

    def add_rule(
        self,
        rule: "ParsedRule",
        workflows: dict[str, "Workflow | callable"] | None = None,
    ) -> int:
        """
        Add a rule to the graph.

        Args:
            rule: The parsed rule to add
            workflows: Optional workflow definitions for dependency merging

        Returns:
            The index of the added rule
        """
        index = len(self.nodes)

        # Start with rule's own reads/writes
        reads = set(rule.reads)
        writes = set(rule.writes)

        # Merge in workflow dependencies
        if workflows:
            for wf_name in rule.workflow_calls:
                if wf_name in workflows:
                    wf = workflows[wf_name]
                    if hasattr(wf, "reads"):
                        reads.update(wf.reads)
                    if hasattr(wf, "writes"):
                        writes.update(wf.writes)

        node = RuleNode(index=index, rule=rule, reads=reads, writes=writes)
        self.nodes.append(node)
        self._analyzed = False

        return index

    def analyze(self) -> None:
        """
        Build the dependency graph from read/write sets.

        Rule B depends on Rule A if: B.reads ∩ A.writes ≠ ∅
        """
        if self._analyzed:
            return

        self.edges.clear()
        self.reverse_edges.clear()

        # For each pair of rules, check for dependencies
        for i, node_a in enumerate(self.nodes):
            for j, node_b in enumerate(self.nodes):
                if i == j:
                    continue

                # Check if node_b reads something that node_a writes
                # This means node_b depends on node_a (node_a must run first)
                if self._paths_overlap(node_b.reads, node_a.writes):
                    self.edges[i].add(j)
                    self.reverse_edges[j].add(i)

        self._analyzed = True

    def _paths_overlap(self, reads: set[str], writes: set[str]) -> bool:
        """
        Check if any read path overlaps with any write path.

        Handles wildcard indices [*] by checking prefix matches.
        """
        for read_path in reads:
            for write_path in writes:
                if self._path_matches(read_path, write_path):
                    return True
        return False

    def _path_matches(self, path1: str, path2: str) -> bool:
        """
        Check if two paths match, considering wildcards.

        A path with [*] matches any specific index.
        Also handles prefix matching for nested attributes.
        """
        # Normalize paths by replacing [*] with a common marker
        p1_parts = path1.replace("[*]", ".[*]").split(".")
        p2_parts = path2.replace("[*]", ".[*]").split(".")

        # Check if one is a prefix of the other or they match exactly
        min_len = min(len(p1_parts), len(p2_parts))

        for i in range(min_len):
            part1 = p1_parts[i]
            part2 = p2_parts[i]

            # Wildcard matches anything
            if part1 == "[*]" or part2 == "[*]":
                continue

            if part1 != part2:
                return False

        return True

    def detect_cycles(self) -> list[list[int]]:
        """
        Detect all cycles in the dependency graph.

        Returns:
            List of cycles, where each cycle is a list of rule indices
        """
        self.analyze()

        cycles: list[list[int]] = []
        visited: set[int] = set()
        rec_stack: set[int] = set()

        def dfs(node: int, path: list[int]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.edges.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for node in range(len(self.nodes)):
            if node not in visited:
                dfs(node, [])

        return cycles

    def get_execution_order(self) -> list[int]:
        """
        Get the topologically sorted execution order.

        If cycles are detected, warns and breaks them by removing
        edges to the lowest-index rule in each cycle.

        Returns:
            List of rule indices in execution order
        """
        self.analyze()

        # Detect and handle cycles
        cycles = self.detect_cycles()
        if cycles:
            self._break_cycles(cycles)

        # Kahn's algorithm for topological sort
        in_degree: dict[int, int] = {i: 0 for i in range(len(self.nodes))}
        for targets in self.edges.values():
            for target in targets:
                in_degree[target] += 1

        # Start with nodes that have no dependencies
        queue: list[int] = [i for i, degree in in_degree.items() if degree == 0]
        result: list[int] = []

        while queue:
            # Sort to ensure deterministic order (prefer lower indices)
            queue.sort()
            node = queue.pop(0)
            result.append(node)

            for neighbor in self.edges.get(node, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If we couldn't process all nodes, there's still a cycle
        # (shouldn't happen after _break_cycles, but just in case)
        if len(result) != len(self.nodes):
            # Add remaining nodes in index order
            remaining = set(range(len(self.nodes))) - set(result)
            result.extend(sorted(remaining))

        return result

    def _break_cycles(self, cycles: list[list[int]]) -> None:
        """
        Break cycles by removing edges.

        Strategy: Remove edge pointing to the lowest-index node in each cycle.
        """
        for cycle in cycles:
            # Find the lowest index in the cycle (excluding the repeated last element)
            cycle_nodes = cycle[:-1] if cycle[0] == cycle[-1] else cycle
            min_node = min(cycle_nodes)

            # Find the edge pointing to min_node and remove it
            for i, node in enumerate(cycle_nodes):
                next_node = cycle_nodes[(i + 1) % len(cycle_nodes)]
                if next_node == min_node and min_node in self.edges.get(node, set()):
                    # Warn about the cycle
                    warnings.warn(
                        CyclicDependencyWarning(cycle),
                        stacklevel=3,
                    )
                    # Remove the edge
                    self.edges[node].discard(min_node)
                    self.reverse_edges[min_node].discard(node)
                    break

    def get_dependencies(self, rule_index: int) -> set[int]:
        """
        Get the indices of rules that a given rule depends on.

        Args:
            rule_index: The index of the rule

        Returns:
            Set of rule indices that must execute before this rule
        """
        self.analyze()
        return self.reverse_edges.get(rule_index, set()).copy()

    def get_dependents(self, rule_index: int) -> set[int]:
        """
        Get the indices of rules that depend on a given rule.

        Args:
            rule_index: The index of the rule

        Returns:
            Set of rule indices that depend on this rule
        """
        self.analyze()
        return self.edges.get(rule_index, set()).copy()

    def get_graph(self) -> dict[int, set[int]]:
        """
        Get the dependency graph as a dictionary.

        Returns:
            Dictionary mapping rule index to set of dependent rule indices
        """
        self.analyze()
        return {k: v.copy() for k, v in self.edges.items()}

    def __len__(self) -> int:
        return len(self.nodes)

