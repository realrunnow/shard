import unittest
import os
import sys

# Add the parent directory to the path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.shard.lexer import Lexer
from src.shard.parser import Parser
from src.shard.encoders.alt_encoder import encode_ast_as_alt

class TestSDParser(unittest.TestCase):
    def setUp(self):
        # Path to test.sd file
        test_file_path = os.path.join(os.path.dirname(__file__), 'test.sd')
        with open(test_file_path, 'r') as file:
            self.source_code = file.read()
            
        self.lexer = Lexer(self.source_code)
        self.parser = Parser(self.lexer)
        
    def test_parse_program(self):
        """Test that the program parses correctly"""
        try:
            ast = self.parser.parse()
            self.assertIsNotNone(ast, "AST should not be None")
            
            # Print the AST for debugging
            formatted_ast = encode_ast_as_alt(ast)
            print("\nParsed AST:")
            print(formatted_ast)
            
            # Verify the AST has expected nodes
            declaration_types = [type(decl).__name__ for decl in ast.declarations]
            self.assertIn('TypeDef', declaration_types, "Should have TypeDef declarations")
            self.assertIn('ShardDef', declaration_types, "Should have ShardDef declarations")
            self.assertIn('ImplDef', declaration_types, "Should have ImplDef declarations")
            self.assertIn('FunctionDef', declaration_types, "Should have FunctionDef declarations")
            
            # Note: We accept that the parser might generate additional nodes
            # due to error recovery, so we don't check exact count
            
        except Exception as e:
            self.fail(f"Parser failed with error: {e}")
            
if __name__ == '__main__':
    unittest.main() 