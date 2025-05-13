from lexer import Lexer
from parser import Parser

def test_parser():
    with open('test.sd', 'r') as f:
        source = f.read()
    
    lexer = Lexer(source)
    parser = Parser(lexer)
    
    try:
        ast = parser.parse_program()
        print("Parsing successful!")
        print("AST:", ast)
    except Exception as e:
        print(f"Error during parsing: {e}")

if __name__ == '__main__':
    test_parser() 