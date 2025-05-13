from ..ast_nodes import (
    Node, Program, ImplDef, TypeDef, ShardDef,
    Statement, Expression, FunctionDef, VariableDef,
    ComponentInstantiation, Literal, Identifier,
    FunctionCall, BinaryOp, AssignmentExpr, MemberAccess,
    ExpressionStatement, ReturnStatement
)
from ..lexer.tokens import TokenTypes

def indent(text: str, level: int = 1) -> str:
    """Helper function to indent multiline text"""
    prefix = "    " * level  # 4 spaces per level
    return "\n".join(prefix + line if line else line for line in text.split("\n"))

class AltASTEncoder:
    @staticmethod
    def encode_modifiers(modifiers):
        return " ".join(mod.name for mod in modifiers) if modifiers else ""

    @staticmethod
    def encode_variable(var: VariableDef, level=0):
        parts = []
        # Add modifiers and name
        mods = AltASTEncoder.encode_modifiers(var.modifiers)
        parts.append(f"{mods + ' ' if mods else ''}{var.name}")
        
        # Add type if exists
        if var.type_name:
            parts.append(f": {var.type_name}")
            
        # Add value if exists
        if var.value is not None:
            parts.append(f" = {AltASTEncoder.encode_expression(var.value)}")
            
        return indent("".join(parts), level)

    @staticmethod
    def encode_expression(expr: Expression) -> str:
        if isinstance(expr, Literal):
            if expr.literal_type == TokenTypes.STRING:
                return f'"{expr.value}"'
            return str(expr.value)
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, MemberAccess):
            obj = AltASTEncoder.encode_expression(expr.object)
            member = AltASTEncoder.encode_expression(expr.member)
            return f"{obj}.{member}"
        elif isinstance(expr, FunctionCall):
            args = ", ".join(AltASTEncoder.encode_expression(arg) for arg in expr.arguments)
            func_name = AltASTEncoder.encode_expression(expr.function)
            return f"{func_name}({args})"
        elif isinstance(expr, BinaryOp):
            return f"{AltASTEncoder.encode_expression(expr.left)} {expr.operator.name} {AltASTEncoder.encode_expression(expr.right)}"
        elif isinstance(expr, AssignmentExpr):
            return f"{AltASTEncoder.encode_expression(expr.target)} {expr.operator.name} {AltASTEncoder.encode_expression(expr.value)}"
        return str(expr)

    @staticmethod
    def encode_function(func: FunctionDef, level=0):
        parts = []
        # Add modifiers and name
        mods = AltASTEncoder.encode_modifiers(func.modifiers)
        parts.append(f"{mods + ' ' if mods else ''}{func.name}")
        
        # Add parameters
        params_str = ", ".join(AltASTEncoder.encode_variable(param, 0) for param in func.params)
        parts.append(f"({params_str})")
        
        # Add return type if exists
        if func.return_type:
            parts.append(f" -> {func.return_type}")
            
        # Add body if exists
        if func.body:
            parts.append(" {")
            # Special handling for meta blocks to ensure component instantiations are encoded correctly
            body_str = "\n".join(
                AltASTEncoder.encode_component_instantiation(stmt, level + 1) 
                if isinstance(stmt, ComponentInstantiation)
                else AltASTEncoder.encode_statement(stmt, level + 1) 
                for stmt in func.body
            )
            parts.append("\n" + body_str)
            parts.append("\n" + "    " * level + "}")
            
        return indent("".join(parts), level)

    @staticmethod
    def encode_object(obj: TypeDef | ShardDef, level=0):
        result = []
        # Add modifiers and name
        mods = AltASTEncoder.encode_modifiers(obj.modifiers)
        result.append(f"{mods + ' ' if mods else ''}{obj.__class__.__name__.replace('Def', '')} {obj.name}")
        
        # Add parent if exists
        if obj.parents:
            if isinstance(obj.parents, list):
                result.append(f" from {', '.join(obj.parents)}")
            else:
                result.append(f" from {obj.parents}")
            
        # Add members
        if obj.members:
            result.append(" {")
            members_str = "\n".join(AltASTEncoder.encode(member, level + 1) for member in obj.members)
            result.append("\n" + members_str)
            result.append("\n" + "    " * level + "}")
        
        return indent("".join(result), level)

    @staticmethod
    def encode_impl(impl: ImplDef, level=0):
        result = []
        # Add modifiers and impl keyword
        mods = AltASTEncoder.encode_modifiers(impl.modifiers)
        result.append(f"{mods + ' ' if mods else ''}impl {impl.target_type}")
        
        # Add for_type if exists
        if impl.for_type:
            result.append(f" for {impl.for_type}")
            
        # Add members
        if impl.members:
            result.append(" {")
            members_str = "\n".join(AltASTEncoder.encode(member, level + 1) for member in impl.members)
            result.append("\n" + members_str)
            result.append("\n" + "    " * level + "}")
        
        return indent("".join(result), level)

    @staticmethod
    def encode_component_instantiation(comp: ComponentInstantiation, level=0):
        args_str = ", ".join(AltASTEncoder.encode_expression(arg) for arg in comp.args)
        
        # Only add "as instance_name" if there's an actual instance name
        if comp.instance_name:
            return indent(f"{comp.component_type}({args_str}) as {comp.instance_name}", level)
        else:
            # This is a regular function call
            return indent(f"{comp.component_type}({args_str})", level)

    @staticmethod
    def encode_statement(stmt: Statement, level=0):
        if isinstance(stmt, ExpressionStatement):
            expr_str = AltASTEncoder.encode_expression(stmt.expr)
            return indent(expr_str + ";", level)
        elif isinstance(stmt, ReturnStatement):
            if stmt.value:
                return indent(f"return {AltASTEncoder.encode_expression(stmt.value)};", level)
            return indent("return;", level)
        elif isinstance(stmt, ComponentInstantiation):
            args_str = ", ".join(AltASTEncoder.encode_expression(arg) for arg in stmt.args)
            return indent(f"{stmt.component_type}({args_str}) as {stmt.instance_name};", level)
        return indent(str(stmt), level)

    @staticmethod
    def encode_program(prog: Program):
        return "Program:\n" + "\n".join(AltASTEncoder.encode(item, 1) for item in prog.declarations)

    @staticmethod
    def encode(node, level=0):
        if isinstance(node, Program):
            return AltASTEncoder.encode_program(node)
        elif isinstance(node, VariableDef):
            return AltASTEncoder.encode_variable(node, level)
        elif isinstance(node, FunctionDef):
            return AltASTEncoder.encode_function(node, level)
        elif isinstance(node, ImplDef):
            return AltASTEncoder.encode_impl(node, level)
        elif isinstance(node, ComponentInstantiation):
            return AltASTEncoder.encode_component_instantiation(node, level)
        elif isinstance(node, (TypeDef, ShardDef)):
            return AltASTEncoder.encode_object(node, level)
        elif isinstance(node, Statement):
            return AltASTEncoder.encode_statement(node, level)
        elif isinstance(node, Expression):
            return indent(AltASTEncoder.encode_expression(node), level)
        else:
            return indent(str(node), level)

def encode_ast_as_alt(ast):
    """Encode AST in an alternative, more readable format"""
    return AltASTEncoder.encode(ast) 