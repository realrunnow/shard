from dataclasses import dataclass

@dataclass
class Program:
    top_level: list

    def __repr__(self):
        return f"Program(top_level={self.top_level})"

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

    def __repr__(self):
        return f"VariableDef(modifiers={self.modifiers}, name='{self.name}', type='{self.type}', value={self.value})"


@dataclass
class FunctionDef(IdentifiedDeclaration):
    params: list
    return_type: str = None
    body: list = None

    def __repr__(self):
        return f"FunctionDef(modifiers={self.modifiers}, name='{self.name}', params={self.params}, return_type='{self.return_type}', body={self.body})"




@dataclass
class TypeDef(ObjectDef):
    def __repr__(self):
        return f"TypeDef(modifiers={self.modifiers}, name='{self.name}', parent='{self.parent}', members={self.members})"


@dataclass
class ShardDef(ObjectDef):
    def __repr__(self):
        return f"ShardDef(modifiers={self.modifiers}, name='{self.name}', parent='{self.parent}', members={self.members})"
    


