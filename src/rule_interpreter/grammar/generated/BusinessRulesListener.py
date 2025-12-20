# Generated from src/rule_interpreter/grammar/BusinessRules.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .BusinessRulesParser import BusinessRulesParser
else:
    from BusinessRulesParser import BusinessRulesParser

# This class defines a complete listener for a parse tree produced by BusinessRulesParser.
class BusinessRulesListener(ParseTreeListener):

    # Enter a parse tree produced by BusinessRulesParser#rule_.
    def enterRule_(self, ctx:BusinessRulesParser.Rule_Context):
        pass

    # Exit a parse tree produced by BusinessRulesParser#rule_.
    def exitRule_(self, ctx:BusinessRulesParser.Rule_Context):
        pass


    # Enter a parse tree produced by BusinessRulesParser#condition.
    def enterCondition(self, ctx:BusinessRulesParser.ConditionContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#condition.
    def exitCondition(self, ctx:BusinessRulesParser.ConditionContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#orExpr.
    def enterOrExpr(self, ctx:BusinessRulesParser.OrExprContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#orExpr.
    def exitOrExpr(self, ctx:BusinessRulesParser.OrExprContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#andExpr.
    def enterAndExpr(self, ctx:BusinessRulesParser.AndExprContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#andExpr.
    def exitAndExpr(self, ctx:BusinessRulesParser.AndExprContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#notExpr.
    def enterNotExpr(self, ctx:BusinessRulesParser.NotExprContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#notExpr.
    def exitNotExpr(self, ctx:BusinessRulesParser.NotExprContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#comparison.
    def enterComparison(self, ctx:BusinessRulesParser.ComparisonContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#comparison.
    def exitComparison(self, ctx:BusinessRulesParser.ComparisonContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#addExpr.
    def enterAddExpr(self, ctx:BusinessRulesParser.AddExprContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#addExpr.
    def exitAddExpr(self, ctx:BusinessRulesParser.AddExprContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#mulExpr.
    def enterMulExpr(self, ctx:BusinessRulesParser.MulExprContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#mulExpr.
    def exitMulExpr(self, ctx:BusinessRulesParser.MulExprContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#unaryExpr.
    def enterUnaryExpr(self, ctx:BusinessRulesParser.UnaryExprContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#unaryExpr.
    def exitUnaryExpr(self, ctx:BusinessRulesParser.UnaryExprContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#primary.
    def enterPrimary(self, ctx:BusinessRulesParser.PrimaryContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#primary.
    def exitPrimary(self, ctx:BusinessRulesParser.PrimaryContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#literal.
    def enterLiteral(self, ctx:BusinessRulesParser.LiteralContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#literal.
    def exitLiteral(self, ctx:BusinessRulesParser.LiteralContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#list_.
    def enterList_(self, ctx:BusinessRulesParser.List_Context):
        pass

    # Exit a parse tree produced by BusinessRulesParser#list_.
    def exitList_(self, ctx:BusinessRulesParser.List_Context):
        pass


    # Enter a parse tree produced by BusinessRulesParser#path.
    def enterPath(self, ctx:BusinessRulesParser.PathContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#path.
    def exitPath(self, ctx:BusinessRulesParser.PathContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#workflowCall.
    def enterWorkflowCall(self, ctx:BusinessRulesParser.WorkflowCallContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#workflowCall.
    def exitWorkflowCall(self, ctx:BusinessRulesParser.WorkflowCallContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#actions.
    def enterActions(self, ctx:BusinessRulesParser.ActionsContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#actions.
    def exitActions(self, ctx:BusinessRulesParser.ActionsContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#action.
    def enterAction(self, ctx:BusinessRulesParser.ActionContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#action.
    def exitAction(self, ctx:BusinessRulesParser.ActionContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#returnStmt.
    def enterReturnStmt(self, ctx:BusinessRulesParser.ReturnStmtContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#returnStmt.
    def exitReturnStmt(self, ctx:BusinessRulesParser.ReturnStmtContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#assignment.
    def enterAssignment(self, ctx:BusinessRulesParser.AssignmentContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#assignment.
    def exitAssignment(self, ctx:BusinessRulesParser.AssignmentContext):
        pass


    # Enter a parse tree produced by BusinessRulesParser#assignOp.
    def enterAssignOp(self, ctx:BusinessRulesParser.AssignOpContext):
        pass

    # Exit a parse tree produced by BusinessRulesParser#assignOp.
    def exitAssignOp(self, ctx:BusinessRulesParser.AssignOpContext):
        pass



del BusinessRulesParser