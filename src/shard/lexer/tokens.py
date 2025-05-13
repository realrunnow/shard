from enum import Enum, auto
from dataclasses import dataclass
from typing import Any

class TokenTypes(Enum):
    # Keywords
    TYPE = auto()
    SHARD = auto()
    IMPL = auto()
    FROM = auto()
    FOR = auto()
    IF = auto()
    ELSE = auto()
    ELIF = auto()
    SWITCH = auto()
    CASE = auto()
    WHILE = auto()
    RETURN = auto()
    AS = auto()

    # Modifiers
    PUB = auto()
    PRIV = auto()
    INTERNAL = auto()
    OPEN = auto()
    CONST = auto()
    MUT = auto()
    PURE = auto()
    IMPURE = auto()
    META = auto()
    BUS = auto()
    ON = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIVIDE = auto()
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    TIMES_ASSIGN = auto()
    DIVIDE_ASSIGN = auto()
    EQ = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    NOT = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    COLON = auto()
    COMMA = auto()
    ARROW = auto()
    DOT = auto()  # . (for member access)

    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    IDENT = auto()

    # Special
    EOF = auto()
    EOL = auto()

@dataclass
class Token:
    """Token class representing a lexical token"""
    type: TokenTypes
    value: Any
    line: int
    column: int

    def __str__(self):
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"

    def __repr__(self):
        return self.__str__() 