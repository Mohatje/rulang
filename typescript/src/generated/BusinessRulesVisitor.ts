// @ts-nocheck
// Generated from BusinessRules.g4 by ANTLR 4.13.2

import {ParseTreeVisitor} from 'antlr4';


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
 * This interface defines a complete generic visitor for a parse tree produced
 * by `BusinessRulesParser`.
 *
 * @param <Result> The return type of the visit operation. Use `void` for
 * operations with no return type.
 */
export default class BusinessRulesVisitor<Result> extends ParseTreeVisitor<Result> {
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.rule_`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitRule_?: (ctx: Rule_Context) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.condition`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitCondition?: (ctx: ConditionContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.orExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitOrExpr?: (ctx: OrExprContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.andExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitAndExpr?: (ctx: AndExprContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.notExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitNotExpr?: (ctx: NotExprContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.comparison`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitComparison?: (ctx: ComparisonContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.nullCoalesce`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitNullCoalesce?: (ctx: NullCoalesceContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.addExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitAddExpr?: (ctx: AddExprContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.mulExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitMulExpr?: (ctx: MulExprContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.unaryExpr`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitUnaryExpr?: (ctx: UnaryExprContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.primary`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitPrimary?: (ctx: PrimaryContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.functionCall`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitFunctionCall?: (ctx: FunctionCallContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.literal`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitLiteral?: (ctx: LiteralContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.list_`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitList_?: (ctx: List_Context) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.path`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitPath?: (ctx: PathContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.pathSegment`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitPathSegment?: (ctx: PathSegmentContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.workflowCall`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitWorkflowCall?: (ctx: WorkflowCallContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.actions`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitActions?: (ctx: ActionsContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.action`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitAction?: (ctx: ActionContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.returnStmt`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitReturnStmt?: (ctx: ReturnStmtContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.assignment`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitAssignment?: (ctx: AssignmentContext) => Result;
	/**
	 * Visit a parse tree produced by `BusinessRulesParser.assignOp`.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	visitAssignOp?: (ctx: AssignOpContext) => Result;
}

