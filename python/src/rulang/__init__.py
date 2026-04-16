"""
Rulang - A lightweight DSL for business rules.
"""

from rulang.engine import RuleEngine
from rulang.workflows import Workflow, workflow
from rulang.exceptions import (
    RuleInterpreterError,
    PathResolutionError,
    RuleSyntaxError,
    CyclicDependencyWarning,
    WorkflowNotFoundError,
    EvaluationError,
)
from rulang.ast import (
    parse,
    walk,
    Span,
    Rule,
    Path,
    FieldSegment,
    NullSafeFieldSegment,
    IndexSegment,
    Literal_,
    PathRef,
    FunctionCall,
    Binary,
    NullCoalesce,
    Unary,
    WorkflowCallExpr,
    Comparison,
    Existence,
    And,
    Or,
    Not,
    Set_,
    Compound,
    WorkflowCallAction,
    Return,
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
    # AST
    "parse",
    "walk",
    "Span",
    "Rule",
    "Path",
    "FieldSegment",
    "NullSafeFieldSegment",
    "IndexSegment",
    "Literal_",
    "PathRef",
    "FunctionCall",
    "Binary",
    "NullCoalesce",
    "Unary",
    "WorkflowCallExpr",
    "Comparison",
    "Existence",
    "And",
    "Or",
    "Not",
    "Set_",
    "Compound",
    "WorkflowCallAction",
    "Return",
]

__version__ = "1.0.0"

