from typing import Dict, Optional, Any
from .base_parser import BaseParser
from ..lexer.tokens import TokenTypes
from ..ast_nodes import (
    Expression, BinaryOp, UnaryOp, Literal, 
    Identifier, FunctionCall, AssignmentExpr, MemberAccess
)

class ExpressionParser(BaseParser):
    """Parser component for handling expressions"""

    # Operator precedence from lowest to highest
    PRECEDENCE: Dict[TokenTypes, int] = {
        TokenTypes.ASSIGN: 1,        # a = b
        TokenTypes.PLUS_ASSIGN: 1,   # a += b
        TokenTypes.MINUS_ASSIGN: 1,  # a -= b
        TokenTypes.TIMES_ASSIGN: 1,  # a *= b
        TokenTypes.DIVIDE_ASSIGN: 1, # a /= b
        TokenTypes.EQ: 2,           # a == b
        TokenTypes.NE: 2,           # a != b
        TokenTypes.LT: 2,           # a < b
        TokenTypes.GT: 2,           # a > b
        TokenTypes.LE: 2,           # a <= b
        TokenTypes.GE: 2,           # a >= b
        TokenTypes.PLUS: 3,         # a + b
        TokenTypes.MINUS: 3,        # a - b
        TokenTypes.TIMES: 4,        # a * b
        TokenTypes.DIVIDE: 4,       # a / b
    }

    def parse_primary_expression(self) -> Expression:
        """Parse a primary expression (literals, identifiers, parenthesized expressions)"""
        token = self.current_token
        location = self.get_location()

        if token.type in {TokenTypes.INTEGER, TokenTypes.FLOAT, TokenTypes.STRING, TokenTypes.BOOL}:
            self.eat(token.type)
            return Literal(value=token.value, literal_type=token.type, location=location)
            
        elif token.type == TokenTypes.IDENT:
            name = token.value
            self.eat(TokenTypes.IDENT)
            
            # Function call
            if self.current_token.type == TokenTypes.LPAREN:
                return self.parse_function_call(name, location)
                
            # Create basic identifier
            expr = Identifier(name=name, location=location)
            
            # Check for member access
            while self.current_token.type == TokenTypes.DOT:
                self.eat(TokenTypes.DOT)
                
                if self.current_token.type != TokenTypes.IDENT:
                    self.error("Expected identifier after '.'")
                    
                member_name = self.current_token.value
                member_location = self.get_location()
                self.eat(TokenTypes.IDENT)
                
                # Create member access expression
                expr = MemberAccess(
                    object=expr,
                    member=Identifier(name=member_name, location=member_location),
                    location=location
                )
                
                # Check if this is a method call
                if self.current_token.type == TokenTypes.LPAREN:
                    return self.parse_function_call(expr, location)
                    
            return expr
            
        elif token.type == TokenTypes.LPAREN:
            self.eat(TokenTypes.LPAREN)
            expr = self.parse_expression()
            self.eat(TokenTypes.RPAREN)
            return expr
            
        self.error(f"Unexpected token {token.type.name}")

    def parse_function_call(self, func_expr, location: Any) -> FunctionCall:
        """Parse a function call with arguments"""
        # For simple name function calls, convert to Identifier
        if isinstance(func_expr, str):
            func_expr = Identifier(name=func_expr, location=location)
            
        self.eat(TokenTypes.LPAREN)
        args = []
        
        # Handle empty argument list
        if self.current_token.type == TokenTypes.RPAREN:
            self.eat(TokenTypes.RPAREN)
            return FunctionCall(
                function=func_expr,
                arguments=args,
                location=location
            )
            
        # Parse first argument
        args.append(self.parse_expression())
        
        # Parse remaining arguments
        while self.current_token.type == TokenTypes.COMMA:
            self.eat(TokenTypes.COMMA)
            args.append(self.parse_expression())
                
        self.eat(TokenTypes.RPAREN)
        return FunctionCall(
            function=func_expr,
            arguments=args,
            location=location
        )

    def parse_expression(self, precedence: int = 0) -> Expression:
        """Parse an expression using operator precedence"""
        left = self.parse_primary_expression()
        
        while (self.current_token.type in self.PRECEDENCE and 
               self.PRECEDENCE[self.current_token.type] > precedence):
            
            operator = self.current_token.type
            op_precedence = self.PRECEDENCE[operator]
            location = self.get_location()
            self.eat(operator)
            
            right = self.parse_expression(op_precedence)
            left = BinaryOp(
                left=left,
                operator=operator,
                right=right,
                location=location
            )
            
        return left 