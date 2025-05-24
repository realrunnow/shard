export enum TokenTypes {
    // Keywords
    TYPE,
    SHARD,
    IMPL,
    ENUM,

    // helper keywords
    FROM,
    AS,

    // dual keyword
    FOR,

    // if statement
    IF,
    ELSE,
    ELIF,

    // switch statement
    SWITCH,
    CASE,

    // while loop
    WHILE,
    CONTINUE, 
    BREAK,
    RETURN,

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
    MULTIPLY,
    DIVIDE,
    MODULO,
    EXPONENT,

    INC,
    DEC,

    QUESTION_MARK,

    ASSIGN,
    PLUS_ASSIGN,
    MINUS_ASSIGN,
    MULTIPLY_ASSIGN,
    DIVIDE_ASSIGN,

    EQ,
    NE,
    LT,
    GT,
    LE,
    GE,
    NOT,
    AND,
    OR,

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