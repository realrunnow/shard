from ast_nodes import *
from lexer import TokenTypes, Token

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type=None):
        if token_type and self.current_token.type != token_type:
            raise SyntaxError(f"Expected {token_type.name}, got {self.current_token.type.name} at line {self.current_token.line}")
        self.current_token = self.lexer.get_next_token()

    def peek(self, ahead = 0):
        return self.lexer.peek(ahead)



    def parse_modifiers(self):
        modifiers = []
        while self.current_token.type in (
            # access modifiers
            TokenTypes.PUB, TokenTypes.PRIV, TokenTypes.INTERNAL, TokenTypes.OPEN,

            # variable mutability
            TokenTypes.CONST, TokenTypes.MUT, 

            # method purity
            TokenTypes.PURE, TokenTypes.IMPURE,

            # for methods / functions
            TokenTypes.META, TokenTypes.BUS, TokenTypes.ON,
        ):
            modifiers.append(self.current_token.type.name)
            self.eat()
        return modifiers

    def parse_type(self):
        if self.current_token.type != TokenTypes.IDENT:
            raise SyntaxError(f"Expected type identifier at line {self.current_token.line}")
        type_name = self.current_token.value
        self.eat()
        return type_name
    


    def parse_variable(self, modifiers):
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)
        type_name = None
        if self.current_token.type == TokenTypes.COLON:
            self.eat()
            type_name = self.parse_type()
        value = None
        if self.current_token.type == TokenTypes.ASSIGN:
            self.eat()
            value = self.current_token.value
            self.eat()
        return VariableDef(modifiers, name, type_name, value)

    def parse_function_header(self, modifiers):
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)

        self.eat(TokenTypes.LPAREN)
        params = []
        while self.current_token.type != TokenTypes.RPAREN:
            if params:
                self.eat(TokenTypes.COMMA)
            
            paraneter_modifiers = self.parse_modifiers()

            param = self.parse_variable(paraneter_modifiers)
            params.append(param)
            
        self.eat(TokenTypes.RPAREN)


        return_type = None
        if self.current_token.type == TokenTypes.ARROW:
            self.eat()
            return_type = self.parse_type()

            
        return FunctionDef(modifiers, name, params, return_type)

    def parse_composite_definition(self, modifiers):
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)


        parent = None
        if self.current_token.type == TokenTypes.FROM:
            self.eat()

            parent = self.parse_type()

        
        self.eat(TokenTypes.LBRACE)
        members = []
        while self.current_token.type != TokenTypes.RBRACE:
            member_modifiers = self.parse_modifiers()

            if self.current_token.type != TokenTypes.IDENT:
                raise SyntaxError(f"Expected identifier at line {self.current_token.line}")
            
            peek = self.lexer.peek(1)

            if peek == '(':
                members.append(self.parse_function_header(member_modifiers))
            else:
                members.append(self.parse_variable(member_modifiers))
        self.eat(TokenTypes.RBRACE)

        
        return ObjectDef(modifiers, name, parent, members)
    


    def parse_type_definition(self, modifiers):
        self.eat(TokenTypes.TYPE)

        return self.parse_composite_definition(modifiers)

    def parse_shard_definition(self, modifiers):
        self.eat(TokenTypes.SHARD)

        return self.parse_composite_definition(modifiers)

    def parse_function(self, modifiers):
        return self.parse_function_header(modifiers)




    def parse_top_level(self):
        modifiers = self.parse_modifiers()

        print(modifiers)
        if self.current_token.type == TokenTypes.TYPE:
            self.eat()
            return self.parse_type_definition(modifiers)
        
        elif self.current_token.type == TokenTypes.SHARD:
            return self.parse_shard_definition(modifiers)
        elif self.current_token.type == TokenTypes.IDENT:
            peek = self.peek(1)
            if peek == '(':
                return self.parse_function_header(modifiers)
            else:
                return self.parse_variable(modifiers)
        else:
            raise SyntaxError(f"Unexpected top-level token: {self.current_token.type.name}")

    def parse_program(self):
        program = Program(top_level=[])
        while self.current_token.type != TokenTypes.EOF:
            try:
                item = self.parse_top_level()
                program.top_level.append(item)
            except SyntaxError as e:
                print(f"⚠️  Error at line {self.current_token.line}: {e}")
                self.synchronize()
        return program

    def synchronize(self):
        while self.current_token.type not in (
            TokenTypes.TYPE, TokenTypes.SHARD,
            TokenTypes.IDENT, TokenTypes.EOF
        ):
            self.eat()