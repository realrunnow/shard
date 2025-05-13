from typing import List, Union
from .declaration_parser import DeclarationParser
from ..ast_nodes import Program, Node
from ..lexer.tokens import TokenTypes

class Parser(DeclarationParser):
    """Main parser class that ties everything together"""

    def parse_top_level(self) -> List[Node]:
        """Parse top-level declarations"""
        declarations = []
        
        while self.current_token.type != TokenTypes.EOF:
            try:
                # Parse modifiers for declarations
                modifiers = self.parse_modifiers()
                
                if self.current_token.type == TokenTypes.TYPE:
                    declarations.append(self.parse_type_definition(modifiers))
                    
                elif self.current_token.type == TokenTypes.SHARD:
                    declarations.append(self.parse_shard_definition(modifiers))
                    
                elif self.current_token.type == TokenTypes.IMPL:
                    declarations.append(self.parse_impl_definition())
                    
                elif self.current_token.type in {TokenTypes.IDENT, TokenTypes.STRING}:
                    # Check if this is a function by looking ahead for '('
                    if self.peek().type == TokenTypes.LPAREN:
                        declarations.append(self.parse_function_header(modifiers))
                    else:
                        # Parse variable declaration
                        declarations.append(self.parse_variable(modifiers))
                else:
                    self.error(f"Unexpected token {self.current_token.type.name} at top level")
                    
            except SyntaxError as e:
                # Log the error but continue parsing
                print(f"Error parsing top-level declaration: {e}")
                self.synchronize(self.TOP_LEVEL_TOKENS)
                
        return declarations

    def parse(self) -> Program:
        """Parse the entire program"""
        declarations = self.parse_top_level()
        return Program(declarations=declarations) 