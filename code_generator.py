from ast_nodes import *
from lexer import TokenTypes


from ast_nodes import *

class CodeGenerator:
    def __init__(self):
        self.asm = []
        self.string_literals = {}
        self.label_counter = 0
        self.scope_stack = [{}]  # Stack of scopes for variable tracking
        self.current_offset = 0  # Current stack offset

    def enter_scope(self):
        self.scope_stack.append({})

    def exit_scope(self):
        self.scope_stack.pop()

    def add_variable(self, name, size=4):
        """Add a variable to current scope and return its offset"""
        self.current_offset -= size
        self.scope_stack[-1][name] = self.current_offset
        return self.current_offset

    def get_variable_offset(self, name):
        """Get variable offset by searching through scope stack"""
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None

    def create_label(self):
        self.label_counter += 1
        return f".L{self.label_counter}"

    def generate(self, node):
        self.asm.append(".section .data")
        self.asm.append(".section .text")
        for item in node.top_level:
            if isinstance(item, Function):
                self.generate_function(item)
            elif isinstance(item, TypeDef):
                self.generate_type(item)
            elif isinstance(item, TraitDef):
                self.generate_trait(item)
            elif isinstance(item, ImplDef):
                self.generate_impl(item)

    def generate_function(self, func):
        self.asm.append(f"{func.name}:")
        self.asm.append("push %ebp")
        self.asm.append("mov %esp, %ebp")
        
        self.enter_scope()
        
        # Reserve space for local variables
        for stmt in func.body:
            if isinstance(stmt, VariableDeclaration):
                self.add_variable(stmt.name)
        
        if self.current_offset < 0:
            self.asm.append(f"sub ${-self.current_offset}, %esp")

        for stmt in func.body:
            self.generate_statement(stmt)

        self.asm.append(".Lend:")
        self.asm.append("leave")
        self.asm.append("ret")
        
        self.exit_scope()
        self.current_offset = 0

    def generate_statement(self, stmt):
        if isinstance(stmt, Return):
            if stmt.value:
                self.generate_expression(stmt.value)
            self.asm.append("jmp .Lend")
        elif isinstance(stmt, VariableDeclaration):
            self.generate_expression(stmt.value)
            offset = self.get_variable_offset(stmt.name)
            self.asm.append(f"mov %eax, {offset}(%ebp)")
        elif isinstance(stmt, If):
            self.generate_if(stmt)
        else:
            raise Exception(f"Unsupported statement type: {type(stmt)}")

    def generate_expression(self, expr):
        if isinstance(expr, IntegerLiteral):
            self.asm.append(f"mov ${expr.value}, %eax")
        elif isinstance(expr, Identifier):
            offset = self.get_variable_offset(expr.name)
            if offset is not None:
                self.asm.append(f"mov {offset}(%ebp), %eax")
            else:
                # Check if it's a parameter
                param_idx = 8  # First parameter is at 8(%ebp)
                self.asm.append(f"mov {param_idx}(%ebp), %eax")
        elif isinstance(expr, BinaryOp):
            self.generate_expression(expr.right)
            self.asm.append("push %eax")
            self.generate_expression(expr.left)
            self.asm.append("pop %ebx")
            
            op_map = {
                TokenTypes.PLUS: "add %ebx, %eax",
                TokenTypes.MINUS: "sub %ebx, %eax",
                TokenTypes.TIMES: "imul %ebx, %eax",
                TokenTypes.DIVIDE: ["xor %edx, %edx", "idiv %ebx"],
            }
            
            if expr.op in op_map:
                if isinstance(op_map[expr.op], list):
                    for instruction in op_map[expr.op]:
                        self.asm.append(instruction)
                else:
                    self.asm.append(op_map[expr.op])
            else:
                raise Exception(f"Unsupported binary operation: {expr.op}")
        elif isinstance(expr, FunctionCall):
            self.generate_function_call(expr)
        else:
            raise Exception(f"Unsupported expression type: {type(expr)}")
        
    def generate_function_call(self, call):
        # Push arguments in reverse order
        for arg in reversed(call.arguments):
            self.generate_expression(arg)
            self.asm.append("push %eax")
        
        self.asm.append(f"call {call.name}")
        
        # Clean up stack
        if call.arguments:
            self.asm.append(f"add ${len(call.arguments) * 4}, %esp")
    
    def generate_if(self, node):
        end_label = self.create_label()
        false_label = self.create_label()
        
        self.generate_expression(node.condition)
        self.asm.append("test %eax, %eax")
        self.asm.append(f"je {false_label}")
        
        self.enter_scope()
        self.generate_block(node.then_block)
        self.exit_scope()
        
        self.asm.append(f"jmp {end_label}")
        
        self.asm.append(f"{false_label}:")
        if node.else_block:
            self.enter_scope()
            self.generate_block(node.else_block)
            self.exit_scope()
            
        self.asm.append(f"{end_label}:")

    def generate_block(self, statements):
        for stmt in statements:
            self.generate_statement(stmt)