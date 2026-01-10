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

// Extended comparison with new operators
comparison
    : nullCoalesce ((EQ | NEQ | LT | GT | LTE | GTE | IN | NOT_IN) nullCoalesce)?
    | nullCoalesce CONTAINS nullCoalesce
    | nullCoalesce NOT_CONTAINS nullCoalesce
    | nullCoalesce STARTS_WITH nullCoalesce
    | nullCoalesce ENDS_WITH nullCoalesce
    | nullCoalesce MATCHES nullCoalesce
    | nullCoalesce CONTAINS_ANY nullCoalesce
    | nullCoalesce CONTAINS_ALL nullCoalesce
    | nullCoalesce IS_EMPTY
    | nullCoalesce EXISTS
    ;

// Null coalescing operator (P1)
nullCoalesce
    : addExpr (NULL_COALESCE addExpr)*
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
    | functionCall
    | path
    | workflowCall
    ;

// Built-in function calls (e.g., lower(), len(), int())
functionCall
    : IDENTIFIER LPAREN (orExpr (COMMA orExpr)*)? RPAREN
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

// Path with null-safe access support
path
    : IDENTIFIER pathSegment*
    ;

pathSegment
    : DOT IDENTIFIER
    | NULL_SAFE_DOT IDENTIFIER
    | LBRACKET orExpr RBRACKET
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

// Keywords (order matters - more specific before general)
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

// String/list operators (must come before IDENTIFIER)
CONTAINS_ANY    : 'contains_any' ;
CONTAINS_ALL    : 'contains_all' ;
NOT_CONTAINS    : 'not' WS+ 'contains' ;
CONTAINS        : 'contains' ;
STARTS_WITH     : 'startswith' | 'starts_with' ;
ENDS_WITH       : 'endswith' | 'ends_with' ;
MATCHES         : 'matches' ;
IS_EMPTY        : 'is_empty' | 'isempty' ;
EXISTS          : 'exists' ;

// Operators
ARROW           : '=>' ;
EQ              : '==' ;
NEQ             : '!=' ;
LTE             : '<=' ;
GTE             : '>=' ;
LT              : '<' ;
GT              : '>' ;
PLUS            : '+' ;
MINUS           : '-' ;
STAR            : '*' ;
SLASH           : '/' ;
MOD             : '%' ;
ASSIGN          : '=' ;
PLUS_ASSIGN     : '+=' ;
MINUS_ASSIGN    : '-=' ;
STAR_ASSIGN     : '*=' ;
SLASH_ASSIGN    : '/=' ;
NULL_COALESCE   : '??' ;
NULL_SAFE_DOT   : '?.' ;

// Delimiters
LPAREN          : '(' ;
RPAREN          : ')' ;
LBRACKET        : '[' ;
RBRACKET        : ']' ;
DOT             : '.' ;
COMMA           : ',' ;
SEMICOLON       : ';' ;

// Literals
NUMBER          : '-'? [0-9]+ ('.' [0-9]+)? ;
STRING          : '"' (~["\r\n\\] | '\\' .)* '"'
                | '\'' (~['\r\n\\] | '\\' .)* '\''
                ;
IDENTIFIER      : [a-zA-Z_][a-zA-Z0-9_]* ;

// Whitespace
WS              : [ \t\r\n]+ -> skip ;

// Comments
LINE_COMMENT    : '#' ~[\r\n]* -> skip ;
