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
        4,1,39,169,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,1,0,1,0,1,0,1,
        0,1,0,1,1,1,1,1,2,1,2,1,2,5,2,49,8,2,10,2,12,2,52,9,2,1,3,1,3,1,
        3,5,3,57,8,3,10,3,12,3,60,9,3,1,4,1,4,1,4,3,4,65,8,4,1,5,1,5,1,5,
        3,5,70,8,5,1,6,1,6,1,6,5,6,75,8,6,10,6,12,6,78,9,6,1,7,1,7,1,7,5,
        7,83,8,7,10,7,12,7,86,9,7,1,8,1,8,1,8,3,8,91,8,8,1,9,1,9,1,9,1,9,
        1,9,1,9,1,9,3,9,100,8,9,1,10,1,10,1,10,1,10,1,10,1,10,3,10,108,8,
        10,1,11,1,11,1,11,1,11,5,11,114,8,11,10,11,12,11,117,9,11,3,11,119,
        8,11,1,11,1,11,1,12,1,12,1,12,1,12,1,12,1,12,1,12,5,12,130,8,12,
        10,12,12,12,133,9,12,1,13,1,13,1,13,1,13,1,13,5,13,140,8,13,10,13,
        12,13,143,9,13,1,13,1,13,1,14,1,14,1,14,5,14,150,8,14,10,14,12,14,
        153,9,14,1,15,1,15,1,15,3,15,158,8,15,1,16,1,16,1,16,1,17,1,17,1,
        17,1,17,1,18,1,18,1,18,0,0,19,0,2,4,6,8,10,12,14,16,18,20,22,24,
        26,28,30,32,34,36,0,4,2,0,7,8,12,17,1,0,18,19,1,0,20,22,1,0,23,27,
        172,0,38,1,0,0,0,2,43,1,0,0,0,4,45,1,0,0,0,6,53,1,0,0,0,8,64,1,0,
        0,0,10,66,1,0,0,0,12,71,1,0,0,0,14,79,1,0,0,0,16,90,1,0,0,0,18,99,
        1,0,0,0,20,107,1,0,0,0,22,109,1,0,0,0,24,122,1,0,0,0,26,134,1,0,
        0,0,28,146,1,0,0,0,30,157,1,0,0,0,32,159,1,0,0,0,34,162,1,0,0,0,
        36,166,1,0,0,0,38,39,3,2,1,0,39,40,5,11,0,0,40,41,3,28,14,0,41,42,
        5,0,0,1,42,1,1,0,0,0,43,44,3,4,2,0,44,3,1,0,0,0,45,50,3,6,3,0,46,
        47,5,5,0,0,47,49,3,6,3,0,48,46,1,0,0,0,49,52,1,0,0,0,50,48,1,0,0,
        0,50,51,1,0,0,0,51,5,1,0,0,0,52,50,1,0,0,0,53,58,3,8,4,0,54,55,5,
        4,0,0,55,57,3,8,4,0,56,54,1,0,0,0,57,60,1,0,0,0,58,56,1,0,0,0,58,
        59,1,0,0,0,59,7,1,0,0,0,60,58,1,0,0,0,61,62,5,6,0,0,62,65,3,8,4,
        0,63,65,3,10,5,0,64,61,1,0,0,0,64,63,1,0,0,0,65,9,1,0,0,0,66,69,
        3,12,6,0,67,68,7,0,0,0,68,70,3,12,6,0,69,67,1,0,0,0,69,70,1,0,0,
        0,70,11,1,0,0,0,71,76,3,14,7,0,72,73,7,1,0,0,73,75,3,14,7,0,74,72,
        1,0,0,0,75,78,1,0,0,0,76,74,1,0,0,0,76,77,1,0,0,0,77,13,1,0,0,0,
        78,76,1,0,0,0,79,84,3,16,8,0,80,81,7,2,0,0,81,83,3,16,8,0,82,80,
        1,0,0,0,83,86,1,0,0,0,84,82,1,0,0,0,84,85,1,0,0,0,85,15,1,0,0,0,
        86,84,1,0,0,0,87,88,5,19,0,0,88,91,3,16,8,0,89,91,3,18,9,0,90,87,
        1,0,0,0,90,89,1,0,0,0,91,17,1,0,0,0,92,93,5,28,0,0,93,94,3,4,2,0,
        94,95,5,29,0,0,95,100,1,0,0,0,96,100,3,20,10,0,97,100,3,24,12,0,
        98,100,3,26,13,0,99,92,1,0,0,0,99,96,1,0,0,0,99,97,1,0,0,0,99,98,
        1,0,0,0,100,19,1,0,0,0,101,108,5,35,0,0,102,108,5,36,0,0,103,108,
        5,1,0,0,104,108,5,2,0,0,105,108,5,3,0,0,106,108,3,22,11,0,107,101,
        1,0,0,0,107,102,1,0,0,0,107,103,1,0,0,0,107,104,1,0,0,0,107,105,
        1,0,0,0,107,106,1,0,0,0,108,21,1,0,0,0,109,118,5,30,0,0,110,115,
        3,4,2,0,111,112,5,33,0,0,112,114,3,4,2,0,113,111,1,0,0,0,114,117,
        1,0,0,0,115,113,1,0,0,0,115,116,1,0,0,0,116,119,1,0,0,0,117,115,
        1,0,0,0,118,110,1,0,0,0,118,119,1,0,0,0,119,120,1,0,0,0,120,121,
        5,31,0,0,121,23,1,0,0,0,122,131,5,37,0,0,123,124,5,32,0,0,124,130,
        5,37,0,0,125,126,5,30,0,0,126,127,3,4,2,0,127,128,5,31,0,0,128,130,
        1,0,0,0,129,123,1,0,0,0,129,125,1,0,0,0,130,133,1,0,0,0,131,129,
        1,0,0,0,131,132,1,0,0,0,132,25,1,0,0,0,133,131,1,0,0,0,134,135,5,
        10,0,0,135,136,5,28,0,0,136,141,5,36,0,0,137,138,5,33,0,0,138,140,
        3,4,2,0,139,137,1,0,0,0,140,143,1,0,0,0,141,139,1,0,0,0,141,142,
        1,0,0,0,142,144,1,0,0,0,143,141,1,0,0,0,144,145,5,29,0,0,145,27,
        1,0,0,0,146,151,3,30,15,0,147,148,5,34,0,0,148,150,3,30,15,0,149,
        147,1,0,0,0,150,153,1,0,0,0,151,149,1,0,0,0,151,152,1,0,0,0,152,
        29,1,0,0,0,153,151,1,0,0,0,154,158,3,32,16,0,155,158,3,34,17,0,156,
        158,3,26,13,0,157,154,1,0,0,0,157,155,1,0,0,0,157,156,1,0,0,0,158,
        31,1,0,0,0,159,160,5,9,0,0,160,161,3,4,2,0,161,33,1,0,0,0,162,163,
        3,24,12,0,163,164,3,36,18,0,164,165,3,4,2,0,165,35,1,0,0,0,166,167,
        7,3,0,0,167,37,1,0,0,0,16,50,58,64,69,76,84,90,99,107,115,118,129,
        131,141,151,157
    ]

class BusinessRulesParser ( Parser ):

    grammarFileName = "BusinessRules.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'and'", "'or'", "'not'", "'in'", "<INVALID>", "'ret'", 
                     "'workflow'", "'=>'", "'=='", "'!='", "'<='", "'>='", 
                     "'<'", "'>'", "'+'", "'-'", "'*'", "'/'", "'%'", "'='", 
                     "'+='", "'-='", "'*='", "'/='", "'('", "')'", "'['", 
                     "']'", "'.'", "','", "';'" ]

    symbolicNames = [ "<INVALID>", "TRUE", "FALSE", "NONE", "AND", "OR", 
                      "NOT", "IN", "NOT_IN", "RET", "WORKFLOW", "ARROW", 
                      "EQ", "NEQ", "LTE", "GTE", "LT", "GT", "PLUS", "MINUS", 
                      "STAR", "SLASH", "MOD", "ASSIGN", "PLUS_ASSIGN", "MINUS_ASSIGN", 
                      "STAR_ASSIGN", "SLASH_ASSIGN", "LPAREN", "RPAREN", 
                      "LBRACKET", "RBRACKET", "DOT", "COMMA", "SEMICOLON", 
                      "NUMBER", "STRING", "IDENTIFIER", "WS", "LINE_COMMENT" ]

    RULE_rule_ = 0
    RULE_condition = 1
    RULE_orExpr = 2
    RULE_andExpr = 3
    RULE_notExpr = 4
    RULE_comparison = 5
    RULE_addExpr = 6
    RULE_mulExpr = 7
    RULE_unaryExpr = 8
    RULE_primary = 9
    RULE_literal = 10
    RULE_list_ = 11
    RULE_path = 12
    RULE_workflowCall = 13
    RULE_actions = 14
    RULE_action = 15
    RULE_returnStmt = 16
    RULE_assignment = 17
    RULE_assignOp = 18

    ruleNames =  [ "rule_", "condition", "orExpr", "andExpr", "notExpr", 
                   "comparison", "addExpr", "mulExpr", "unaryExpr", "primary", 
                   "literal", "list_", "path", "workflowCall", "actions", 
                   "action", "returnStmt", "assignment", "assignOp" ]

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
    ARROW=11
    EQ=12
    NEQ=13
    LTE=14
    GTE=15
    LT=16
    GT=17
    PLUS=18
    MINUS=19
    STAR=20
    SLASH=21
    MOD=22
    ASSIGN=23
    PLUS_ASSIGN=24
    MINUS_ASSIGN=25
    STAR_ASSIGN=26
    SLASH_ASSIGN=27
    LPAREN=28
    RPAREN=29
    LBRACKET=30
    RBRACKET=31
    DOT=32
    COMMA=33
    SEMICOLON=34
    NUMBER=35
    STRING=36
    IDENTIFIER=37
    WS=38
    LINE_COMMENT=39

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
            self.state = 38
            self.condition()
            self.state = 39
            self.match(BusinessRulesParser.ARROW)
            self.state = 40
            self.actions()
            self.state = 41
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
            self.state = 43
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
            self.state = 45
            self.andExpr()
            self.state = 50
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==5:
                self.state = 46
                self.match(BusinessRulesParser.OR)
                self.state = 47
                self.andExpr()
                self.state = 52
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
            self.state = 53
            self.notExpr()
            self.state = 58
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==4:
                self.state = 54
                self.match(BusinessRulesParser.AND)
                self.state = 55
                self.notExpr()
                self.state = 60
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
            self.state = 64
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [6]:
                self.enterOuterAlt(localctx, 1)
                self.state = 61
                self.match(BusinessRulesParser.NOT)
                self.state = 62
                self.notExpr()
                pass
            elif token in [1, 2, 3, 10, 19, 28, 30, 35, 36, 37]:
                self.enterOuterAlt(localctx, 2)
                self.state = 63
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

        def addExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.AddExprContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.AddExprContext,i)


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
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self.addExpr()
            self.state = 69
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 258432) != 0):
                self.state = 67
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 258432) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 68
                self.addExpr()


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
        self.enterRule(localctx, 12, self.RULE_addExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 71
            self.mulExpr()
            self.state = 76
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==18 or _la==19:
                self.state = 72
                _la = self._input.LA(1)
                if not(_la==18 or _la==19):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 73
                self.mulExpr()
                self.state = 78
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
        self.enterRule(localctx, 14, self.RULE_mulExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 79
            self.unaryExpr()
            self.state = 84
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 7340032) != 0):
                self.state = 80
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 7340032) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 81
                self.unaryExpr()
                self.state = 86
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
        self.enterRule(localctx, 16, self.RULE_unaryExpr)
        try:
            self.state = 90
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [19]:
                self.enterOuterAlt(localctx, 1)
                self.state = 87
                self.match(BusinessRulesParser.MINUS)
                self.state = 88
                self.unaryExpr()
                pass
            elif token in [1, 2, 3, 10, 28, 30, 35, 36, 37]:
                self.enterOuterAlt(localctx, 2)
                self.state = 89
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
        self.enterRule(localctx, 18, self.RULE_primary)
        try:
            self.state = 99
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [28]:
                self.enterOuterAlt(localctx, 1)
                self.state = 92
                self.match(BusinessRulesParser.LPAREN)
                self.state = 93
                self.orExpr()
                self.state = 94
                self.match(BusinessRulesParser.RPAREN)
                pass
            elif token in [1, 2, 3, 30, 35, 36]:
                self.enterOuterAlt(localctx, 2)
                self.state = 96
                self.literal()
                pass
            elif token in [37]:
                self.enterOuterAlt(localctx, 3)
                self.state = 97
                self.path()
                pass
            elif token in [10]:
                self.enterOuterAlt(localctx, 4)
                self.state = 98
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
        self.enterRule(localctx, 20, self.RULE_literal)
        try:
            self.state = 107
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [35]:
                self.enterOuterAlt(localctx, 1)
                self.state = 101
                self.match(BusinessRulesParser.NUMBER)
                pass
            elif token in [36]:
                self.enterOuterAlt(localctx, 2)
                self.state = 102
                self.match(BusinessRulesParser.STRING)
                pass
            elif token in [1]:
                self.enterOuterAlt(localctx, 3)
                self.state = 103
                self.match(BusinessRulesParser.TRUE)
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 4)
                self.state = 104
                self.match(BusinessRulesParser.FALSE)
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 5)
                self.state = 105
                self.match(BusinessRulesParser.NONE)
                pass
            elif token in [30]:
                self.enterOuterAlt(localctx, 6)
                self.state = 106
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
        self.enterRule(localctx, 22, self.RULE_list_)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 109
            self.match(BusinessRulesParser.LBRACKET)
            self.state = 118
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 241860871246) != 0):
                self.state = 110
                self.orExpr()
                self.state = 115
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==33:
                    self.state = 111
                    self.match(BusinessRulesParser.COMMA)
                    self.state = 112
                    self.orExpr()
                    self.state = 117
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 120
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

        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.IDENTIFIER)
            else:
                return self.getToken(BusinessRulesParser.IDENTIFIER, i)

        def DOT(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.DOT)
            else:
                return self.getToken(BusinessRulesParser.DOT, i)

        def LBRACKET(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.LBRACKET)
            else:
                return self.getToken(BusinessRulesParser.LBRACKET, i)

        def orExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(BusinessRulesParser.OrExprContext)
            else:
                return self.getTypedRuleContext(BusinessRulesParser.OrExprContext,i)


        def RBRACKET(self, i:int=None):
            if i is None:
                return self.getTokens(BusinessRulesParser.RBRACKET)
            else:
                return self.getToken(BusinessRulesParser.RBRACKET, i)

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
        self.enterRule(localctx, 24, self.RULE_path)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 122
            self.match(BusinessRulesParser.IDENTIFIER)
            self.state = 131
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==30 or _la==32:
                self.state = 129
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [32]:
                    self.state = 123
                    self.match(BusinessRulesParser.DOT)
                    self.state = 124
                    self.match(BusinessRulesParser.IDENTIFIER)
                    pass
                elif token in [30]:
                    self.state = 125
                    self.match(BusinessRulesParser.LBRACKET)
                    self.state = 126
                    self.orExpr()
                    self.state = 127
                    self.match(BusinessRulesParser.RBRACKET)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 133
                self._errHandler.sync(self)
                _la = self._input.LA(1)

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
        self.enterRule(localctx, 26, self.RULE_workflowCall)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 134
            self.match(BusinessRulesParser.WORKFLOW)
            self.state = 135
            self.match(BusinessRulesParser.LPAREN)
            self.state = 136
            self.match(BusinessRulesParser.STRING)
            self.state = 141
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==33:
                self.state = 137
                self.match(BusinessRulesParser.COMMA)
                self.state = 138
                self.orExpr()
                self.state = 143
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 144
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
        self.enterRule(localctx, 28, self.RULE_actions)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 146
            self.action()
            self.state = 151
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==34:
                self.state = 147
                self.match(BusinessRulesParser.SEMICOLON)
                self.state = 148
                self.action()
                self.state = 153
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
        self.enterRule(localctx, 30, self.RULE_action)
        try:
            self.state = 157
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [9]:
                self.enterOuterAlt(localctx, 1)
                self.state = 154
                self.returnStmt()
                pass
            elif token in [37]:
                self.enterOuterAlt(localctx, 2)
                self.state = 155
                self.assignment()
                pass
            elif token in [10]:
                self.enterOuterAlt(localctx, 3)
                self.state = 156
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
        self.enterRule(localctx, 32, self.RULE_returnStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 159
            self.match(BusinessRulesParser.RET)
            self.state = 160
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
        self.enterRule(localctx, 34, self.RULE_assignment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 162
            self.path()
            self.state = 163
            self.assignOp()
            self.state = 164
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
        self.enterRule(localctx, 36, self.RULE_assignOp)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 166
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 260046848) != 0)):
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





