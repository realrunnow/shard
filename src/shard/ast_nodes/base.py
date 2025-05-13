from dataclasses import dataclass
from typing import Optional, Any
from abc import ABC, abstractmethod

@dataclass
class SourceLocation:
    """Source code location information"""
    line: int
    column: int
    length: int
    file: str

class NodeVisitor(ABC):
    """Abstract base class for AST visitors"""
    
    @abstractmethod
    def visit(self, node: 'Node') -> Any:
        """Visit a node"""
        pass

    def generic_visit(self, node: 'Node') -> Any:
        """Called if no explicit visitor function exists for a node"""
        pass

class Node:
    """Base class for all AST nodes"""
    location: Optional[SourceLocation] = None

    def accept(self, visitor: NodeVisitor) -> Any:
        """Accept a visitor"""
        method = f'visit_{self.__class__.__name__}'
        if hasattr(visitor, method):
            return getattr(visitor, method)(self)
        return visitor.generic_visit(self)

@dataclass
class Expression(Node):
    """Base class for all expression nodes"""
    pass

@dataclass
class Statement(Node):
    """Base class for all statement nodes"""
    pass

@dataclass
class Declaration(Node):
    """Base class for all declaration nodes"""
    pass 