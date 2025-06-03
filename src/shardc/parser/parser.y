%{
#include <stdio.h>
#include <stdlib.h>
int yylex(void);
void yyerror(char *s) { fprintf(stderr, "error: %s\n", s); }
%}
%token NUMBER PLUS TIMES LPAREN RPAREN
%left PLUS
%left TIMES
%%
expr:
expr PLUS expr { = $1 + $3; } | expr TIMES expr { = $1 * $3; }
| LPAREN expr RPAREN { = $2; } | NUMBER { = $1; }
;
%%
int main() {
if(yyparse() == 0) printf("result: %d\n", $$);
return 0;
}