#!/usr/bin/env python3
"""
Test framework for the Shard parser.
Provides base classes and utilities for testing different components.
"""

import unittest
import os
import logging
from typing import List, Dict, Any, Optional, Tuple

from src.shard.lexer import Lexer, TokenTypes, Token
from src.shard.parser import Parser
from src.shard.encoders.alt_encoder import encode_ast_as_alt


class ShardTestCase(unittest.TestCase):
    """Base class for Shard language tests"""
    
    @classmethod
    def setUpClass(cls):
        """Setup resources shared by all test methods"""
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.test_files_dir = os.path.join(cls.test_dir, "test_files")
        
        # Create test files directory if it doesn't exist
        if not os.path.exists(cls.test_files_dir):
            os.makedirs(cls.test_files_dir)
            
    def setUp(self):
        """Setup for each test method"""
        pass
    
    def get_test_file_path(self, filename: str) -> str:
        """Get the full path to a test file"""
        return os.path.join(self.test_files_dir, filename)
    
    def create_test_file(self, filename: str, content: str) -> str:
        """Create a test file with given content and return its path"""
        path = self.get_test_file_path(filename)
        with open(path, 'w') as f:
            f.write(content)
        return path
    
    def parse_source(self, source: str, should_raise: bool = False) -> Tuple[Any, List[str]]:
        """Parse source code and return AST and any parser messages"""
        lexer = Lexer(source)
        parser = Parser(lexer)
        parser_messages = []

        # Log the source code
        logging.debug(f"Source code to parse:\n{source}")
        
        # Log the tokens from lexer
        tokens = self._get_all_tokens(source)
        token_str = "\n".join([f"{t.type}: '{t.value}' at line {t.line}" for t in tokens])
        logging.debug(f"Lexer output:\n{token_str}")
        
        if should_raise:
            ast = parser.parse()
            # Log the AST
            encoded_ast = encode_ast_as_alt(ast)
            logging.debug(f"Parser output (AST):\n{encoded_ast}")
            return ast, parser_messages
        
        try:
            ast = parser.parse()
            # Log the AST
            encoded_ast = encode_ast_as_alt(ast)
            logging.debug(f"Parser output (AST):\n{encoded_ast}")
            return ast, parser_messages
        except Exception as e:
            error_msg = f"Error: {e}"
            parser_messages.append(error_msg)
            logging.debug(error_msg)
            return None, parser_messages
    
    def parse_file(self, filepath: str, should_raise: bool = False) -> Tuple[Any, List[str]]:
        """Parse a file and return AST and parser messages"""
        with open(filepath, 'r') as f:
            source = f.read()
        logging.debug(f"Parsing file: {filepath}")
        return self.parse_source(source, should_raise)
    
    def _get_all_tokens(self, source: str) -> List[Token]:
        """Get all tokens from the source without consuming them in the parser"""
        lexer = Lexer(source)
        tokens = []
        
        token = lexer.get_next_token()
        while token.type != TokenTypes.EOF:
            tokens.append(token)
            token = lexer.get_next_token()
            
        return tokens
    
    def tokenize_source(self, source: str) -> List[Token]:
        """Tokenize source code and return list of tokens"""
        tokens = self._get_all_tokens(source)
        
        # Log the tokens
        token_str = "\n".join([f"{t.type}: '{t.value}' at line {t.line}" for t in tokens])
        logging.debug(f"Source code:\n{source}\n\nLexer output:\n{token_str}")
            
        return tokens
    
    def assert_ast_contains(self, ast: Any, node_type: str, expected_attributes: Dict[str, Any]):
        """Assert that AST contains a node of given type with expected attributes"""
        encoded_ast = encode_ast_as_alt(ast)
        logging.debug(f"Checking AST for node type {node_type} with attributes {expected_attributes}")
        logging.debug(f"AST: {encoded_ast}")
        
        # Simple string-based check as a starting point
        # In a real implementation, this would traverse the AST properly
        self.assertIn(node_type, encoded_ast, f"AST does not contain {node_type}")
        
        for attr, value in expected_attributes.items():
            self.assertIn(str(value), encoded_ast, 
                         f"AST does not contain {node_type} with {attr}={value}")
    
    def assert_no_errors(self, ast: Any):
        """Assert that AST was created without errors"""
        self.assertIsNotNone(ast, "AST should not be None (parsing error occurred)")
        logging.debug("Verified AST has no errors")
    
    def assert_has_errors(self, ast: Any):
        """Assert that AST has errors or is None"""
        self.assertIsNone(ast, "AST should be None (parsing error should have occurred)")
        logging.debug("Verified AST has errors as expected")


def run_tests():
    """Run all tests"""
    unittest.main()


if __name__ == "__main__":
    run_tests() 