from typing import List, Optional, Set, Union
from .expression_parser import ExpressionParser
from ..lexer import TokenTypes
from ..ast_nodes import (
    Statement, ExpressionStatement, ReturnStatement,
    VariableDef, If, While, ComponentInstantiation, Node, FunctionDef, Expression,
    Literal, Identifier, FunctionCall, Parameter
)
from ..ast_nodes.declarations import *

class StatementParser(ExpressionParser):
    """Parser component for handling statements"""

    # Token type sets for better organization and checking
    MODIFIER_TOKENS: Set[TokenTypes] = {
        # Access modifiers
        TokenTypes.PUB, TokenTypes.PRIV, TokenTypes.INTERNAL, TokenTypes.OPEN,
        # Variable mutability
        TokenTypes.CONST, TokenTypes.MUT,
        # Method purity
        TokenTypes.PURE, TokenTypes.IMPURE,
        # Special modifiers
        TokenTypes.META, TokenTypes.BUS, TokenTypes.ON,
    }

    def parse_type(self) -> str:
        """Parse a type identifier"""
        if self.current_token.type not in {TokenTypes.IDENT, TokenTypes.STRING}:
            self.error("Expected type identifier or string literal")
        type_name = self.current_token.value
        self.eat(self.current_token.type)
        return type_name

    def parse_parameter(self) -> Parameter:
        """Parse a single parameter in a function declaration"""
        location = self.get_location()
        modifiers = self.parse_modifiers()
        
        if self.current_token.type != TokenTypes.IDENT:
            self.error("Expected parameter name")
            
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)

        # Parse optional type annotation
        param_type = None
        if self.current_token.type == TokenTypes.COLON:
            self.eat(TokenTypes.COLON)
            param_type = self.parse_type()
            
        # Parse optional default value
        default_value = None
        if self.current_token.type == TokenTypes.ASSIGN:
            self.eat(TokenTypes.ASSIGN)
            default_value = self.parse_expression()
            
        return Parameter(
            modifiers=modifiers,
            name=name,
            param_type=param_type,
            default_value=default_value,
            location=location
        )

    def parse_parameter_list(self, is_declaration: bool = True) -> List[Union[Parameter, Expression]]:
        """Parse a parameter list"""
        params = []
        self.eat(TokenTypes.LPAREN)
        
        # Handle empty parameter list
        if self.current_token.type == TokenTypes.RPAREN:
            self.eat(TokenTypes.RPAREN)
            return params
            
        if is_declaration:
            # Parse declaration parameters
            params.append(self.parse_parameter())
            while self.current_token.type == TokenTypes.COMMA:
                self.eat(TokenTypes.COMMA)
                params.append(self.parse_parameter())
        else:
            # Parse function call arguments
            params.append(self.parse_expression())
            while self.current_token.type == TokenTypes.COMMA:
                self.eat(TokenTypes.COMMA)
                params.append(self.parse_expression())
            
        self.eat(TokenTypes.RPAREN)
        return params

    def parse_function_header(self, modifiers: List[TokenTypes]) -> FunctionDef:
        """Parse a function declaration header"""
        location = self.get_location()
        
        if self.current_token.type not in {TokenTypes.IDENT, TokenTypes.STRING}:
            self.error(f"Expected function name or string literal")
            
        name = self.current_token.value
        self.eat(self.current_token.type)

        # Handle function declarations with empty parameter lists: init()
        if self.current_token.type == TokenTypes.LPAREN and self.peek().type == TokenTypes.RPAREN:
            self.eat(TokenTypes.LPAREN)
            self.eat(TokenTypes.RPAREN)
            params = []
        else:
            # Normal parameter list
            params = self.parse_parameter_list(is_declaration=True)

        # Parse optional return type
        return_type = None
        if self.current_token.type == TokenTypes.ARROW:
            self.eat(TokenTypes.ARROW)
            return_type = self.parse_type()

        # Parse optional body
        body = None
        if self.current_token.type == TokenTypes.LBRACE:
            body = self.parse_block()
        else:
            self.expect_semicolon()

        return FunctionDef(
            modifiers=modifiers,
            name=name,
            params=params,
            return_type=return_type,
            body=body,
            location=location
        )

    def parse_modifiers(self) -> List[TokenTypes]:
        """Parse a sequence of modifiers"""
        modifiers = []
        while self.current_token.type in self.MODIFIER_TOKENS:
            modifier = self.current_token.type
            # Only add non-PRIV modifiers as PRIV is default
            if modifier != TokenTypes.PRIV:
                modifiers.append(modifier)
            self.eat()

        # Add PRIV by default if no access modifier specified
        if not any(mod in {TokenTypes.PUB, TokenTypes.PRIV, TokenTypes.INTERNAL} 
                  for mod in modifiers):
            modifiers.append(TokenTypes.PRIV)

        return modifiers

    def parse_variable(self, modifiers: List[TokenTypes]) -> VariableDef:
        """Parse a variable declaration"""
        location = self.get_location()
        
        if self.current_token.type not in {TokenTypes.IDENT, TokenTypes.STRING}:
            self.error("Expected identifier or string literal")
            
        name = self.current_token.value
        self.eat(self.current_token.type)

        # Parse optional type annotation
        type_name = None
        if self.current_token.type == TokenTypes.COLON:
            self.eat(TokenTypes.COLON)
            type_name = self.parse_type()

        # Parse optional initializer
        value = None
        if self.current_token.type == TokenTypes.ASSIGN:
            self.eat(TokenTypes.ASSIGN)
            value = self.parse_expression()

        self.expect_semicolon()
        return VariableDef(
            modifiers=modifiers,
            name=name,
            type_name=type_name,
            value=value,
            location=location
        )

    def parse_if_statement(self) -> If:
        """Parse an if statement with optional else"""
        location = self.get_location()
        self.eat(TokenTypes.IF)
        self.eat(TokenTypes.LPAREN)
        condition = self.parse_expression()
        self.eat(TokenTypes.RPAREN)
        
        then_block = self.parse_block()
        
        else_block = None
        if self.current_token.type == TokenTypes.ELSE:
            self.eat(TokenTypes.ELSE)
            else_block = self.parse_block()
            
        return If(
            condition=condition,
            then_block=then_block,
            else_block=else_block,
            location=location
        )

    def parse_while_statement(self) -> While:
        """Parse a while statement"""
        location = self.get_location()
        self.eat(TokenTypes.WHILE)
        self.eat(TokenTypes.LPAREN)
        condition = self.parse_expression()
        self.eat(TokenTypes.RPAREN)
        
        body = self.parse_block()
        
        return While(
            condition=condition,
            body=body,
            location=location
        )

    def parse_return_statement(self) -> ReturnStatement:
        """Parse a return statement"""
        location = self.get_location()
        self.eat(TokenTypes.RETURN)
        
        value = None
        if self.current_token.type != TokenTypes.SEMICOLON:
            value = self.parse_expression()
            
        self.expect_semicolon()
        return ReturnStatement(value=value, location=location)

    def parse_statement(self) -> Statement:
        """Parse a statement"""
        if self.current_token.type == TokenTypes.RETURN:
            return self.parse_return_statement()
            
        elif self.current_token.type == TokenTypes.IF:
            return self.parse_if_statement()
            
        elif self.current_token.type == TokenTypes.WHILE:
            return self.parse_while_statement()
        
        # Check for IDENT(args) - could be function call or component instantiation
        elif self.current_token.type == TokenTypes.IDENT and self.peek().type == TokenTypes.LPAREN:
            ident_value = self.current_token.value
            location = self.get_location()
            self.eat(TokenTypes.IDENT)
            
            # Parse arguments
            self.eat(TokenTypes.LPAREN)
            args = []
            if self.current_token.type != TokenTypes.RPAREN:
                args.append(self.parse_expression())
                while self.current_token.type == TokenTypes.COMMA:
                    self.eat(TokenTypes.COMMA)
                    args.append(self.parse_expression())
            self.eat(TokenTypes.RPAREN)
            
            # Check if this is a component instantiation (with 'as') or just a function call
            instance_name = None
            if self.current_token.type == TokenTypes.AS:
                self.eat(TokenTypes.AS)
                
                if self.current_token.type != TokenTypes.IDENT:
                    self.error("Expected instance name after 'as'")
                    
                instance_name = self.current_token.value
                self.eat(TokenTypes.IDENT)
                
                # Create a component instantiation
                comp = ComponentInstantiation(
                    component_type=ident_value,
                    instance_name=instance_name,
                    args=args,
                    location=location
                )
                self.expect_semicolon()
                return comp
            else:
                # Create a function call expression
                ident = Identifier(name=ident_value, location=location)
                func_call = FunctionCall(
                    function=ident,
                    arguments=args,
                    location=location
                )
                # Wrap in ExpressionStatement
                stmt = ExpressionStatement(expr=func_call, location=location)
                self.expect_semicolon()
                return stmt
        
        # Handle string literals as expression statements (for debugging statements)
        elif self.current_token.type == TokenTypes.STRING:
            location = self.get_location()
            value = self.current_token.value
            self.eat(TokenTypes.STRING)
            expr = Literal(value=value, literal_type=TokenTypes.STRING, location=location)
            self.expect_semicolon()
            return ExpressionStatement(expr=expr, location=location)
            
        else:
            # Handle expression statement
            location = self.get_location()
            expr = self.parse_expression()
            self.expect_semicolon()
            return ExpressionStatement(expr=expr, location=location)

    def parse_block(self) -> List[Node]:
        """Parse a block of statements and declarations"""
        items = []
        self.eat(TokenTypes.LBRACE)
        
        while self.current_token.type != TokenTypes.RBRACE:
            if self.current_token.type == TokenTypes.EOF:
                self.error("Unexpected end of file inside block")
                
            # First, try to parse it as a statement (expressions, return, if, while, etc.)
            if self.current_token.type in {TokenTypes.RETURN, TokenTypes.IF, TokenTypes.WHILE, 
                                         TokenTypes.STRING, TokenTypes.INTEGER, TokenTypes.FLOAT, 
                                         TokenTypes.BOOL}:
                stmt = self.parse_statement()
                items.append(stmt)
                continue
            
            # Check if this is a member declaration with potential modifiers    
            if self.current_token.type in self.MODIFIER_TOKENS:
                modifiers = self.parse_modifiers()
                
                # Check if this is a function declaration or variable
                if self.current_token.type in {TokenTypes.IDENT, TokenTypes.STRING}:
                    # For function declarations, check for empty parameter list
                    if self.current_token.type == TokenTypes.IDENT:
                        ident_value = self.current_token.value
                        saved_token = self.current_token
                        self.eat(TokenTypes.IDENT)
                        
                        # Check for empty parameter list: init()
                        if self.current_token.type == TokenTypes.LPAREN and self.peek().type == TokenTypes.RPAREN:
                            # This is a function with empty parameter list
                            self.eat(TokenTypes.LPAREN)
                            self.eat(TokenTypes.RPAREN)
                            
                            # Save current token position to restore if needed
                            return_type = None
                            if self.current_token.type == TokenTypes.ARROW:
                                self.eat(TokenTypes.ARROW)
                                return_type = self.parse_type()
                            
                            body = None
                            if self.current_token.type == TokenTypes.LBRACE:
                                body = self.parse_block()
                            else:
                                self.expect_semicolon()
                                
                            # Create function with empty parameter list
                            location = saved_token.location if hasattr(saved_token, 'location') else None
                            func = FunctionDef(
                                modifiers=modifiers,
                                name=ident_value,
                                params=[],
                                return_type=return_type,
                                body=body,
                                location=location
                            )
                            items.append(func)
                            continue
                        elif self.current_token.type == TokenTypes.LPAREN:
                            # Normal function declaration with parameters
                            # Restore token position
                            self.current_token = saved_token
                            items.append(self.parse_function_header(modifiers))
                            continue
                        else:
                            # Not a function, restore token position
                            self.current_token = saved_token
                    
                    # Look ahead to see if this is a function declaration or variable
                    # Function declarations have parentheses after the name
                    is_function = False
                    if self.current_token.type == TokenTypes.IDENT:
                        saved_token = self.current_token
                        self.eat(TokenTypes.IDENT)
                        if self.current_token.type == TokenTypes.LPAREN:
                            is_function = True
                            
                        # Restore token
                        self.current_token = saved_token
                        
                    if is_function:
                        items.append(self.parse_function_header(modifiers))
                    else:
                        # Variable declaration 
                        items.append(self.parse_variable(modifiers))
                else:
                    self.error(f"Unexpected token {self.current_token.type.name} in block")
                continue
            
            # Check for field declarations (x: int;) without modifiers
            if self.current_token.type == TokenTypes.IDENT and self.peek().type == TokenTypes.COLON:
                var = self.parse_variable([TokenTypes.PRIV])  # default private
                items.append(var)
                continue
            
            # Check for unmodified function declarations or function calls
            if self.current_token.type == TokenTypes.IDENT:
                ident_value = self.current_token.value
                
                # Special handling for functions with empty parameter lists: init()
                if self.peek().type == TokenTypes.LPAREN:
                    next_token = self.peek(2)  # Look two tokens ahead
                    
                    if next_token.type == TokenTypes.RPAREN:
                        # This is a function with empty parameter list
                        location = self.get_location()
                        self.eat(TokenTypes.IDENT)
                        self.eat(TokenTypes.LPAREN)
                        self.eat(TokenTypes.RPAREN)
                        
                        # Check if this is a function definition
                        if self.current_token.type in {TokenTypes.LBRACE, TokenTypes.ARROW}:
                            # Function definition
                            return_type = None
                            if self.current_token.type == TokenTypes.ARROW:
                                self.eat(TokenTypes.ARROW)
                                return_type = self.parse_type()
                                
                            # Parse body if present
                            body = None
                            if self.current_token.type == TokenTypes.LBRACE:
                                body = self.parse_block()
                            else:
                                self.expect_semicolon()
                                
                            # Create function with empty parameter list
                            func = FunctionDef(
                                modifiers=[TokenTypes.PRIV],  # default private
                                name=ident_value,
                                params=[],
                                return_type=return_type,
                                body=body,
                                location=location
                            )
                            items.append(func)
                            continue
                        else:
                            # Function call followed by semicolon
                            ident = Identifier(name=ident_value, location=location)
                            func_call = FunctionCall(
                                function=ident,
                                arguments=[],
                                location=location
                            )
                            stmt = ExpressionStatement(expr=func_call, location=location)
                            self.expect_semicolon()
                            items.append(stmt)
                            continue
                
                # Check if it might be a function definition without modifiers
                if self.peek().type == TokenTypes.LPAREN:
                    # We need to distinguish between function declarations and function calls
                    # Let's look ahead to see if there's a block after the parameter list (indicating a function)
                    saved_pos = self.lexer.pos
                    saved_line = self.lexer.line
                    saved_column = self.lexer.column
                    saved_token = self.current_token
                    
                    # Skip identifier and parenthesis
                    self.eat(TokenTypes.IDENT)
                    self.eat(TokenTypes.LPAREN)
                    
                    # Skip parameters until we reach closing paren
                    while self.current_token.type != TokenTypes.RPAREN and self.current_token.type != TokenTypes.EOF:
                        self.eat(self.current_token.type)
                    
                    if self.current_token.type == TokenTypes.RPAREN:
                        self.eat(TokenTypes.RPAREN)
                    
                    # Check what follows the closing paren
                    is_function_def = False
                    if self.current_token.type in {TokenTypes.LBRACE, TokenTypes.ARROW}:
                        is_function_def = True
                    elif self.current_token.type == TokenTypes.AS:
                        is_function_def = False
                    else:
                        # If followed by semicolon, it's a function call
                        is_function_def = False
                    
                    # Restore lexer state
                    self.lexer.pos = saved_pos
                    self.lexer.line = saved_line
                    self.lexer.column = saved_column
                    self.current_token = saved_token
                    
                    if is_function_def:
                        # This is a function declaration without modifiers
                        items.append(self.parse_function_header([TokenTypes.PRIV]))  # default private
                        continue
                
                # If we get here, treat it as a general statement (function call or expression)
                stmt = self.parse_statement()
                items.append(stmt)
                continue
            
            # If we get here, try to parse it as a general statement
            stmt = self.parse_statement()
            items.append(stmt)
            
        self.eat(TokenTypes.RBRACE)
        return items 