import sys
import argparse
from lexer import Lexer, TokenTypes
from parser import Parser
from code_generator import CodeGenerator
from ast_nodes import *
from encoders.json_encoder import encode_ast_as_json
from encoders.alt_encoder import encode_ast_as_alt
from encoders.token_encoder import encode_tokens

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Shard compiler')
    parser.add_argument('file', help='The source file to compile')
    parser.add_argument('--print_tokens', action='store_true', help='Print tokens after lexical analysis')
    parser.add_argument('--print_json_ast', action='store_true', help='Print AST in JSON format')
    parser.add_argument('--print_alt_ast', action='store_true', help='Print AST in alternative format')
    
    args = parser.parse_args()

    print("=== Aether Compiler ===")
    
    print(f"[1] Reading source code from: {args.file}")
    
    try:
        with open(args.file, 'r') as file:
            input_text = file.read()
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
        
    print("    ✓ Source code loaded")
    print("    First 100 characters:")
    print("    ------------------------------")
    print(input_text[:100] + ("..." if len(input_text) > 100 else ""))
    print("    ------------------------------\n")

    print("[2] Initializing lexer...")
    lexer = Lexer(input_text)
    print("    ✓ Lexer initialized\n")

    print("[2.5] Tokenizing source code...")
    tokens = []
    if args.print_tokens:
        # Only collect tokens if we need to print them
        while True:
            token = lexer.get_next_token()
            tokens.append(token)
            if token.type == TokenTypes.EOF:
                break
        print("    ✓ Token stream generated")
        print("    Tokens:")
        print("    Line | Column | Type     | Value")
        print("    ------------------------------")
        for token in tokens:
            value = ''
            if token.value is not None:
                value = str(token.value)
            print(f"    {token.line:<4} | {token.column:<4} | {token.type:<8} | {value}")
        print()
        # Reset lexer for parsing
        lexer = Lexer(input_text)

    print("[3] Initializing parser...")
    parser = Parser(lexer)
    print("    ✓ Parser initialized\n")

    print("[4] Parsing Abstract Syntax Tree (AST)...")
    try:
        ast = parser.parse_program()
        print("    ✓ AST generated\n")
    except SyntaxError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Print AST in requested format(s)
    if args.print_json_ast:
        print("\nAST (JSON format):")
        print(encode_ast_as_json(ast))

    if args.print_alt_ast:
        print("\nAST (Alternative format):")
        print(encode_ast_as_alt(ast))

    print("\n[5] Compilation complete.")

if __name__ == '__main__':
    main()

    