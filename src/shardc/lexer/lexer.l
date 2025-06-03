%%
[0-9]+ { yylval = atoi(yytext); return NUMBER; }
[ \t\n] { /* skip whitespace / }
"+" { return PLUS; }
"" { return TIMES; }
"(" { return LPAREN; }
")" { return RPAREN; }
. { return yytext[0]; }
%%  