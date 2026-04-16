"""
Rulang - A lightweight DSL for business rules.
"""

from rulang.engine import RuleEngine
from rulang.dry_run import (
    ActionChange,
    DryRunResult,
    ExecutedAction,
    MatchedRule,
)
from rulang.workflows import Workflow, workflow
from rulang.exceptions import (
    RuleInterpreterError,
    PathResolutionError,
    RuleSyntaxError,
    CyclicDependencyWarning,
    WorkflowNotFoundError,
    EvaluationError,
)
from rulang.formatter import (
    format,
    format_action,
    format_ast,
    format_condition,
    format_expr,
    format_path,
)
from rulang.reference import grammar_reference
from rulang.conflicts import Conflict, detect_conflicts
from rulang.validation import (
    BaseResolver,
    Diagnostic,
    OK,
    PathInfo,
    Resolver,
    UNKNOWN,
    validate,
)
from rulang import builders
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
    "DryRunResult",
    "MatchedRule",
    "ExecutedAction",
    "ActionChange",
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
    "format",
    "format_ast",
    "format_condition",
    "format_action",
    "format_path",
    "format_expr",
    "grammar_reference",
    "Conflict",
    "detect_conflicts",
    "validate",
    "BaseResolver",
    "Resolver",
    "Diagnostic",
    "PathInfo",
    "OK",
    "UNKNOWN",
    "builders",
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

__version__ = "1.1.0"

