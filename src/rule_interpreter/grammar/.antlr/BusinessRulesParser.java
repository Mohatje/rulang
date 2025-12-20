// Generated from /home/mo/Github/rule-interpreter/src/rule_interpreter/grammar/BusinessRules.g4 by ANTLR 4.9.2
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class BusinessRulesParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.9.2", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		TRUE=1, FALSE=2, NONE=3, AND=4, OR=5, NOT=6, IN=7, NOT_IN=8, RET=9, WORKFLOW=10, 
		ARROW=11, EQ=12, NEQ=13, LTE=14, GTE=15, LT=16, GT=17, PLUS=18, MINUS=19, 
		STAR=20, SLASH=21, MOD=22, ASSIGN=23, PLUS_ASSIGN=24, MINUS_ASSIGN=25, 
		STAR_ASSIGN=26, SLASH_ASSIGN=27, LPAREN=28, RPAREN=29, LBRACKET=30, RBRACKET=31, 
		DOT=32, COMMA=33, SEMICOLON=34, NUMBER=35, STRING=36, IDENTIFIER=37, WS=38, 
		LINE_COMMENT=39;
	public static final int
		RULE_rule_ = 0, RULE_condition = 1, RULE_orExpr = 2, RULE_andExpr = 3, 
		RULE_notExpr = 4, RULE_comparison = 5, RULE_addExpr = 6, RULE_mulExpr = 7, 
		RULE_unaryExpr = 8, RULE_primary = 9, RULE_literal = 10, RULE_list_ = 11, 
		RULE_path = 12, RULE_workflowCall = 13, RULE_actions = 14, RULE_action = 15, 
		RULE_returnStmt = 16, RULE_assignment = 17, RULE_assignOp = 18;
	private static String[] makeRuleNames() {
		return new String[] {
			"rule_", "condition", "orExpr", "andExpr", "notExpr", "comparison", "addExpr", 
			"mulExpr", "unaryExpr", "primary", "literal", "list_", "path", "workflowCall", 
			"actions", "action", "returnStmt", "assignment", "assignOp"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, null, null, null, "'and'", "'or'", "'not'", "'in'", null, "'ret'", 
			"'workflow'", "'=>'", "'=='", "'!='", "'<='", "'>='", "'<'", "'>'", "'+'", 
			"'-'", "'*'", "'/'", "'%'", "'='", "'+='", "'-='", "'*='", "'/='", "'('", 
			"')'", "'['", "']'", "'.'", "','", "';'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, "TRUE", "FALSE", "NONE", "AND", "OR", "NOT", "IN", "NOT_IN", "RET", 
			"WORKFLOW", "ARROW", "EQ", "NEQ", "LTE", "GTE", "LT", "GT", "PLUS", "MINUS", 
			"STAR", "SLASH", "MOD", "ASSIGN", "PLUS_ASSIGN", "MINUS_ASSIGN", "STAR_ASSIGN", 
			"SLASH_ASSIGN", "LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "DOT", "COMMA", 
			"SEMICOLON", "NUMBER", "STRING", "IDENTIFIER", "WS", "LINE_COMMENT"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "BusinessRules.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public BusinessRulesParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	public static class Rule_Context extends ParserRuleContext {
		public ConditionContext condition() {
			return getRuleContext(ConditionContext.class,0);
		}
		public TerminalNode ARROW() { return getToken(BusinessRulesParser.ARROW, 0); }
		public ActionsContext actions() {
			return getRuleContext(ActionsContext.class,0);
		}
		public TerminalNode EOF() { return getToken(BusinessRulesParser.EOF, 0); }
		public Rule_Context(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_rule_; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterRule_(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitRule_(this);
		}
	}

	public final Rule_Context rule_() throws RecognitionException {
		Rule_Context _localctx = new Rule_Context(_ctx, getState());
		enterRule(_localctx, 0, RULE_rule_);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(38);
			condition();
			setState(39);
			match(ARROW);
			setState(40);
			actions();
			setState(41);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ConditionContext extends ParserRuleContext {
		public OrExprContext orExpr() {
			return getRuleContext(OrExprContext.class,0);
		}
		public ConditionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_condition; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterCondition(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitCondition(this);
		}
	}

	public final ConditionContext condition() throws RecognitionException {
		ConditionContext _localctx = new ConditionContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_condition);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(43);
			orExpr();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class OrExprContext extends ParserRuleContext {
		public List<AndExprContext> andExpr() {
			return getRuleContexts(AndExprContext.class);
		}
		public AndExprContext andExpr(int i) {
			return getRuleContext(AndExprContext.class,i);
		}
		public List<TerminalNode> OR() { return getTokens(BusinessRulesParser.OR); }
		public TerminalNode OR(int i) {
			return getToken(BusinessRulesParser.OR, i);
		}
		public OrExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_orExpr; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterOrExpr(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitOrExpr(this);
		}
	}

	public final OrExprContext orExpr() throws RecognitionException {
		OrExprContext _localctx = new OrExprContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_orExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(45);
			andExpr();
			setState(50);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==OR) {
				{
				{
				setState(46);
				match(OR);
				setState(47);
				andExpr();
				}
				}
				setState(52);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class AndExprContext extends ParserRuleContext {
		public List<NotExprContext> notExpr() {
			return getRuleContexts(NotExprContext.class);
		}
		public NotExprContext notExpr(int i) {
			return getRuleContext(NotExprContext.class,i);
		}
		public List<TerminalNode> AND() { return getTokens(BusinessRulesParser.AND); }
		public TerminalNode AND(int i) {
			return getToken(BusinessRulesParser.AND, i);
		}
		public AndExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_andExpr; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterAndExpr(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitAndExpr(this);
		}
	}

	public final AndExprContext andExpr() throws RecognitionException {
		AndExprContext _localctx = new AndExprContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_andExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(53);
			notExpr();
			setState(58);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==AND) {
				{
				{
				setState(54);
				match(AND);
				setState(55);
				notExpr();
				}
				}
				setState(60);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class NotExprContext extends ParserRuleContext {
		public TerminalNode NOT() { return getToken(BusinessRulesParser.NOT, 0); }
		public NotExprContext notExpr() {
			return getRuleContext(NotExprContext.class,0);
		}
		public ComparisonContext comparison() {
			return getRuleContext(ComparisonContext.class,0);
		}
		public NotExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_notExpr; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterNotExpr(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitNotExpr(this);
		}
	}

	public final NotExprContext notExpr() throws RecognitionException {
		NotExprContext _localctx = new NotExprContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_notExpr);
		try {
			setState(64);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case NOT:
				enterOuterAlt(_localctx, 1);
				{
				setState(61);
				match(NOT);
				setState(62);
				notExpr();
				}
				break;
			case TRUE:
			case FALSE:
			case NONE:
			case WORKFLOW:
			case MINUS:
			case LPAREN:
			case LBRACKET:
			case NUMBER:
			case STRING:
			case IDENTIFIER:
				enterOuterAlt(_localctx, 2);
				{
				setState(63);
				comparison();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ComparisonContext extends ParserRuleContext {
		public List<AddExprContext> addExpr() {
			return getRuleContexts(AddExprContext.class);
		}
		public AddExprContext addExpr(int i) {
			return getRuleContext(AddExprContext.class,i);
		}
		public TerminalNode EQ() { return getToken(BusinessRulesParser.EQ, 0); }
		public TerminalNode NEQ() { return getToken(BusinessRulesParser.NEQ, 0); }
		public TerminalNode LT() { return getToken(BusinessRulesParser.LT, 0); }
		public TerminalNode GT() { return getToken(BusinessRulesParser.GT, 0); }
		public TerminalNode LTE() { return getToken(BusinessRulesParser.LTE, 0); }
		public TerminalNode GTE() { return getToken(BusinessRulesParser.GTE, 0); }
		public TerminalNode IN() { return getToken(BusinessRulesParser.IN, 0); }
		public TerminalNode NOT_IN() { return getToken(BusinessRulesParser.NOT_IN, 0); }
		public ComparisonContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_comparison; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterComparison(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitComparison(this);
		}
	}

	public final ComparisonContext comparison() throws RecognitionException {
		ComparisonContext _localctx = new ComparisonContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_comparison);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(66);
			addExpr();
			setState(69);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << IN) | (1L << NOT_IN) | (1L << EQ) | (1L << NEQ) | (1L << LTE) | (1L << GTE) | (1L << LT) | (1L << GT))) != 0)) {
				{
				setState(67);
				_la = _input.LA(1);
				if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << IN) | (1L << NOT_IN) | (1L << EQ) | (1L << NEQ) | (1L << LTE) | (1L << GTE) | (1L << LT) | (1L << GT))) != 0)) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(68);
				addExpr();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class AddExprContext extends ParserRuleContext {
		public List<MulExprContext> mulExpr() {
			return getRuleContexts(MulExprContext.class);
		}
		public MulExprContext mulExpr(int i) {
			return getRuleContext(MulExprContext.class,i);
		}
		public List<TerminalNode> PLUS() { return getTokens(BusinessRulesParser.PLUS); }
		public TerminalNode PLUS(int i) {
			return getToken(BusinessRulesParser.PLUS, i);
		}
		public List<TerminalNode> MINUS() { return getTokens(BusinessRulesParser.MINUS); }
		public TerminalNode MINUS(int i) {
			return getToken(BusinessRulesParser.MINUS, i);
		}
		public AddExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_addExpr; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterAddExpr(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitAddExpr(this);
		}
	}

	public final AddExprContext addExpr() throws RecognitionException {
		AddExprContext _localctx = new AddExprContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_addExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(71);
			mulExpr();
			setState(76);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==PLUS || _la==MINUS) {
				{
				{
				setState(72);
				_la = _input.LA(1);
				if ( !(_la==PLUS || _la==MINUS) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(73);
				mulExpr();
				}
				}
				setState(78);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class MulExprContext extends ParserRuleContext {
		public List<UnaryExprContext> unaryExpr() {
			return getRuleContexts(UnaryExprContext.class);
		}
		public UnaryExprContext unaryExpr(int i) {
			return getRuleContext(UnaryExprContext.class,i);
		}
		public List<TerminalNode> STAR() { return getTokens(BusinessRulesParser.STAR); }
		public TerminalNode STAR(int i) {
			return getToken(BusinessRulesParser.STAR, i);
		}
		public List<TerminalNode> SLASH() { return getTokens(BusinessRulesParser.SLASH); }
		public TerminalNode SLASH(int i) {
			return getToken(BusinessRulesParser.SLASH, i);
		}
		public List<TerminalNode> MOD() { return getTokens(BusinessRulesParser.MOD); }
		public TerminalNode MOD(int i) {
			return getToken(BusinessRulesParser.MOD, i);
		}
		public MulExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_mulExpr; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterMulExpr(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitMulExpr(this);
		}
	}

	public final MulExprContext mulExpr() throws RecognitionException {
		MulExprContext _localctx = new MulExprContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_mulExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(79);
			unaryExpr();
			setState(84);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << STAR) | (1L << SLASH) | (1L << MOD))) != 0)) {
				{
				{
				setState(80);
				_la = _input.LA(1);
				if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << STAR) | (1L << SLASH) | (1L << MOD))) != 0)) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(81);
				unaryExpr();
				}
				}
				setState(86);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class UnaryExprContext extends ParserRuleContext {
		public TerminalNode MINUS() { return getToken(BusinessRulesParser.MINUS, 0); }
		public UnaryExprContext unaryExpr() {
			return getRuleContext(UnaryExprContext.class,0);
		}
		public PrimaryContext primary() {
			return getRuleContext(PrimaryContext.class,0);
		}
		public UnaryExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_unaryExpr; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterUnaryExpr(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitUnaryExpr(this);
		}
	}

	public final UnaryExprContext unaryExpr() throws RecognitionException {
		UnaryExprContext _localctx = new UnaryExprContext(_ctx, getState());
		enterRule(_localctx, 16, RULE_unaryExpr);
		try {
			setState(90);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case MINUS:
				enterOuterAlt(_localctx, 1);
				{
				setState(87);
				match(MINUS);
				setState(88);
				unaryExpr();
				}
				break;
			case TRUE:
			case FALSE:
			case NONE:
			case WORKFLOW:
			case LPAREN:
			case LBRACKET:
			case NUMBER:
			case STRING:
			case IDENTIFIER:
				enterOuterAlt(_localctx, 2);
				{
				setState(89);
				primary();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class PrimaryContext extends ParserRuleContext {
		public TerminalNode LPAREN() { return getToken(BusinessRulesParser.LPAREN, 0); }
		public OrExprContext orExpr() {
			return getRuleContext(OrExprContext.class,0);
		}
		public TerminalNode RPAREN() { return getToken(BusinessRulesParser.RPAREN, 0); }
		public LiteralContext literal() {
			return getRuleContext(LiteralContext.class,0);
		}
		public PathContext path() {
			return getRuleContext(PathContext.class,0);
		}
		public WorkflowCallContext workflowCall() {
			return getRuleContext(WorkflowCallContext.class,0);
		}
		public PrimaryContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_primary; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterPrimary(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitPrimary(this);
		}
	}

	public final PrimaryContext primary() throws RecognitionException {
		PrimaryContext _localctx = new PrimaryContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_primary);
		try {
			setState(99);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case LPAREN:
				enterOuterAlt(_localctx, 1);
				{
				setState(92);
				match(LPAREN);
				setState(93);
				orExpr();
				setState(94);
				match(RPAREN);
				}
				break;
			case TRUE:
			case FALSE:
			case NONE:
			case LBRACKET:
			case NUMBER:
			case STRING:
				enterOuterAlt(_localctx, 2);
				{
				setState(96);
				literal();
				}
				break;
			case IDENTIFIER:
				enterOuterAlt(_localctx, 3);
				{
				setState(97);
				path();
				}
				break;
			case WORKFLOW:
				enterOuterAlt(_localctx, 4);
				{
				setState(98);
				workflowCall();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class LiteralContext extends ParserRuleContext {
		public TerminalNode NUMBER() { return getToken(BusinessRulesParser.NUMBER, 0); }
		public TerminalNode STRING() { return getToken(BusinessRulesParser.STRING, 0); }
		public TerminalNode TRUE() { return getToken(BusinessRulesParser.TRUE, 0); }
		public TerminalNode FALSE() { return getToken(BusinessRulesParser.FALSE, 0); }
		public TerminalNode NONE() { return getToken(BusinessRulesParser.NONE, 0); }
		public List_Context list_() {
			return getRuleContext(List_Context.class,0);
		}
		public LiteralContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_literal; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterLiteral(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitLiteral(this);
		}
	}

	public final LiteralContext literal() throws RecognitionException {
		LiteralContext _localctx = new LiteralContext(_ctx, getState());
		enterRule(_localctx, 20, RULE_literal);
		try {
			setState(107);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case NUMBER:
				enterOuterAlt(_localctx, 1);
				{
				setState(101);
				match(NUMBER);
				}
				break;
			case STRING:
				enterOuterAlt(_localctx, 2);
				{
				setState(102);
				match(STRING);
				}
				break;
			case TRUE:
				enterOuterAlt(_localctx, 3);
				{
				setState(103);
				match(TRUE);
				}
				break;
			case FALSE:
				enterOuterAlt(_localctx, 4);
				{
				setState(104);
				match(FALSE);
				}
				break;
			case NONE:
				enterOuterAlt(_localctx, 5);
				{
				setState(105);
				match(NONE);
				}
				break;
			case LBRACKET:
				enterOuterAlt(_localctx, 6);
				{
				setState(106);
				list_();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class List_Context extends ParserRuleContext {
		public TerminalNode LBRACKET() { return getToken(BusinessRulesParser.LBRACKET, 0); }
		public TerminalNode RBRACKET() { return getToken(BusinessRulesParser.RBRACKET, 0); }
		public List<OrExprContext> orExpr() {
			return getRuleContexts(OrExprContext.class);
		}
		public OrExprContext orExpr(int i) {
			return getRuleContext(OrExprContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(BusinessRulesParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(BusinessRulesParser.COMMA, i);
		}
		public List_Context(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_list_; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterList_(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitList_(this);
		}
	}

	public final List_Context list_() throws RecognitionException {
		List_Context _localctx = new List_Context(_ctx, getState());
		enterRule(_localctx, 22, RULE_list_);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(109);
			match(LBRACKET);
			setState(118);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << TRUE) | (1L << FALSE) | (1L << NONE) | (1L << NOT) | (1L << WORKFLOW) | (1L << MINUS) | (1L << LPAREN) | (1L << LBRACKET) | (1L << NUMBER) | (1L << STRING) | (1L << IDENTIFIER))) != 0)) {
				{
				setState(110);
				orExpr();
				setState(115);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==COMMA) {
					{
					{
					setState(111);
					match(COMMA);
					setState(112);
					orExpr();
					}
					}
					setState(117);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				}
			}

			setState(120);
			match(RBRACKET);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class PathContext extends ParserRuleContext {
		public List<TerminalNode> IDENTIFIER() { return getTokens(BusinessRulesParser.IDENTIFIER); }
		public TerminalNode IDENTIFIER(int i) {
			return getToken(BusinessRulesParser.IDENTIFIER, i);
		}
		public List<TerminalNode> DOT() { return getTokens(BusinessRulesParser.DOT); }
		public TerminalNode DOT(int i) {
			return getToken(BusinessRulesParser.DOT, i);
		}
		public List<TerminalNode> LBRACKET() { return getTokens(BusinessRulesParser.LBRACKET); }
		public TerminalNode LBRACKET(int i) {
			return getToken(BusinessRulesParser.LBRACKET, i);
		}
		public List<OrExprContext> orExpr() {
			return getRuleContexts(OrExprContext.class);
		}
		public OrExprContext orExpr(int i) {
			return getRuleContext(OrExprContext.class,i);
		}
		public List<TerminalNode> RBRACKET() { return getTokens(BusinessRulesParser.RBRACKET); }
		public TerminalNode RBRACKET(int i) {
			return getToken(BusinessRulesParser.RBRACKET, i);
		}
		public PathContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_path; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterPath(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitPath(this);
		}
	}

	public final PathContext path() throws RecognitionException {
		PathContext _localctx = new PathContext(_ctx, getState());
		enterRule(_localctx, 24, RULE_path);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(122);
			match(IDENTIFIER);
			setState(131);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==LBRACKET || _la==DOT) {
				{
				setState(129);
				_errHandler.sync(this);
				switch (_input.LA(1)) {
				case DOT:
					{
					setState(123);
					match(DOT);
					setState(124);
					match(IDENTIFIER);
					}
					break;
				case LBRACKET:
					{
					setState(125);
					match(LBRACKET);
					setState(126);
					orExpr();
					setState(127);
					match(RBRACKET);
					}
					break;
				default:
					throw new NoViableAltException(this);
				}
				}
				setState(133);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class WorkflowCallContext extends ParserRuleContext {
		public TerminalNode WORKFLOW() { return getToken(BusinessRulesParser.WORKFLOW, 0); }
		public TerminalNode LPAREN() { return getToken(BusinessRulesParser.LPAREN, 0); }
		public TerminalNode STRING() { return getToken(BusinessRulesParser.STRING, 0); }
		public TerminalNode RPAREN() { return getToken(BusinessRulesParser.RPAREN, 0); }
		public List<TerminalNode> COMMA() { return getTokens(BusinessRulesParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(BusinessRulesParser.COMMA, i);
		}
		public List<OrExprContext> orExpr() {
			return getRuleContexts(OrExprContext.class);
		}
		public OrExprContext orExpr(int i) {
			return getRuleContext(OrExprContext.class,i);
		}
		public WorkflowCallContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_workflowCall; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterWorkflowCall(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitWorkflowCall(this);
		}
	}

	public final WorkflowCallContext workflowCall() throws RecognitionException {
		WorkflowCallContext _localctx = new WorkflowCallContext(_ctx, getState());
		enterRule(_localctx, 26, RULE_workflowCall);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(134);
			match(WORKFLOW);
			setState(135);
			match(LPAREN);
			setState(136);
			match(STRING);
			setState(141);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(137);
				match(COMMA);
				setState(138);
				orExpr();
				}
				}
				setState(143);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(144);
			match(RPAREN);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ActionsContext extends ParserRuleContext {
		public List<ActionContext> action() {
			return getRuleContexts(ActionContext.class);
		}
		public ActionContext action(int i) {
			return getRuleContext(ActionContext.class,i);
		}
		public List<TerminalNode> SEMICOLON() { return getTokens(BusinessRulesParser.SEMICOLON); }
		public TerminalNode SEMICOLON(int i) {
			return getToken(BusinessRulesParser.SEMICOLON, i);
		}
		public ActionsContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_actions; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterActions(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitActions(this);
		}
	}

	public final ActionsContext actions() throws RecognitionException {
		ActionsContext _localctx = new ActionsContext(_ctx, getState());
		enterRule(_localctx, 28, RULE_actions);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(146);
			action();
			setState(151);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==SEMICOLON) {
				{
				{
				setState(147);
				match(SEMICOLON);
				setState(148);
				action();
				}
				}
				setState(153);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ActionContext extends ParserRuleContext {
		public ReturnStmtContext returnStmt() {
			return getRuleContext(ReturnStmtContext.class,0);
		}
		public AssignmentContext assignment() {
			return getRuleContext(AssignmentContext.class,0);
		}
		public WorkflowCallContext workflowCall() {
			return getRuleContext(WorkflowCallContext.class,0);
		}
		public ActionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_action; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterAction(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitAction(this);
		}
	}

	public final ActionContext action() throws RecognitionException {
		ActionContext _localctx = new ActionContext(_ctx, getState());
		enterRule(_localctx, 30, RULE_action);
		try {
			setState(157);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case RET:
				enterOuterAlt(_localctx, 1);
				{
				setState(154);
				returnStmt();
				}
				break;
			case IDENTIFIER:
				enterOuterAlt(_localctx, 2);
				{
				setState(155);
				assignment();
				}
				break;
			case WORKFLOW:
				enterOuterAlt(_localctx, 3);
				{
				setState(156);
				workflowCall();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ReturnStmtContext extends ParserRuleContext {
		public TerminalNode RET() { return getToken(BusinessRulesParser.RET, 0); }
		public OrExprContext orExpr() {
			return getRuleContext(OrExprContext.class,0);
		}
		public ReturnStmtContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_returnStmt; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterReturnStmt(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitReturnStmt(this);
		}
	}

	public final ReturnStmtContext returnStmt() throws RecognitionException {
		ReturnStmtContext _localctx = new ReturnStmtContext(_ctx, getState());
		enterRule(_localctx, 32, RULE_returnStmt);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(159);
			match(RET);
			setState(160);
			orExpr();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class AssignmentContext extends ParserRuleContext {
		public PathContext path() {
			return getRuleContext(PathContext.class,0);
		}
		public AssignOpContext assignOp() {
			return getRuleContext(AssignOpContext.class,0);
		}
		public OrExprContext orExpr() {
			return getRuleContext(OrExprContext.class,0);
		}
		public AssignmentContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_assignment; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterAssignment(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitAssignment(this);
		}
	}

	public final AssignmentContext assignment() throws RecognitionException {
		AssignmentContext _localctx = new AssignmentContext(_ctx, getState());
		enterRule(_localctx, 34, RULE_assignment);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(162);
			path();
			setState(163);
			assignOp();
			setState(164);
			orExpr();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class AssignOpContext extends ParserRuleContext {
		public TerminalNode ASSIGN() { return getToken(BusinessRulesParser.ASSIGN, 0); }
		public TerminalNode PLUS_ASSIGN() { return getToken(BusinessRulesParser.PLUS_ASSIGN, 0); }
		public TerminalNode MINUS_ASSIGN() { return getToken(BusinessRulesParser.MINUS_ASSIGN, 0); }
		public TerminalNode STAR_ASSIGN() { return getToken(BusinessRulesParser.STAR_ASSIGN, 0); }
		public TerminalNode SLASH_ASSIGN() { return getToken(BusinessRulesParser.SLASH_ASSIGN, 0); }
		public AssignOpContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_assignOp; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).enterAssignOp(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof BusinessRulesListener ) ((BusinessRulesListener)listener).exitAssignOp(this);
		}
	}

	public final AssignOpContext assignOp() throws RecognitionException {
		AssignOpContext _localctx = new AssignOpContext(_ctx, getState());
		enterRule(_localctx, 36, RULE_assignOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(166);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << ASSIGN) | (1L << PLUS_ASSIGN) | (1L << MINUS_ASSIGN) | (1L << STAR_ASSIGN) | (1L << SLASH_ASSIGN))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static final String _serializedATN =
		"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3)\u00ab\4\2\t\2\4"+
		"\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t"+
		"\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22"+
		"\4\23\t\23\4\24\t\24\3\2\3\2\3\2\3\2\3\2\3\3\3\3\3\4\3\4\3\4\7\4\63\n"+
		"\4\f\4\16\4\66\13\4\3\5\3\5\3\5\7\5;\n\5\f\5\16\5>\13\5\3\6\3\6\3\6\5"+
		"\6C\n\6\3\7\3\7\3\7\5\7H\n\7\3\b\3\b\3\b\7\bM\n\b\f\b\16\bP\13\b\3\t\3"+
		"\t\3\t\7\tU\n\t\f\t\16\tX\13\t\3\n\3\n\3\n\5\n]\n\n\3\13\3\13\3\13\3\13"+
		"\3\13\3\13\3\13\5\13f\n\13\3\f\3\f\3\f\3\f\3\f\3\f\5\fn\n\f\3\r\3\r\3"+
		"\r\3\r\7\rt\n\r\f\r\16\rw\13\r\5\ry\n\r\3\r\3\r\3\16\3\16\3\16\3\16\3"+
		"\16\3\16\3\16\7\16\u0084\n\16\f\16\16\16\u0087\13\16\3\17\3\17\3\17\3"+
		"\17\3\17\7\17\u008e\n\17\f\17\16\17\u0091\13\17\3\17\3\17\3\20\3\20\3"+
		"\20\7\20\u0098\n\20\f\20\16\20\u009b\13\20\3\21\3\21\3\21\5\21\u00a0\n"+
		"\21\3\22\3\22\3\22\3\23\3\23\3\23\3\23\3\24\3\24\3\24\2\2\25\2\4\6\b\n"+
		"\f\16\20\22\24\26\30\32\34\36 \"$&\2\6\4\2\t\n\16\23\3\2\24\25\3\2\26"+
		"\30\3\2\31\35\2\u00ae\2(\3\2\2\2\4-\3\2\2\2\6/\3\2\2\2\b\67\3\2\2\2\n"+
		"B\3\2\2\2\fD\3\2\2\2\16I\3\2\2\2\20Q\3\2\2\2\22\\\3\2\2\2\24e\3\2\2\2"+
		"\26m\3\2\2\2\30o\3\2\2\2\32|\3\2\2\2\34\u0088\3\2\2\2\36\u0094\3\2\2\2"+
		" \u009f\3\2\2\2\"\u00a1\3\2\2\2$\u00a4\3\2\2\2&\u00a8\3\2\2\2()\5\4\3"+
		"\2)*\7\r\2\2*+\5\36\20\2+,\7\2\2\3,\3\3\2\2\2-.\5\6\4\2.\5\3\2\2\2/\64"+
		"\5\b\5\2\60\61\7\7\2\2\61\63\5\b\5\2\62\60\3\2\2\2\63\66\3\2\2\2\64\62"+
		"\3\2\2\2\64\65\3\2\2\2\65\7\3\2\2\2\66\64\3\2\2\2\67<\5\n\6\289\7\6\2"+
		"\29;\5\n\6\2:8\3\2\2\2;>\3\2\2\2<:\3\2\2\2<=\3\2\2\2=\t\3\2\2\2><\3\2"+
		"\2\2?@\7\b\2\2@C\5\n\6\2AC\5\f\7\2B?\3\2\2\2BA\3\2\2\2C\13\3\2\2\2DG\5"+
		"\16\b\2EF\t\2\2\2FH\5\16\b\2GE\3\2\2\2GH\3\2\2\2H\r\3\2\2\2IN\5\20\t\2"+
		"JK\t\3\2\2KM\5\20\t\2LJ\3\2\2\2MP\3\2\2\2NL\3\2\2\2NO\3\2\2\2O\17\3\2"+
		"\2\2PN\3\2\2\2QV\5\22\n\2RS\t\4\2\2SU\5\22\n\2TR\3\2\2\2UX\3\2\2\2VT\3"+
		"\2\2\2VW\3\2\2\2W\21\3\2\2\2XV\3\2\2\2YZ\7\25\2\2Z]\5\22\n\2[]\5\24\13"+
		"\2\\Y\3\2\2\2\\[\3\2\2\2]\23\3\2\2\2^_\7\36\2\2_`\5\6\4\2`a\7\37\2\2a"+
		"f\3\2\2\2bf\5\26\f\2cf\5\32\16\2df\5\34\17\2e^\3\2\2\2eb\3\2\2\2ec\3\2"+
		"\2\2ed\3\2\2\2f\25\3\2\2\2gn\7%\2\2hn\7&\2\2in\7\3\2\2jn\7\4\2\2kn\7\5"+
		"\2\2ln\5\30\r\2mg\3\2\2\2mh\3\2\2\2mi\3\2\2\2mj\3\2\2\2mk\3\2\2\2ml\3"+
		"\2\2\2n\27\3\2\2\2ox\7 \2\2pu\5\6\4\2qr\7#\2\2rt\5\6\4\2sq\3\2\2\2tw\3"+
		"\2\2\2us\3\2\2\2uv\3\2\2\2vy\3\2\2\2wu\3\2\2\2xp\3\2\2\2xy\3\2\2\2yz\3"+
		"\2\2\2z{\7!\2\2{\31\3\2\2\2|\u0085\7\'\2\2}~\7\"\2\2~\u0084\7\'\2\2\177"+
		"\u0080\7 \2\2\u0080\u0081\5\6\4\2\u0081\u0082\7!\2\2\u0082\u0084\3\2\2"+
		"\2\u0083}\3\2\2\2\u0083\177\3\2\2\2\u0084\u0087\3\2\2\2\u0085\u0083\3"+
		"\2\2\2\u0085\u0086\3\2\2\2\u0086\33\3\2\2\2\u0087\u0085\3\2\2\2\u0088"+
		"\u0089\7\f\2\2\u0089\u008a\7\36\2\2\u008a\u008f\7&\2\2\u008b\u008c\7#"+
		"\2\2\u008c\u008e\5\6\4\2\u008d\u008b\3\2\2\2\u008e\u0091\3\2\2\2\u008f"+
		"\u008d\3\2\2\2\u008f\u0090\3\2\2\2\u0090\u0092\3\2\2\2\u0091\u008f\3\2"+
		"\2\2\u0092\u0093\7\37\2\2\u0093\35\3\2\2\2\u0094\u0099\5 \21\2\u0095\u0096"+
		"\7$\2\2\u0096\u0098\5 \21\2\u0097\u0095\3\2\2\2\u0098\u009b\3\2\2\2\u0099"+
		"\u0097\3\2\2\2\u0099\u009a\3\2\2\2\u009a\37\3\2\2\2\u009b\u0099\3\2\2"+
		"\2\u009c\u00a0\5\"\22\2\u009d\u00a0\5$\23\2\u009e\u00a0\5\34\17\2\u009f"+
		"\u009c\3\2\2\2\u009f\u009d\3\2\2\2\u009f\u009e\3\2\2\2\u00a0!\3\2\2\2"+
		"\u00a1\u00a2\7\13\2\2\u00a2\u00a3\5\6\4\2\u00a3#\3\2\2\2\u00a4\u00a5\5"+
		"\32\16\2\u00a5\u00a6\5&\24\2\u00a6\u00a7\5\6\4\2\u00a7%\3\2\2\2\u00a8"+
		"\u00a9\t\5\2\2\u00a9\'\3\2\2\2\22\64<BGNV\\emux\u0083\u0085\u008f\u0099"+
		"\u009f";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}