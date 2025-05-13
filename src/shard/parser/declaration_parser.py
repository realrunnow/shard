from typing import List, Optional, Set, Union
from .statement_parser import StatementParser
from ..lexer.tokens import TokenTypes
from ..ast_nodes import (
    TypeDef, ShardDef, ImplDef, FunctionDef,
    VariableDef, Parameter, Expression
)
from ..ast_nodes.declarations import *

class DeclarationParser(StatementParser):
    """Parser component for handling top-level declarations"""

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

    TOP_LEVEL_TOKENS: Set[TokenTypes] = {
        TokenTypes.TYPE,
        TokenTypes.SHARD,
        TokenTypes.IDENT,
        TokenTypes.IMPL,
    }

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

    def parse_type(self) -> str:
        """Parse a type identifier"""
        if self.current_token.type not in {TokenTypes.IDENT, TokenTypes.STRING}:
            self.error("Expected type identifier or string literal")
        type_name = self.current_token.value
        self.eat(self.current_token.type)
        return type_name
    
    def parse_type_list(self) -> List[str]:
        """Parse a comma-separated list of type names"""
        types = [self.parse_type()]
        while self.current_token.type == TokenTypes.COMMA:
            self.eat(TokenTypes.COMMA)
            types.append(self.parse_type())
        return types

    def parse_parameter(self) -> Parameter:
        """Parse a parameter in a function declaration"""
        location = self.get_location()
        modifiers = self.parse_modifiers()
        
        # Parameter must be an identifier
        if self.current_token.type != TokenTypes.IDENT:
            # If it's a STRING token, it's likely a string literal inside a function body
            # This is a special case for handling common mistakes in syntax
            if self.current_token.type == TokenTypes.STRING:
                self.error("String literals cannot be used as parameter names")
            else:
                self.error("Expected parameter name")
            
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)
        
        # Parse optional type annotation
        type_name = None
        if self.current_token.type == TokenTypes.COLON:
            self.eat(TokenTypes.COLON)
            type_name = self.parse_type()
            
        # Parse optional default value
        default_value = None
        if self.current_token.type == TokenTypes.ASSIGN:
            self.eat(TokenTypes.ASSIGN)
            default_value = self.parse_expression()
            
        # Create Parameter instead of VariableDef
        return Parameter(
            modifiers=modifiers,
            name=name,
            param_type=type_name,
            default_value=default_value,
            location=location
        )

    def parse_parameter_list(self, is_declaration: bool = True) -> List[Union[Parameter, Expression]]:
        """Parse a comma-separated list of parameters or expressions"""
        params = []
        self.eat(TokenTypes.LPAREN)
        
        # Handle empty parameter list
        if self.current_token.type == TokenTypes.RPAREN:
            self.eat(TokenTypes.RPAREN)
            return params
            
        if is_declaration:
            # Parse declaration parameters (for function declarations)
            params.append(self.parse_parameter())
            
            # Parse remaining parameters
            while self.current_token.type == TokenTypes.COMMA:
                self.eat(TokenTypes.COMMA)
                params.append(self.parse_parameter())
        else:
            # Parse expressions (for function calls)
            params.append(self.parse_expression())
            
            # Parse remaining arguments
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
            # Only expect semicolon for function declarations without a body
            self.expect_semicolon()

        return FunctionDef(
            modifiers=modifiers,
            name=name,
            params=params,
            return_type=return_type,
            body=body,
            location=location
        )

    def parse_type_definition(self, modifiers: List[TokenTypes]) -> TypeDef:
        """Parse a type definition"""
        location = self.get_location()
        self.eat(TokenTypes.TYPE)
        name = self.parse_type()
        
        # Parse optional parent types
        parents = None
        if self.current_token.type == TokenTypes.FROM:
            self.eat(TokenTypes.FROM)
            parents = self.parse_type_list()

        # Parse body if present
        members = None
        if self.current_token.type == TokenTypes.LBRACE:
            members = self.parse_block()
        else:
            # Only expect semicolon for type declarations without a body
            self.expect_semicolon()
            
        return TypeDef(
            modifiers=modifiers,
            name=name,
            parents=parents,
            members=members,
            location=location
        )

    def parse_shard_definition(self, modifiers: List[TokenTypes]) -> ShardDef:
        """Parse a shard definition"""
        location = self.get_location()
        self.eat(TokenTypes.SHARD)
        name = self.parse_type()
        
        # Parse optional parent types
        parents = None
        if self.current_token.type == TokenTypes.FROM:
            self.eat(TokenTypes.FROM)
            parents = self.parse_type_list()

        # Parse body if present
        members = None
        if self.current_token.type == TokenTypes.LBRACE:
            members = self.parse_block()
        else:
            # Only expect semicolon for shard declarations without a body
            self.expect_semicolon()
            
        return ShardDef(
            modifiers=modifiers,
            name=name,
            parents=parents,
            members=members,
            location=location
        )

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
            # We expect a type name (identifier)
            if self.current_token.type != TokenTypes.IDENT:
                self.error(f"Expected type name, got {self.current_token.type.name}")
            type_name = self.current_token.value  
            self.eat(TokenTypes.IDENT)

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

    def parse_impl_definition(self) -> ImplDef:
        """Parse an impl block"""
        location = self.get_location()
        modifiers = self.parse_modifiers()
        self.eat(TokenTypes.IMPL)
        
        # Handle impl with no type name (base impl)
        if self.current_token.type == TokenTypes.LBRACE:
            body = self.parse_block()
            return ImplDef(
                modifiers=modifiers,
                target_type=None,
                for_type=None,
                members=body,
                location=location
            )
            
        if self.current_token.type != TokenTypes.IDENT:
            self.error("Expected type name after impl")
            
        type_name = self.current_token.value
        self.eat(TokenTypes.IDENT)
        
        # Handle for_type if present
        for_type = None
        if self.current_token.type == TokenTypes.FOR:
            self.eat(TokenTypes.FOR)
            
            if self.current_token.type != TokenTypes.IDENT:
                self.error("Expected type name after 'for'")
                
            for_type = self.current_token.value
            self.eat(TokenTypes.IDENT)
            
        # Parse body if present
        body = None
        if self.current_token.type == TokenTypes.LBRACE:
            body = self.parse_block()
        else:
            # Only expect semicolon for impl declarations without a body
            self.expect_semicolon()
            
        return ImplDef(
            modifiers=modifiers,
            target_type=type_name,
            for_type=for_type,
            members=body,
            location=location
        ) 