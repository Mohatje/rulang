"""
AST visitor/interpreter for business rules.

Walks the ANTLR parse tree to:
- Evaluate conditions
- Execute actions (mutations, workflow calls, returns)
- Track read/write sets for dependency analysis
"""

from dataclasses import dataclass, field
from typing import Any, Callable

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from rule_interpreter.grammar.generated.BusinessRulesLexer import BusinessRulesLexer
from rule_interpreter.grammar.generated.BusinessRulesParser import BusinessRulesParser
from rule_interpreter.grammar.generated.BusinessRulesVisitor import (
    BusinessRulesVisitor as BaseVisitor,
)
from rule_interpreter.exceptions import (
    EvaluationError,
    PathResolutionError,
    RuleSyntaxError,
    WorkflowNotFoundError,
)
from rule_interpreter.path_resolver import PathResolver


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

    def __init__(self):
        self.reads: set[str] = set()
        self.writes: set[str] = set()
        self.workflow_calls: set[str] = set()
        self._in_condition = False
        self._in_assignment_target = False

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
        """Convert a path context to a string representation."""
        parts = []
        children = list(ctx.getChildren())
        i = 0
        while i < len(children):
            child = children[i]
            token_type = getattr(child, "symbol", None)
            if token_type:
                if token_type.type == BusinessRulesParser.IDENTIFIER:
                    parts.append(child.getText())
                elif token_type.type == BusinessRulesParser.DOT:
                    i += 1  # Skip dot, next is identifier
                    if i < len(children):
                        parts.append(children[i].getText())
                elif token_type.type == BusinessRulesParser.LBRACKET:
                    # For analysis, we just note that there's indexing
                    # We can't know the exact index statically
                    parts.append("[*]")
                    # Skip until RBRACKET
                    while i < len(children):
                        child = children[i]
                        token_type = getattr(child, "symbol", None)
                        if token_type and token_type.type == BusinessRulesParser.RBRACKET:
                            break
                        i += 1
            i += 1

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
        left = self.visit(ctx.addExpr(0))

        if len(ctx.addExpr()) == 1:
            return left

        right = self.visit(ctx.addExpr(1))

        if ctx.EQ():
            return left == right
        elif ctx.NEQ():
            return left != right
        elif ctx.LT():
            return left < right
        elif ctx.GT():
            return left > right
        elif ctx.LTE():
            return left <= right
        elif ctx.GTE():
            return left >= right
        elif ctx.IN():
            return left in right
        elif ctx.NOT_IN():
            return left not in right

        return left

    def visitAddExpr(self, ctx: BusinessRulesParser.AddExprContext) -> Any:
        result = self.visit(ctx.mulExpr(0))
        children = list(ctx.getChildren())

        op_idx = 1
        for i in range(1, len(ctx.mulExpr())):
            # Find the operator
            while op_idx < len(children):
                child = children[op_idx]
                token = getattr(child, "symbol", None)
                if token and token.type in (BusinessRulesParser.PLUS, BusinessRulesParser.MINUS):
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
        elif ctx.path():
            return self.visit(ctx.path())
        elif ctx.workflowCall():
            return self.visit(ctx.workflowCall())

    def visitLiteral(self, ctx: BusinessRulesParser.LiteralContext) -> Any:
        if ctx.NUMBER():
            text = ctx.NUMBER().getText()
            return float(text) if "." in text else int(text)
        elif ctx.STRING():
            text = ctx.STRING().getText()
            return text[1:-1]  # Remove quotes
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
        path_parts = self._get_path_parts(ctx)
        return self.resolver.resolve(path_parts)

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
        path_parts = self._get_path_parts(ctx.path())
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

    def _get_path_parts(self, ctx: BusinessRulesParser.PathContext) -> list[str | int]:
        """Convert a path context to a list of parts for the resolver."""
        parts: list[str | int] = []
        children = list(ctx.getChildren())
        i = 0

        while i < len(children):
            child = children[i]
            token = getattr(child, "symbol", None)

            if token:
                if token.type == BusinessRulesParser.IDENTIFIER:
                    parts.append(child.getText())
                elif token.type == BusinessRulesParser.DOT:
                    pass  # Skip, next will be identifier
                elif token.type == BusinessRulesParser.LBRACKET:
                    # Find the expression inside brackets
                    i += 1
                    if i < len(children):
                        expr_ctx = children[i]
                        if hasattr(expr_ctx, "getRuleIndex"):
                            # It's an expression context
                            index = self.visit(expr_ctx)
                            if isinstance(index, (int, float)):
                                parts.append(int(index))
                            else:
                                parts.append(index)
                    # Skip to RBRACKET
                    while i < len(children):
                        child = children[i]
                        token = getattr(child, "symbol", None)
                        if token and token.type == BusinessRulesParser.RBRACKET:
                            break
                        i += 1
            i += 1

        return parts


def parse_rule(rule_text: str) -> ParsedRule:
    """
    Parse a rule string and return a ParsedRule with analysis.

    Args:
        rule_text: The rule string to parse

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
    analyzer = RuleAnalyzer()
    analyzer.visit(tree)

    return ParsedRule(
        rule_text=rule_text,
        tree=tree,
        reads=analyzer.reads,
        writes=analyzer.writes,
        workflow_calls=analyzer.workflow_calls,
    )

