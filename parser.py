from ast_nodes import *
from lexer import TokenTypes, Token

class Parser:
    # Token type sets for better organization and checking
    MODIFIER_TOKENS = {
        # Access modifiers
        TokenTypes.PUB, TokenTypes.PRIV, TokenTypes.INTERNAL, TokenTypes.OPEN,
        # Variable mutability
        TokenTypes.CONST, TokenTypes.MUT,
        # Method purity
        TokenTypes.PURE, TokenTypes.IMPURE,
        # Special modifiers
        TokenTypes.META, TokenTypes.BUS, TokenTypes.ON,
    }

    TOP_LEVEL_TOKENS = {
        TokenTypes.TYPE,
        TokenTypes.SHARD,
        TokenTypes.IDENT,
    }

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message):
        raise SyntaxError(f"⚠️  Error at line {self.current_token.line}: {message}")

    def eat(self, token_type=None):
        if token_type and self.current_token.type != token_type:
            self.error(f"Expected {token_type.name}, got {self.current_token.type.name}")
        self.current_token = self.lexer.get_next_token()

    def peek(self, ahead=0):
        return self.lexer.peek(ahead)

    def parse_modifiers(self):
        """Parse a sequence of modifiers and return them as a list"""
        modifiers = []
        while self.current_token.type in self.MODIFIER_TOKENS:
            modifier = self.current_token.type
            # Only add non-PRIV modifiers as PRIV is default
            if modifier != TokenTypes.PRIV:
                modifiers.append(modifier)
            self.eat()

        # Add PRIV by default if no access modifier specified
        if not any(mod in {TokenTypes.PUB, TokenTypes.PRIV, TokenTypes.INTERNAL} for mod in modifiers):
            modifiers.append(TokenTypes.PRIV)

        return modifiers

    def parse_type(self):
        """Parse a type identifier"""
        if self.current_token.type != TokenTypes.IDENT:
            self.error("Expected type identifier")
        type_name = self.current_token.value
        self.eat()
        return type_name

    def parse_variable(self, modifiers):
        """Parse a variable declaration"""
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)

        # Parse optional type annotation
        type_name = None
        if self.current_token.type == TokenTypes.COLON:
            self.eat()
            type_name = self.parse_type()

        # Parse optional initializer
        value = None
        if self.current_token.type == TokenTypes.ASSIGN:
            self.eat()
            value = self.current_token.value
            self.eat()

        return VariableDef(modifiers, name, type_name, value)

    def parse_parameter_list(self):
        """Parse a comma-separated list of parameters"""
        params = []
        self.eat(TokenTypes.LPAREN)
        
        while self.current_token.type != TokenTypes.RPAREN:
            if params:
                self.eat(TokenTypes.COMMA)
            
            param_modifiers = self.parse_modifiers()
            param = self.parse_variable(param_modifiers)
            params.append(param)
            
        self.eat(TokenTypes.RPAREN)
        return params

    def parse_function_header(self, modifiers):
        """Parse a function declaration header"""
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)

        params = self.parse_parameter_list()

        # Parse optional return type
        return_type = None
        if self.current_token.type == TokenTypes.ARROW:
            self.eat()
            return_type = self.parse_type()

        return FunctionDef(modifiers, name, params, return_type)

    def parse_object_body(self):
        """Parse the body of an object/type/shard definition"""
        self.eat(TokenTypes.LBRACE)
        members = []
        
        while self.current_token.type != TokenTypes.RBRACE:
            member_modifiers = self.parse_modifiers()

            if self.current_token.type != TokenTypes.IDENT:
                self.error("Expected identifier")
            
            # Look ahead to determine if this is a function or variable
            is_function = self.peek() == '('
            
            if is_function:
                members.append(self.parse_function_header(member_modifiers))
            else:
                members.append(self.parse_variable(member_modifiers))
                
        self.eat(TokenTypes.RBRACE)
        return members

    def parse_object_definition(self, modifiers):
        """Parse an object definition (type/shard)"""
        name = self.current_token.value
        self.eat(TokenTypes.IDENT)

        # Parse optional parent
        parent = None
        if self.current_token.type == TokenTypes.FROM:
            self.eat()
            parent = self.parse_type()

        members = self.parse_object_body()
        return ObjectDef(modifiers, name, parent, members)

    def parse_top_level(self):
        """Parse a top-level declaration"""
        modifiers = self.parse_modifiers()

        if self.current_token.type == TokenTypes.TYPE:
            self.eat(TokenTypes.TYPE)
            return self.parse_object_definition(modifiers)
        
        elif self.current_token.type == TokenTypes.SHARD:
            self.eat(TokenTypes.SHARD)
            return self.parse_object_definition(modifiers)
        
        elif self.current_token.type == TokenTypes.IDENT:
            is_function = self.peek() == '('
            if is_function:
                return self.parse_function_header(modifiers)
            else:
                return self.parse_variable(modifiers)
        else:
            self.error(f"Unexpected token {self.current_token.type.name}")

    def parse_program(self):
        """Parse the entire program"""
        program = Program(top_level=[])
        while self.current_token.type != TokenTypes.EOF:
            try:
                item = self.parse_top_level()
                program.top_level.append(item)
            except SyntaxError as e:
                print(e)  # Log the error
                self.synchronize()  # Skip to next valid point
        return program

    def synchronize(self):
        """Skip tokens until we find a safe point to resume parsing"""
        while self.current_token.type not in self.TOP_LEVEL_TOKENS:
            if self.current_token.type == TokenTypes.EOF:
                break
            self.eat()