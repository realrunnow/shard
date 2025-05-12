from ast_nodes import *
from lexer import TokenTypes


from ast_nodes import *

class CodeGenerator:
    def __init__(self):
        self.asm = []
        self.string_literals = {}
        self.label_counter = 0
        self.local_vars = {}
        self.var_offset = -4  # Start from -4 (locals go below ebp)

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

        # Track local variables
        local_vars = {}
        var_offset = -4  # Start below ebp

        for stmt in func.body:
            if isinstance(stmt, VariableDeclaration):
                self.generate_expression(stmt.value, local_vars)
                local_vars[stmt.name] = var_offset
                self.asm.append(f"mov %eax, {var_offset}(%ebp)")
                var_offset -= 4
            elif isinstance(stmt, Return):
                if stmt.value:
                    self.generate_expression(stmt.value, local_vars)
                self.asm.append("jmp .Lend")

        self.asm.append(".Lend:")
        self.asm.append("leave")
        self.asm.append("ret")

    def generate_variable(self, var):
        if var.name in self.local_vars:
            return
        self.local_vars[var.name] = self.var_offset
        self.var_offset -= 4  # Each variable is 4 bytes

    def generate_statement(self, stmt):
        if isinstance(stmt, Return):
            if stmt.value:
                self.generate_expression(stmt.value)
            self.asm.append("jmp .Lend")
        elif isinstance(stmt, VariableDeclaration):
            self.generate_expression(stmt.value)
            offset = self.local_vars[stmt.name]
            self.asm.append(f"mov %eax, {offset}(%ebp)")
        else:
            raise Exception(f"Unsupported statement type: {type(stmt)}")

    def generate_expression(self, expr):
        if isinstance(expr, IntegerLiteral):
            self.asm.append(f"mov ${expr.value}, %eax")
        elif isinstance(expr, Identifier):
            if expr.name in self.local_vars:
                offset = self.local_vars[expr.name]
                self.asm.append(f"mov {offset}(%ebp), %eax")
            else:
                # Assume parameter (ebp + offset > 0)
                # e.g., first param is at 8(%ebp)
                raise Exception(f"Undefined variable: {expr.name}")
        elif isinstance(expr, BinaryOp):
            self.generate_expression(expr.right)
            self.asm.append("push %eax")
            self.generate_expression(expr.left)
            self.asm.append("pop %ebx")
            if expr.op == TOKEN_TYPES['PLUS']:
                self.asm.append("add %ebx, %eax")
            elif expr.op == TOKEN_TYPES['MINUS']:
                self.asm.append("sub %ebx, %eax")
            elif expr.op == TOKEN_TYPES['TIMES']:
                self.asm.append("imul %ebx, %eax")
            elif expr.op == TOKEN_TYPES['DIVIDE']:
                self.asm.append("xor %edx, %edx")
                self.asm.append("idiv %ebx")
            else:
                raise Exception(f"Unsupported binary operation: {expr.op}")
        else:
            raise Exception(f"Unsupported expression type: {type(expr)}")

    def generate_expression(self, expr, local_vars):
        if isinstance(expr, IntegerLiteral):
            self.asm.append(f"mov ${expr.value}, %eax")
        elif isinstance(expr, Identifier):
            if expr.name in local_vars:
                offset = local_vars[expr.name]
                self.asm.append(f"mov {offset}(%ebp), %eax")
            else:
                # Assume parameter (positive offset from ebp)
                idx = (list(local_vars.keys()).index(expr.name) + 1) * 4
                self.asm.append(f"mov {idx}(%ebp), %eax")
        elif isinstance(expr, BinaryOp):
            self.generate_expression(expr.right, local_vars)
            self.asm.append("push %eax")
            self.generate_expression(expr.left, local_vars)
            self.asm.append("pop %ebx")
            if expr.op == TokenTypes.PLUS:
                self.asm.append("add %ebx, %eax")
            elif expr.op == TokenTypes.MINUS:
                self.asm.append("sub %ebx, %eax")
            elif expr.op == TokenTypes.TIMES:
                self.asm.append("imul %ebx, %eax")
            elif expr.op == TokenTypes.DIVIDE:
                self.asm.append("xor %edx, %edx")
                self.asm.append("idiv %ebx")
        else:
            raise Exception(f"Unsupported expression type: {type(expr)}")
        
    def generate_function_call(self, call, local_vars):
        for arg in reversed(call.arguments):
            self.generate_expression(arg, local_vars)
            self.asm.append("push %eax")
        self.asm.append(f"call {call.name}")
        self.asm.append("add $8, %esp")  # Clean up stack
    
    def generate_if(self, node, local_vars):
        end_label = self.create_label()
        false_label = self.create_label()
        
        self.generate_expression(node.condition, local_vars)
        self.asm.append(f"je {false_label}")
        
        self.generate_block(node.then_block, local_vars)
        self.asm.append(f"jmp {end_label}")
        
        self.asm.append(f"{false_label}:")
        if node.else_block:
            self.generate_block(node.else_block, local_vars)
        self.asm.append(f"{end_label}:")