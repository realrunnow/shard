from dataclasses import dataclass
from typing import List, Optional, Union
from .base import Declaration, Statement, Expression, SourceLocation
from ..lexer.tokens import TokenTypes

@dataclass
class VariableDef(Declaration):
    """Variable definition node"""
    modifiers: List[TokenTypes]
    name: str
    type_name: Optional[str]
    value: Optional[Expression]
    location: Optional[SourceLocation] = None

@dataclass
class FunctionDef(Declaration):
    """Function definition node"""
    modifiers: List[TokenTypes]
    name: str
    params: List['VariableDef']
    return_type: Optional[str]
    body: Optional[List[Statement]]
    location: Optional[SourceLocation] = None

@dataclass
class ObjectDef(Declaration):
    """Base class for type and shard definitions"""
    modifiers: List[TokenTypes]
    name: str
    parents: Optional[Union[str, List[str]]]
    members: Optional[List[Union[FunctionDef, VariableDef]]]
    location: Optional[SourceLocation] = None

@dataclass
class TypeDef(ObjectDef):
    """Type definition node"""
    pass

@dataclass
class ShardDef(ObjectDef):
    """Shard definition node"""
    pass

@dataclass
class ImplDef(Declaration):
    """Implementation block node"""
    modifiers: List[TokenTypes]
    target_type: str
    for_type: Optional[str]
    members: List[Union[FunctionDef, VariableDef]]
    location: Optional[SourceLocation] = None

@dataclass
class Program(Declaration):
    """Root program node"""
    declarations: List[Union[ObjectDef, ImplDef]] 