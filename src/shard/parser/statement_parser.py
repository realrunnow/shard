from typing import List, Optional, Set, Union
from .expression_parser import ExpressionParser
from ..lexer import TokenTypes
from ..ast_nodes import (
    Statement, ExpressionStatement, ReturnStatement,
    VariableDef, If, While, ComponentInstantiation, Node, FunctionDef, Expression
)

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

    def parse_parameter_list(self, is_declaration: bool = True) -> List[Union[VariableDef, Expression]]:
        """Parse a parameter list"""
        params = []
        self.eat(TokenTypes.LPAREN)
        
        if self.current_token.type != TokenTypes.RPAREN:
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

    def parse_parameter(self) -> VariableDef:
        """Parse a single parameter in a function declaration"""
        location = self.get_location()
        modifiers = self.parse_modifiers()
        
        if self.current_token.type != TokenTypes.IDENT:
            self.error("Expected parameter name")
            
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)

        # Parse optional type annotation
        type_name = None
        if self.current_token.type == TokenTypes.COLON:
            self.eat(TokenTypes.COLON)
            type_name = self.parse_type()
            
        # Parse optional default value
        value = None
        if self.current_token.type == TokenTypes.ASSIGN:
            self.eat(TokenTypes.ASSIGN)
            value = self.parse_expression()
            
        return VariableDef(
            modifiers=modifiers,
            name=name,
            type_name=type_name,
            value=value,
            location=location
        )

    def parse_function_header(self, modifiers: List[TokenTypes]) -> FunctionDef:
        """Parse a function declaration header"""
        location = self.get_location()
        
        if self.current_token.type not in {TokenTypes.IDENT, TokenTypes.STRING}:
            self.error(f"Expected function name or string literal")
            
        name = self.current_token.value
        self.eat(self.current_token.type)

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

    def parse_component_instantiation(self, component_type: str) -> ComponentInstantiation:
        """
        Parse a component instantiation statement or function call.
        If 'as' is present, it's a component instantiation.
        Otherwise, it's treated as a function call.
        """
        location = self.get_location()
        args = self.parse_parameter_list(is_declaration=False)
        
        # Check if this is a component instantiation (with 'as') or just a function call
        instance_name = None
        if self.current_token.type == TokenTypes.AS:
            self.eat(TokenTypes.AS)
            
            if self.current_token.type != TokenTypes.IDENT:
                self.error("Expected instance name after 'as'")
                
            instance_name = self.current_token.value
            self.eat(TokenTypes.IDENT)
        
        return ComponentInstantiation(
            component_type=component_type,
            instance_name=instance_name,
            args=args,
            location=location
        )

    def parse_statement(self) -> Statement:
        """Parse a statement"""
        if self.current_token.type == TokenTypes.RETURN:
            return self.parse_return_statement()
            
        elif self.current_token.type == TokenTypes.IF:
            return self.parse_if_statement()
            
        elif self.current_token.type == TokenTypes.WHILE:
            return self.parse_while_statement()
        
        # Check for component instantiation or function call syntax
        elif self.current_token.type == TokenTypes.IDENT and self.peek().type == TokenTypes.LPAREN:
            component_type = self.current_token.value
            self.eat(TokenTypes.IDENT)
            component = self.parse_component_instantiation(component_type)
            self.expect_semicolon()
            return component
            
        else:
            # Handle expression statement
            expr = self.parse_expression()
            self.expect_semicolon()
            return ExpressionStatement(expr=expr)

    def parse_block(self) -> List[Node]:
        """Parse a block of statements and declarations"""
        items = []
        self.eat(TokenTypes.LBRACE)
        
        while self.current_token.type != TokenTypes.RBRACE:
            if self.current_token.type == TokenTypes.EOF:
                self.error("Unexpected end of file inside block")
            
            # Check if this is a member declaration with potential modifiers    
            if self.current_token.type in self.MODIFIER_TOKENS:
                modifiers = self.parse_modifiers()
                
                # Check if this is a function declaration or variable
                if self.current_token.type in {TokenTypes.IDENT, TokenTypes.STRING}:
                    if self.peek().type == TokenTypes.LPAREN:
                        # Function declaration
                        items.append(self.parse_function_header(modifiers))
                    else:
                        # Variable declaration 
                        items.append(self.parse_variable(modifiers))
                else:
                    self.error(f"Unexpected token {self.current_token.type.name} in block")
            
            # Component instantiation inside meta blocks
            elif self.current_token.type == TokenTypes.IDENT and self.peek().type == TokenTypes.LPAREN:
                component_type = self.current_token.value
                self.eat(TokenTypes.IDENT)
                component = self.parse_component_instantiation(component_type)
                self.expect_semicolon()
                items.append(component)
            
            # Handle string literals properly (for comments in the code)
            elif self.current_token.type == TokenTypes.STRING:
                # Skip over string literal "comments" inside blocks
                self.eat(TokenTypes.STRING)
                self.expect_semicolon()
                continue
                
            # Handle fields without modifiers (x: float;)
            elif self.current_token.type == TokenTypes.IDENT and (
                self.peek().type == TokenTypes.COLON or self.peek().type == TokenTypes.SEMICOLON
            ):
                var = self.parse_variable([TokenTypes.PRIV])  # default private
                items.append(var)
            
            else:
                # Regular statement
                stmt = self.parse_statement()
                items.append(stmt)
            
        self.eat(TokenTypes.RBRACE)
        return items 