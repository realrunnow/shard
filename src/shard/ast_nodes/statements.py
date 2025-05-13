from dataclasses import dataclass
from typing import List, Optional
from .base import Statement, Expression, SourceLocation

@dataclass
class ExpressionStatement(Statement):
    """Expression statement node"""
    expr: Expression
    location: Optional[SourceLocation] = None

@dataclass
class ReturnStatement(Statement):
    """Return statement node"""
    value: Optional[Expression] = None
    location: Optional[SourceLocation] = None

@dataclass
class If(Statement):
    """If statement node"""
    condition: Expression
    then_block: List[Statement]
    else_block: Optional[List[Statement]] = None
    location: Optional[SourceLocation] = None

@dataclass
class While(Statement):
    """While statement node"""
    condition: Expression
    body: List[Statement]
    location: Optional[SourceLocation] = None

@dataclass
class ComponentInstantiation(Statement):
    """Component instantiation statement node"""
    component_type: str
    instance_name: str
    args: List[Expression]
    location: Optional[SourceLocation] = None 