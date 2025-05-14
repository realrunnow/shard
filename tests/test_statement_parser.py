#!/usr/bin/env python3
"""
Test cases for the Shard statement parser.
"""

import unittest
from typing import List, Dict, Any

from src.shard.lexer import Lexer, TokenTypes
from src.shard.parser.statement_parser import StatementParser
from src.shard.ast_nodes import (
    Statement, ExpressionStatement, ReturnStatement,
    VariableDef, If, While, ComponentInstantiation,
    Literal, Identifier, FunctionCall, FunctionDef
)
from tests.test_framework import ShardTestCase


class StatementParserTestCase(ShardTestCase):
    """Test case for the statement parser component"""

    def parse_statement(self, source: str) -> Statement:
        """Parse a single statement from source code"""
        lexer = Lexer(source)
        parser = StatementParser(lexer)
        return parser.parse_statement()

    def parse_block(self, source: str) -> List[Statement]:
        """Parse a block of statements from source code"""
        lexer = Lexer(source)
        parser = StatementParser(lexer)
        return parser.parse_block()

    def test_expression_statement(self):
        """Test parsing expression statements"""
        expr_stmts = [
            "x = 5;",
            "func();",
            "a + b;",
            '"string literal";'
        ]
        
        for stmt_str in expr_stmts:
            stmt = self.parse_statement(stmt_str)
            self.assertIsInstance(stmt, ExpressionStatement, 
                                 f"Expected ExpressionStatement for '{stmt_str}'")

    def test_return_statement(self):
        """Test parsing return statements"""
        return_stmts = {
            "return;": None,
            "return 42;": 42,
            'return "value";': "value",
            "return a + b;": None  # Just check that it's a BinaryOp
        }
        
        for stmt_str, expected_value in return_stmts.items():
            stmt = self.parse_statement(stmt_str)
            self.assertIsInstance(stmt, ReturnStatement, 
                                 f"Expected ReturnStatement for '{stmt_str}'")
            
            if expected_value is None and stmt_str == "return;":
                self.assertIsNone(stmt.value, f"Expected no return value for '{stmt_str}'")
            elif expected_value is None:
                # Just check that it has a value
                self.assertIsNotNone(stmt.value, f"Expected a return value for '{stmt_str}'")
            else:
                self.assertIsInstance(stmt.value, Literal, 
                                     f"Expected Literal value for '{stmt_str}'")
                self.assertEqual(stmt.value.value, expected_value, 
                                f"Expected return value {expected_value} for '{stmt_str}'")

    def test_if_statement(self):
        """Test parsing if statements"""
        # Simple if
        stmt = self.parse_statement("if (x > 0) { return 1; }")
        self.assertIsInstance(stmt, If, "Expected If statement")
        self.assertIsNotNone(stmt.condition, "Expected condition")
        self.assertIsInstance(stmt.then_block, list, "Expected then_block to be a list")
        self.assertEqual(len(stmt.then_block), 1, "Expected 1 statement in then_block")
        self.assertIsNone(stmt.else_block, "Expected no else_block")
        
        # If-else
        stmt = self.parse_statement("if (x > 0) { return 1; } else { return 0; }")
        self.assertIsInstance(stmt, If, "Expected If statement")
        self.assertIsNotNone(stmt.condition, "Expected condition")
        self.assertIsInstance(stmt.then_block, list, "Expected then_block to be a list")
        self.assertEqual(len(stmt.then_block), 1, "Expected 1 statement in then_block")
        self.assertIsInstance(stmt.else_block, list, "Expected else_block to be a list")
        self.assertEqual(len(stmt.else_block), 1, "Expected 1 statement in else_block")

    def test_while_statement(self):
        """Test parsing while statements"""
        stmt = self.parse_statement("while (x > 0) { x = x - 1; }")
        self.assertIsInstance(stmt, While, "Expected While statement")
        self.assertIsNotNone(stmt.condition, "Expected condition")
        self.assertIsInstance(stmt.body, list, "Expected body to be a list")
        self.assertEqual(len(stmt.body), 1, "Expected 1 statement in body")

    def test_variable_declaration(self):
        """Test parsing variable declarations in a block"""
        block = self.parse_block("{ x: int; y: float = 3.14; }")
        self.assertEqual(len(block), 2, "Expected 2 statements in block")
        
        # First variable
        self.assertIsInstance(block[0], VariableDef, "Expected VariableDef for first statement")
        self.assertEqual(block[0].name, "x", "Expected name 'x' for first variable")
        self.assertEqual(block[0].type_name, "int", "Expected type 'int' for first variable")
        self.assertIsNone(block[0].value, "Expected no value for first variable")
        
        # Second variable
        self.assertIsInstance(block[1], VariableDef, "Expected VariableDef for second statement")
        self.assertEqual(block[1].name, "y", "Expected name 'y' for second variable")
        self.assertEqual(block[1].type_name, "float", "Expected type 'float' for second variable")
        self.assertIsNotNone(block[1].value, "Expected value for second variable")
        self.assertIsInstance(block[1].value, Literal, "Expected Literal value for second variable")
        self.assertEqual(block[1].value.value, 3.14, "Expected value 3.14 for second variable")

    def test_function_declaration(self):
        """Test parsing function declarations in a block"""
        block = self.parse_block("{ func1(); func2(x: int) { return x + 1; } }")
        self.assertEqual(len(block), 2, "Expected 2 statements in block")
        
        # Function declaration with body
        self.assertIsInstance(block[1], FunctionDef, "Expected FunctionDef for second statement")
        self.assertEqual(block[1].name, "func2", "Expected name 'func2'")
        self.assertEqual(len(block[1].params), 1, "Expected 1 parameter")
        self.assertEqual(block[1].params[0].name, "x", "Expected parameter name 'x'")
        self.assertEqual(block[1].params[0].param_type, "int", "Expected parameter type 'int'")
        self.assertIsInstance(block[1].body, list, "Expected body to be a list")
        self.assertEqual(len(block[1].body), 1, "Expected 1 statement in body")
        self.assertIsInstance(block[1].body[0], ReturnStatement, "Expected ReturnStatement in body")

    def test_component_instantiation(self):
        """Test parsing component instantiations"""
        stmt = self.parse_statement("Component(x = 1, y = 2) as instance;")
        self.assertIsInstance(stmt, ComponentInstantiation, "Expected ComponentInstantiation")
        self.assertEqual(stmt.component_type, "Component", "Expected component type 'Component'")
        self.assertEqual(stmt.instance_name, "instance", "Expected instance name 'instance'")
        self.assertEqual(len(stmt.args), 2, "Expected 2 arguments")

    def test_empty_parameter_function(self):
        """Test parsing functions with empty parameter lists"""
        block = self.parse_block("{ init() { print(\"Constructor\"); } }")
        self.assertEqual(len(block), 1, "Expected 1 statement in block")
        self.assertIsInstance(block[0], FunctionDef, "Expected FunctionDef")
        self.assertEqual(block[0].name, "init", "Expected name 'init'")
        self.assertEqual(len(block[0].params), 0, "Expected 0 parameters")
        self.assertIsInstance(block[0].body, list, "Expected body to be a list")
        self.assertEqual(len(block[0].body), 1, "Expected 1 statement in body")


if __name__ == "__main__":
    unittest.main() 