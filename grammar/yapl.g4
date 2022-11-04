grammar yapl;

/*
YAPL Syntax
*/
start :
   program EOF
   ;

program:
   classSpecification ';' program
   | EOF
   ;

classSpecification :
    CLASS TYPE (INHERITS TYPE)? '{' (feature ';')* '}'
    ;

feature : 
    (ID) '(' (formal (','formal)*)? ')' ':' TYPE '{' expr '}'                               #method
    | ID ':' TYPE (ASSIGNMENT expr)?                                                        #attribute
    ;

formal:
    ID ':' TYPE
    ;

expr :

    expr ('@' TYPE)? '.' ID '(' (expr (',' expr)*)? ')'                                   #classMethodCall
    | ID '(' (expr (',' expr)*)? ')'                                                        #functionCall
    | IF expr THEN expr ELSE expr FI                                                        #ifElse
    | WHILE expr LOOP expr POOL                                                             #while
    | '{' (expr ';')* '}'                                                                   #expressionContext
    | 'let' ID ':' TYPE (ASSIGNMENT expr)? (',' ID ':' TYPE (ASSIGNMENT expr)?)* IN expr    #letIn
    | NEW TYPE                                                                              #newObjectInstance
    | ISVOID expr                                                                           #void
    // These follow arithmetic precedence
    | '(' expr ')'                                                                          #parenthesis
    | expr '*' expr                                                                         #multiplication
    | expr '/' expr                                                                         #division
    | expr '+' expr                                                                         #add
    | expr '-' expr                                                                         #subtract
    | '~' expr                                                                              #negation
    | expr '<' expr                                                                         #lessThan
    | expr '<=' expr                                                                        #lessOrEqual
    | expr '=' expr                                                                         #equal
    | NOT expr                                                                              #not
    | ID                                                                                    #identifier
    | INT                                                                                   #integer
    | STR                                                                                   #string
    | TRUE                                                                                  #true
    | FALSE                                                                                 #false
    // Moved this to the end because it was causing problems when visiting nested declarations
    | ID ASSIGNMENT expr                                                                    #assignmentExpression
    ;


/*
Reserved words
*/
CLASS: C L A S S;
ELSE: E L S E ;
TRUE: 'true';
FALSE: 'false';
FI: F I ;
IF: I F ;
IN: I N ;
INHERITS: I N H E R I T S;
ISVOID: I S V O I D ;
LOOP: L O O P ;
POOL: P O O L ;
THEN: T H E N ;
WHILE: W H I L E ;
NEW: N E W ;
NOT: N O T ;
LET: L E T ;


/*
TYPES
*/
INT: [0-9]+;
ID: [a-z] [_a-zA-Z0-9]*;
TYPE: [A-Z] [_a-zA-Z0-9]*;
STR: '"' (ESC | ~ ["\\])* '"';


/*
ASSIGNATIONS & OPERATORS
*/
ASSIGNMENT: '<-';


/*
Case insensitive fragments
*/
fragment A: [Aa];
fragment B: [Bb];
fragment C: [Cc];
fragment D: [Dd];
fragment E: [Ee];
fragment F: [Ff];
fragment G: [Gg];
fragment H: [Hh];
fragment I: [Ii];
fragment J: [Jj];
fragment K: [Kk];
fragment L: [Ll];
fragment M: [Mm];
fragment N: [Nn];
fragment O: [Oo];
fragment P: [Pp];
fragment Q: [Qq];
fragment R: [Rr];
fragment S: [Ss];
fragment T: [Tt];
fragment U: [Uu];
fragment V: [Vv];
fragment W: [Ww];
fragment X: [Xx];
fragment Y: [Yy];
fragment Z: [Zz];

/*
ESC
*/
fragment ESC: '\\' (["\\/bfnrt] | UNICODE);
fragment UNICODE: 'u' HEX HEX HEX HEX;
fragment HEX: [0-9a-fA-F];


/*
COMMENTS
*/
START_COMMENT: '(*';
END_COMMENT: '*)';
COMMENT: START_COMMENT (COMMENT | .)*? END_COMMENT -> skip;
LINE_COMMENT: '--' (~ '\n')* '\n'? -> skip;


/*
WHITESPACES
*/
WHITESPACE: [ \t\r\n\f]+ -> skip;
   