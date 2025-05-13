#!/usr/bin/env python3

from src.shard.lexer import Lexer, TokenTypes
from src.shard.parser import Parser
from src.shard.encoders.alt_encoder import encode_ast_as_alt
import sys

def debug_tokens(filename):
    """Print all tokens in the file to help debug parsing issues"""
    with open(filename, 'r') as f:
        source = f.read()
    
    print(f"Token stream for: {filename}")
    print("=" * 50)
    
    lexer = Lexer(source)
    token = lexer.get_next_token()
    
    while token.type != TokenTypes.EOF:
        print(f"Line {token.line}: {token.type.name} - '{token.value}'")
        token = lexer.get_next_token()
    
    print(f"Line {token.line}: {token.type.name} - '{token.value}'")
    print("=" * 50)

def test_parser(filename, debug=False):
    with open(filename, 'r') as f:
        source = f.read()
    
    print(f"Testing parser on: {filename}")
    print("=" * 50)
    
    if debug:
        # Print token stream first
        debug_tokens(filename)
    
    lexer = Lexer(source)
    parser = Parser(lexer)
    
    try:
        ast = parser.parse()
        print("Parsing successful!")
        print("\nAST structure:")
        print(encode_ast_as_alt(ast))
    except Exception as e:
        print(f"Error: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    # Check if a file is specified as a command-line argument
    if len(sys.argv) > 1:
        test_parser(sys.argv[1], debug=True)
    else:
        # Test the complex file by default
        test_parser("tests/complex.sd", debug=True) 