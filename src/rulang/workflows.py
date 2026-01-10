"""
Workflow system with dependency declarations.

Provides:
- Workflow wrapper class for declaring read/write dependencies
- Decorator for registering workflows with dependency tracking
- Global workflow registry
"""

from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class Workflow:
    """
    Wrapper class for workflow functions with dependency declarations.

    Use this to declare what entity attributes a workflow reads and writes,
    enabling accurate dependency analysis even though the rule engine
    cannot inspect the workflow's internal logic.

    Example:
        workflows = {
            "calculate_area": Workflow(
                fn=lambda e: setattr(e, 'area', e.length * e.width),
                reads=["entity.length", "entity.width"],
                writes=["entity.area"]
            )
        }
    """

    fn: Callable[..., Any]
    reads: list[str] = field(default_factory=list)
    writes: list[str] = field(default_factory=list)

    def __call__(self, *args, **kwargs) -> Any:
        """Allow the Workflow to be called directly."""
        return self.fn(*args, **kwargs)


# Global registry for decorated workflows
_workflow_registry: dict[str, Workflow] = {}


def workflow(
    name: str,
    reads: list[str] | None = None,
    writes: list[str] | None = None,
) -> Callable[[Callable], Callable]:
    """
    Decorator for registering workflow functions with dependency declarations.

    Args:
        name: The name used to reference this workflow in rules
        reads: List of entity attribute paths this workflow reads
        writes: List of entity attribute paths this workflow writes/mutates

    Example:
        @workflow("calculate_total", reads=["entity.price", "entity.quantity"], writes=["entity.total"])
        def calculate_total(entity):
            entity.total = entity.price * entity.quantity

        # Then in a rule:
        # entity.needs_calculation == true => workflow("calculate_total")
    """

    def decorator(fn: Callable) -> Callable:
        wf = Workflow(
            fn=fn,
            reads=reads or [],
            writes=writes or [],
        )
        _workflow_registry[name] = wf
        return fn

    return decorator


def get_registered_workflows() -> dict[str, Workflow]:
    """
    Get all workflows registered via the @workflow decorator.

    Returns:
        Dictionary mapping workflow names to Workflow objects
    """
    return _workflow_registry.copy()


def clear_workflow_registry() -> None:
    """Clear all registered workflows. Useful for testing."""
    _workflow_registry.clear()


def merge_workflows(
    passed_workflows: dict[str, Callable | Workflow] | None,
) -> dict[str, Workflow | Callable]:
    """
    Merge passed workflows with registered workflows.

    Passed workflows take precedence over registered workflows.

    Args:
        passed_workflows: Workflows passed to evaluate()

    Returns:
        Merged dictionary of workflows
    """
    result: dict[str, Workflow | Callable] = get_registered_workflows()

    if passed_workflows:
        for name, wf in passed_workflows.items():
            result[name] = wf

    return result

