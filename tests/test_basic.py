import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shard.lexer import Lexer
from src.shard.parser import Parser
from src.shard.encoders.json_encoder import ASTJsonEncoder
import json

def test_basic_parsing():
    # Test input
    input_text = """
type Vehicle {
    priv speed: i32;
    pub accelerate(mut self, const amount: i32) {
        self.speed = self.speed + amount;
    }
}
    """
    
    try:
        # Create lexer and parser
        lexer = Lexer(input_text)
        
        # Debug token info
        token = lexer.get_next_token()
        print(f"First token: {token}")
        print(f"Token type: {token.type}, id(token.type): {id(token.type)}")
        
        # Reset lexer for parsing
        lexer = Lexer(input_text)
        parser = Parser(lexer)
        
        # Debug token comparison
        print(f"Checking tokens - current: {parser.current_token}")
        print(f"Current token type: {parser.current_token.type}, id: {id(parser.current_token.type)}")
        from src.shard.lexer.tokens import TokenTypes
        print(f"TokenTypes.TYPE id: {id(TokenTypes.TYPE)}")
        print(f"Is TYPE equal?: {parser.current_token.type == TokenTypes.TYPE}")
        
        # Parse and get AST
        ast = parser.parse()
        
        # Convert to JSON for inspection
        ast_json = json.dumps(ast, cls=ASTJsonEncoder, indent=2)
        print("Successfully parsed input. AST:")
        print(ast_json)
        return True
        
    except Exception as e:
        print(f"Error during parsing: {e}")
        return False

if __name__ == "__main__":
    test_basic_parsing() 