import sys
import argparse
from src.shard.lexer import Lexer
from src.shard.parser import Parser
from src.shard.encoders.json_encoder import ASTJsonEncoder, encode_ast_as_json
from src.shard.encoders.alt_encoder import encode_ast_as_alt

def main():
    # Set up argument parser
    arg_parser = argparse.ArgumentParser(description='Shard compiler')
    arg_parser.add_argument('file', help='The source file to compile')
    arg_parser.add_argument('--print_tokens', action='store_true', help='Print tokens after lexical analysis')
    arg_parser.add_argument('--print_ast', action='store_true', help='Print AST in JSON format')
    arg_parser.add_argument('--print_alt', action='store_true', help='Print AST in alternative readable format')
    
    args = arg_parser.parse_args()

    print("=== Shard Compiler ===")
    
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

    if args.print_tokens:
        print("[2.5] Tokenizing source code...")
        # Only collect tokens if we need to print them
        tokens = []
        token_lexer = Lexer(input_text)  # Create a separate lexer for token printing
        while True:
            token = token_lexer.get_next_token()
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
            print(f"    {token.line:<4} | {token.column:<6} | {token.type.name:<8} | {value}")
        print()

    print("[3] Initializing parser...")
    parser = Parser(lexer)
    print("    ✓ Parser initialized\n")

    print("[4] Parsing Abstract Syntax Tree (AST)...")
    try:
        ast = parser.parse()
        print("    ✓ AST generated\n")
    except SyntaxError as e:
        print(f"Error during parsing: {e}")
        sys.exit(1)

    # Print AST if requested
    if args.print_ast:
        print("\nAST (JSON format):")
        import json
        print(json.dumps(ast, cls=ASTJsonEncoder, indent=2))
        
    # Print alternative AST format if requested
    if args.print_alt:
        print("\nAST (Alternative format):")
        print(encode_ast_as_alt(ast))

    print("\n[5] Compilation complete.")

if __name__ == '__main__':
    main()