"""
Rule Interpreter - A lightweight DSL for business rules.
"""

from rule_interpreter.engine import RuleEngine
from rule_interpreter.workflows import Workflow, workflow
from rule_interpreter.exceptions import (
    RuleInterpreterError,
    PathResolutionError,
    RuleSyntaxError,
    CyclicDependencyWarning,
    WorkflowNotFoundError,
    EvaluationError,
)

__all__ = [
    "RuleEngine",
    "Workflow",
    "workflow",
    "RuleInterpreterError",
    "PathResolutionError",
    "RuleSyntaxError",
    "CyclicDependencyWarning",
    "WorkflowNotFoundError",
    "EvaluationError",
]

__version__ = "0.1.0"

