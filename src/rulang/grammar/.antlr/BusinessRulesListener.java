// Generated from /home/mo/Github/rule-interpreter/src/rule_interpreter/grammar/BusinessRules.g4 by ANTLR 4.9.2
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link BusinessRulesParser}.
 */
public interface BusinessRulesListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#rule_}.
	 * @param ctx the parse tree
	 */
	void enterRule_(BusinessRulesParser.Rule_Context ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#rule_}.
	 * @param ctx the parse tree
	 */
	void exitRule_(BusinessRulesParser.Rule_Context ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#condition}.
	 * @param ctx the parse tree
	 */
	void enterCondition(BusinessRulesParser.ConditionContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#condition}.
	 * @param ctx the parse tree
	 */
	void exitCondition(BusinessRulesParser.ConditionContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#orExpr}.
	 * @param ctx the parse tree
	 */
	void enterOrExpr(BusinessRulesParser.OrExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#orExpr}.
	 * @param ctx the parse tree
	 */
	void exitOrExpr(BusinessRulesParser.OrExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#andExpr}.
	 * @param ctx the parse tree
	 */
	void enterAndExpr(BusinessRulesParser.AndExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#andExpr}.
	 * @param ctx the parse tree
	 */
	void exitAndExpr(BusinessRulesParser.AndExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#notExpr}.
	 * @param ctx the parse tree
	 */
	void enterNotExpr(BusinessRulesParser.NotExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#notExpr}.
	 * @param ctx the parse tree
	 */
	void exitNotExpr(BusinessRulesParser.NotExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#comparison}.
	 * @param ctx the parse tree
	 */
	void enterComparison(BusinessRulesParser.ComparisonContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#comparison}.
	 * @param ctx the parse tree
	 */
	void exitComparison(BusinessRulesParser.ComparisonContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#addExpr}.
	 * @param ctx the parse tree
	 */
	void enterAddExpr(BusinessRulesParser.AddExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#addExpr}.
	 * @param ctx the parse tree
	 */
	void exitAddExpr(BusinessRulesParser.AddExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#mulExpr}.
	 * @param ctx the parse tree
	 */
	void enterMulExpr(BusinessRulesParser.MulExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#mulExpr}.
	 * @param ctx the parse tree
	 */
	void exitMulExpr(BusinessRulesParser.MulExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#unaryExpr}.
	 * @param ctx the parse tree
	 */
	void enterUnaryExpr(BusinessRulesParser.UnaryExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#unaryExpr}.
	 * @param ctx the parse tree
	 */
	void exitUnaryExpr(BusinessRulesParser.UnaryExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterPrimary(BusinessRulesParser.PrimaryContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitPrimary(BusinessRulesParser.PrimaryContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#literal}.
	 * @param ctx the parse tree
	 */
	void enterLiteral(BusinessRulesParser.LiteralContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#literal}.
	 * @param ctx the parse tree
	 */
	void exitLiteral(BusinessRulesParser.LiteralContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#list_}.
	 * @param ctx the parse tree
	 */
	void enterList_(BusinessRulesParser.List_Context ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#list_}.
	 * @param ctx the parse tree
	 */
	void exitList_(BusinessRulesParser.List_Context ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#path}.
	 * @param ctx the parse tree
	 */
	void enterPath(BusinessRulesParser.PathContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#path}.
	 * @param ctx the parse tree
	 */
	void exitPath(BusinessRulesParser.PathContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#workflowCall}.
	 * @param ctx the parse tree
	 */
	void enterWorkflowCall(BusinessRulesParser.WorkflowCallContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#workflowCall}.
	 * @param ctx the parse tree
	 */
	void exitWorkflowCall(BusinessRulesParser.WorkflowCallContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#actions}.
	 * @param ctx the parse tree
	 */
	void enterActions(BusinessRulesParser.ActionsContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#actions}.
	 * @param ctx the parse tree
	 */
	void exitActions(BusinessRulesParser.ActionsContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#action}.
	 * @param ctx the parse tree
	 */
	void enterAction(BusinessRulesParser.ActionContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#action}.
	 * @param ctx the parse tree
	 */
	void exitAction(BusinessRulesParser.ActionContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#returnStmt}.
	 * @param ctx the parse tree
	 */
	void enterReturnStmt(BusinessRulesParser.ReturnStmtContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#returnStmt}.
	 * @param ctx the parse tree
	 */
	void exitReturnStmt(BusinessRulesParser.ReturnStmtContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#assignment}.
	 * @param ctx the parse tree
	 */
	void enterAssignment(BusinessRulesParser.AssignmentContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#assignment}.
	 * @param ctx the parse tree
	 */
	void exitAssignment(BusinessRulesParser.AssignmentContext ctx);
	/**
	 * Enter a parse tree produced by {@link BusinessRulesParser#assignOp}.
	 * @param ctx the parse tree
	 */
	void enterAssignOp(BusinessRulesParser.AssignOpContext ctx);
	/**
	 * Exit a parse tree produced by {@link BusinessRulesParser#assignOp}.
	 * @param ctx the parse tree
	 */
	void exitAssignOp(BusinessRulesParser.AssignOpContext ctx);
}