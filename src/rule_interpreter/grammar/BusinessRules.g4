grammar BusinessRules;

// Parser Rules

rule_
    : condition ARROW actions EOF
    ;

condition
    : orExpr
    ;

orExpr
    : andExpr (OR andExpr)*
    ;

andExpr
    : notExpr (AND notExpr)*
    ;

notExpr
    : NOT notExpr
    | comparison
    ;

comparison
    : addExpr ((EQ | NEQ | LT | GT | LTE | GTE | IN | NOT_IN) addExpr)?
    ;

addExpr
    : mulExpr ((PLUS | MINUS) mulExpr)*
    ;

mulExpr
    : unaryExpr ((STAR | SLASH | MOD) unaryExpr)*
    ;

unaryExpr
    : MINUS unaryExpr
    | primary
    ;

primary
    : LPAREN orExpr RPAREN
    | literal
    | path
    | workflowCall
    ;

literal
    : NUMBER
    | STRING
    | TRUE
    | FALSE
    | NONE
    | list_
    ;

list_
    : LBRACKET (orExpr (COMMA orExpr)*)? RBRACKET
    ;

path
    : IDENTIFIER (DOT IDENTIFIER | LBRACKET orExpr RBRACKET)*
    ;

workflowCall
    : WORKFLOW LPAREN STRING (COMMA orExpr)* RPAREN
    ;

actions
    : action (SEMICOLON action)*
    ;

action
    : returnStmt
    | assignment
    | workflowCall
    ;

returnStmt
    : RET orExpr
    ;

assignment
    : path assignOp orExpr
    ;

assignOp
    : ASSIGN
    | PLUS_ASSIGN
    | MINUS_ASSIGN
    | STAR_ASSIGN
    | SLASH_ASSIGN
    ;

// Lexer Rules

// Keywords
TRUE        : 'true' | 'True' ;
FALSE       : 'false' | 'False' ;
NONE        : 'none' | 'None' | 'null' ;
AND         : 'and' ;
OR          : 'or' ;
NOT         : 'not' ;
IN          : 'in' ;
NOT_IN      : 'not' WS+ 'in' ;
RET         : 'ret' ;
WORKFLOW    : 'workflow' ;

// Operators
ARROW       : '=>' ;
EQ          : '==' ;
NEQ         : '!=' ;
LTE         : '<=' ;
GTE         : '>=' ;
LT          : '<' ;
GT          : '>' ;
PLUS        : '+' ;
MINUS       : '-' ;
STAR        : '*' ;
SLASH       : '/' ;
MOD         : '%' ;
ASSIGN      : '=' ;
PLUS_ASSIGN : '+=' ;
MINUS_ASSIGN: '-=' ;
STAR_ASSIGN : '*=' ;
SLASH_ASSIGN: '/=' ;

// Delimiters
LPAREN      : '(' ;
RPAREN      : ')' ;
LBRACKET    : '[' ;
RBRACKET    : ']' ;
DOT         : '.' ;
COMMA       : ',' ;
SEMICOLON   : ';' ;

// Literals
NUMBER      : '-'? [0-9]+ ('.' [0-9]+)? ;
STRING      : '"' (~["\r\n\\] | '\\' .)* '"'
            | '\'' (~['\r\n\\] | '\\' .)* '\''
            ;
IDENTIFIER  : [a-zA-Z_][a-zA-Z0-9_]* ;

// Whitespace
WS          : [ \t\r\n]+ -> skip ;

// Comments
LINE_COMMENT: '#' ~[\r\n]* -> skip ;

