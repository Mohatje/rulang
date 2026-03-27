// @ts-nocheck
// Generated from BusinessRules.g4 by ANTLR 4.13.2
// noinspection ES6UnusedImports,JSUnusedGlobalSymbols,JSUnusedLocalSymbols

import {
	ATN,
	ATNDeserializer, DecisionState, DFA, FailedPredicateException,
	RecognitionException, NoViableAltException, BailErrorStrategy,
	Parser, ParserATNSimulator,
	RuleContext, ParserRuleContext, PredictionMode, PredictionContextCache,
	TerminalNode, RuleNode,
	Token, TokenStream,
	Interval, IntervalSet
} from 'antlr4';
import BusinessRulesListener from "./BusinessRulesListener.js";
import BusinessRulesVisitor from "./BusinessRulesVisitor.js";

// for running tests with parameters, TODO: discuss strategy for typed parameters in CI
// eslint-disable-next-line no-unused-vars
type int = number;

export default class BusinessRulesParser extends Parser {
	public static readonly TRUE = 1;
	public static readonly FALSE = 2;
	public static readonly NONE = 3;
	public static readonly AND = 4;
	public static readonly OR = 5;
	public static readonly NOT = 6;
	public static readonly IN = 7;
	public static readonly NOT_IN = 8;
	public static readonly RET = 9;
	public static readonly WORKFLOW = 10;
	public static readonly CONTAINS_ANY = 11;
	public static readonly CONTAINS_ALL = 12;
	public static readonly NOT_CONTAINS = 13;
	public static readonly CONTAINS = 14;
	public static readonly STARTS_WITH = 15;
	public static readonly ENDS_WITH = 16;
	public static readonly MATCHES = 17;
	public static readonly IS_EMPTY = 18;
	public static readonly EXISTS = 19;
	public static readonly ARROW = 20;
	public static readonly EQ = 21;
	public static readonly NEQ = 22;
	public static readonly LTE = 23;
	public static readonly GTE = 24;
	public static readonly LT = 25;
	public static readonly GT = 26;
	public static readonly PLUS = 27;
	public static readonly MINUS = 28;
	public static readonly STAR = 29;
	public static readonly SLASH = 30;
	public static readonly MOD = 31;
	public static readonly ASSIGN = 32;
	public static readonly PLUS_ASSIGN = 33;
	public static readonly MINUS_ASSIGN = 34;
	public static readonly STAR_ASSIGN = 35;
	public static readonly SLASH_ASSIGN = 36;
	public static readonly NULL_COALESCE = 37;
	public static readonly NULL_SAFE_DOT = 38;
	public static readonly LPAREN = 39;
	public static readonly RPAREN = 40;
	public static readonly LBRACKET = 41;
	public static readonly RBRACKET = 42;
	public static readonly DOT = 43;
	public static readonly COMMA = 44;
	public static readonly SEMICOLON = 45;
	public static readonly NUMBER = 46;
	public static readonly STRING = 47;
	public static readonly IDENTIFIER = 48;
	public static readonly WS = 49;
	public static readonly LINE_COMMENT = 50;
	public static override readonly EOF = Token.EOF;
	public static readonly RULE_rule_ = 0;
	public static readonly RULE_condition = 1;
	public static readonly RULE_orExpr = 2;
	public static readonly RULE_andExpr = 3;
	public static readonly RULE_notExpr = 4;
	public static readonly RULE_comparison = 5;
	public static readonly RULE_nullCoalesce = 6;
	public static readonly RULE_addExpr = 7;
	public static readonly RULE_mulExpr = 8;
	public static readonly RULE_unaryExpr = 9;
	public static readonly RULE_primary = 10;
	public static readonly RULE_functionCall = 11;
	public static readonly RULE_literal = 12;
	public static readonly RULE_list_ = 13;
	public static readonly RULE_path = 14;
	public static readonly RULE_pathSegment = 15;
	public static readonly RULE_workflowCall = 16;
	public static readonly RULE_actions = 17;
	public static readonly RULE_action = 18;
	public static readonly RULE_returnStmt = 19;
	public static readonly RULE_assignment = 20;
	public static readonly RULE_assignOp = 21;
	public static readonly literalNames: (string | null)[] = [ null, null, 
                                                            null, null, 
                                                            "'and'", "'or'", 
                                                            "'not'", "'in'", 
                                                            null, "'ret'", 
                                                            "'workflow'", 
                                                            "'contains_any'", 
                                                            "'contains_all'", 
                                                            null, "'contains'", 
                                                            null, null, 
                                                            "'matches'", 
                                                            null, "'exists'", 
                                                            "'=>'", "'=='", 
                                                            "'!='", "'<='", 
                                                            "'>='", "'<'", 
                                                            "'>'", "'+'", 
                                                            "'-'", "'*'", 
                                                            "'/'", "'%'", 
                                                            "'='", "'+='", 
                                                            "'-='", "'*='", 
                                                            "'/='", "'??'", 
                                                            "'?.'", "'('", 
                                                            "')'", "'['", 
                                                            "']'", "'.'", 
                                                            "','", "';'" ];
	public static readonly symbolicNames: (string | null)[] = [ null, "TRUE", 
                                                             "FALSE", "NONE", 
                                                             "AND", "OR", 
                                                             "NOT", "IN", 
                                                             "NOT_IN", "RET", 
                                                             "WORKFLOW", 
                                                             "CONTAINS_ANY", 
                                                             "CONTAINS_ALL", 
                                                             "NOT_CONTAINS", 
                                                             "CONTAINS", 
                                                             "STARTS_WITH", 
                                                             "ENDS_WITH", 
                                                             "MATCHES", 
                                                             "IS_EMPTY", 
                                                             "EXISTS", "ARROW", 
                                                             "EQ", "NEQ", 
                                                             "LTE", "GTE", 
                                                             "LT", "GT", 
                                                             "PLUS", "MINUS", 
                                                             "STAR", "SLASH", 
                                                             "MOD", "ASSIGN", 
                                                             "PLUS_ASSIGN", 
                                                             "MINUS_ASSIGN", 
                                                             "STAR_ASSIGN", 
                                                             "SLASH_ASSIGN", 
                                                             "NULL_COALESCE", 
                                                             "NULL_SAFE_DOT", 
                                                             "LPAREN", "RPAREN", 
                                                             "LBRACKET", 
                                                             "RBRACKET", 
                                                             "DOT", "COMMA", 
                                                             "SEMICOLON", 
                                                             "NUMBER", "STRING", 
                                                             "IDENTIFIER", 
                                                             "WS", "LINE_COMMENT" ];
	// tslint:disable:no-trailing-whitespace
	public static readonly ruleNames: string[] = [
		"rule_", "condition", "orExpr", "andExpr", "notExpr", "comparison", "nullCoalesce", 
		"addExpr", "mulExpr", "unaryExpr", "primary", "functionCall", "literal", 
		"list_", "path", "pathSegment", "workflowCall", "actions", "action", "returnStmt", 
		"assignment", "assignOp",
	];
	public get grammarFileName(): string { return "BusinessRules.g4"; }
	public get literalNames(): (string | null)[] { return BusinessRulesParser.literalNames; }
	public get symbolicNames(): (string | null)[] { return BusinessRulesParser.symbolicNames; }
	public get ruleNames(): string[] { return BusinessRulesParser.ruleNames; }
	public get serializedATN(): number[] { return BusinessRulesParser._serializedATN; }

	protected createFailedPredicateException(predicate?: string, message?: string): FailedPredicateException {
		return new FailedPredicateException(this, predicate, message);
	}

	constructor(input: TokenStream) {
		super(input);
		this._interp = new ParserATNSimulator(this, BusinessRulesParser._ATN, BusinessRulesParser.DecisionsToDFA, new PredictionContextCache());
	}
	// @RuleVersion(0)
	public rule_(): Rule_Context {
		let localctx: Rule_Context = new Rule_Context(this, this._ctx, this.state);
		this.enterRule(localctx, 0, BusinessRulesParser.RULE_rule_);
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 44;
			this.condition();
			this.state = 45;
			this.match(BusinessRulesParser.ARROW);
			this.state = 46;
			this.actions();
			this.state = 47;
			this.match(BusinessRulesParser.EOF);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public condition(): ConditionContext {
		let localctx: ConditionContext = new ConditionContext(this, this._ctx, this.state);
		this.enterRule(localctx, 2, BusinessRulesParser.RULE_condition);
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 49;
			this.orExpr();
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public orExpr(): OrExprContext {
		let localctx: OrExprContext = new OrExprContext(this, this._ctx, this.state);
		this.enterRule(localctx, 4, BusinessRulesParser.RULE_orExpr);
		let _la: number;
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 51;
			this.andExpr();
			this.state = 56;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la===5) {
				{
				{
				this.state = 52;
				this.match(BusinessRulesParser.OR);
				this.state = 53;
				this.andExpr();
				}
				}
				this.state = 58;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public andExpr(): AndExprContext {
		let localctx: AndExprContext = new AndExprContext(this, this._ctx, this.state);
		this.enterRule(localctx, 6, BusinessRulesParser.RULE_andExpr);
		let _la: number;
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 59;
			this.notExpr();
			this.state = 64;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la===4) {
				{
				{
				this.state = 60;
				this.match(BusinessRulesParser.AND);
				this.state = 61;
				this.notExpr();
				}
				}
				this.state = 66;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public notExpr(): NotExprContext {
		let localctx: NotExprContext = new NotExprContext(this, this._ctx, this.state);
		this.enterRule(localctx, 8, BusinessRulesParser.RULE_notExpr);
		try {
			this.state = 70;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case 6:
				this.enterOuterAlt(localctx, 1);
				{
				this.state = 67;
				this.match(BusinessRulesParser.NOT);
				this.state = 68;
				this.notExpr();
				}
				break;
			case 1:
			case 2:
			case 3:
			case 10:
			case 28:
			case 39:
			case 41:
			case 46:
			case 47:
			case 48:
				this.enterOuterAlt(localctx, 2);
				{
				this.state = 69;
				this.comparison();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public comparison(): ComparisonContext {
		let localctx: ComparisonContext = new ComparisonContext(this, this._ctx, this.state);
		this.enterRule(localctx, 10, BusinessRulesParser.RULE_comparison);
		let _la: number;
		try {
			this.state = 111;
			this._errHandler.sync(this);
			switch ( this._interp.adaptivePredict(this._input, 4, this._ctx) ) {
			case 1:
				this.enterOuterAlt(localctx, 1);
				{
				this.state = 72;
				this.nullCoalesce();
				this.state = 75;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
				if ((((_la) & ~0x1F) === 0 && ((1 << _la) & 132120960) !== 0)) {
					{
					this.state = 73;
					_la = this._input.LA(1);
					if(!((((_la) & ~0x1F) === 0 && ((1 << _la) & 132120960) !== 0))) {
					this._errHandler.recoverInline(this);
					}
					else {
						this._errHandler.reportMatch(this);
					    this.consume();
					}
					this.state = 74;
					this.nullCoalesce();
					}
				}

				}
				break;
			case 2:
				this.enterOuterAlt(localctx, 2);
				{
				this.state = 77;
				this.nullCoalesce();
				this.state = 78;
				this.match(BusinessRulesParser.CONTAINS);
				this.state = 79;
				this.nullCoalesce();
				}
				break;
			case 3:
				this.enterOuterAlt(localctx, 3);
				{
				this.state = 81;
				this.nullCoalesce();
				this.state = 82;
				this.match(BusinessRulesParser.NOT_CONTAINS);
				this.state = 83;
				this.nullCoalesce();
				}
				break;
			case 4:
				this.enterOuterAlt(localctx, 4);
				{
				this.state = 85;
				this.nullCoalesce();
				this.state = 86;
				this.match(BusinessRulesParser.STARTS_WITH);
				this.state = 87;
				this.nullCoalesce();
				}
				break;
			case 5:
				this.enterOuterAlt(localctx, 5);
				{
				this.state = 89;
				this.nullCoalesce();
				this.state = 90;
				this.match(BusinessRulesParser.ENDS_WITH);
				this.state = 91;
				this.nullCoalesce();
				}
				break;
			case 6:
				this.enterOuterAlt(localctx, 6);
				{
				this.state = 93;
				this.nullCoalesce();
				this.state = 94;
				this.match(BusinessRulesParser.MATCHES);
				this.state = 95;
				this.nullCoalesce();
				}
				break;
			case 7:
				this.enterOuterAlt(localctx, 7);
				{
				this.state = 97;
				this.nullCoalesce();
				this.state = 98;
				this.match(BusinessRulesParser.CONTAINS_ANY);
				this.state = 99;
				this.nullCoalesce();
				}
				break;
			case 8:
				this.enterOuterAlt(localctx, 8);
				{
				this.state = 101;
				this.nullCoalesce();
				this.state = 102;
				this.match(BusinessRulesParser.CONTAINS_ALL);
				this.state = 103;
				this.nullCoalesce();
				}
				break;
			case 9:
				this.enterOuterAlt(localctx, 9);
				{
				this.state = 105;
				this.nullCoalesce();
				this.state = 106;
				this.match(BusinessRulesParser.IS_EMPTY);
				}
				break;
			case 10:
				this.enterOuterAlt(localctx, 10);
				{
				this.state = 108;
				this.nullCoalesce();
				this.state = 109;
				this.match(BusinessRulesParser.EXISTS);
				}
				break;
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public nullCoalesce(): NullCoalesceContext {
		let localctx: NullCoalesceContext = new NullCoalesceContext(this, this._ctx, this.state);
		this.enterRule(localctx, 12, BusinessRulesParser.RULE_nullCoalesce);
		let _la: number;
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 113;
			this.addExpr();
			this.state = 118;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la===37) {
				{
				{
				this.state = 114;
				this.match(BusinessRulesParser.NULL_COALESCE);
				this.state = 115;
				this.addExpr();
				}
				}
				this.state = 120;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public addExpr(): AddExprContext {
		let localctx: AddExprContext = new AddExprContext(this, this._ctx, this.state);
		this.enterRule(localctx, 14, BusinessRulesParser.RULE_addExpr);
		let _la: number;
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 121;
			this.mulExpr();
			this.state = 126;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la===27 || _la===28) {
				{
				{
				this.state = 122;
				_la = this._input.LA(1);
				if(!(_la===27 || _la===28)) {
				this._errHandler.recoverInline(this);
				}
				else {
					this._errHandler.reportMatch(this);
				    this.consume();
				}
				this.state = 123;
				this.mulExpr();
				}
				}
				this.state = 128;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public mulExpr(): MulExprContext {
		let localctx: MulExprContext = new MulExprContext(this, this._ctx, this.state);
		this.enterRule(localctx, 16, BusinessRulesParser.RULE_mulExpr);
		let _la: number;
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 129;
			this.unaryExpr();
			this.state = 134;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while ((((_la) & ~0x1F) === 0 && ((1 << _la) & 3758096384) !== 0)) {
				{
				{
				this.state = 130;
				_la = this._input.LA(1);
				if(!((((_la) & ~0x1F) === 0 && ((1 << _la) & 3758096384) !== 0))) {
				this._errHandler.recoverInline(this);
				}
				else {
					this._errHandler.reportMatch(this);
				    this.consume();
				}
				this.state = 131;
				this.unaryExpr();
				}
				}
				this.state = 136;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public unaryExpr(): UnaryExprContext {
		let localctx: UnaryExprContext = new UnaryExprContext(this, this._ctx, this.state);
		this.enterRule(localctx, 18, BusinessRulesParser.RULE_unaryExpr);
		try {
			this.state = 140;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case 28:
				this.enterOuterAlt(localctx, 1);
				{
				this.state = 137;
				this.match(BusinessRulesParser.MINUS);
				this.state = 138;
				this.unaryExpr();
				}
				break;
			case 1:
			case 2:
			case 3:
			case 10:
			case 39:
			case 41:
			case 46:
			case 47:
			case 48:
				this.enterOuterAlt(localctx, 2);
				{
				this.state = 139;
				this.primary();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public primary(): PrimaryContext {
		let localctx: PrimaryContext = new PrimaryContext(this, this._ctx, this.state);
		this.enterRule(localctx, 20, BusinessRulesParser.RULE_primary);
		try {
			this.state = 150;
			this._errHandler.sync(this);
			switch ( this._interp.adaptivePredict(this._input, 9, this._ctx) ) {
			case 1:
				this.enterOuterAlt(localctx, 1);
				{
				this.state = 142;
				this.match(BusinessRulesParser.LPAREN);
				this.state = 143;
				this.orExpr();
				this.state = 144;
				this.match(BusinessRulesParser.RPAREN);
				}
				break;
			case 2:
				this.enterOuterAlt(localctx, 2);
				{
				this.state = 146;
				this.literal();
				}
				break;
			case 3:
				this.enterOuterAlt(localctx, 3);
				{
				this.state = 147;
				this.functionCall();
				}
				break;
			case 4:
				this.enterOuterAlt(localctx, 4);
				{
				this.state = 148;
				this.path();
				}
				break;
			case 5:
				this.enterOuterAlt(localctx, 5);
				{
				this.state = 149;
				this.workflowCall();
				}
				break;
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public functionCall(): FunctionCallContext {
		let localctx: FunctionCallContext = new FunctionCallContext(this, this._ctx, this.state);
		this.enterRule(localctx, 22, BusinessRulesParser.RULE_functionCall);
		let _la: number;
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 152;
			this.match(BusinessRulesParser.IDENTIFIER);
			this.state = 153;
			this.match(BusinessRulesParser.LPAREN);
			this.state = 162;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if ((((_la) & ~0x1F) === 0 && ((1 << _la) & 268436558) !== 0) || ((((_la - 39)) & ~0x1F) === 0 && ((1 << (_la - 39)) & 901) !== 0)) {
				{
				this.state = 154;
				this.orExpr();
				this.state = 159;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
				while (_la===44) {
					{
					{
					this.state = 155;
					this.match(BusinessRulesParser.COMMA);
					this.state = 156;
					this.orExpr();
					}
					}
					this.state = 161;
					this._errHandler.sync(this);
					_la = this._input.LA(1);
				}
				}
			}

			this.state = 164;
			this.match(BusinessRulesParser.RPAREN);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public literal(): LiteralContext {
		let localctx: LiteralContext = new LiteralContext(this, this._ctx, this.state);
		this.enterRule(localctx, 24, BusinessRulesParser.RULE_literal);
		try {
			this.state = 172;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case 46:
				this.enterOuterAlt(localctx, 1);
				{
				this.state = 166;
				this.match(BusinessRulesParser.NUMBER);
				}
				break;
			case 47:
				this.enterOuterAlt(localctx, 2);
				{
				this.state = 167;
				this.match(BusinessRulesParser.STRING);
				}
				break;
			case 1:
				this.enterOuterAlt(localctx, 3);
				{
				this.state = 168;
				this.match(BusinessRulesParser.TRUE);
				}
				break;
			case 2:
				this.enterOuterAlt(localctx, 4);
				{
				this.state = 169;
				this.match(BusinessRulesParser.FALSE);
				}
				break;
			case 3:
				this.enterOuterAlt(localctx, 5);
				{
				this.state = 170;
				this.match(BusinessRulesParser.NONE);
				}
				break;
			case 41:
				this.enterOuterAlt(localctx, 6);
				{
				this.state = 171;
				this.list_();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public list_(): List_Context {
		let localctx: List_Context = new List_Context(this, this._ctx, this.state);
		this.enterRule(localctx, 26, BusinessRulesParser.RULE_list_);
		let _la: number;
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 174;
			this.match(BusinessRulesParser.LBRACKET);
			this.state = 183;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			if ((((_la) & ~0x1F) === 0 && ((1 << _la) & 268436558) !== 0) || ((((_la - 39)) & ~0x1F) === 0 && ((1 << (_la - 39)) & 901) !== 0)) {
				{
				this.state = 175;
				this.orExpr();
				this.state = 180;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
				while (_la===44) {
					{
					{
					this.state = 176;
					this.match(BusinessRulesParser.COMMA);
					this.state = 177;
					this.orExpr();
					}
					}
					this.state = 182;
					this._errHandler.sync(this);
					_la = this._input.LA(1);
				}
				}
			}

			this.state = 185;
			this.match(BusinessRulesParser.RBRACKET);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public path(): PathContext {
		let localctx: PathContext = new PathContext(this, this._ctx, this.state);
		this.enterRule(localctx, 28, BusinessRulesParser.RULE_path);
		let _la: number;
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 187;
			this.match(BusinessRulesParser.IDENTIFIER);
			this.state = 191;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (((((_la - 38)) & ~0x1F) === 0 && ((1 << (_la - 38)) & 41) !== 0)) {
				{
				{
				this.state = 188;
				this.pathSegment();
				}
				}
				this.state = 193;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public pathSegment(): PathSegmentContext {
		let localctx: PathSegmentContext = new PathSegmentContext(this, this._ctx, this.state);
		this.enterRule(localctx, 30, BusinessRulesParser.RULE_pathSegment);
		try {
			this.state = 202;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case 43:
				this.enterOuterAlt(localctx, 1);
				{
				this.state = 194;
				this.match(BusinessRulesParser.DOT);
				this.state = 195;
				this.match(BusinessRulesParser.IDENTIFIER);
				}
				break;
			case 38:
				this.enterOuterAlt(localctx, 2);
				{
				this.state = 196;
				this.match(BusinessRulesParser.NULL_SAFE_DOT);
				this.state = 197;
				this.match(BusinessRulesParser.IDENTIFIER);
				}
				break;
			case 41:
				this.enterOuterAlt(localctx, 3);
				{
				this.state = 198;
				this.match(BusinessRulesParser.LBRACKET);
				this.state = 199;
				this.orExpr();
				this.state = 200;
				this.match(BusinessRulesParser.RBRACKET);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public workflowCall(): WorkflowCallContext {
		let localctx: WorkflowCallContext = new WorkflowCallContext(this, this._ctx, this.state);
		this.enterRule(localctx, 32, BusinessRulesParser.RULE_workflowCall);
		let _la: number;
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 204;
			this.match(BusinessRulesParser.WORKFLOW);
			this.state = 205;
			this.match(BusinessRulesParser.LPAREN);
			this.state = 206;
			this.match(BusinessRulesParser.STRING);
			this.state = 211;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la===44) {
				{
				{
				this.state = 207;
				this.match(BusinessRulesParser.COMMA);
				this.state = 208;
				this.orExpr();
				}
				}
				this.state = 213;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			this.state = 214;
			this.match(BusinessRulesParser.RPAREN);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public actions(): ActionsContext {
		let localctx: ActionsContext = new ActionsContext(this, this._ctx, this.state);
		this.enterRule(localctx, 34, BusinessRulesParser.RULE_actions);
		let _la: number;
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 216;
			this.action();
			this.state = 221;
			this._errHandler.sync(this);
			_la = this._input.LA(1);
			while (_la===45) {
				{
				{
				this.state = 217;
				this.match(BusinessRulesParser.SEMICOLON);
				this.state = 218;
				this.action();
				}
				}
				this.state = 223;
				this._errHandler.sync(this);
				_la = this._input.LA(1);
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public action(): ActionContext {
		let localctx: ActionContext = new ActionContext(this, this._ctx, this.state);
		this.enterRule(localctx, 36, BusinessRulesParser.RULE_action);
		try {
			this.state = 227;
			this._errHandler.sync(this);
			switch (this._input.LA(1)) {
			case 9:
				this.enterOuterAlt(localctx, 1);
				{
				this.state = 224;
				this.returnStmt();
				}
				break;
			case 48:
				this.enterOuterAlt(localctx, 2);
				{
				this.state = 225;
				this.assignment();
				}
				break;
			case 10:
				this.enterOuterAlt(localctx, 3);
				{
				this.state = 226;
				this.workflowCall();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public returnStmt(): ReturnStmtContext {
		let localctx: ReturnStmtContext = new ReturnStmtContext(this, this._ctx, this.state);
		this.enterRule(localctx, 38, BusinessRulesParser.RULE_returnStmt);
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 229;
			this.match(BusinessRulesParser.RET);
			this.state = 230;
			this.orExpr();
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public assignment(): AssignmentContext {
		let localctx: AssignmentContext = new AssignmentContext(this, this._ctx, this.state);
		this.enterRule(localctx, 40, BusinessRulesParser.RULE_assignment);
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 232;
			this.path();
			this.state = 233;
			this.assignOp();
			this.state = 234;
			this.orExpr();
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}
	// @RuleVersion(0)
	public assignOp(): AssignOpContext {
		let localctx: AssignOpContext = new AssignOpContext(this, this._ctx, this.state);
		this.enterRule(localctx, 42, BusinessRulesParser.RULE_assignOp);
		let _la: number;
		try {
			this.enterOuterAlt(localctx, 1);
			{
			this.state = 236;
			_la = this._input.LA(1);
			if(!(((((_la - 32)) & ~0x1F) === 0 && ((1 << (_la - 32)) & 31) !== 0))) {
			this._errHandler.recoverInline(this);
			}
			else {
				this._errHandler.reportMatch(this);
			    this.consume();
			}
			}
		}
		catch (re) {
			if (re instanceof RecognitionException) {
				localctx.exception = re;
				this._errHandler.reportError(this, re);
				this._errHandler.recover(this, re);
			} else {
				throw re;
			}
		}
		finally {
			this.exitRule();
		}
		return localctx;
	}

	public static readonly _serializedATN: number[] = [4,1,50,239,2,0,7,0,2,
	1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,
	10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,2,14,7,14,2,15,7,15,2,16,7,16,2,17,
	7,17,2,18,7,18,2,19,7,19,2,20,7,20,2,21,7,21,1,0,1,0,1,0,1,0,1,0,1,1,1,
	1,1,2,1,2,1,2,5,2,55,8,2,10,2,12,2,58,9,2,1,3,1,3,1,3,5,3,63,8,3,10,3,12,
	3,66,9,3,1,4,1,4,1,4,3,4,71,8,4,1,5,1,5,1,5,3,5,76,8,5,1,5,1,5,1,5,1,5,
	1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,
	1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,3,5,112,8,5,1,6,1,6,1,6,
	5,6,117,8,6,10,6,12,6,120,9,6,1,7,1,7,1,7,5,7,125,8,7,10,7,12,7,128,9,7,
	1,8,1,8,1,8,5,8,133,8,8,10,8,12,8,136,9,8,1,9,1,9,1,9,3,9,141,8,9,1,10,
	1,10,1,10,1,10,1,10,1,10,1,10,1,10,3,10,151,8,10,1,11,1,11,1,11,1,11,1,
	11,5,11,158,8,11,10,11,12,11,161,9,11,3,11,163,8,11,1,11,1,11,1,12,1,12,
	1,12,1,12,1,12,1,12,3,12,173,8,12,1,13,1,13,1,13,1,13,5,13,179,8,13,10,
	13,12,13,182,9,13,3,13,184,8,13,1,13,1,13,1,14,1,14,5,14,190,8,14,10,14,
	12,14,193,9,14,1,15,1,15,1,15,1,15,1,15,1,15,1,15,1,15,3,15,203,8,15,1,
	16,1,16,1,16,1,16,1,16,5,16,210,8,16,10,16,12,16,213,9,16,1,16,1,16,1,17,
	1,17,1,17,5,17,220,8,17,10,17,12,17,223,9,17,1,18,1,18,1,18,3,18,228,8,
	18,1,19,1,19,1,19,1,20,1,20,1,20,1,20,1,21,1,21,1,21,0,0,22,0,2,4,6,8,10,
	12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,0,4,2,0,7,8,21,26,1,0,27,
	28,1,0,29,31,1,0,32,36,253,0,44,1,0,0,0,2,49,1,0,0,0,4,51,1,0,0,0,6,59,
	1,0,0,0,8,70,1,0,0,0,10,111,1,0,0,0,12,113,1,0,0,0,14,121,1,0,0,0,16,129,
	1,0,0,0,18,140,1,0,0,0,20,150,1,0,0,0,22,152,1,0,0,0,24,172,1,0,0,0,26,
	174,1,0,0,0,28,187,1,0,0,0,30,202,1,0,0,0,32,204,1,0,0,0,34,216,1,0,0,0,
	36,227,1,0,0,0,38,229,1,0,0,0,40,232,1,0,0,0,42,236,1,0,0,0,44,45,3,2,1,
	0,45,46,5,20,0,0,46,47,3,34,17,0,47,48,5,0,0,1,48,1,1,0,0,0,49,50,3,4,2,
	0,50,3,1,0,0,0,51,56,3,6,3,0,52,53,5,5,0,0,53,55,3,6,3,0,54,52,1,0,0,0,
	55,58,1,0,0,0,56,54,1,0,0,0,56,57,1,0,0,0,57,5,1,0,0,0,58,56,1,0,0,0,59,
	64,3,8,4,0,60,61,5,4,0,0,61,63,3,8,4,0,62,60,1,0,0,0,63,66,1,0,0,0,64,62,
	1,0,0,0,64,65,1,0,0,0,65,7,1,0,0,0,66,64,1,0,0,0,67,68,5,6,0,0,68,71,3,
	8,4,0,69,71,3,10,5,0,70,67,1,0,0,0,70,69,1,0,0,0,71,9,1,0,0,0,72,75,3,12,
	6,0,73,74,7,0,0,0,74,76,3,12,6,0,75,73,1,0,0,0,75,76,1,0,0,0,76,112,1,0,
	0,0,77,78,3,12,6,0,78,79,5,14,0,0,79,80,3,12,6,0,80,112,1,0,0,0,81,82,3,
	12,6,0,82,83,5,13,0,0,83,84,3,12,6,0,84,112,1,0,0,0,85,86,3,12,6,0,86,87,
	5,15,0,0,87,88,3,12,6,0,88,112,1,0,0,0,89,90,3,12,6,0,90,91,5,16,0,0,91,
	92,3,12,6,0,92,112,1,0,0,0,93,94,3,12,6,0,94,95,5,17,0,0,95,96,3,12,6,0,
	96,112,1,0,0,0,97,98,3,12,6,0,98,99,5,11,0,0,99,100,3,12,6,0,100,112,1,
	0,0,0,101,102,3,12,6,0,102,103,5,12,0,0,103,104,3,12,6,0,104,112,1,0,0,
	0,105,106,3,12,6,0,106,107,5,18,0,0,107,112,1,0,0,0,108,109,3,12,6,0,109,
	110,5,19,0,0,110,112,1,0,0,0,111,72,1,0,0,0,111,77,1,0,0,0,111,81,1,0,0,
	0,111,85,1,0,0,0,111,89,1,0,0,0,111,93,1,0,0,0,111,97,1,0,0,0,111,101,1,
	0,0,0,111,105,1,0,0,0,111,108,1,0,0,0,112,11,1,0,0,0,113,118,3,14,7,0,114,
	115,5,37,0,0,115,117,3,14,7,0,116,114,1,0,0,0,117,120,1,0,0,0,118,116,1,
	0,0,0,118,119,1,0,0,0,119,13,1,0,0,0,120,118,1,0,0,0,121,126,3,16,8,0,122,
	123,7,1,0,0,123,125,3,16,8,0,124,122,1,0,0,0,125,128,1,0,0,0,126,124,1,
	0,0,0,126,127,1,0,0,0,127,15,1,0,0,0,128,126,1,0,0,0,129,134,3,18,9,0,130,
	131,7,2,0,0,131,133,3,18,9,0,132,130,1,0,0,0,133,136,1,0,0,0,134,132,1,
	0,0,0,134,135,1,0,0,0,135,17,1,0,0,0,136,134,1,0,0,0,137,138,5,28,0,0,138,
	141,3,18,9,0,139,141,3,20,10,0,140,137,1,0,0,0,140,139,1,0,0,0,141,19,1,
	0,0,0,142,143,5,39,0,0,143,144,3,4,2,0,144,145,5,40,0,0,145,151,1,0,0,0,
	146,151,3,24,12,0,147,151,3,22,11,0,148,151,3,28,14,0,149,151,3,32,16,0,
	150,142,1,0,0,0,150,146,1,0,0,0,150,147,1,0,0,0,150,148,1,0,0,0,150,149,
	1,0,0,0,151,21,1,0,0,0,152,153,5,48,0,0,153,162,5,39,0,0,154,159,3,4,2,
	0,155,156,5,44,0,0,156,158,3,4,2,0,157,155,1,0,0,0,158,161,1,0,0,0,159,
	157,1,0,0,0,159,160,1,0,0,0,160,163,1,0,0,0,161,159,1,0,0,0,162,154,1,0,
	0,0,162,163,1,0,0,0,163,164,1,0,0,0,164,165,5,40,0,0,165,23,1,0,0,0,166,
	173,5,46,0,0,167,173,5,47,0,0,168,173,5,1,0,0,169,173,5,2,0,0,170,173,5,
	3,0,0,171,173,3,26,13,0,172,166,1,0,0,0,172,167,1,0,0,0,172,168,1,0,0,0,
	172,169,1,0,0,0,172,170,1,0,0,0,172,171,1,0,0,0,173,25,1,0,0,0,174,183,
	5,41,0,0,175,180,3,4,2,0,176,177,5,44,0,0,177,179,3,4,2,0,178,176,1,0,0,
	0,179,182,1,0,0,0,180,178,1,0,0,0,180,181,1,0,0,0,181,184,1,0,0,0,182,180,
	1,0,0,0,183,175,1,0,0,0,183,184,1,0,0,0,184,185,1,0,0,0,185,186,5,42,0,
	0,186,27,1,0,0,0,187,191,5,48,0,0,188,190,3,30,15,0,189,188,1,0,0,0,190,
	193,1,0,0,0,191,189,1,0,0,0,191,192,1,0,0,0,192,29,1,0,0,0,193,191,1,0,
	0,0,194,195,5,43,0,0,195,203,5,48,0,0,196,197,5,38,0,0,197,203,5,48,0,0,
	198,199,5,41,0,0,199,200,3,4,2,0,200,201,5,42,0,0,201,203,1,0,0,0,202,194,
	1,0,0,0,202,196,1,0,0,0,202,198,1,0,0,0,203,31,1,0,0,0,204,205,5,10,0,0,
	205,206,5,39,0,0,206,211,5,47,0,0,207,208,5,44,0,0,208,210,3,4,2,0,209,
	207,1,0,0,0,210,213,1,0,0,0,211,209,1,0,0,0,211,212,1,0,0,0,212,214,1,0,
	0,0,213,211,1,0,0,0,214,215,5,40,0,0,215,33,1,0,0,0,216,221,3,36,18,0,217,
	218,5,45,0,0,218,220,3,36,18,0,219,217,1,0,0,0,220,223,1,0,0,0,221,219,
	1,0,0,0,221,222,1,0,0,0,222,35,1,0,0,0,223,221,1,0,0,0,224,228,3,38,19,
	0,225,228,3,40,20,0,226,228,3,32,16,0,227,224,1,0,0,0,227,225,1,0,0,0,227,
	226,1,0,0,0,228,37,1,0,0,0,229,230,5,9,0,0,230,231,3,4,2,0,231,39,1,0,0,
	0,232,233,3,28,14,0,233,234,3,42,21,0,234,235,3,4,2,0,235,41,1,0,0,0,236,
	237,7,3,0,0,237,43,1,0,0,0,20,56,64,70,75,111,118,126,134,140,150,159,162,
	172,180,183,191,202,211,221,227];

	private static __ATN: ATN;
	public static get _ATN(): ATN {
		if (!BusinessRulesParser.__ATN) {
			BusinessRulesParser.__ATN = new ATNDeserializer().deserialize(BusinessRulesParser._serializedATN);
		}

		return BusinessRulesParser.__ATN;
	}


	static DecisionsToDFA = BusinessRulesParser._ATN.decisionToState.map( (ds: DecisionState, index: number) => new DFA(ds, index) );

}

export class Rule_Context extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public condition(): ConditionContext {
		return this.getTypedRuleContext(ConditionContext, 0) as ConditionContext;
	}
	public ARROW(): TerminalNode {
		return this.getToken(BusinessRulesParser.ARROW, 0);
	}
	public actions(): ActionsContext {
		return this.getTypedRuleContext(ActionsContext, 0) as ActionsContext;
	}
	public EOF(): TerminalNode {
		return this.getToken(BusinessRulesParser.EOF, 0);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_rule_;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterRule_) {
	 		listener.enterRule_(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitRule_) {
	 		listener.exitRule_(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitRule_) {
			return visitor.visitRule_(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ConditionContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public orExpr(): OrExprContext {
		return this.getTypedRuleContext(OrExprContext, 0) as OrExprContext;
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_condition;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterCondition) {
	 		listener.enterCondition(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitCondition) {
	 		listener.exitCondition(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitCondition) {
			return visitor.visitCondition(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class OrExprContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public andExpr_list(): AndExprContext[] {
		return this.getTypedRuleContexts(AndExprContext) as AndExprContext[];
	}
	public andExpr(i: number): AndExprContext {
		return this.getTypedRuleContext(AndExprContext, i) as AndExprContext;
	}
	public OR_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.OR);
	}
	public OR(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.OR, i);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_orExpr;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterOrExpr) {
	 		listener.enterOrExpr(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitOrExpr) {
	 		listener.exitOrExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitOrExpr) {
			return visitor.visitOrExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class AndExprContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public notExpr_list(): NotExprContext[] {
		return this.getTypedRuleContexts(NotExprContext) as NotExprContext[];
	}
	public notExpr(i: number): NotExprContext {
		return this.getTypedRuleContext(NotExprContext, i) as NotExprContext;
	}
	public AND_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.AND);
	}
	public AND(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.AND, i);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_andExpr;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterAndExpr) {
	 		listener.enterAndExpr(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitAndExpr) {
	 		listener.exitAndExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitAndExpr) {
			return visitor.visitAndExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class NotExprContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public NOT(): TerminalNode {
		return this.getToken(BusinessRulesParser.NOT, 0);
	}
	public notExpr(): NotExprContext {
		return this.getTypedRuleContext(NotExprContext, 0) as NotExprContext;
	}
	public comparison(): ComparisonContext {
		return this.getTypedRuleContext(ComparisonContext, 0) as ComparisonContext;
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_notExpr;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterNotExpr) {
	 		listener.enterNotExpr(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitNotExpr) {
	 		listener.exitNotExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitNotExpr) {
			return visitor.visitNotExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ComparisonContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public nullCoalesce_list(): NullCoalesceContext[] {
		return this.getTypedRuleContexts(NullCoalesceContext) as NullCoalesceContext[];
	}
	public nullCoalesce(i: number): NullCoalesceContext {
		return this.getTypedRuleContext(NullCoalesceContext, i) as NullCoalesceContext;
	}
	public EQ(): TerminalNode {
		return this.getToken(BusinessRulesParser.EQ, 0);
	}
	public NEQ(): TerminalNode {
		return this.getToken(BusinessRulesParser.NEQ, 0);
	}
	public LT(): TerminalNode {
		return this.getToken(BusinessRulesParser.LT, 0);
	}
	public GT(): TerminalNode {
		return this.getToken(BusinessRulesParser.GT, 0);
	}
	public LTE(): TerminalNode {
		return this.getToken(BusinessRulesParser.LTE, 0);
	}
	public GTE(): TerminalNode {
		return this.getToken(BusinessRulesParser.GTE, 0);
	}
	public IN(): TerminalNode {
		return this.getToken(BusinessRulesParser.IN, 0);
	}
	public NOT_IN(): TerminalNode {
		return this.getToken(BusinessRulesParser.NOT_IN, 0);
	}
	public CONTAINS(): TerminalNode {
		return this.getToken(BusinessRulesParser.CONTAINS, 0);
	}
	public NOT_CONTAINS(): TerminalNode {
		return this.getToken(BusinessRulesParser.NOT_CONTAINS, 0);
	}
	public STARTS_WITH(): TerminalNode {
		return this.getToken(BusinessRulesParser.STARTS_WITH, 0);
	}
	public ENDS_WITH(): TerminalNode {
		return this.getToken(BusinessRulesParser.ENDS_WITH, 0);
	}
	public MATCHES(): TerminalNode {
		return this.getToken(BusinessRulesParser.MATCHES, 0);
	}
	public CONTAINS_ANY(): TerminalNode {
		return this.getToken(BusinessRulesParser.CONTAINS_ANY, 0);
	}
	public CONTAINS_ALL(): TerminalNode {
		return this.getToken(BusinessRulesParser.CONTAINS_ALL, 0);
	}
	public IS_EMPTY(): TerminalNode {
		return this.getToken(BusinessRulesParser.IS_EMPTY, 0);
	}
	public EXISTS(): TerminalNode {
		return this.getToken(BusinessRulesParser.EXISTS, 0);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_comparison;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterComparison) {
	 		listener.enterComparison(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitComparison) {
	 		listener.exitComparison(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitComparison) {
			return visitor.visitComparison(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class NullCoalesceContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public addExpr_list(): AddExprContext[] {
		return this.getTypedRuleContexts(AddExprContext) as AddExprContext[];
	}
	public addExpr(i: number): AddExprContext {
		return this.getTypedRuleContext(AddExprContext, i) as AddExprContext;
	}
	public NULL_COALESCE_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.NULL_COALESCE);
	}
	public NULL_COALESCE(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.NULL_COALESCE, i);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_nullCoalesce;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterNullCoalesce) {
	 		listener.enterNullCoalesce(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitNullCoalesce) {
	 		listener.exitNullCoalesce(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitNullCoalesce) {
			return visitor.visitNullCoalesce(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class AddExprContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public mulExpr_list(): MulExprContext[] {
		return this.getTypedRuleContexts(MulExprContext) as MulExprContext[];
	}
	public mulExpr(i: number): MulExprContext {
		return this.getTypedRuleContext(MulExprContext, i) as MulExprContext;
	}
	public PLUS_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.PLUS);
	}
	public PLUS(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.PLUS, i);
	}
	public MINUS_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.MINUS);
	}
	public MINUS(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.MINUS, i);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_addExpr;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterAddExpr) {
	 		listener.enterAddExpr(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitAddExpr) {
	 		listener.exitAddExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitAddExpr) {
			return visitor.visitAddExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class MulExprContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public unaryExpr_list(): UnaryExprContext[] {
		return this.getTypedRuleContexts(UnaryExprContext) as UnaryExprContext[];
	}
	public unaryExpr(i: number): UnaryExprContext {
		return this.getTypedRuleContext(UnaryExprContext, i) as UnaryExprContext;
	}
	public STAR_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.STAR);
	}
	public STAR(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.STAR, i);
	}
	public SLASH_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.SLASH);
	}
	public SLASH(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.SLASH, i);
	}
	public MOD_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.MOD);
	}
	public MOD(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.MOD, i);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_mulExpr;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterMulExpr) {
	 		listener.enterMulExpr(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitMulExpr) {
	 		listener.exitMulExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitMulExpr) {
			return visitor.visitMulExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class UnaryExprContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public MINUS(): TerminalNode {
		return this.getToken(BusinessRulesParser.MINUS, 0);
	}
	public unaryExpr(): UnaryExprContext {
		return this.getTypedRuleContext(UnaryExprContext, 0) as UnaryExprContext;
	}
	public primary(): PrimaryContext {
		return this.getTypedRuleContext(PrimaryContext, 0) as PrimaryContext;
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_unaryExpr;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterUnaryExpr) {
	 		listener.enterUnaryExpr(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitUnaryExpr) {
	 		listener.exitUnaryExpr(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitUnaryExpr) {
			return visitor.visitUnaryExpr(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class PrimaryContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public LPAREN(): TerminalNode {
		return this.getToken(BusinessRulesParser.LPAREN, 0);
	}
	public orExpr(): OrExprContext {
		return this.getTypedRuleContext(OrExprContext, 0) as OrExprContext;
	}
	public RPAREN(): TerminalNode {
		return this.getToken(BusinessRulesParser.RPAREN, 0);
	}
	public literal(): LiteralContext {
		return this.getTypedRuleContext(LiteralContext, 0) as LiteralContext;
	}
	public functionCall(): FunctionCallContext {
		return this.getTypedRuleContext(FunctionCallContext, 0) as FunctionCallContext;
	}
	public path(): PathContext {
		return this.getTypedRuleContext(PathContext, 0) as PathContext;
	}
	public workflowCall(): WorkflowCallContext {
		return this.getTypedRuleContext(WorkflowCallContext, 0) as WorkflowCallContext;
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_primary;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterPrimary) {
	 		listener.enterPrimary(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitPrimary) {
	 		listener.exitPrimary(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitPrimary) {
			return visitor.visitPrimary(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class FunctionCallContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public IDENTIFIER(): TerminalNode {
		return this.getToken(BusinessRulesParser.IDENTIFIER, 0);
	}
	public LPAREN(): TerminalNode {
		return this.getToken(BusinessRulesParser.LPAREN, 0);
	}
	public RPAREN(): TerminalNode {
		return this.getToken(BusinessRulesParser.RPAREN, 0);
	}
	public orExpr_list(): OrExprContext[] {
		return this.getTypedRuleContexts(OrExprContext) as OrExprContext[];
	}
	public orExpr(i: number): OrExprContext {
		return this.getTypedRuleContext(OrExprContext, i) as OrExprContext;
	}
	public COMMA_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.COMMA);
	}
	public COMMA(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.COMMA, i);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_functionCall;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterFunctionCall) {
	 		listener.enterFunctionCall(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitFunctionCall) {
	 		listener.exitFunctionCall(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitFunctionCall) {
			return visitor.visitFunctionCall(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class LiteralContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public NUMBER(): TerminalNode {
		return this.getToken(BusinessRulesParser.NUMBER, 0);
	}
	public STRING(): TerminalNode {
		return this.getToken(BusinessRulesParser.STRING, 0);
	}
	public TRUE(): TerminalNode {
		return this.getToken(BusinessRulesParser.TRUE, 0);
	}
	public FALSE(): TerminalNode {
		return this.getToken(BusinessRulesParser.FALSE, 0);
	}
	public NONE(): TerminalNode {
		return this.getToken(BusinessRulesParser.NONE, 0);
	}
	public list_(): List_Context {
		return this.getTypedRuleContext(List_Context, 0) as List_Context;
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_literal;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterLiteral) {
	 		listener.enterLiteral(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitLiteral) {
	 		listener.exitLiteral(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitLiteral) {
			return visitor.visitLiteral(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class List_Context extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public LBRACKET(): TerminalNode {
		return this.getToken(BusinessRulesParser.LBRACKET, 0);
	}
	public RBRACKET(): TerminalNode {
		return this.getToken(BusinessRulesParser.RBRACKET, 0);
	}
	public orExpr_list(): OrExprContext[] {
		return this.getTypedRuleContexts(OrExprContext) as OrExprContext[];
	}
	public orExpr(i: number): OrExprContext {
		return this.getTypedRuleContext(OrExprContext, i) as OrExprContext;
	}
	public COMMA_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.COMMA);
	}
	public COMMA(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.COMMA, i);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_list_;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterList_) {
	 		listener.enterList_(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitList_) {
	 		listener.exitList_(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitList_) {
			return visitor.visitList_(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class PathContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public IDENTIFIER(): TerminalNode {
		return this.getToken(BusinessRulesParser.IDENTIFIER, 0);
	}
	public pathSegment_list(): PathSegmentContext[] {
		return this.getTypedRuleContexts(PathSegmentContext) as PathSegmentContext[];
	}
	public pathSegment(i: number): PathSegmentContext {
		return this.getTypedRuleContext(PathSegmentContext, i) as PathSegmentContext;
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_path;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterPath) {
	 		listener.enterPath(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitPath) {
	 		listener.exitPath(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitPath) {
			return visitor.visitPath(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class PathSegmentContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public DOT(): TerminalNode {
		return this.getToken(BusinessRulesParser.DOT, 0);
	}
	public IDENTIFIER(): TerminalNode {
		return this.getToken(BusinessRulesParser.IDENTIFIER, 0);
	}
	public NULL_SAFE_DOT(): TerminalNode {
		return this.getToken(BusinessRulesParser.NULL_SAFE_DOT, 0);
	}
	public LBRACKET(): TerminalNode {
		return this.getToken(BusinessRulesParser.LBRACKET, 0);
	}
	public orExpr(): OrExprContext {
		return this.getTypedRuleContext(OrExprContext, 0) as OrExprContext;
	}
	public RBRACKET(): TerminalNode {
		return this.getToken(BusinessRulesParser.RBRACKET, 0);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_pathSegment;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterPathSegment) {
	 		listener.enterPathSegment(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitPathSegment) {
	 		listener.exitPathSegment(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitPathSegment) {
			return visitor.visitPathSegment(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class WorkflowCallContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public WORKFLOW(): TerminalNode {
		return this.getToken(BusinessRulesParser.WORKFLOW, 0);
	}
	public LPAREN(): TerminalNode {
		return this.getToken(BusinessRulesParser.LPAREN, 0);
	}
	public STRING(): TerminalNode {
		return this.getToken(BusinessRulesParser.STRING, 0);
	}
	public RPAREN(): TerminalNode {
		return this.getToken(BusinessRulesParser.RPAREN, 0);
	}
	public COMMA_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.COMMA);
	}
	public COMMA(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.COMMA, i);
	}
	public orExpr_list(): OrExprContext[] {
		return this.getTypedRuleContexts(OrExprContext) as OrExprContext[];
	}
	public orExpr(i: number): OrExprContext {
		return this.getTypedRuleContext(OrExprContext, i) as OrExprContext;
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_workflowCall;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterWorkflowCall) {
	 		listener.enterWorkflowCall(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitWorkflowCall) {
	 		listener.exitWorkflowCall(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitWorkflowCall) {
			return visitor.visitWorkflowCall(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ActionsContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public action_list(): ActionContext[] {
		return this.getTypedRuleContexts(ActionContext) as ActionContext[];
	}
	public action(i: number): ActionContext {
		return this.getTypedRuleContext(ActionContext, i) as ActionContext;
	}
	public SEMICOLON_list(): TerminalNode[] {
	    	return this.getTokens(BusinessRulesParser.SEMICOLON);
	}
	public SEMICOLON(i: number): TerminalNode {
		return this.getToken(BusinessRulesParser.SEMICOLON, i);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_actions;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterActions) {
	 		listener.enterActions(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitActions) {
	 		listener.exitActions(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitActions) {
			return visitor.visitActions(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ActionContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public returnStmt(): ReturnStmtContext {
		return this.getTypedRuleContext(ReturnStmtContext, 0) as ReturnStmtContext;
	}
	public assignment(): AssignmentContext {
		return this.getTypedRuleContext(AssignmentContext, 0) as AssignmentContext;
	}
	public workflowCall(): WorkflowCallContext {
		return this.getTypedRuleContext(WorkflowCallContext, 0) as WorkflowCallContext;
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_action;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterAction) {
	 		listener.enterAction(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitAction) {
	 		listener.exitAction(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitAction) {
			return visitor.visitAction(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class ReturnStmtContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public RET(): TerminalNode {
		return this.getToken(BusinessRulesParser.RET, 0);
	}
	public orExpr(): OrExprContext {
		return this.getTypedRuleContext(OrExprContext, 0) as OrExprContext;
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_returnStmt;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterReturnStmt) {
	 		listener.enterReturnStmt(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitReturnStmt) {
	 		listener.exitReturnStmt(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitReturnStmt) {
			return visitor.visitReturnStmt(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class AssignmentContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public path(): PathContext {
		return this.getTypedRuleContext(PathContext, 0) as PathContext;
	}
	public assignOp(): AssignOpContext {
		return this.getTypedRuleContext(AssignOpContext, 0) as AssignOpContext;
	}
	public orExpr(): OrExprContext {
		return this.getTypedRuleContext(OrExprContext, 0) as OrExprContext;
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_assignment;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterAssignment) {
	 		listener.enterAssignment(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitAssignment) {
	 		listener.exitAssignment(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitAssignment) {
			return visitor.visitAssignment(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}


export class AssignOpContext extends ParserRuleContext {
	constructor(parser?: BusinessRulesParser, parent?: ParserRuleContext, invokingState?: number) {
		super(parent, invokingState);
    	this.parser = parser;
	}
	public ASSIGN(): TerminalNode {
		return this.getToken(BusinessRulesParser.ASSIGN, 0);
	}
	public PLUS_ASSIGN(): TerminalNode {
		return this.getToken(BusinessRulesParser.PLUS_ASSIGN, 0);
	}
	public MINUS_ASSIGN(): TerminalNode {
		return this.getToken(BusinessRulesParser.MINUS_ASSIGN, 0);
	}
	public STAR_ASSIGN(): TerminalNode {
		return this.getToken(BusinessRulesParser.STAR_ASSIGN, 0);
	}
	public SLASH_ASSIGN(): TerminalNode {
		return this.getToken(BusinessRulesParser.SLASH_ASSIGN, 0);
	}
    public get ruleIndex(): number {
    	return BusinessRulesParser.RULE_assignOp;
	}
	public enterRule(listener: BusinessRulesListener): void {
	    if(listener.enterAssignOp) {
	 		listener.enterAssignOp(this);
		}
	}
	public exitRule(listener: BusinessRulesListener): void {
	    if(listener.exitAssignOp) {
	 		listener.exitAssignOp(this);
		}
	}
	// @Override
	public accept<Result>(visitor: BusinessRulesVisitor<Result>): Result {
		if (visitor.visitAssignOp) {
			return visitor.visitAssignOp(this);
		} else {
			return visitor.visitChildren(this);
		}
	}
}
