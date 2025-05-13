from dataclasses import dataclass
from typing import Any, List, Union, Optional
from .base import Expression, SourceLocation
from ..lexer.tokens import TokenTypes

@dataclass
class BinaryOp(Expression):
    """Binary operation node"""
    left: Expression
    operator: TokenTypes
    right: Expression
    location: Optional[SourceLocation] = None

@dataclass
class UnaryOp(Expression):
    """Unary operation node"""
    operator: TokenTypes
    operand: Expression
    location: Optional[SourceLocation] = None

@dataclass
class Literal(Expression):
    """Literal value node"""
    value: Union[str, int, float, bool]
    literal_type: TokenTypes  # STRING, INTEGER, FLOAT, BOOL
    location: Optional[SourceLocation] = None

@dataclass 
class Identifier(Expression):
    """Identifier reference node"""
    name: str
    location: Optional[SourceLocation] = None

@dataclass
class MemberAccess(Expression):
    """Member access expression (e.g., obj.field)"""
    object: Expression
    member: Identifier
    location: Optional[SourceLocation] = None

@dataclass
class FunctionCall(Expression):
    """Function call node"""
    function: Expression
    arguments: List[Expression]
    location: Optional[SourceLocation] = None

@dataclass
class AssignmentExpr(Expression):
    """Assignment expression node"""
    target: Union[Identifier, 'MemberAccess']
    operator: TokenTypes  # ASSIGN or compound assignments like PLUS_ASSIGN
    value: Expression
    location: Optional[SourceLocation] = None 