from ast_nodes import Program, Declaration, ObjectDef, FunctionDef, VariableDef

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
        if var.type:
            parts.append(f": {var.type}")
            
        # Add value if exists
        if var.value is not None:
            parts.append(f" = {repr(var.value)}")
            
        return indent("".join(parts), level)

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
            body_str = "\n".join(AltASTEncoder.encode(stmt, level + 1) for stmt in func.body)
            parts.append("\n" + body_str)
            parts.append("\n" + "    " * level + "}")
            
        return indent("".join(parts), level)

    @staticmethod
    def encode_object(obj: ObjectDef, level=0):
        result = []
        # Add modifiers and name
        mods = AltASTEncoder.encode_modifiers(obj.modifiers)
        result.append(f"{mods + ' ' if mods else ''}{obj.__class__.__name__.replace('Def', '')} {obj.name}")
        
        # Add parent if exists
        if obj.parent:
            result.append(f" from {obj.parent}")
            
        # Add members
        if obj.members:
            result.append(" {")
            members_str = "\n".join(AltASTEncoder.encode(member, level + 1) for member in obj.members)
            result.append("\n" + members_str)
            result.append("\n" + "    " * level + "}")
        
        return indent("".join(result), level)

    @staticmethod
    def encode_program(prog: Program):
        return "Program:\n" + "\n".join(AltASTEncoder.encode(item, 1) for item in prog.top_level)

    @staticmethod
    def encode(node, level=0):
        if isinstance(node, Program):
            return AltASTEncoder.encode_program(node)
        elif isinstance(node, (VariableDef)):
            return AltASTEncoder.encode_variable(node, level)
        elif isinstance(node, FunctionDef):
            return AltASTEncoder.encode_function(node, level)
        elif isinstance(node, ObjectDef):
            return AltASTEncoder.encode_object(node, level)
        else:
            return indent(str(node), level)

def encode_ast_as_alt(ast):
    """Encode AST in an alternative, more readable format"""
    return AltASTEncoder.encode(ast) 