import { TokenTypes } from "../tokens/token_types";

// Compound operators
export const PATTERNS:  Record<string, TokenTypes> = {

    '->': TokenTypes.ARROW,

    '=': TokenTypes.ASSIGN,
    '+=': TokenTypes.PLUS_ASSIGN,
    '-=': TokenTypes.MINUS_ASSIGN,
    '*=': TokenTypes.MULTIPLY_ASSIGN,
    '/=': TokenTypes.DIVIDE_ASSIGN,




    'pub': TokenTypes.PUB,
    'priv': TokenTypes.PRIV,
    'internal': TokenTypes.INTERNAL,
    'open': TokenTypes.OPEN,
    'const': TokenTypes.CONST,
    'mut': TokenTypes.MUT,
    'pure': TokenTypes.PURE,
    'impure': TokenTypes.IMPURE,
    'meta': TokenTypes.META,
    'bus': TokenTypes.BUS,
    'on': TokenTypes.ON,

    'enum': TokenTypes.ENUM,
    'type': TokenTypes.TYPE,
    'shard': TokenTypes.SHARD,
    'impl': TokenTypes.IMPL,
    

    'for': TokenTypes.FOR,
    'from': TokenTypes.FROM,
    'if': TokenTypes.IF,
    'else': TokenTypes.ELSE,
    'elif': TokenTypes.ELIF,
    'switch': TokenTypes.SWITCH,
    'case': TokenTypes.CASE,
    'while': TokenTypes.WHILE,
    'return': TokenTypes.RETURN,
    'as': TokenTypes.AS,
    'true': TokenTypes.BOOL,
    'false': TokenTypes.BOOL,

    '+': TokenTypes.PLUS,
    '-': TokenTypes.MINUS,
    '*': TokenTypes.MULTIPLY,
    '/': TokenTypes.DIVIDE,

    // not
    '!': TokenTypes.NOT,

    // logical
    '<': TokenTypes.LT,
    '>': TokenTypes.GT,
    '<=': TokenTypes.LE,
    '>=': TokenTypes.GE,
    '==': TokenTypes.EQ,
    '!=': TokenTypes.NE,
    'and': TokenTypes.AND, 
    'or': TokenTypes.OR, 
    '&&': TokenTypes.AND, 
    '||': TokenTypes.OR, 

    '(': TokenTypes.LPAREN,
    ')': TokenTypes.RPAREN,
    '{': TokenTypes.LBRACE,
    '}': TokenTypes.RBRACE,
    ',': TokenTypes.COMMA,
    ':': TokenTypes.COLON,
    '.': TokenTypes.DOT,
    ';': TokenTypes.SEMICOLON,

    '?': TokenTypes.QUESTION_MARK,

    '++': TokenTypes.INC,
    '--': TokenTypes.DEC,
   

};