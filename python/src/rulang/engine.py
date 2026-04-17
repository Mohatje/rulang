"""
RuleEngine - Main entry point for the business rules DSL.

Provides a clean API for:
- Adding rules (single or list)
- Evaluating rules against entities
- Dry-running rules (with per-path diff)
- Dependency graph introspection
- Workflow registration
"""

import copy as _copy
from typing import Any, Callable, Literal

from rulang.dependency_graph import DependencyGraph
from rulang.dry_run import (
    ActionChange,
    DryRunResult,
    ExecutedAction,
    MatchedRule,
    _diff_entities,
)
from rulang.exceptions import EvaluationError, PathResolutionError, WorkflowNotFoundError
from rulang.visitor import ParsedRule, ReturnValue, RuleInterpreter, parse_rule
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
        self._execution_order_workflow_key: tuple | None = None

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
        self._execution_order_workflow_key = None

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
        self._ensure_execution_order(all_workflows)

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

    def dry_run(
        self,
        entity: Any,
        workflows: dict[str, Callable | Workflow] | None = None,
        entity_name: str = "entity",
        *,
        deep_copy: bool = True,
    ) -> DryRunResult:
        """
        Evaluate rules against an entity and return a structured trace.

        Unlike `evaluate`, this collects:
        - every rule's condition result (matched vs. not) in the order they
          were evaluated,
        - which rules actually executed (in first_match mode, later matching
          rules appear with `executed=False` so UIs can surface them),
        - per-action before/after values at every path that changed,
        - an aggregated diff across the whole run,
        - the final entity and the value `evaluate()` would have returned.

        Args:
            entity: the entity to evaluate against.
            workflows: optional mapping of workflow name → callable / Workflow.
            entity_name: identifier that rules use for the entity (default "entity").
            deep_copy: when True (default), the entity is deep-copied before
                evaluation so this call is non-mutating.

        Returns:
            A `DryRunResult`.
        """
        if deep_copy:
            entity = _copy.deepcopy(entity)

        all_workflows = merge_workflows(workflows)
        self._ensure_execution_order(all_workflows)

        matched_rules: list[MatchedRule] = []
        executed_actions: list[ExecutedAction] = []
        aggregate_diff: dict[str, tuple[Any, Any]] = {}
        last_return_value: Any = None
        any_executed = False
        first_match_executed = False
        returned: Any = None
        stop_after_return = False

        for rule_index in self._execution_order:
            if stop_after_return:
                # Still trace remaining rules as not-executed (in first_match after ret)
                parsed = self._rules[rule_index]
                matched_rules.append(
                    MatchedRule(
                        index=rule_index,
                        rule_text=parsed.rule_text,
                        condition_result=False,
                        executed=False,
                    )
                )
                continue

            parsed = self._rules[rule_index]
            interpreter = RuleInterpreter(entity, all_workflows, entity_name)

            try:
                condition_value = interpreter.visit(parsed.tree.condition())
            except (EvaluationError, PathResolutionError, WorkflowNotFoundError):
                raise
            except Exception as e:  # noqa: BLE001
                raise EvaluationError(parsed.rule_text, str(e)) from e

            matched = bool(condition_value)
            execute_this = False
            if matched:
                if self.mode == "all_match":
                    execute_this = True
                elif not first_match_executed:
                    execute_this = True
                    first_match_executed = True

            if execute_this:
                any_executed = True
                rule_returned = self._execute_actions_traced(
                    parsed,
                    rule_index,
                    interpreter,
                    entity,
                    executed_actions,
                    aggregate_diff,
                )
                if rule_returned is not _NO_RETURN:
                    last_return_value = rule_returned
                    # In first_match mode, a ret ends evaluation entirely.
                    if self.mode == "first_match":
                        stop_after_return = True
                else:
                    # No explicit ret: matched rule returns True by engine convention.
                    if last_return_value is None:
                        last_return_value = True

            matched_rules.append(
                MatchedRule(
                    index=rule_index,
                    rule_text=parsed.rule_text,
                    condition_result=matched,
                    executed=execute_this,
                )
            )

            # first_match semantics: stop after the first executing rule.
            if execute_this and self.mode == "first_match" and not stop_after_return:
                stop_after_return = True

        if any_executed:
            returned = last_return_value

        return DryRunResult(
            matched_rules=tuple(matched_rules),
            executed_actions=tuple(executed_actions),
            diff=aggregate_diff,
            final_entity=entity,
            returned=returned,
        )

    def _execute_actions_traced(
        self,
        parsed: ParsedRule,
        rule_index: int,
        interpreter: RuleInterpreter,
        entity: Any,
        executed_actions: list[ExecutedAction],
        aggregate_diff: dict[str, tuple[Any, Any]],
    ) -> Any:
        """Execute a rule's actions, recording per-action diffs.

        Returns the explicit return value if `ret` was hit, else `_NO_RETURN`.
        """
        actions_ctx = parsed.tree.actions()
        for action_ctx in actions_ctx.action():
            before_snapshot = _copy.deepcopy(entity)
            try:
                interpreter.visit(action_ctx)
            except ReturnValue as rv:
                changes = _to_changes(_diff_entities(before_snapshot, entity))
                for path, (b, a) in _diff_entities(before_snapshot, entity).items():
                    _merge_into_diff(aggregate_diff, path, b, a)
                executed_actions.append(
                    ExecutedAction(
                        rule_index=rule_index,
                        action_kind="return",
                        changes=changes,
                        returned=rv.value,
                    )
                )
                return rv.value

            # No ret: record what changed and classify the action kind.
            kind = _action_kind(action_ctx)
            diff_map = _diff_entities(before_snapshot, entity)
            for path, (b, a) in diff_map.items():
                _merge_into_diff(aggregate_diff, path, b, a)
            executed_actions.append(
                ExecutedAction(
                    rule_index=rule_index,
                    action_kind=kind,
                    changes=_to_changes(diff_map),
                )
            )

        return _NO_RETURN

    def _build_execution_order(
        self,
        workflows: dict[str, Workflow | Callable] | None = None,
        workflow_key: tuple | None = None,
    ) -> None:
        """Build the dependency graph and compute execution order."""
        self._graph = DependencyGraph()

        for rule in self._rules:
            self._graph.add_rule(rule, workflows)

        self._execution_order = self._graph.get_execution_order()
        self._execution_order_workflow_key = workflow_key

    def _get_workflow_dependency_key(
        self,
        workflows: dict[str, Workflow | Callable] | None,
    ) -> tuple:
        if not workflows:
            return ()

        entries: list[tuple] = []
        for name, workflow in sorted(workflows.items()):
            if callable(workflow) and not hasattr(workflow, "reads") and not hasattr(workflow, "writes"):
                entries.append((name, None))
                continue

            reads = tuple(sorted(getattr(workflow, "reads", [])))
            writes = tuple(sorted(getattr(workflow, "writes", [])))
            entries.append((name, reads, writes))

        return tuple(entries)

    def _ensure_execution_order(
        self,
        workflows: dict[str, Workflow | Callable] | None = None,
    ) -> None:
        workflow_key = self._get_workflow_dependency_key(workflows)
        if self._execution_order is None or self._execution_order_workflow_key != workflow_key:
            self._build_execution_order(workflows, workflow_key)

    def get_dependency_graph(self) -> dict[int, set[int]]:
        """
        Get the computed dependency graph.

        Returns:
            Dictionary mapping rule index to set of dependent rule indices.
            An edge from A to B means rule B depends on rule A.
        """
        self._ensure_execution_order()

        return self._graph.get_graph()

    def get_execution_order(self) -> list[int]:
        """
        Get the computed execution order of rules.

        Returns:
            List of rule indices in the order they will be executed.
        """
        self._ensure_execution_order()

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
        self._execution_order_workflow_key = None

    def __len__(self) -> int:
        """Return the number of rules in the engine."""
        return len(self._rules)


# --- Helpers for dry_run ------------------------------------------------


_NO_RETURN = object()


def _to_changes(diff_map: dict[str, tuple[Any, Any]]) -> tuple[ActionChange, ...]:
    return tuple(
        ActionChange(path=p, before=b, after=a) for p, (b, a) in sorted(diff_map.items())
    )


def _merge_into_diff(
    aggregate: dict[str, tuple[Any, Any]],
    path: str,
    before: Any,
    after: Any,
) -> None:
    """Merge a single action's change into the aggregate diff.

    First writer keeps the `before`; latest writer supplies the `after`. If the
    aggregated change net-out to the initial value, drop the entry.
    """
    if path in aggregate:
        original_before, _ = aggregate[path]
        if original_before == after:
            del aggregate[path]
        else:
            aggregate[path] = (original_before, after)
    else:
        aggregate[path] = (before, after)


def _action_kind(action_ctx: Any) -> str:
    if action_ctx.returnStmt():
        return "return"
    if action_ctx.assignment():
        assign_op = action_ctx.assignment().assignOp()
        if assign_op.ASSIGN():
            return "set"
        return "compound"
    if action_ctx.workflowCall():
        return "workflow"
    return "set"
