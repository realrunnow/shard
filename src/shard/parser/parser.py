from typing import List, Optional, Any
from .declaration_parser import DeclarationParser
from ..ast_nodes import (
    Program, Declaration, TypeDef, ShardDef, ImplDef, 
    FunctionDef, VariableDef, ComponentInstantiation, Expression,
    Identifier, FunctionCall, ExpressionStatement, Parameter
)
from ..lexer.tokens import TokenTypes

class Parser(DeclarationParser):
    """Main parser class for Shard language"""

    def parse_top_level_parameter(self) -> Parameter:
        """Parse parameter declaration at top level"""
        location = self.get_location()
        
        if self.current_token.type != TokenTypes.IDENT:
            self.error("Expected parameter name")
            
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)
        
        # Parse type annotation
        param_type = None
        if self.current_token.type == TokenTypes.COLON:
            self.eat(TokenTypes.COLON)
            param_type = self.parse_type()
            
        # Parse default value
        default_value = None
        if self.current_token.type == TokenTypes.ASSIGN:
            self.eat(TokenTypes.ASSIGN)
            default_value = self.parse_expression()
            
        return Parameter(
            modifiers=[TokenTypes.PRIV],  # Default to private
            name=name,
            param_type=param_type,
            default_value=default_value,
            location=location
        )

    def parse_top_level_function(self, modifiers: List[TokenTypes]) -> FunctionDef:
        """Parse top-level function declaration"""
        location = self.get_location()
        
        if self.current_token.type != TokenTypes.IDENT:
            self.error("Expected function name")
            
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)
        
        # Parse parameter list
        self.eat(TokenTypes.LPAREN)
        params = []
        if self.current_token.type != TokenTypes.RPAREN:
            # Parse first parameter
            params.append(self.parse_top_level_parameter())
            
            # Parse additional parameters
            while self.current_token.type == TokenTypes.COMMA:
                self.eat(TokenTypes.COMMA)
                params.append(self.parse_top_level_parameter())
                
        self.eat(TokenTypes.RPAREN)
        
        # Parse return type if present
        return_type = None
        if self.current_token.type == TokenTypes.ARROW:
            self.eat(TokenTypes.ARROW)
            return_type = self.parse_type()
            
        # Parse function body if present
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

    def parse_declarations(self) -> List[Declaration]:
        """Parse top-level declarations in a Shard program"""
        declarations = []
        
        while self.current_token.type != TokenTypes.EOF:
            # Parse modifiers (pub, priv, etc.)
            modifiers = self.parse_modifiers()
            
            # Parse type definitions
            if self.current_token.type == TokenTypes.TYPE:
                declarations.append(self.parse_type_definition(modifiers))
                
            # Parse shard definitions
            elif self.current_token.type == TokenTypes.SHARD:
                declarations.append(self.parse_shard_definition(modifiers))
                
            # Parse impl blocks
            elif self.current_token.type == TokenTypes.IMPL:
                declarations.append(self.parse_impl_definition())
                
            # Parse top-level functions or component instantiations
            elif self.current_token.type == TokenTypes.IDENT:
                ident_value = self.current_token.value
                
                # Look ahead to check if it's a function
                if self.peek().type == TokenTypes.LPAREN:
                    saved_pos = self.lexer.pos
                    saved_line = self.lexer.line
                    saved_column = self.lexer.column
                    saved_token = self.current_token
                    
                    # Check if this is a function call with "as" (component instantiation)
                    self.eat(TokenTypes.IDENT)
                    self.eat(TokenTypes.LPAREN)
                    
                    # Skip arguments
                    param_depth = 1  # Track nested parentheses
                    while param_depth > 0 and self.current_token.type != TokenTypes.EOF:
                        if self.current_token.type == TokenTypes.LPAREN:
                            param_depth += 1
                        elif self.current_token.type == TokenTypes.RPAREN:
                            param_depth -= 1
                        
                        if param_depth > 0:
                            self.eat(self.current_token.type)
                    
                    # At this point we've found the closing parenthesis
                    self.eat(TokenTypes.RPAREN)
                    
                    is_component = self.current_token.type == TokenTypes.AS
                    
                    # Restore lexer state
                    self.lexer.pos = saved_pos
                    self.lexer.line = saved_line
                    self.lexer.column = saved_column
                    self.current_token = saved_token
                    
                    if is_component:
                        # Parse component instantiation
                        location = self.get_location()
                        self.eat(TokenTypes.IDENT)  # Component type
                        
                        # Parse arguments
                        self.eat(TokenTypes.LPAREN)
                        args = []
                        if self.current_token.type != TokenTypes.RPAREN:
                            args.append(self.parse_expression())
                            while self.current_token.type == TokenTypes.COMMA:
                                self.eat(TokenTypes.COMMA)
                                args.append(self.parse_expression())
                        self.eat(TokenTypes.RPAREN)
                        
                        # Parse instance name
                        self.eat(TokenTypes.AS)
                        if self.current_token.type != TokenTypes.IDENT:
                            self.error("Expected instance name after 'as'")
                        
                        instance_name = self.current_token.value
                        self.eat(TokenTypes.IDENT)
                        
                        comp = ComponentInstantiation(
                            component_type=ident_value,
                            instance_name=instance_name,
                            args=args,
                            location=location
                        )
                        self.expect_semicolon()
                        declarations.append(comp)
                    else:
                        # Parse function declaration
                        declarations.append(self.parse_top_level_function(modifiers))
                else:
                    # Parse as a variable declaration
                    declarations.append(self.parse_variable(modifiers))
            # Parse string literals (function names, etc)
            elif self.current_token.type == TokenTypes.STRING:
                # This is likely a function with a string literal name
                declarations.append(self.parse_function_header(modifiers))
            else:
                self.error(f"Unexpected token {self.current_token.type.name} at top level")
                
        return declarations

    def parse(self) -> Program:
        """Parse a Shard program"""
        declarations = self.parse_declarations()
        return Program(declarations=declarations) 
