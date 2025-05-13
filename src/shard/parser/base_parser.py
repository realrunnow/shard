from typing import Set, Dict, Optional
from dataclasses import dataclass
from ..lexer.tokens import TokenTypes, Token

@dataclass
class SourceLocation:
    line: int
    column: int
    length: int
    file: str
    position: int

class BaseParser:
    """Base parser class with common utilities and error handling"""
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.token_buffer = []
        self.current_pos = 0
        self.current_file = lexer.filename if hasattr(lexer, 'filename') else '<unknown>'

    def error(self, message: str):
        """Raise a syntax error with traceback information"""
        import traceback
        error_msg = f"⚠️  Error at line {self.current_token.line}: {message}\n"
        error_msg += "Traceback (most recent call last):\n"
        error_msg += ''.join(traceback.format_stack()[:-1])
        error_msg += f"Current token: {self.current_token}\n"
        error_msg += f"Parser state: pos={self.lexer.pos}, line={self.lexer.line}, column={self.lexer.column}"
        raise SyntaxError(error_msg)

    def get_location(self) -> SourceLocation:
        """Get the current source location"""
        return SourceLocation(
            line=self.lexer.line,
            column=self.lexer.column,
            length=len(str(self.current_token.value)),
            file=self.current_file,
            position=self.lexer.pos
        )

    def eat(self, token_type: Optional[TokenTypes] = None) -> Token:
        """Consume a token of the expected type"""
        if token_type and self.current_token.type != token_type:
            self.error(f"Expected {token_type.name}, got {self.current_token.type.name}")
        token = self.current_token
        self.current_token = self.lexer.get_next_token()
        return token

    def peek(self, ahead: int = 1) -> Token:
        """Look ahead at tokens without consuming them"""
        # Save lexer state
        saved_pos = self.lexer.pos
        saved_line = self.lexer.line
        saved_column = self.lexer.column
        saved_token = self.current_token
        
        # Get tokens
        result = None
        for _ in range(ahead):
            result = self.lexer.get_next_token()
            
        # Restore lexer state
        self.lexer.pos = saved_pos
        self.lexer.line = saved_line
        self.lexer.column = saved_column
        
        # Restore current token
        self.current_token = saved_token
        
        return result

    def synchronize(self, sync_tokens: Set[TokenTypes]):
        """Recover from errors by skipping to the next synchronization point"""
        while (self.current_token.type not in sync_tokens and 
               self.current_token.type != TokenTypes.EOF):
            self.eat()

    def expect_semicolon(self):
        """Enforce semicolon as statement terminator"""
        if self.current_token.type != TokenTypes.SEMICOLON:
            self.error(f"Expected semicolon at end of statement, got {self.current_token.type.name}")
        self.eat(TokenTypes.SEMICOLON) 