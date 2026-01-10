# Generated from src/rule_interpreter/grammar/BusinessRules.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .BusinessRulesParser import BusinessRulesParser
else:
    from BusinessRulesParser import BusinessRulesParser

# This class defines a complete generic visitor for a parse tree produced by BusinessRulesParser.

class BusinessRulesVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by BusinessRulesParser#rule_.
    def visitRule_(self, ctx:BusinessRulesParser.Rule_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#condition.
    def visitCondition(self, ctx:BusinessRulesParser.ConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#orExpr.
    def visitOrExpr(self, ctx:BusinessRulesParser.OrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#andExpr.
    def visitAndExpr(self, ctx:BusinessRulesParser.AndExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#notExpr.
    def visitNotExpr(self, ctx:BusinessRulesParser.NotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#comparison.
    def visitComparison(self, ctx:BusinessRulesParser.ComparisonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#nullCoalesce.
    def visitNullCoalesce(self, ctx:BusinessRulesParser.NullCoalesceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#addExpr.
    def visitAddExpr(self, ctx:BusinessRulesParser.AddExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#mulExpr.
    def visitMulExpr(self, ctx:BusinessRulesParser.MulExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#unaryExpr.
    def visitUnaryExpr(self, ctx:BusinessRulesParser.UnaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#primary.
    def visitPrimary(self, ctx:BusinessRulesParser.PrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#functionCall.
    def visitFunctionCall(self, ctx:BusinessRulesParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#literal.
    def visitLiteral(self, ctx:BusinessRulesParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#list_.
    def visitList_(self, ctx:BusinessRulesParser.List_Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#path.
    def visitPath(self, ctx:BusinessRulesParser.PathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#pathSegment.
    def visitPathSegment(self, ctx:BusinessRulesParser.PathSegmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#workflowCall.
    def visitWorkflowCall(self, ctx:BusinessRulesParser.WorkflowCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#actions.
    def visitActions(self, ctx:BusinessRulesParser.ActionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#action.
    def visitAction(self, ctx:BusinessRulesParser.ActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#returnStmt.
    def visitReturnStmt(self, ctx:BusinessRulesParser.ReturnStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#assignment.
    def visitAssignment(self, ctx:BusinessRulesParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by BusinessRulesParser#assignOp.
    def visitAssignOp(self, ctx:BusinessRulesParser.AssignOpContext):
        return self.visitChildren(ctx)



del BusinessRulesParser