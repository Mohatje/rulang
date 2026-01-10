"""
AST visitor/interpreter for business rules.

Walks the ANTLR parse tree to:
- Evaluate conditions
- Execute actions (mutations, workflow calls, returns)
- Track read/write sets for dependency analysis
"""

import re
from dataclasses import dataclass, field
from typing import Any, Callable

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from rulang.grammar.generated.BusinessRulesLexer import BusinessRulesLexer
from rulang.grammar.generated.BusinessRulesParser import BusinessRulesParser
from rulang.grammar.generated.BusinessRulesVisitor import (
    BusinessRulesVisitor as BaseVisitor,
)
from rulang.exceptions import (
    EvaluationError,
    PathResolutionError,
    RuleSyntaxError,
    WorkflowNotFoundError,
)
from rulang.path_resolver import PathResolver


# Built-in functions registry
BUILTIN_FUNCTIONS: dict[str, Callable[..., Any]] = {
    # String functions
    "lower": lambda x: str(x).lower() if x is not None else None,
    "upper": lambda x: str(x).upper() if x is not None else None,
    "trim": lambda x: str(x).strip() if x is not None else None,
    "strip": lambda x: str(x).strip() if x is not None else None,
    # Type coercion
    "int": lambda x: int(float(x)) if x is not None else None,
    "float": lambda x: float(x) if x is not None else None,
    "str": lambda x: str(x) if x is not None else None,
    "bool": lambda x: bool(x),
    # Collection functions
    "len": lambda x: len(x) if x is not None else 0,
    "first": lambda x: x[0] if x and len(x) > 0 else None,
    "last": lambda x: x[-1] if x and len(x) > 0 else None,
    "keys": lambda d: list(d.keys()) if isinstance(d, dict) else [],
    "values": lambda d: list(d.values()) if isinstance(d, dict) else [],
    # Math functions
    "abs": lambda x: abs(x) if x is not None else None,
    "round": lambda x, n=0: round(x, n) if x is not None else None,
    "min": lambda *args: min(args) if args else None,
    "max": lambda *args: max(args) if args else None,
    # Type checking
    "is_list": lambda x: isinstance(x, (list, tuple)),
    "is_string": lambda x: isinstance(x, str),
    "is_number": lambda x: isinstance(x, (int, float)),
    "is_none": lambda x: x is None,
}


class RuleSyntaxErrorListener(ErrorListener):
    """Custom error listener to capture syntax errors."""

    def __init__(self, rule_text: str):
        self.rule_text = rule_text
        self.errors: list[tuple[int, int, str]] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append((line, column, msg))


@dataclass
class ParsedRule:
    """Represents a parsed rule with its parse tree and metadata."""

    rule_text: str
    tree: BusinessRulesParser.Rule_Context
    reads: set[str] = field(default_factory=set)
    writes: set[str] = field(default_factory=set)
    workflow_calls: set[str] = field(default_factory=set)


class ReturnValue(Exception):
    """Used to signal an early return from rule execution."""

    def __init__(self, value: Any):
        self.value = value


class RuleAnalyzer(BaseVisitor):
    """
    Analyzes a rule to extract read/write sets without executing it.
    Used for dependency graph construction.
    """

    def __init__(self, entity_name: str = "entity"):
        self.reads: set[str] = set()
        self.writes: set[str] = set()
        self.workflow_calls: set[str] = set()
        self._in_condition = False
        self._in_assignment_target = False
        self._entity_name = entity_name

    def visitRule_(self, ctx: BusinessRulesParser.Rule_Context):
        # Visit condition (left side) - all paths here are reads
        self._in_condition = True
        self.visit(ctx.condition())
        self._in_condition = False

        # Visit actions (right side)
        self.visit(ctx.actions())

        return None

    def visitPath(self, ctx: BusinessRulesParser.PathContext):
        path_str = self._get_path_string(ctx)

        if self._in_condition:
            self.reads.add(path_str)
        elif self._in_assignment_target:
            self.writes.add(path_str)
        else:
            # Reading in the RHS of an assignment or in workflow args
            self.reads.add(path_str)

        return None

    def visitAssignment(self, ctx: BusinessRulesParser.AssignmentContext):
        # The path on the left is a write
        self._in_assignment_target = True
        self.visit(ctx.path())
        self._in_assignment_target = False

        # For compound assignments (+=, -=, etc.), the target is also read
        assign_op = ctx.assignOp()
        if assign_op.ASSIGN() is None:  # It's a compound assignment
            path_str = self._get_path_string(ctx.path())
            self.reads.add(path_str)

        # The expression on the right is read
        self.visit(ctx.orExpr())

        return None

    def visitWorkflowCall(self, ctx: BusinessRulesParser.WorkflowCallContext):
        workflow_name = ctx.STRING().getText()[1:-1]  # Remove quotes
        self.workflow_calls.add(workflow_name)

        # Visit arguments (they are reads)
        for expr in ctx.orExpr():
            self.visit(expr)

        return None

    def _get_path_string(self, ctx: BusinessRulesParser.PathContext) -> str:
        """Convert a path context to a string representation.

        Normalizes paths to always include the entity prefix for consistent
        dependency tracking. This allows both 'entity.age' and 'age' syntax
        to produce the same path string.
        """
        parts = [ctx.IDENTIFIER().getText()]

        for segment in ctx.pathSegment():
            if segment.IDENTIFIER():
                parts.append(segment.IDENTIFIER().getText())
            elif segment.LBRACKET():
                # For analysis, we just note that there's indexing
                parts.append("[*]")

        # Normalize: if path doesn't start with entity_name, prepend it
        if parts[0] != self._entity_name:
            parts = [self._entity_name] + parts

        return ".".join(parts)


class RuleInterpreter(BaseVisitor):
    """
    Interprets a parsed rule against an entity.
    """

    def __init__(
        self,
        entity: Any,
        workflows: dict[str, Callable] | None = None,
        entity_name: str = "entity",
    ):
        self.resolver = PathResolver(entity, entity_name)
        self.entity = entity
        self.entity_name = entity_name
        self.workflows = workflows or {}
        self._return_value: Any = None
        self._has_returned = False

    def execute(self, tree: BusinessRulesParser.Rule_Context) -> tuple[bool, Any]:
        """
        Execute a rule and return (matched, return_value).

        Returns:
            Tuple of (condition_matched, return_value)
            - If condition is False: (False, None)
            - If condition is True and no explicit return: (True, True)
            - If condition is True with explicit return: (True, return_value)
        """
        try:
            result = self.visit(tree)
            return result
        except ReturnValue as rv:
            return (True, rv.value)
        except (PathResolutionError, WorkflowNotFoundError):
            raise
        except Exception as e:
            raise EvaluationError("", str(e)) from e

    def visitRule_(self, ctx: BusinessRulesParser.Rule_Context) -> tuple[bool, Any]:
        # Evaluate condition
        condition_result = self.visit(ctx.condition())

        if not condition_result:
            return (False, None)

        # Execute actions
        self.visit(ctx.actions())

        # If no explicit return, return True
        if self._has_returned:
            return (True, self._return_value)
        return (True, True)

    def visitCondition(self, ctx: BusinessRulesParser.ConditionContext) -> Any:
        return self.visit(ctx.orExpr())

    def visitOrExpr(self, ctx: BusinessRulesParser.OrExprContext) -> Any:
        result = self.visit(ctx.andExpr(0))
        for i in range(1, len(ctx.andExpr())):
            if result:  # Short-circuit
                return result
            result = self.visit(ctx.andExpr(i))
        return result

    def visitAndExpr(self, ctx: BusinessRulesParser.AndExprContext) -> Any:
        result = self.visit(ctx.notExpr(0))
        for i in range(1, len(ctx.notExpr())):
            if not result:  # Short-circuit
                return result
            result = self.visit(ctx.notExpr(i))
        return result

    def visitNotExpr(self, ctx: BusinessRulesParser.NotExprContext) -> Any:
        if ctx.NOT():
            return not self.visit(ctx.notExpr())
        return self.visit(ctx.comparison())

    def visitComparison(self, ctx: BusinessRulesParser.ComparisonContext) -> Any:
        left = self.visit(ctx.nullCoalesce(0))

        # Unary operators (no right operand)
        if ctx.IS_EMPTY():
            return self._is_empty(left)
        if ctx.EXISTS():
            return left is not None

        # Check if there's a second operand
        if len(ctx.nullCoalesce()) == 1:
            return left

        right = self.visit(ctx.nullCoalesce(1))

        # Standard comparison operators
        if ctx.EQ():
            return self._compare_eq(left, right)
        elif ctx.NEQ():
            return not self._compare_eq(left, right)
        elif ctx.LT():
            return left < right
        elif ctx.GT():
            return left > right
        elif ctx.LTE():
            return left <= right
        elif ctx.GTE():
            return left >= right
        elif ctx.IN():
            return self._check_in(left, right)
        elif ctx.NOT_IN():
            return not self._check_in(left, right)
        # New string operators
        elif ctx.CONTAINS():
            return self._contains(left, right)
        elif ctx.NOT_CONTAINS():
            return not self._contains(left, right)
        elif ctx.STARTS_WITH():
            return self._starts_with(left, right)
        elif ctx.ENDS_WITH():
            return self._ends_with(left, right)
        elif ctx.MATCHES():
            return self._matches(left, right)
        # New list operators
        elif ctx.CONTAINS_ANY():
            return self._contains_any(left, right)
        elif ctx.CONTAINS_ALL():
            return self._contains_all(left, right)

        return left

    # --- Helper methods for operators with list any-satisfies semantics ---

    def _is_empty(self, value: Any) -> bool:
        """Check if value is None, empty string, or empty collection."""
        if value is None:
            return True
        if isinstance(value, str):
            return value.strip() == ""
        if isinstance(value, (list, tuple, set, dict)):
            return len(value) == 0
        return False

    def _compare_eq(self, left: Any, right: Any) -> bool:
        """Equality with list any-satisfies semantics.

        Any-satisfies applies only when one side is a list and the other is not.
        When both sides are lists, exact equality is used.
        """
        left_is_list = isinstance(left, (list, tuple))
        right_is_list = isinstance(right, (list, tuple))

        # If both are lists, use exact equality
        if left_is_list and right_is_list:
            return list(left) == list(right)

        # If left is list and right is scalar, any-satisfies
        if left_is_list:
            return any(item == right for item in left)

        # If right is list and left is scalar, any-satisfies
        if right_is_list:
            return any(left == item for item in right)

        return left == right

    def _check_in(self, left: Any, right: Any) -> bool:
        """Membership check with list any-satisfies semantics."""
        if isinstance(left, (list, tuple)):
            return any(item in right for item in left)
        return left in right

    def _contains(self, haystack: Any, needle: Any) -> bool:
        """Substring check: haystack contains needle."""
        if haystack is None or needle is None:
            return False
        if isinstance(haystack, (list, tuple)):
            # Any element contains the needle
            return any(self._contains(item, needle) for item in haystack)
        return str(needle) in str(haystack)

    def _starts_with(self, value: Any, prefix: Any) -> bool:
        """Check if value starts with prefix."""
        if value is None or prefix is None:
            return False
        if isinstance(value, (list, tuple)):
            return any(self._starts_with(item, prefix) for item in value)
        return str(value).startswith(str(prefix))

    def _ends_with(self, value: Any, suffix: Any) -> bool:
        """Check if value ends with suffix."""
        if value is None or suffix is None:
            return False
        if isinstance(value, (list, tuple)):
            return any(self._ends_with(item, suffix) for item in value)
        return str(value).endswith(str(suffix))

    def _matches(self, value: Any, pattern: Any) -> bool:
        """Regex match check."""
        if value is None or pattern is None:
            return False
        if isinstance(value, (list, tuple)):
            return any(self._matches(item, pattern) for item in value)
        try:
            return bool(re.search(str(pattern), str(value)))
        except re.error:
            return False

    def _contains_any(self, collection: Any, values: Any) -> bool:
        """Check if collection contains ANY of the values."""
        if collection is None or values is None:
            return False
        if not isinstance(values, (list, tuple)):
            values = [values]
        if not isinstance(collection, (list, tuple)):
            collection = [collection]
        return any(v in collection for v in values)

    def _contains_all(self, collection: Any, values: Any) -> bool:
        """Check if collection contains ALL of the values."""
        if collection is None or values is None:
            return False
        if not isinstance(values, (list, tuple)):
            values = [values]
        if not isinstance(collection, (list, tuple)):
            collection = [collection]
        return all(v in collection for v in values)

    # --- End helper methods ---

    def visitNullCoalesce(self, ctx: BusinessRulesParser.NullCoalesceContext) -> Any:
        """Handle null coalescing: a ?? b returns a if a is not None, else b."""
        result = self.visit(ctx.addExpr(0))
        for i in range(1, len(ctx.addExpr())):
            if result is not None:
                return result
            result = self.visit(ctx.addExpr(i))
        return result

    def visitAddExpr(self, ctx: BusinessRulesParser.AddExprContext) -> Any:
        result = self.visit(ctx.mulExpr(0))
        children = list(ctx.getChildren())

        op_idx = 1
        for i in range(1, len(ctx.mulExpr())):
            # Find the operator
            while op_idx < len(children):
                child = children[op_idx]
                token = getattr(child, "symbol", None)
                if token and token.type in (
                    BusinessRulesParser.PLUS,
                    BusinessRulesParser.MINUS,
                ):
                    break
                op_idx += 1

            op = children[op_idx]
            op_idx += 1
            operand = self.visit(ctx.mulExpr(i))

            if op.symbol.type == BusinessRulesParser.PLUS:
                result = result + operand
            else:
                result = result - operand

        return result

    def visitMulExpr(self, ctx: BusinessRulesParser.MulExprContext) -> Any:
        result = self.visit(ctx.unaryExpr(0))
        children = list(ctx.getChildren())

        op_idx = 1
        for i in range(1, len(ctx.unaryExpr())):
            # Find the operator
            while op_idx < len(children):
                child = children[op_idx]
                token = getattr(child, "symbol", None)
                if token and token.type in (
                    BusinessRulesParser.STAR,
                    BusinessRulesParser.SLASH,
                    BusinessRulesParser.MOD,
                ):
                    break
                op_idx += 1

            op = children[op_idx]
            op_idx += 1
            operand = self.visit(ctx.unaryExpr(i))

            if op.symbol.type == BusinessRulesParser.STAR:
                result = result * operand
            elif op.symbol.type == BusinessRulesParser.SLASH:
                result = result / operand
            else:
                result = result % operand

        return result

    def visitUnaryExpr(self, ctx: BusinessRulesParser.UnaryExprContext) -> Any:
        if ctx.MINUS():
            return -self.visit(ctx.unaryExpr())
        return self.visit(ctx.primary())

    def visitPrimary(self, ctx: BusinessRulesParser.PrimaryContext) -> Any:
        if ctx.LPAREN():
            return self.visit(ctx.orExpr())
        elif ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.functionCall():
            return self.visit(ctx.functionCall())
        elif ctx.path():
            return self.visit(ctx.path())
        elif ctx.workflowCall():
            return self.visit(ctx.workflowCall())

    def visitFunctionCall(self, ctx: BusinessRulesParser.FunctionCallContext) -> Any:
        """Handle built-in function calls like lower(), len(), int()."""
        func_name = ctx.IDENTIFIER().getText()

        if func_name not in BUILTIN_FUNCTIONS:
            raise EvaluationError("", f"Unknown function: {func_name}")

        # Evaluate arguments
        args = [self.visit(expr) for expr in ctx.orExpr()]

        func = BUILTIN_FUNCTIONS[func_name]
        try:
            return func(*args)
        except Exception as e:
            raise EvaluationError("", f"Error in {func_name}(): {e}") from e

    def visitLiteral(self, ctx: BusinessRulesParser.LiteralContext) -> Any:
        if ctx.NUMBER():
            text = ctx.NUMBER().getText()
            return float(text) if "." in text else int(text)
        elif ctx.STRING():
            text = ctx.STRING().getText()
            # Handle escape sequences
            return text[1:-1].replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"').replace("\\'", "'").replace("\\\\", "\\")
        elif ctx.TRUE():
            return True
        elif ctx.FALSE():
            return False
        elif ctx.NONE():
            return None
        elif ctx.list_():
            return self.visit(ctx.list_())

    def visitList_(self, ctx: BusinessRulesParser.List_Context) -> list:
        return [self.visit(expr) for expr in ctx.orExpr()]

    def visitPath(self, ctx: BusinessRulesParser.PathContext) -> Any:
        path_parts, null_safe_indices = self._get_path_parts(ctx)
        return self.resolver.resolve(path_parts, null_safe_indices)

    def visitWorkflowCall(self, ctx: BusinessRulesParser.WorkflowCallContext) -> Any:
        workflow_name = ctx.STRING().getText()[1:-1]  # Remove quotes

        if workflow_name not in self.workflows:
            raise WorkflowNotFoundError(workflow_name)

        workflow = self.workflows[workflow_name]

        # Get the callable (handle Workflow wrapper)
        if hasattr(workflow, "fn"):
            fn = workflow.fn
        else:
            fn = workflow

        # Evaluate arguments
        args = [self.visit(expr) for expr in ctx.orExpr()]

        # Call with entity as first argument, then any additional args
        return fn(self.entity, *args)

    def visitActions(self, ctx: BusinessRulesParser.ActionsContext) -> None:
        for action in ctx.action():
            self.visit(action)
            if self._has_returned:
                break

    def visitAction(self, ctx: BusinessRulesParser.ActionContext) -> None:
        if ctx.returnStmt():
            self.visit(ctx.returnStmt())
        elif ctx.assignment():
            self.visit(ctx.assignment())
        elif ctx.workflowCall():
            self.visit(ctx.workflowCall())

    def visitReturnStmt(self, ctx: BusinessRulesParser.ReturnStmtContext) -> None:
        value = self.visit(ctx.orExpr())
        self._return_value = value
        self._has_returned = True
        raise ReturnValue(value)

    def visitAssignment(self, ctx: BusinessRulesParser.AssignmentContext) -> None:
        path_parts, _ = self._get_path_parts(ctx.path())
        value = self.visit(ctx.orExpr())
        assign_op = ctx.assignOp()

        if assign_op.ASSIGN():
            self.resolver.assign(path_parts, value)
        else:
            # Compound assignment - need to read current value first
            current = self.resolver.resolve(path_parts)
            if assign_op.PLUS_ASSIGN():
                new_value = current + value
            elif assign_op.MINUS_ASSIGN():
                new_value = current - value
            elif assign_op.STAR_ASSIGN():
                new_value = current * value
            elif assign_op.SLASH_ASSIGN():
                new_value = current / value
            else:
                new_value = value
            self.resolver.assign(path_parts, new_value)

    def _get_path_parts(
        self, ctx: BusinessRulesParser.PathContext
    ) -> tuple[list[str | int], set[int]]:
        """Convert a path context to a list of parts for the resolver.

        Returns:
            Tuple of (parts list, null_safe_indices set)
        """
        parts: list[str | int] = [ctx.IDENTIFIER().getText()]
        null_safe_indices: set[int] = set()

        for segment in ctx.pathSegment():
            if segment.NULL_SAFE_DOT():
                null_safe_indices.add(len(parts))
                parts.append(segment.IDENTIFIER().getText())
            elif segment.DOT():
                parts.append(segment.IDENTIFIER().getText())
            elif segment.LBRACKET():
                # Evaluate the expression inside brackets
                index = self.visit(segment.orExpr())
                if isinstance(index, (int, float)):
                    parts.append(int(index))
                else:
                    parts.append(index)

        return parts, null_safe_indices


def parse_rule(rule_text: str, entity_name: str = "entity") -> ParsedRule:
    """
    Parse a rule string and return a ParsedRule with analysis.

    Args:
        rule_text: The rule string to parse
        entity_name: The name of the entity variable (default: "entity").
                    Used to normalize paths in dependency analysis.

    Returns:
        ParsedRule with parse tree and read/write analysis

    Raises:
        RuleSyntaxError: If the rule cannot be parsed
    """
    input_stream = InputStream(rule_text)
    lexer = BusinessRulesLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = BusinessRulesParser(token_stream)

    # Remove default error listeners and add our own
    error_listener = RuleSyntaxErrorListener(rule_text)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = parser.rule_()

    if error_listener.errors:
        line, column, msg = error_listener.errors[0]
        raise RuleSyntaxError(rule_text, msg, line, column)

    # Analyze the rule for reads/writes
    analyzer = RuleAnalyzer(entity_name)
    analyzer.visit(tree)

    return ParsedRule(
        rule_text=rule_text,
        tree=tree,
        reads=analyzer.reads,
        writes=analyzer.writes,
        workflow_calls=analyzer.workflow_calls,
    )
