import json
from ast_nodes import Declaration, Program
from lexer import TokenTypes

class ASTJsonEncoder(json.JSONEncoder):
    """Custom JSON encoder for AST nodes"""
    def default(self, obj):
        if isinstance(obj, Program):
            return {
                "type": "Program",
                "top_level": [self.default(item) for item in obj.top_level]
            }
        elif isinstance(obj, Declaration):
            # Convert to dict and add node type
            result = {
                "type": obj.__class__.__name__,
            }
            # Handle each field
            for k, v in obj.__dict__.items():
                if v is not None:  # Only include non-None values
                    if k == "modifiers":
                        # Convert modifiers from enums to strings
                        result[k] = [mod.name for mod in v]
                    elif isinstance(v, list):
                        # Handle lists (like params, body, members)
                        result[k] = [self.default(item) if isinstance(item, Declaration) else item for item in v]
                    else:
                        result[k] = v
            return result
        elif isinstance(obj, TokenTypes):
            return obj.name
        return str(obj)

def encode_ast_as_json(ast):
    """Encode AST as JSON string"""
    return json.dumps(ast, cls=ASTJsonEncoder, indent=2) 