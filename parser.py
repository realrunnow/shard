from ast_nodes import *
from lexer import TokenTypes, Token

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    ###
    # UTILITY METHODS
    ###
    def eat(self, token_type=None):
        if token_type and self.current_token.type != token_type:
            raise SyntaxError(f"Expected {token_type.name}, got {self.current_token.type.name} at line {self.current_token.line}")
        self.current_token = self.lexer.get_next_token()

    def peek(self, ahead = 0):
        return self.lexer.peek(ahead)


    ###
    # UTILITY PARSERS
    ###
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
            modifier = self.current_token.type

            # if token is PRIV do not add it, as it will be automatically added.
            if modifier != TokenTypes.PRIV :
                modifiers.append(modifier)

            self.eat()

        # add PRIV by default
        if modifiers.count <= 0:
             modifiers.append(TokenTypes.PRIV.name)

        return modifiers

    def parse_type(self):
        if self.current_token.type != TokenTypes.IDENT:
            raise SyntaxError(f"Expected type identifier at line {self.current_token.line}")
        
        type_name = self.current_token.value
        self.eat()

        return type_name
    

    ###
    # LOGIC PARSERS
    ###
    def parse_variable(self, modifiers):
        ## var_identifier
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)

        ## : type
        type_name = None
        if self.current_token.type == TokenTypes.COLON:
            self.eat()

            type_name = self.parse_type()

        ## = value (optional)
        value = None
        if self.current_token.type == TokenTypes.ASSIGN:
            self.eat()

            value = self.current_token.value
            self.eat()

        return VariableDef(modifiers, name, type_name, value)

    def parse_function_header(self, modifiers):
        ## fn_idenfifier
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)

        ## (<param_modifiers> parse_variable_output, ...)
        self.eat(TokenTypes.LPAREN)
        params = []
        while self.current_token.type != TokenTypes.RPAREN:
            if params:
                self.eat(TokenTypes.COMMA)
            
            paraneter_modifiers = self.parse_modifiers()

            param = self.parse_variable(paraneter_modifiers)
            params.append(param)
            
        self.eat(TokenTypes.RPAREN)


        ## -> return_type (optional)
        return_type = None
        if self.current_token.type == TokenTypes.ARROW:
            self.eat()
            return_type = self.parse_type()

            
        return FunctionDef(modifiers, name, params, return_type)



    ###
    # CONSTRUCT PARSERS
    ###
    def parse_object_definition(self, modifiers):
        ## object_name
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)

        ## from object_parent (optional)
        parent = None
        if self.current_token.type == TokenTypes.FROM:
            self.eat()

            parent = self.parse_type()

        ## { 
        ##    <function_modifiers> parse_function_header_ouput
        ##    <variable_modifiers> parse_variable_ouput
        ##    ...
        ## }
        self.eat(TokenTypes.LBRACE)
        members = []
        while self.current_token.type != TokenTypes.RBRACE:
            member_modifiers = self.parse_modifiers()

            if self.current_token.type != TokenTypes.IDENT:
                raise SyntaxError(f"Expected identifier at line {self.current_token.line}, got {self.current_token.type}")
            
            peek = self.lexer.peek()

            if peek == '(':
                members.append(self.parse_function_header(member_modifiers))
            else:
                members.append(self.parse_variable(member_modifiers))
        self.eat(TokenTypes.RBRACE)

        
        return ObjectDef(modifiers, name, parent, members)
    


    def parse_type_definition(self, modifiers):
        ## type
        self.eat(TokenTypes.TYPE)

        ## parse_object_outpu
        return self.parse_object_definition(modifiers)

    def parse_shard_definition(self, modifiers):
        ## shard
        self.eat(TokenTypes.SHARD)

        ## parse_object_output
        return self.parse_object_definition(modifiers)

    def parse_function(self, modifiers):
        ## parse_function_header_ouput
        return self.parse_function_header(modifiers)



    ###
    # GENERAL PARSERS
    ###
    def parse_top_level(self):
        ## parse_modifiers_output
        modifiers = self.parse_modifiers()

        ## parse_type_output
        if self.current_token.type == TokenTypes.TYPE:
            return self.parse_type_definition(modifiers)
        
        ## parse_shard_output
        elif self.current_token.type == TokenTypes.SHARD:
            return self.parse_shard_definition(modifiers)
        
        elif self.current_token.type == TokenTypes.IDENT:
            peek = self.peek(1)
            if peek == '(':
                ## parse_function_header_output
                return self.parse_function(modifiers)
            else:
                ## parse_variable_output
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
                raise SyntaxError(f"⚠️  Error at line {self.current_token.line}: {e}")
                self.synchronize()
        return program

    def synchronize(self):
        while self.current_token.type not in (
            TokenTypes.TYPE, TokenTypes.SHARD,
            TokenTypes.IDENT, TokenTypes.EOF
        ):
            self.eat()