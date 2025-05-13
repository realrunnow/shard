from enum import Enum, auto
from dataclasses import dataclass
from .tokens import TokenTypes, Token


# Constants for token patterns
COMPOUND_OPERATORS = {
    '==': TokenTypes.EQ,
    '!=': TokenTypes.NE,
    '<=': TokenTypes.LE,
    '>=': TokenTypes.GE,
    '->': TokenTypes.ARROW,
    '+=': TokenTypes.PLUS_ASSIGN,
    '-=': TokenTypes.MINUS_ASSIGN,
    '*=': TokenTypes.TIMES_ASSIGN,
    '/=': TokenTypes.DIVIDE_ASSIGN,
}

KEYWORDS = {
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
    'as': TokenTypes.AS,
    'true': TokenTypes.BOOL,
    'false': TokenTypes.BOOL,
}

SINGLE_CHAR_TOKENS = {
    '+': TokenTypes.PLUS,
    '-': TokenTypes.MINUS,
    '*': TokenTypes.TIMES,
    '/': TokenTypes.DIVIDE,
    '=': TokenTypes.ASSIGN,
    '!': TokenTypes.NOT,
    '<': TokenTypes.LT,
    '>': TokenTypes.GT,
    '(': TokenTypes.LPAREN,
    ')': TokenTypes.RPAREN,
    '{': TokenTypes.LBRACE,
    '}': TokenTypes.RBRACE,
    ',': TokenTypes.COMMA,
    ';': TokenTypes.SEMICOLON,
    ':': TokenTypes.COLON,
    '.': TokenTypes.DOT,
}

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
        """Look ahead at characters without consuming them"""
        pos = self.pos + ahead
        if pos >= len(self.text):
            return ''
        return self.text[pos]

    def skip_whitespace_and_comments(self):
        """Skip whitespace and comments in the input text"""
        while self.pos < len(self.text):
            if self.text[self.pos].isspace():
                if self.text[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1
            elif self.text[self.pos:].startswith('//'):
                # Skip single-line comment
                while self.pos < len(self.text) and self.text[self.pos] != '\n':
                    self.pos += 1
            elif self.text[self.pos:].startswith('/*'):
                # Skip multi-line comment
                self.pos += 2
                while self.pos < len(self.text) and not self.text[self.pos:].startswith('*/'):
                    if self.text[self.pos] == '\n':
                        self.line += 1
                        self.column = 1
                    self.pos += 1
                if self.pos < len(self.text):
                    self.pos += 2  # Skip the closing */
            else:
                break

    def get_next_token(self):
        self.skip_whitespace_and_comments()
        
        if self.pos >= len(self.text):
            return Token(TokenTypes.EOF, None, self.line, self.column)

        # Store current position info for error messages
        line = self.line
        column = self.column
        
        char = self.peek()

        # Check for compound operators
        for pattern, token_type in COMPOUND_OPERATORS.items():
            if self.text[self.pos:].startswith(pattern):
                token = Token(token_type, pattern, line, column)
                self.pos += len(pattern)
                self.column += len(pattern)
                return token

        # Handle identifiers and keywords
        if char.isalpha() or char == '_':
            start = self.pos
            start_col = self.column
            while self.peek().isalnum() or self.peek() == '_':
                self.advance()
            value = self.text[start:self.pos]
            token_type = KEYWORDS.get(value, TokenTypes.IDENT)
            # Special handling for boolean literals
            if token_type == TokenTypes.BOOL:
                value = value == 'true'
            return Token(token_type, value, line, start_col)

        # Handle numbers
        if char.isdigit():
            return self._handle_number()

        # Handle strings
        if char == '"':
            return self._handle_string()

        # Handle single character tokens
        if char in SINGLE_CHAR_TOKENS:
            token_type = SINGLE_CHAR_TOKENS[char]
            self.advance()
            return Token(token_type, char, line, column)

        raise SyntaxError(f"Invalid character '{char}' at line {line}, column {column}")

    def _handle_number(self):
        start = self.pos
        start_col = self.column
        while self.peek().isdigit():
            self.advance()
        
        if self.peek() != '.':
            return Token(TokenTypes.INTEGER, int(self.text[start:self.pos]), self.line, start_col)
            
        self.advance()  # consume dot
        while self.peek().isdigit():
            self.advance()
        return Token(TokenTypes.FLOAT, float(self.text[start:self.pos]), self.line, start_col)

    def _handle_string(self):
        start_col = self.column
        self.advance()  # consume opening quote
        value = []
        while True:
            char = self.peek()
            if char == '"':
                break
            if char == '\n' or char == '':
                raise SyntaxError(f"Unterminated string at line {self.line}, column {start_col}")
            self.advance()
            if char == '\\':
                escape_map = {
                    'n': '\n',
                    't': '\t',
                    '"': '"',
                    '\\': '\\',
                    '0': '\0'
                }
                next_char = self.peek()
                if next_char == '':
                    raise SyntaxError(f"Unterminated escape sequence at line {self.line}, column {self.column}")
                self.advance()
                value.append(escape_map.get(next_char, next_char))
            else:
                value.append(char)
        self.advance()  # consume closing quote
        return Token(TokenTypes.STRING, ''.join(value), self.line, start_col)