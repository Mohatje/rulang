// @ts-nocheck
// Generated from BusinessRules.g4 by ANTLR 4.13.2

import * as antlr4 from "antlr4";
const {
  ParseTreeListener
} = antlr4;


import { Rule_Context } from "./BusinessRulesParser.js";
import { ConditionContext } from "./BusinessRulesParser.js";
import { OrExprContext } from "./BusinessRulesParser.js";
import { AndExprContext } from "./BusinessRulesParser.js";
import { NotExprContext } from "./BusinessRulesParser.js";
import { ComparisonContext } from "./BusinessRulesParser.js";
import { NullCoalesceContext } from "./BusinessRulesParser.js";
import { AddExprContext } from "./BusinessRulesParser.js";
import { MulExprContext } from "./BusinessRulesParser.js";
import { UnaryExprContext } from "./BusinessRulesParser.js";
import { PrimaryContext } from "./BusinessRulesParser.js";
import { FunctionCallContext } from "./BusinessRulesParser.js";
import { LiteralContext } from "./BusinessRulesParser.js";
import { List_Context } from "./BusinessRulesParser.js";
import { PathContext } from "./BusinessRulesParser.js";
import { PathSegmentContext } from "./BusinessRulesParser.js";
import { WorkflowCallContext } from "./BusinessRulesParser.js";
import { ActionsContext } from "./BusinessRulesParser.js";
import { ActionContext } from "./BusinessRulesParser.js";
import { ReturnStmtContext } from "./BusinessRulesParser.js";
import { AssignmentContext } from "./BusinessRulesParser.js";
import { AssignOpContext } from "./BusinessRulesParser.js";


/**
 * This interface defines a complete listener for a parse tree produced by
 * `BusinessRulesParser`.
 */
export default class BusinessRulesListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.rule_`.
	 * @param ctx the parse tree
	 */
	enterRule_?: (ctx: Rule_Context) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.rule_`.
	 * @param ctx the parse tree
	 */
	exitRule_?: (ctx: Rule_Context) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.condition`.
	 * @param ctx the parse tree
	 */
	enterCondition?: (ctx: ConditionContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.condition`.
	 * @param ctx the parse tree
	 */
	exitCondition?: (ctx: ConditionContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.orExpr`.
	 * @param ctx the parse tree
	 */
	enterOrExpr?: (ctx: OrExprContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.orExpr`.
	 * @param ctx the parse tree
	 */
	exitOrExpr?: (ctx: OrExprContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.andExpr`.
	 * @param ctx the parse tree
	 */
	enterAndExpr?: (ctx: AndExprContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.andExpr`.
	 * @param ctx the parse tree
	 */
	exitAndExpr?: (ctx: AndExprContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.notExpr`.
	 * @param ctx the parse tree
	 */
	enterNotExpr?: (ctx: NotExprContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.notExpr`.
	 * @param ctx the parse tree
	 */
	exitNotExpr?: (ctx: NotExprContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.comparison`.
	 * @param ctx the parse tree
	 */
	enterComparison?: (ctx: ComparisonContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.comparison`.
	 * @param ctx the parse tree
	 */
	exitComparison?: (ctx: ComparisonContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.nullCoalesce`.
	 * @param ctx the parse tree
	 */
	enterNullCoalesce?: (ctx: NullCoalesceContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.nullCoalesce`.
	 * @param ctx the parse tree
	 */
	exitNullCoalesce?: (ctx: NullCoalesceContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.addExpr`.
	 * @param ctx the parse tree
	 */
	enterAddExpr?: (ctx: AddExprContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.addExpr`.
	 * @param ctx the parse tree
	 */
	exitAddExpr?: (ctx: AddExprContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.mulExpr`.
	 * @param ctx the parse tree
	 */
	enterMulExpr?: (ctx: MulExprContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.mulExpr`.
	 * @param ctx the parse tree
	 */
	exitMulExpr?: (ctx: MulExprContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.unaryExpr`.
	 * @param ctx the parse tree
	 */
	enterUnaryExpr?: (ctx: UnaryExprContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.unaryExpr`.
	 * @param ctx the parse tree
	 */
	exitUnaryExpr?: (ctx: UnaryExprContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.primary`.
	 * @param ctx the parse tree
	 */
	enterPrimary?: (ctx: PrimaryContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.primary`.
	 * @param ctx the parse tree
	 */
	exitPrimary?: (ctx: PrimaryContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.functionCall`.
	 * @param ctx the parse tree
	 */
	enterFunctionCall?: (ctx: FunctionCallContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.functionCall`.
	 * @param ctx the parse tree
	 */
	exitFunctionCall?: (ctx: FunctionCallContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.literal`.
	 * @param ctx the parse tree
	 */
	enterLiteral?: (ctx: LiteralContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.literal`.
	 * @param ctx the parse tree
	 */
	exitLiteral?: (ctx: LiteralContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.list_`.
	 * @param ctx the parse tree
	 */
	enterList_?: (ctx: List_Context) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.list_`.
	 * @param ctx the parse tree
	 */
	exitList_?: (ctx: List_Context) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.path`.
	 * @param ctx the parse tree
	 */
	enterPath?: (ctx: PathContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.path`.
	 * @param ctx the parse tree
	 */
	exitPath?: (ctx: PathContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.pathSegment`.
	 * @param ctx the parse tree
	 */
	enterPathSegment?: (ctx: PathSegmentContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.pathSegment`.
	 * @param ctx the parse tree
	 */
	exitPathSegment?: (ctx: PathSegmentContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.workflowCall`.
	 * @param ctx the parse tree
	 */
	enterWorkflowCall?: (ctx: WorkflowCallContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.workflowCall`.
	 * @param ctx the parse tree
	 */
	exitWorkflowCall?: (ctx: WorkflowCallContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.actions`.
	 * @param ctx the parse tree
	 */
	enterActions?: (ctx: ActionsContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.actions`.
	 * @param ctx the parse tree
	 */
	exitActions?: (ctx: ActionsContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.action`.
	 * @param ctx the parse tree
	 */
	enterAction?: (ctx: ActionContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.action`.
	 * @param ctx the parse tree
	 */
	exitAction?: (ctx: ActionContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.returnStmt`.
	 * @param ctx the parse tree
	 */
	enterReturnStmt?: (ctx: ReturnStmtContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.returnStmt`.
	 * @param ctx the parse tree
	 */
	exitReturnStmt?: (ctx: ReturnStmtContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.assignment`.
	 * @param ctx the parse tree
	 */
	enterAssignment?: (ctx: AssignmentContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.assignment`.
	 * @param ctx the parse tree
	 */
	exitAssignment?: (ctx: AssignmentContext) => void;
	/**
	 * Enter a parse tree produced by `BusinessRulesParser.assignOp`.
	 * @param ctx the parse tree
	 */
	enterAssignOp?: (ctx: AssignOpContext) => void;
	/**
	 * Exit a parse tree produced by `BusinessRulesParser.assignOp`.
	 * @param ctx the parse tree
	 */
	exitAssignOp?: (ctx: AssignOpContext) => void;
}

