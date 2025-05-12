from enum import Enum
from dataclasses import dataclass


@dataclass
class Token:
    type: 'TokenTypes'
    value: object
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"


# Unified token types
class TokenTypes(Enum):
    EOF = 'EOF'
    EOL = 'EOL'
    IDENT = 'IDENT'

    INT = 'INT'
    FLOAT = 'FLOAT'
    STRING = 'STRING'

    # Modifiers
    PUB = 'PUB'
    PRIV = 'PRIV'
    INTERNAL = 'INTERNAL'
    OPEN = 'OPEN'
    CONST = 'CONST'
    MUT = 'MUT'
    PURE = 'PURE'
    IMPURE = 'IMPURE'
    META = 'META'
    BUS = 'BUS'
    ON = 'ON'

    # Language constructs
    TYPE = 'TYPE'
    SHARD = 'SHARD'
    IMPL = 'IMPL'
    FOR = 'FOR'
    FROM = 'FROM'
    IF = 'IF'
    ELSE = 'ELSE'
    ELIF = 'ELIF'
    SWITCH = 'SWITCH'
    CASE = 'CASE'
    WHILE = 'WHILE'
    RETURN = 'RETURN'

    # Punctuation
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    COLON = 'COLON'
    COMMA = 'COMMA'
    ARROW = 'ARROW'  # ->

    # Operators
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    TIMES = 'TIMES'
    DIVIDE = 'DIVIDE'
    EQ = 'EQ'     # ==
    NE = 'NE'     # !=
    LT = 'LT'     # <
    GT = 'GT'     # >
    LE = 'LE'     # <=
    GE = 'GE'     # >=
    ASSIGN = 'ASSIGN'  # =
    NOT = 'NOT'       # !





class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

    def advance(self):
        if self.pos >= len(self.text):
            return None
        char = self.text[self.pos]
        self.pos += 1
        self.column += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        return char

    def peek(self, ahead=0):
        pos = self.pos + ahead
        if pos >= len(self.text):
            return ''
        return self.text[pos]

    def get_next_token(self):
        while self.pos < len(self.text):
            char = self.peek()

            if char.isspace():
                self.advance()
                continue

            if char == '/':
                self.advance()
                if self.peek() == '/':
                    self.advance()
                    while self.peek() not in ('', '\n'):
                        self.advance()
                    continue
                elif self.peek() == '*':
                    self.advance()
                    depth = 1
                    while depth > 0:
                        if self.peek() == '/' and self.peek(1) == '*':
                            self.advance()
                            self.advance()
                            depth += 1
                        elif self.peek() == '*' and self.peek(1) == '/':
                            self.advance()
                            self.advance()
                            depth -= 1
                        else:
                            self.advance()
                    continue
                else:
                    return Token(TokenTypes.DIVIDE, '/', self.line, self.column)

            for pattern, token_type in [
                ('==', TokenTypes.EQ),
                ('!=', TokenTypes.NE),
                ('<=', TokenTypes.LE),
                ('>=', TokenTypes.GE),
                ('->', TokenTypes.ARROW),
            ]:
                if self.text[self.pos:].startswith(pattern):
                    token = Token(token_type, pattern, self.line, self.column)
                    self.pos += len(pattern)
                    self.column += len(pattern)
                    return token

            if char.isalpha() or char == '_':
                start = self.pos
                while self.peek().isalnum() or self.peek() == '_':
                    self.advance()
                value = self.text[start:self.pos]
                keyword_map = {
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
                }
                token_type = keyword_map.get(value, TokenTypes.IDENT)
                return Token(token_type, value, self.line, self.column)

            if char.isdigit():
                start = self.pos
                while self.peek().isdigit():
                    self.advance()
                integer_part = self.text[start:self.pos]
                if self.peek() == '.':
                    self.advance()
                    start_decimal = self.pos
                    while self.peek().isdigit():
                        self.advance()
                    decimal_part = self.text[start_decimal:self.pos]
                    num_str = integer_part + '.' + decimal_part
                    return Token(TokenTypes.FLOAT, float(num_str), self.line, self.column)
                else:
                    return Token(TokenTypes.INT, int(integer_part), self.line, self.column)

            if char == '"':
                self.advance()
                value = []
                while True:
                    char = self.peek()
                    if char == '"':
                        break
                    if char == '\n':
                        raise Exception(f"Unterminated string at {self.line}:{self.column}")
                    self.advance()
                    if char == '\\':
                        next_char = self.peek()
                        if next_char == '':
                            raise Exception(f"Unterminated escape sequence at {self.line}:{self.column}")
                        self.advance()
                        if next_char == 'n':
                            value.append('\n')
                        elif next_char == 't':
                            value.append('\t')
                        elif next_char == '"':
                            value.append('"')
                        elif next_char == '\\':
                            value.append('\\')
                        elif next_char == '0':
                            value.append('\0')
                        else:
                            value.append('\\')
                            value.append(next_char)
                    else:
                        value.append(char)
                self.advance()
                return Token(TokenTypes.STRING, ''.join(value), self.line, self.column)

            char_map = {
                '+': TokenTypes.PLUS,
                '-': TokenTypes.MINUS,
                '*': TokenTypes.TIMES,
                '=': TokenTypes.ASSIGN,
                '!': TokenTypes.NOT,
                '<': TokenTypes.LT,
                '>': TokenTypes.GT,
                '(': TokenTypes.LPAREN,
                ')': TokenTypes.RPAREN,
                '{': TokenTypes.LBRACE,
                '}': TokenTypes.RBRACE,
                ',': TokenTypes.COMMA,
                ';': TokenTypes.EOL,
                ':': TokenTypes.COLON,
            }

            if char in char_map:
                token_type = char_map[char]
                self.advance()
                return Token(token_type, char, self.line, self.column)

            raise Exception(f"Unknown character '{char}' at line {self.line}, column {self.column}")

        return Token(TokenTypes.EOF, None, self.line, self.column)