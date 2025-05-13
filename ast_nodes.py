from dataclasses import dataclass
import json
from typing import Any

def indent(text: str, level: int = 1) -> str:
    """Helper function to indent multiline text"""
    prefix = "    " * level  # 4 spaces per level
    return "\n".join(prefix + line if line else line for line in text.split("\n"))

class ASTEncoder(json.JSONEncoder):
    """Custom JSON encoder for AST nodes"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Declaration):
            # Convert to dict and add node type
            result = {
                "node_type": obj.__class__.__name__,
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
                        # Handle other fields
                        result[k] = v
            return result
        return str(obj)  # Convert any other objects to strings

@dataclass
class Program:
    top_level: list

# abstract classes
@dataclass
class Declaration:
    modifiers: list

@dataclass 
class IdentifiedDeclaration(Declaration):
    name: str

@dataclass
class ObjectDef(IdentifiedDeclaration):
    parent: str = None
    members: list = None

@dataclass
class VariableDef(IdentifiedDeclaration):
    type: str = None
    value: object = None

@dataclass
class FunctionDef(IdentifiedDeclaration):
    params: list
    return_type: str = None
    body: list = None

@dataclass
class TypeDef(ObjectDef):
    def __init__(self, modifiers, name, parent=None, members=None):
        super().__init__(modifiers, name, parent, members)
        # Convert any ObjectDef members to appropriate type
        if members:
            self.members = [
                TypeDef(m.modifiers, m.name, m.parent, m.members) 
                if isinstance(m, ObjectDef) and not isinstance(m, (TypeDef, ShardDef))
                else m 
                for m in members
            ]

@dataclass
class ShardDef(ObjectDef):
    def __init__(self, modifiers, name, parent=None, members=None):
        super().__init__(modifiers, name, parent, members)
        # Convert any ObjectDef members to appropriate type
        if members:
            self.members = [
                ShardDef(m.modifiers, m.name, m.parent, m.members)
                if isinstance(m, ObjectDef) and not isinstance(m, (TypeDef, ShardDef))
                else m 
                for m in members
            ]

    def __str__(self):
        return f"ShardDef(modifiers={self.modifiers}, name='{self.name}', parent='{self.parent}', members={self.members})"
    


