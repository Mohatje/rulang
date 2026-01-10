# Generated from src/rule_interpreter/grammar/BusinessRules.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,50,239,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,2,1,2,1,2,5,2,55,8,
        2,10,2,12,2,58,9,2,1,3,1,3,1,3,5,3,63,8,3,10,3,12,3,66,9,3,1,4,1,
        4,1,4,3,4,71,8,4,1,5,1,5,1,5,3,5,76,8,5,1,5,1,5,1,5,1,5,1,5,1,5,
        1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,
        1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,3,5,112,8,5,1,6,
        1,6,1,6,5,6,117,8,6,10,6,12,6,120,9,6,1,7,1,7,1,7,5,7,125,8,7,10,
        7,12,7,128,9,7,1,8,1,8,1,8,5,8,133,8,8,10,8,12,8,136,9,8,1,9,1,9,
        1,9,3,9,141,8,9,1,10,1,10,1,10,1,10,1,10,1,10,1,10,1,10,3,10,151,
        8,10,1,11,1,11,1,11,1,11,1,11,5,11,158,8,11,10,11,12,11,161,9,11,
        3,11,163,8,11,1,11,1,11,1,12,1,12,1,12,1,12,1,12,1,12,3,12,173,8,
        12,1,13,1,13,1,13,1,13,5,13,179,8,13,10,13,12,13,182,9,13,3,13,184,
        8,13,1,13,1,13,1,14,1,14,5,14,190,8,14,10,14,12,14,193,9,14,1,15,
        1,15,1,15,1,15,1,15,1,15,1,15,1,15,3,15,203,8,15,1,16,1,16,1,16,
        1,16,1,16,5,16,210,8,16,10,16,12,16,213,9,16,1,16,1,16,1,17,1,17,
        1,17,5,17,220,8,17,10,17,12,17,223,9,17,1,18,1,18,1,18,3,18,228,
        8,18,1,19,1,19,1,19,1,20,1,20,1,20,1,20,1,21,1,21,1,21,0,0,22,0,
        2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,0,4,2,
        0,7,8,21,26,1,0,27,28,1,0,29,31,1,0,32,36,253,0,44,1,0,0,0,2,49,
        1,0,0,0,4,51,1,0,0,0,6,59,1,0,0,0,8,70,1,0,0,0,10,111,1,0,0,0,12,
        113,1,0,0,0,14,121,1,0,0,0,16,129,1,0,0,0,18,140,1,0,0,0,20,150,
        1,0,0,0,22,152,1,0,0,0,24,172,1,0,0,0,26,174,1,0,0,0,28,187,1,0,
        0,0,30,202,1,0,0,0,32,204,1,0,0,0,34,216,1,0,0,0,36,227,1,0,0,0,
        38,229,1,0,0,0,40,232,1,0,0,0,42,236,1,0,0,0,44,45,3,2,1,0,45,46,
        5,20,0,0,46,47,3,34,17,0,47,48,5,0,0,1,48,1,1,0,0,0,49,50,3,4,2,
        0,50,3,1,0,0,0,51,56,3,6,3,0,52,53,5,5,0,0,53,55,3,6,3,0,54,52,1,
        0,0,0,55,58,1,0,0,0,56,54,1,0,0,0,56,57,1,0,0,0,57,5,1,0,0,0,58,
        56,1,0,0,0,59,64,3,8,4,0,60,61,5,4,0,0,61,63,3,8,4,0,62,60,1,0,0,
        0,63,66,1,0,0,0,64,62,1,0,0,0,64,65,1,0,0,0,65,7,1,0,0,0,66,64,1,
        0,0,0,67,68,5,6,0,0,68,71,3,8,4,0,69,71,3,10,5,0,70,67,1,0,0,0,70,
        69,1,0,0,0,71,9,1,0,0,0,72,75,3,12,6,0,73,74,7,0,0,0,74,76,3,12,
        6,0,75,73,1,0,0,0,75,76,1,0,0,0,76,112,1,0,0,0,77,78,3,12,6,0,78,
        79,5,14,0,0,79,80,3,12,6,0,80,112,1,0,0,0,81,82,3,12,6,0,82,83,5,
        13,0,0,83,84,3,12,6,0,84,112,1,0,0,0,85,86,3,12,6,0,86,87,5,15,0,
        0,87,88,3,12,6,0,88,112,1,0,0,0,89,90,3,12,6,0,90,91,5,16,0,0,91,
        92,3,12,6,0,92,112,1,0,0,0,93,94,3,12,6,0,94,95,5,17,0,0,95,96,3,
        12,6,0,96,112,1,0,0,0,97,98,3,12,6,0,98,99,5,11,0,0,99,100,3,12,
        6,0,100,112,1,0,0,0,101,102,3,12,6,0,102,103,5,12,0,0,103,104,3,
        12,6,0,104,112,1,0,0,0,105,106,3,12,6,0,106,107,5,18,0,0,107,112,
        1,0,0,0,108,109,3,12,6,0,109,110,5,19,0,0,110,112,1,0,0,0,111,72,
        1,0,0,0,111,77,1,0,0,0,111,81,1,0,0,0,111,85,1,0,0,0,111,89,1,0,
        0,0,111,93,1,0,0,0,111,97,1,0,0,0,111,101,1,0,0,0,111,105,1,0,0,
        0,111,108,1,0,0,0,112,11,1,0,0,0,113,118,3,14,7,0,114,115,5,37,0,
        0,115,117,3,14,7,0,116,114,1,0,0,0,117,120,1,0,0,0,118,116,1,0,0,
        0,118,119,1,0,0,0,119,13,1,0,0,0,120,118,1,0,0,0,121,126,3,16,8,
        0,122,123,7,1,0,0,123,125,3,16,8,0,124,122,1,0,0,0,125,128,1,0,0,
        0,126,124,1,0,0,0,126,127,1,0,0,0,127,15,1,0,0,0,128,126,1,0,0,0,
        129,134,3,18,9,0,130,131,7,2,0,0,131,133,3,18,9,0,132,130,1,0,0,
        0,133,136,1,0,0,0,134,132,1,0,0,0,134,135,1,0,0,0,135,17,1,0,0,0,
        136,134,1,0,0,0,137,138,5,28,0,0,138,141,3,18,9,0,139,141,3,20,10,
        0,140,137,1,0,0,0,140,139,1,0,0,0,141,19,1,0,0,0,142,143,5,39,0,
        0,143,144,3,4,2,0,144,145,5,40,0,0,145,151,1,0,0,0,146,151,3,24,
        12,0,147,151,3,22,11,0,148,151,3,28,14,0,149,151,3,32,16,0,150,142,
        1,0,0,0,150,146,1,0,0,0,150,147,1,0,0,0,150,148,1,0,0,0,150,149,
        1,0,0,0,151,21,1,0,0,0,152,153,5,48,0,0,153,162,5,39,0,0,154,159,
        3,4,2,0,155,156,5,44,0,0,156,158,3,4,2,0,157,155,1,0,0,0,158,161,
        1,0,0,0,159,157,1,0,0,0,159,160,1,0,0,0,160,163,1,0,0,0,161,159,
        1,0,0,0,162,154,1,0,0,0,162,163,1,0,0,0,163,164,1,0,0,0,164,165,
        5,40,0,0,165,23,1,0,0,0,166,173,5,46,0,0,167,173,5,47,0,0,168,173,
        5,1,0,0,169,173,5,2,0,0,170,173,5,3,0,0,171,173,3,26,13,0,172,166,
        1,0,0,0,172,167,1,0,0,0,172,168,1,0,0,0,172,169,1,0,0,0,172,170,
        1,0,0,0,172,171,1,0,0,0,173,25,1,0,0,0,174,183,5,41,0,0,175,180,
        3,4,2,0,176,177,5,44,0,0,177,179,3,4,2,0,178,176,1,0,0,0,179,182,
        1,0,0,0,180,178,1,0,0,0,180,181,1,0,0,0,181,184,1,0,0,0,182,180,
        1,0,0,0,183,175,1,0,0,0,183,184,1,0,0,0,184,185,1,0,0,0,185,186,
        5,42,0,0,186,27,1,0,0,0,187,191,5,48,0,0,188,190,3,30,15,0,189,188,
        1,0,0,0,190,193,1,0,0,0,191,189,1,0,0,0,191,192,1,0,0,0,192,29,1,
        0,0,0,193,191,1,0,0,0,194,195,5,43,0,0,195,203,5,48,0,0,196,197,
        5,38,0,0,197,203,5,48,0,0,198,199,5,41,0,0,199,200,3,4,2,0,200,201,
        5,42,0,0,201,203,1,0,0,0,202,194,1,0,0,0,202,196,1,0,0,0,202,198,
        1,0,0,0,203,31,1,0,0,0,204,205,5,10,0,0,205,206,5,39,0,0,206,211,
        5,47,0,0,207,208,5,44,0,0,208,210,3,4,2,0,209,207,1,0,0,0,210,213,
        1,0,0,0,211,209,1,0,0,0,211,212,1,0,0,0,212,214,1,0,0,0,213,211,
        1,0,0,0,214,215,5,40,0,0,215,33,1,0,0,0,216,221,3,36,18,0,217,218,
        5,45,0,0,218,220,3,36,18,0,219,217,1,0,0,0,220,223,1,0,0,0,221,219,
        1,0,0,0,221,222,1,0,0,0,222,35,1,0,0,0,223,221,1,0,0,0,224,228,3,
        38,19,0,225,228,3,40,20,0,226,228,3,32,16,0,227,224,1,0,0,0,227,
        225,1,0,0,0,227,226,1,0,0,0,228,37,1,0,0,0,229,230,5,9,0,0,230,231,
        3,4,2,0,231,39,1,0,0,0,232,233,3,28,14,0,233,234,3,42,21,0,234,235,
        3,4,2,0,235,41,1,0,0,0,236,237,7,3,0,0,237,43,1,0,0,0,20,56,64,70,
        75,111,118,126,134,140,150,159,162,172,180,183,191,202,211,221,227
    ]

class BusinessRulesParser ( Parser ):

    grammarFileName = "BusinessRules.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'and'", "'or'", "'not'", "'in'", "<INVALID>", "'ret'", 
                     "'workflow'", "'contains_any'", "'contains_all'", "<INVALID>", 
                     "'contains'", "<INVALID>", "<INVALID>", "'matches'", 
                     "<INVALID>", "'exists'", "'=>'", "'=='", "'!='", "'<='", 
                     "'>='", "'<'", "'>'", "'+'", "'-'", "'*'", "'/'", "'%'", 
                     "'='", "'+='", "'-='", "'*='", "'/='", "'??'", "'?.'", 
                     "'('", "')'", "'['", "']'", "'.'", "','", "';'" ]

    symbolicNames = [ "<INVALID>", "TRUE", "FALSE", "NONE", "AND", "OR", 
                      "NOT", "IN", "NOT_IN", "RET", "WORKFLOW", "CONTAINS_ANY", 
                      "CONTAINS_ALL", "NOT_CONTAINS", "CONTAINS", "STARTS_WITH", 
                      "ENDS_WITH", "MATCHES", "IS_EMPTY", "EXISTS", "ARROW", 
                      "EQ", "NEQ", "LTE", "GTE", "LT", "GT", "PLUS", "MINUS", 
                      "STAR", "SLASH", "MOD", "ASSIGN", "PLUS_ASSIGN", "MINUS_ASSIGN", 
                      "STAR_ASSIGN", "SLASH_ASSIGN", "NULL_COALESCE", "NULL_SAFE_DOT", 
                      "LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "DOT", 
                      "COMMA", "SEMICOLON", "NUMBER", "STRING", "IDENTIFIER", 
                      "WS", "LINE_COMMENT" ]

    RULE_rule_ = 0
    RULE_condition = 1
    RULE_orExpr = 2
    RULE_andExpr = 3
    RULE_notExpr = 4
    RULE_comparison = 5
    RULE_nullCoalesce = 6
    RULE_addExpr = 7
    RULE_mulExpr = 8
    RULE_unaryExpr = 9
    RULE_primary = 10
    RULE_functionCall = 11
    RULE_literal = 12
    RULE_list_ = 13
    RULE_path = 14
    RULE_pathSegment = 15
    RULE_workflowCall = 16
    RULE_actions = 17
    RULE_action = 18
    RULE_returnStmt = 19
    RULE_assignment = 20
    RULE_assignOp = 21

    ruleNames =  [ "rule_", "condition", "orExpr", "andExpr", "notExpr", 
                   "comparison", "nullCoalesce", "addExpr", "mulExpr", "unaryExpr", 
                   "primary", "functionCall", "literal", "list_", "path", 
                   "pathSegment", "workflowCall", "actions", "action", "returnStmt", 
                   "assignment", "assignOp" ]

    EOF = Token.EOF
    TRUE=1
    FALSE=2
    NONE=3
    AND=4
    OR=5
    NOT=6
    IN=7
    NOT_IN=8
    RET=9
    WORKFLOW=10
    CONTAINS_ANY=11
    CONTAINS_ALL=12
    NOT_CONTAINS=13
    CONTAINS=14
    STARTS_WITH=15
    ENDS_WITH=16
    MATCHES=17
    IS_EMPTY=18
    EXISTS=19
    ARROW=20
    EQ=21
    NEQ=22
    LTE=23
    GTE=24
    LT=25
    GT=26
    PLUS=27
    MINUS=28
    STAR=29
    SLASH=30
    MOD=31
    ASSIGN=32
    PLUS_ASSIGN=33
    MINUS_ASSIGN=34
    STAR_ASSIGN=35
    SLASH_ASSIGN=36
    NULL_COALESCE=37
    NULL_SAFE_DOT=38
    LPAREN=39
    RPAREN=40
    LBRACKET=41
    RBRACKET=42
    DOT=43
    COMMA=44
    SEMICOLON=45
    NUMBER=46
    STRING=47
    IDENTIFIER=48
    WS=49
    LINE_COMMENT=50

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Rule_Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def condition(self):
            return self.getTypedRuleContext(BusinessRulesParser.ConditionContext,0)


        def ARROW(self):
            return self.getToken(BusinessRulesParser.ARROW, 0)

        def actions(self):
            return self.getTypedRuleContext(BusinessRulesParser.ActionsContext,0)


        def EOF(self):
            return self.getToken(BusinessRulesParser.EOF, 0)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_rule_

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRule_" ):
                listener.enterRule_(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRule_" ):
                listener.exitRule_(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRule_" ):
                return visitor.visitRule_(self)
            else:
                return visitor.visitChildren(self)




    def rule_(self):

        localctx = BusinessRulesParser.Rule_Context(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_rule_)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44
            self.condition()
            self.state = 45
            self.match(BusinessRulesParser.ARROW)
            self.state = 46
            self.actions()
            self.state = 47
            self.match(BusinessRulesParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def orExpr(self):
            return self.getTypedRuleContext(BusinessRulesParser.OrExprContext,0)


        def getRuleIndex(self):
            return BusinessRulesParser.RULE_condition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCondition" ):
                listener.enterCondition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCondition" ):
                listener.exitCondition(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCondition" ):
                return visitor.visitCondition(self)
            else:
                return visitor.visitChildren(self)




    def condition(self):

        localctx = BusinessRulesParser.ConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_condition)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 49
            self.orExpr()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OrExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def andExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.AndExprContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.AndExprContext,i)


        def OR(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.OR)
            else:
                return self.getToken(BusinessRulesParser.OR, i)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_orExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrExpr" ):
                listener.enterOrExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrExpr" ):
                listener.exitOrExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOrExpr" ):
                return visitor.visitOrExpr(self)
            else:
                return visitor.visitChildren(self)




    def orExpr(self):

        localctx = BusinessRulesParser.OrExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_orExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self.andExpr()
            self.state = 56
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==5:
                self.state = 52
                self.match(BusinessRulesParser.OR)
                self.state = 53
                self.andExpr()
                self.state = 58
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AndExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def notExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.NotExprContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.NotExprContext,i)


        def AND(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.AND)
            else:
                return self.getToken(BusinessRulesParser.AND, i)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_andExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAndExpr" ):
                listener.enterAndExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAndExpr" ):
                listener.exitAndExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAndExpr" ):
                return visitor.visitAndExpr(self)
            else:
                return visitor.visitChildren(self)




    def andExpr(self):

        localctx = BusinessRulesParser.AndExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_andExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 59
            self.notExpr()
            self.state = 64
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4:
                self.state = 60
                self.match(BusinessRulesParser.AND)
                self.state = 61
                self.notExpr()
                self.state = 66
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NotExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NOT(self):
            return self.getToken(BusinessRulesParser.NOT, 0)

        def notExpr(self):
            return self.getTypedRuleContext(BusinessRulesParser.NotExprContext,0)


        def comparison(self):
            return self.getTypedRuleContext(BusinessRulesParser.ComparisonContext,0)


        def getRuleIndex(self):
            return BusinessRulesParser.RULE_notExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNotExpr" ):
                listener.enterNotExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNotExpr" ):
                listener.exitNotExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNotExpr" ):
                return visitor.visitNotExpr(self)
            else:
                return visitor.visitChildren(self)




    def notExpr(self):

        localctx = BusinessRulesParser.NotExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_notExpr)
        try:
            self.state = 70
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [6]:
                self.enterOuterAlt(localctx, 1)
                self.state = 67
                self.match(BusinessRulesParser.NOT)
                self.state = 68
                self.notExpr()
                pass
            elif token in [1, 2, 3, 10, 28, 39, 41, 46, 47, 48]:
                self.enterOuterAlt(localctx, 2)
                self.state = 69
                self.comparison()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ComparisonContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nullCoalesce(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.NullCoalesceContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.NullCoalesceContext,i)


        def EQ(self):
            return self.getToken(BusinessRulesParser.EQ, 0)

        def NEQ(self):
            return self.getToken(BusinessRulesParser.NEQ, 0)

        def LT(self):
            return self.getToken(BusinessRulesParser.LT, 0)

        def GT(self):
            return self.getToken(BusinessRulesParser.GT, 0)

        def LTE(self):
            return self.getToken(BusinessRulesParser.LTE, 0)

        def GTE(self):
            return self.getToken(BusinessRulesParser.GTE, 0)

        def IN(self):
            return self.getToken(BusinessRulesParser.IN, 0)

        def NOT_IN(self):
            return self.getToken(BusinessRulesParser.NOT_IN, 0)

        def CONTAINS(self):
            return self.getToken(BusinessRulesParser.CONTAINS, 0)

        def NOT_CONTAINS(self):
            return self.getToken(BusinessRulesParser.NOT_CONTAINS, 0)

        def STARTS_WITH(self):
            return self.getToken(BusinessRulesParser.STARTS_WITH, 0)

        def ENDS_WITH(self):
            return self.getToken(BusinessRulesParser.ENDS_WITH, 0)

        def MATCHES(self):
            return self.getToken(BusinessRulesParser.MATCHES, 0)

        def CONTAINS_ANY(self):
            return self.getToken(BusinessRulesParser.CONTAINS_ANY, 0)

        def CONTAINS_ALL(self):
            return self.getToken(BusinessRulesParser.CONTAINS_ALL, 0)

        def IS_EMPTY(self):
            return self.getToken(BusinessRulesParser.IS_EMPTY, 0)

        def EXISTS(self):
            return self.getToken(BusinessRulesParser.EXISTS, 0)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_comparison

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComparison" ):
                listener.enterComparison(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComparison" ):
                listener.exitComparison(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitComparison" ):
                return visitor.visitComparison(self)
            else:
                return visitor.visitChildren(self)




    def comparison(self):

        localctx = BusinessRulesParser.ComparisonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_comparison)
        self._la = 0 # Token type
        try:
            self.state = 111
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 72
                self.nullCoalesce()
                self.state = 75
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 132120960) != 0):
                    self.state = 73
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 132120960) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 74
                    self.nullCoalesce()


                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 77
                self.nullCoalesce()
                self.state = 78
                self.match(BusinessRulesParser.CONTAINS)
                self.state = 79
                self.nullCoalesce()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 81
                self.nullCoalesce()
                self.state = 82
                self.match(BusinessRulesParser.NOT_CONTAINS)
                self.state = 83
                self.nullCoalesce()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 85
                self.nullCoalesce()
                self.state = 86
                self.match(BusinessRulesParser.STARTS_WITH)
                self.state = 87
                self.nullCoalesce()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 89
                self.nullCoalesce()
                self.state = 90
                self.match(BusinessRulesParser.ENDS_WITH)
                self.state = 91
                self.nullCoalesce()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 93
                self.nullCoalesce()
                self.state = 94
                self.match(BusinessRulesParser.MATCHES)
                self.state = 95
                self.nullCoalesce()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 97
                self.nullCoalesce()
                self.state = 98
                self.match(BusinessRulesParser.CONTAINS_ANY)
                self.state = 99
                self.nullCoalesce()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 101
                self.nullCoalesce()
                self.state = 102
                self.match(BusinessRulesParser.CONTAINS_ALL)
                self.state = 103
                self.nullCoalesce()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 105
                self.nullCoalesce()
                self.state = 106
                self.match(BusinessRulesParser.IS_EMPTY)
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 108
                self.nullCoalesce()
                self.state = 109
                self.match(BusinessRulesParser.EXISTS)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NullCoalesceContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def addExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.AddExprContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.AddExprContext,i)


        def NULL_COALESCE(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.NULL_COALESCE)
            else:
                return self.getToken(BusinessRulesParser.NULL_COALESCE, i)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_nullCoalesce

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNullCoalesce" ):
                listener.enterNullCoalesce(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNullCoalesce" ):
                listener.exitNullCoalesce(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNullCoalesce" ):
                return visitor.visitNullCoalesce(self)
            else:
                return visitor.visitChildren(self)




    def nullCoalesce(self):

        localctx = BusinessRulesParser.NullCoalesceContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_nullCoalesce)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            self.addExpr()
            self.state = 118
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==37:
                self.state = 114
                self.match(BusinessRulesParser.NULL_COALESCE)
                self.state = 115
                self.addExpr()
                self.state = 120
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AddExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def mulExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.MulExprContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.MulExprContext,i)


        def PLUS(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.PLUS)
            else:
                return self.getToken(BusinessRulesParser.PLUS, i)

        def MINUS(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.MINUS)
            else:
                return self.getToken(BusinessRulesParser.MINUS, i)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_addExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddExpr" ):
                listener.enterAddExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddExpr" ):
                listener.exitAddExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddExpr" ):
                return visitor.visitAddExpr(self)
            else:
                return visitor.visitChildren(self)




    def addExpr(self):

        localctx = BusinessRulesParser.AddExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_addExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 121
            self.mulExpr()
            self.state = 126
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==27 or _la==28:
                self.state = 122
                _la = self._input.LA(1)
                if not(_la==27 or _la==28):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 123
                self.mulExpr()
                self.state = 128
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MulExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def unaryExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.UnaryExprContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.UnaryExprContext,i)


        def STAR(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.STAR)
            else:
                return self.getToken(BusinessRulesParser.STAR, i)

        def SLASH(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.SLASH)
            else:
                return self.getToken(BusinessRulesParser.SLASH, i)

        def MOD(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.MOD)
            else:
                return self.getToken(BusinessRulesParser.MOD, i)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_mulExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMulExpr" ):
                listener.enterMulExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMulExpr" ):
                listener.exitMulExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMulExpr" ):
                return visitor.visitMulExpr(self)
            else:
                return visitor.visitChildren(self)




    def mulExpr(self):

        localctx = BusinessRulesParser.MulExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_mulExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 129
            self.unaryExpr()
            self.state = 134
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3758096384) != 0):
                self.state = 130
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 3758096384) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 131
                self.unaryExpr()
                self.state = 136
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class UnaryExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def MINUS(self):
            return self.getToken(BusinessRulesParser.MINUS, 0)

        def unaryExpr(self):
            return self.getTypedRuleContext(BusinessRulesParser.UnaryExprContext,0)


        def primary(self):
            return self.getTypedRuleContext(BusinessRulesParser.PrimaryContext,0)


        def getRuleIndex(self):
            return BusinessRulesParser.RULE_unaryExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUnaryExpr" ):
                listener.enterUnaryExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUnaryExpr" ):
                listener.exitUnaryExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUnaryExpr" ):
                return visitor.visitUnaryExpr(self)
            else:
                return visitor.visitChildren(self)




    def unaryExpr(self):

        localctx = BusinessRulesParser.UnaryExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_unaryExpr)
        try:
            self.state = 140
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [28]:
                self.enterOuterAlt(localctx, 1)
                self.state = 137
                self.match(BusinessRulesParser.MINUS)
                self.state = 138
                self.unaryExpr()
                pass
            elif token in [1, 2, 3, 10, 39, 41, 46, 47, 48]:
                self.enterOuterAlt(localctx, 2)
                self.state = 139
                self.primary()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PrimaryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(BusinessRulesParser.LPAREN, 0)

        def orExpr(self):
            return self.getTypedRuleContext(BusinessRulesParser.OrExprContext,0)


        def RPAREN(self):
            return self.getToken(BusinessRulesParser.RPAREN, 0)

        def literal(self):
            return self.getTypedRuleContext(BusinessRulesParser.LiteralContext,0)


        def functionCall(self):
            return self.getTypedRuleContext(BusinessRulesParser.FunctionCallContext,0)


        def path(self):
            return self.getTypedRuleContext(BusinessRulesParser.PathContext,0)


        def workflowCall(self):
            return self.getTypedRuleContext(BusinessRulesParser.WorkflowCallContext,0)


        def getRuleIndex(self):
            return BusinessRulesParser.RULE_primary

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrimary" ):
                listener.enterPrimary(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrimary" ):
                listener.exitPrimary(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrimary" ):
                return visitor.visitPrimary(self)
            else:
                return visitor.visitChildren(self)




    def primary(self):

        localctx = BusinessRulesParser.PrimaryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_primary)
        try:
            self.state = 150
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,9,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 142
                self.match(BusinessRulesParser.LPAREN)
                self.state = 143
                self.orExpr()
                self.state = 144
                self.match(BusinessRulesParser.RPAREN)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 146
                self.literal()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 147
                self.functionCall()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 148
                self.path()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 149
                self.workflowCall()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FunctionCallContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(BusinessRulesParser.IDENTIFIER, 0)

        def LPAREN(self):
            return self.getToken(BusinessRulesParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(BusinessRulesParser.RPAREN, 0)

        def orExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.OrExprContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.OrExprContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.COMMA)
            else:
                return self.getToken(BusinessRulesParser.COMMA, i)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_functionCall

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunctionCall" ):
                listener.enterFunctionCall(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunctionCall" ):
                listener.exitFunctionCall(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFunctionCall" ):
                return visitor.visitFunctionCall(self)
            else:
                return visitor.visitChildren(self)




    def functionCall(self):

        localctx = BusinessRulesParser.FunctionCallContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_functionCall)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 152
            self.match(BusinessRulesParser.IDENTIFIER)
            self.state = 153
            self.match(BusinessRulesParser.LPAREN)
            self.state = 162
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 495330256749646) != 0):
                self.state = 154
                self.orExpr()
                self.state = 159
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==44:
                    self.state = 155
                    self.match(BusinessRulesParser.COMMA)
                    self.state = 156
                    self.orExpr()
                    self.state = 161
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 164
            self.match(BusinessRulesParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(BusinessRulesParser.NUMBER, 0)

        def STRING(self):
            return self.getToken(BusinessRulesParser.STRING, 0)

        def TRUE(self):
            return self.getToken(BusinessRulesParser.TRUE, 0)

        def FALSE(self):
            return self.getToken(BusinessRulesParser.FALSE, 0)

        def NONE(self):
            return self.getToken(BusinessRulesParser.NONE, 0)

        def list_(self):
            return self.getTypedRuleContext(BusinessRulesParser.List_Context,0)


        def getRuleIndex(self):
            return BusinessRulesParser.RULE_literal

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteral" ):
                listener.enterLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteral" ):
                listener.exitLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLiteral" ):
                return visitor.visitLiteral(self)
            else:
                return visitor.visitChildren(self)




    def literal(self):

        localctx = BusinessRulesParser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_literal)
        try:
            self.state = 172
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [46]:
                self.enterOuterAlt(localctx, 1)
                self.state = 166
                self.match(BusinessRulesParser.NUMBER)
                pass
            elif token in [47]:
                self.enterOuterAlt(localctx, 2)
                self.state = 167
                self.match(BusinessRulesParser.STRING)
                pass
            elif token in [1]:
                self.enterOuterAlt(localctx, 3)
                self.state = 168
                self.match(BusinessRulesParser.TRUE)
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 4)
                self.state = 169
                self.match(BusinessRulesParser.FALSE)
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 5)
                self.state = 170
                self.match(BusinessRulesParser.NONE)
                pass
            elif token in [41]:
                self.enterOuterAlt(localctx, 6)
                self.state = 171
                self.list_()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class List_Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACKET(self):
            return self.getToken(BusinessRulesParser.LBRACKET, 0)

        def RBRACKET(self):
            return self.getToken(BusinessRulesParser.RBRACKET, 0)

        def orExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.OrExprContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.OrExprContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.COMMA)
            else:
                return self.getToken(BusinessRulesParser.COMMA, i)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_list_

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterList_" ):
                listener.enterList_(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitList_" ):
                listener.exitList_(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitList_" ):
                return visitor.visitList_(self)
            else:
                return visitor.visitChildren(self)




    def list_(self):

        localctx = BusinessRulesParser.List_Context(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_list_)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 174
            self.match(BusinessRulesParser.LBRACKET)
            self.state = 183
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 495330256749646) != 0):
                self.state = 175
                self.orExpr()
                self.state = 180
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==44:
                    self.state = 176
                    self.match(BusinessRulesParser.COMMA)
                    self.state = 177
                    self.orExpr()
                    self.state = 182
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 185
            self.match(BusinessRulesParser.RBRACKET)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PathContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(BusinessRulesParser.IDENTIFIER, 0)

        def pathSegment(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.PathSegmentContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.PathSegmentContext,i)


        def getRuleIndex(self):
            return BusinessRulesParser.RULE_path

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPath" ):
                listener.enterPath(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPath" ):
                listener.exitPath(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPath" ):
                return visitor.visitPath(self)
            else:
                return visitor.visitChildren(self)




    def path(self):

        localctx = BusinessRulesParser.PathContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_path)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 187
            self.match(BusinessRulesParser.IDENTIFIER)
            self.state = 191
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 11269994184704) != 0):
                self.state = 188
                self.pathSegment()
                self.state = 193
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PathSegmentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOT(self):
            return self.getToken(BusinessRulesParser.DOT, 0)

        def IDENTIFIER(self):
            return self.getToken(BusinessRulesParser.IDENTIFIER, 0)

        def NULL_SAFE_DOT(self):
            return self.getToken(BusinessRulesParser.NULL_SAFE_DOT, 0)

        def LBRACKET(self):
            return self.getToken(BusinessRulesParser.LBRACKET, 0)

        def orExpr(self):
            return self.getTypedRuleContext(BusinessRulesParser.OrExprContext,0)


        def RBRACKET(self):
            return self.getToken(BusinessRulesParser.RBRACKET, 0)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_pathSegment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPathSegment" ):
                listener.enterPathSegment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPathSegment" ):
                listener.exitPathSegment(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPathSegment" ):
                return visitor.visitPathSegment(self)
            else:
                return visitor.visitChildren(self)




    def pathSegment(self):

        localctx = BusinessRulesParser.PathSegmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_pathSegment)
        try:
            self.state = 202
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [43]:
                self.enterOuterAlt(localctx, 1)
                self.state = 194
                self.match(BusinessRulesParser.DOT)
                self.state = 195
                self.match(BusinessRulesParser.IDENTIFIER)
                pass
            elif token in [38]:
                self.enterOuterAlt(localctx, 2)
                self.state = 196
                self.match(BusinessRulesParser.NULL_SAFE_DOT)
                self.state = 197
                self.match(BusinessRulesParser.IDENTIFIER)
                pass
            elif token in [41]:
                self.enterOuterAlt(localctx, 3)
                self.state = 198
                self.match(BusinessRulesParser.LBRACKET)
                self.state = 199
                self.orExpr()
                self.state = 200
                self.match(BusinessRulesParser.RBRACKET)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WorkflowCallContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORKFLOW(self):
            return self.getToken(BusinessRulesParser.WORKFLOW, 0)

        def LPAREN(self):
            return self.getToken(BusinessRulesParser.LPAREN, 0)

        def STRING(self):
            return self.getToken(BusinessRulesParser.STRING, 0)

        def RPAREN(self):
            return self.getToken(BusinessRulesParser.RPAREN, 0)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.COMMA)
            else:
                return self.getToken(BusinessRulesParser.COMMA, i)

        def orExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.OrExprContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.OrExprContext,i)


        def getRuleIndex(self):
            return BusinessRulesParser.RULE_workflowCall

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWorkflowCall" ):
                listener.enterWorkflowCall(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWorkflowCall" ):
                listener.exitWorkflowCall(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWorkflowCall" ):
                return visitor.visitWorkflowCall(self)
            else:
                return visitor.visitChildren(self)




    def workflowCall(self):

        localctx = BusinessRulesParser.WorkflowCallContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_workflowCall)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 204
            self.match(BusinessRulesParser.WORKFLOW)
            self.state = 205
            self.match(BusinessRulesParser.LPAREN)
            self.state = 206
            self.match(BusinessRulesParser.STRING)
            self.state = 211
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==44:
                self.state = 207
                self.match(BusinessRulesParser.COMMA)
                self.state = 208
                self.orExpr()
                self.state = 213
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 214
            self.match(BusinessRulesParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ActionsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def action(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.ActionContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.ActionContext,i)


        def SEMICOLON(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.SEMICOLON)
            else:
                return self.getToken(BusinessRulesParser.SEMICOLON, i)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_actions

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterActions" ):
                listener.enterActions(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitActions" ):
                listener.exitActions(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitActions" ):
                return visitor.visitActions(self)
            else:
                return visitor.visitChildren(self)




    def actions(self):

        localctx = BusinessRulesParser.ActionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_actions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 216
            self.action()
            self.state = 221
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==45:
                self.state = 217
                self.match(BusinessRulesParser.SEMICOLON)
                self.state = 218
                self.action()
                self.state = 223
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ActionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def returnStmt(self):
            return self.getTypedRuleContext(BusinessRulesParser.ReturnStmtContext,0)


        def assignment(self):
            return self.getTypedRuleContext(BusinessRulesParser.AssignmentContext,0)


        def workflowCall(self):
            return self.getTypedRuleContext(BusinessRulesParser.WorkflowCallContext,0)


        def getRuleIndex(self):
            return BusinessRulesParser.RULE_action

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAction" ):
                listener.enterAction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAction" ):
                listener.exitAction(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAction" ):
                return visitor.visitAction(self)
            else:
                return visitor.visitChildren(self)




    def action(self):

        localctx = BusinessRulesParser.ActionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_action)
        try:
            self.state = 227
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [9]:
                self.enterOuterAlt(localctx, 1)
                self.state = 224
                self.returnStmt()
                pass
            elif token in [48]:
                self.enterOuterAlt(localctx, 2)
                self.state = 225
                self.assignment()
                pass
            elif token in [10]:
                self.enterOuterAlt(localctx, 3)
                self.state = 226
                self.workflowCall()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReturnStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RET(self):
            return self.getToken(BusinessRulesParser.RET, 0)

        def orExpr(self):
            return self.getTypedRuleContext(BusinessRulesParser.OrExprContext,0)


        def getRuleIndex(self):
            return BusinessRulesParser.RULE_returnStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReturnStmt" ):
                listener.enterReturnStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReturnStmt" ):
                listener.exitReturnStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitReturnStmt" ):
                return visitor.visitReturnStmt(self)
            else:
                return visitor.visitChildren(self)




    def returnStmt(self):

        localctx = BusinessRulesParser.ReturnStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_returnStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 229
            self.match(BusinessRulesParser.RET)
            self.state = 230
            self.orExpr()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssignmentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def path(self):
            return self.getTypedRuleContext(BusinessRulesParser.PathContext,0)


        def assignOp(self):
            return self.getTypedRuleContext(BusinessRulesParser.AssignOpContext,0)


        def orExpr(self):
            return self.getTypedRuleContext(BusinessRulesParser.OrExprContext,0)


        def getRuleIndex(self):
            return BusinessRulesParser.RULE_assignment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAssignment" ):
                listener.enterAssignment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAssignment" ):
                listener.exitAssignment(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAssignment" ):
                return visitor.visitAssignment(self)
            else:
                return visitor.visitChildren(self)




    def assignment(self):

        localctx = BusinessRulesParser.AssignmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_assignment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 232
            self.path()
            self.state = 233
            self.assignOp()
            self.state = 234
            self.orExpr()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssignOpContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ASSIGN(self):
            return self.getToken(BusinessRulesParser.ASSIGN, 0)

        def PLUS_ASSIGN(self):
            return self.getToken(BusinessRulesParser.PLUS_ASSIGN, 0)

        def MINUS_ASSIGN(self):
            return self.getToken(BusinessRulesParser.MINUS_ASSIGN, 0)

        def STAR_ASSIGN(self):
            return self.getToken(BusinessRulesParser.STAR_ASSIGN, 0)

        def SLASH_ASSIGN(self):
            return self.getToken(BusinessRulesParser.SLASH_ASSIGN, 0)

        def getRuleIndex(self):
            return BusinessRulesParser.RULE_assignOp

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAssignOp" ):
                listener.enterAssignOp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAssignOp" ):
                listener.exitAssignOp(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAssignOp" ):
                return visitor.visitAssignOp(self)
            else:
                return visitor.visitChildren(self)




    def assignOp(self):

        localctx = BusinessRulesParser.AssignOpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_assignOp)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 236
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 133143986176) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





