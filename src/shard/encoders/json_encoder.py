import json
from ..ast_nodes import (
    Node, Program, ImplDef, TypeDef, ShardDef,
    Statement, Expression, FunctionDef, VariableDef,
    ComponentInstantiation, Literal, Identifier,
    FunctionCall, BinaryOp, AssignmentExpr,
    ExpressionStatement, ReturnStatement
)
from ..lexer.tokens import TokenTypes

class ASTJsonEncoder(json.JSONEncoder):
    """Custom JSON encoder for AST nodes"""
    def default(self, obj):
        if isinstance(obj, Node):
            result = {
                "type": obj.__class__.__name__,
            }
            for k, v in obj.__dict__.items():
                if v is not None:  # Only include non-None values
                    if k == "modifiers":
                        result[k] = [mod.name for mod in v]
                    elif isinstance(v, list):
                        result[k] = [self.default(item) if isinstance(item, Node) else item for item in v]
                    elif isinstance(v, (Node, TokenTypes)):
                        result[k] = self.default(v)
                    else:
                        result[k] = v
            return result
        elif isinstance(obj, TokenTypes):
            return obj.name
        return str(obj)

def encode_ast_as_json(ast):
    """Encode AST as JSON string"""
    return json.dumps(ast, cls=ASTJsonEncoder, indent=2) 