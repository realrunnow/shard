import sys
from lexer import Lexer, TokenTypes
from parser import Parser
from code_generator import CodeGenerator
from ast_nodes import *

def main():
    print("=== Aether Compiler ===")
    
    if len(sys.argv) != 2:
        print("Usage: python main.py <input.ae>")
        return

    input_file = sys.argv[1]
    print(f"[1] Reading source code from: {input_file}")
    
    with open(input_file, 'r') as file:
         input_text = file.read()
        
    print("    ✓ Source code loaded")
    print("    First 100 characters:")
    print("    ------------------------------")
    print(input_text[:100] + ("..." if len(input_text) > 100 else ""))
    print("    ------------------------------\n")

    print("[2] Initializing lexer...")
    lexer_for_tokens = Lexer(input_text)
    print("    ✓ Lexer initialized\n")

    print("[2.5] Tokenizing source code...")
    tokens = []
    while True:
        token = lexer_for_tokens.get_next_token()
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

    print("[3] Initializing parser...")
    # Create a fresh lexer for parsing
    lexer_for_parsing = Lexer(input_text)
    parser = Parser(lexer_for_parsing)
    print("    ✓ Parser initialized\n")

    print("[4] Parsing Abstract Syntax Tree (AST)...")
    ast = parser.parse_program()

    print(ast)
    print("\n[6] Compilation complete.")



if __name__ == '__main__':
    main()

    