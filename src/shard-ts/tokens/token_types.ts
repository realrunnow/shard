export enum TokenTypes {
    // Keywords
    TYPE,
    SHARD,
    IMPL,
    FROM,
    FOR,
    IF,
    ELSE,
    ELIF,
    SWITCH,
    CASE,
    WHILE,
    RETURN,
    AS,

    // Modifiers
    PUB,
    PRIV,
    INTERNAL,
    OPEN,
    CONST,
    MUT,
    PURE,
    IMPURE,
    META,
    BUS,
    ON,

    // Operators
    PLUS,
    MINUS,
    TIMES,
    DIVIDE,
    ASSIGN,
    PLUS_ASSIGN,
    MINUS_ASSIGN,
    TIMES_ASSIGN,
    DIVIDE_ASSIGN,
    EQ,
    NE,
    LT,
    GT,
    LE,
    GE,
    NOT,

    // Punctuation
    LPAREN,
    RPAREN,
    LBRACE,
    RBRACE,
    SEMICOLON,
    COLON,
    COMMA,
    ARROW,
    DOT,

    // Literals
    INTEGER,
    FLOAT,
    STRING,
    BOOL,
    IDENT,

    // Special
    EOF,
    EOL,
    COMMENT,
    UNKNOWN
}