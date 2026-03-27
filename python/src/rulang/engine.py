"""
RuleEngine - Main entry point for the business rules DSL.

Provides a clean API for:
- Adding rules (single or list)
- Evaluating rules against entities
- Dependency graph introspection
- Workflow registration
"""

from typing import Any, Callable, Literal

from rulang.dependency_graph import DependencyGraph
from rulang.exceptions import EvaluationError, PathResolutionError, WorkflowNotFoundError
from rulang.visitor import ParsedRule, RuleInterpreter, parse_rule
from rulang.workflows import Workflow, merge_workflows, workflow as workflow_decorator


class RuleEngine:
    """
    Main entry point for the business rules DSL.

    Example:
        engine = RuleEngine()
        engine.add_rules([
            "entity.age >= 18 => entity.is_adult = true",
            "entity.is_adult == true => entity.discount += 0.1",
        ])

        entity = {"age": 25, "is_adult": False, "discount": 0.0}
        result = engine.evaluate(entity)
        # entity is now {"age": 25, "is_adult": True, "discount": 0.1}
    """

    # Class-level decorator for workflow registration
    workflow = staticmethod(workflow_decorator)

    def __init__(self, mode: Literal["first_match", "all_match"] = "first_match"):
        """
        Initialize the rule engine.

        Args:
            mode: Evaluation mode
                - "first_match": Stop after the first matching rule
                - "all_match": Execute all matching rules in dependency order
        """
        self.mode = mode
        self._rules: list[ParsedRule] = []
        self._graph: DependencyGraph = DependencyGraph()
        self._execution_order: list[int] | None = None

    def add_rules(self, rules: str | list[str]) -> None:
        """
        Parse and add rule(s) to the engine.

        Args:
            rules: A single rule string or a list of rule strings

        Raises:
            RuleSyntaxError: If any rule cannot be parsed
        """
        if isinstance(rules, str):
            rules = [rules]

        for rule_text in rules:
            parsed = parse_rule(rule_text)
            self._rules.append(parsed)

        # Invalidate cached execution order
        self._execution_order = None

    def evaluate(
        self,
        entity: Any,
        workflows: dict[str, Callable | Workflow] | None = None,
        entity_name: str = "entity",
    ) -> Any:
        """
        Evaluate rules against an entity.

        Args:
            entity: The entity to evaluate rules against (dict, object, or dataclass)
            workflows: Optional dictionary of workflow functions
            entity_name: The name used in rules to reference the entity (default: "entity")

        Returns:
            - If no rules match: None
            - If a rule matches with explicit return: the return value
            - If a rule matches without explicit return: True
            - In "all_match" mode: the last return value, or True if any matched

        Raises:
            PathResolutionError: If a rule references a non-existent attribute
            WorkflowNotFoundError: If a rule calls an unknown workflow
            EvaluationError: If an error occurs during rule evaluation
        """
        # Merge workflows
        all_workflows = merge_workflows(workflows)

        # Build dependency graph if needed
        if self._execution_order is None:
            self._build_execution_order(all_workflows)

        # Execute rules in dependency order
        any_matched = False
        last_return_value: Any = None

        for rule_index in self._execution_order:
            rule = self._rules[rule_index]

            try:
                interpreter = RuleInterpreter(entity, all_workflows, entity_name)
                matched, return_value = interpreter.execute(rule.tree)

                if matched:
                    any_matched = True
                    last_return_value = return_value

                    if self.mode == "first_match":
                        return return_value

            except (EvaluationError, PathResolutionError, WorkflowNotFoundError):
                raise
            except Exception as e:
                raise EvaluationError(rule.rule_text, str(e)) from e

        if any_matched:
            return last_return_value

        return None

    def _build_execution_order(
        self,
        workflows: dict[str, Workflow | Callable] | None = None,
    ) -> None:
        """Build the dependency graph and compute execution order."""
        self._graph = DependencyGraph()

        for rule in self._rules:
            self._graph.add_rule(rule, workflows)

        self._execution_order = self._graph.get_execution_order()

    def get_dependency_graph(self) -> dict[int, set[int]]:
        """
        Get the computed dependency graph.

        Returns:
            Dictionary mapping rule index to set of dependent rule indices.
            An edge from A to B means rule B depends on rule A.
        """
        if self._execution_order is None:
            self._build_execution_order()

        return self._graph.get_graph()

    def get_execution_order(self) -> list[int]:
        """
        Get the computed execution order of rules.

        Returns:
            List of rule indices in the order they will be executed.
        """
        if self._execution_order is None:
            self._build_execution_order()

        return self._execution_order.copy()

    def get_rules(self) -> list[str]:
        """
        Get all rule strings in the order they were added.

        Returns:
            List of rule strings
        """
        return [r.rule_text for r in self._rules]

    def get_rule_analysis(self, index: int) -> dict[str, Any]:
        """
        Get the read/write analysis for a specific rule.

        Args:
            index: The rule index

        Returns:
            Dictionary with 'reads', 'writes', and 'workflow_calls' sets
        """
        if index < 0 or index >= len(self._rules):
            raise IndexError(f"Rule index {index} out of range")

        rule = self._rules[index]
        return {
            "rule": rule.rule_text,
            "reads": rule.reads.copy(),
            "writes": rule.writes.copy(),
            "workflow_calls": rule.workflow_calls.copy(),
        }

    def clear(self) -> None:
        """Remove all rules from the engine."""
        self._rules.clear()
        self._graph = DependencyGraph()
        self._execution_order = None

    def __len__(self) -> int:
        """Return the number of rules in the engine."""
        return len(self._rules)

