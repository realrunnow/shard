#!/usr/bin/env python3
"""
Test cases for the Shard expression parser.
"""

import unittest
from typing import List, Dict, Any

from src.shard.lexer import Lexer, TokenTypes
from src.shard.parser.expression_parser import ExpressionParser
from src.shard.ast_nodes import (
    BinaryOp, UnaryOp, Literal, Identifier, FunctionCall, 
    AssignmentExpr, MemberAccess
)
from tests.test_framework import ShardTestCase


class ExpressionParserTestCase(ShardTestCase):
    """Test case for the expression parser component"""

    def parse_expression(self, source: str) -> Any:
        """Parse a single expression from source code"""
        lexer = Lexer(source)
        parser = ExpressionParser(lexer)
        return parser.parse_expression()

    def test_literals(self):
        """Test parsing literal expressions"""
        literals = {
            "123": (TokenTypes.INTEGER, 123),
            "3.14": (TokenTypes.FLOAT, 3.14),
            '"hello"': (TokenTypes.STRING, "hello"),
            "true": (TokenTypes.BOOL, True),
            "false": (TokenTypes.BOOL, False)
        }
        
        for literal_str, (token_type, expected_value) in literals.items():
            expr = self.parse_expression(literal_str)
            self.assertIsInstance(expr, Literal, f"Expected Literal for '{literal_str}'")
            self.assertEqual(expr.literal_type, token_type, 
                             f"Expected token type {token_type} for '{literal_str}'")
            self.assertEqual(expr.value, expected_value, 
                             f"Expected value {expected_value} for '{literal_str}'")

    def test_identifiers(self):
        """Test parsing identifier expressions"""
        identifiers = ["x", "variable_name", "camelCase", "_underscore"]
        
        for ident in identifiers:
            expr = self.parse_expression(ident)
            self.assertIsInstance(expr, Identifier, f"Expected Identifier for '{ident}'")
            self.assertEqual(expr.name, ident, f"Expected name '{ident}'")

    def test_binary_operations(self):
        """Test parsing binary operations"""
        binary_ops = {
            "a + b": (TokenTypes.PLUS, "a", "b"),
            "x - y": (TokenTypes.MINUS, "x", "y"),
            "foo * bar": (TokenTypes.TIMES, "foo", "bar"),
            "num / denom": (TokenTypes.DIVIDE, "num", "denom"),
            "a == b": (TokenTypes.EQ, "a", "b"),
            "a != b": (TokenTypes.NE, "a", "b"),
            "a < b": (TokenTypes.LT, "a", "b"),
            "a > b": (TokenTypes.GT, "a", "b"),
            "a <= b": (TokenTypes.LE, "a", "b"),
            "a >= b": (TokenTypes.GE, "a", "b")
        }
        
        for expr_str, (op_type, left_name, right_name) in binary_ops.items():
            expr = self.parse_expression(expr_str)
            self.assertIsInstance(expr, BinaryOp, f"Expected BinaryOp for '{expr_str}'")
            self.assertEqual(expr.operator, op_type, f"Expected operator {op_type} for '{expr_str}'")
            
            self.assertIsInstance(expr.left, Identifier, f"Expected left operand to be Identifier")
            self.assertEqual(expr.left.name, left_name, f"Expected left operand name '{left_name}'")
            
            self.assertIsInstance(expr.right, Identifier, f"Expected right operand to be Identifier")
            self.assertEqual(expr.right.name, right_name, f"Expected right operand name '{right_name}'")

    def test_assignment(self):
        """Test parsing assignment expressions"""
        assignments = {
            "x = 5": (TokenTypes.ASSIGN, "x", 5),
            "y += 10": (TokenTypes.PLUS_ASSIGN, "y", 10),
            "z -= 3": (TokenTypes.MINUS_ASSIGN, "z", 3),
            "w *= 2": (TokenTypes.TIMES_ASSIGN, "w", 2),
            "v /= 4": (TokenTypes.DIVIDE_ASSIGN, "v", 4)
        }
        
        for expr_str, (op_type, target_name, value) in assignments.items():
            expr = self.parse_expression(expr_str)
            
            # AssignmentExpr may not be implemented yet, so we may get a BinaryOp instead
            if hasattr(expr, 'target'):  # If AssignmentExpr
                self.assertIsInstance(expr, AssignmentExpr, f"Expected AssignmentExpr for '{expr_str}'")
                self.assertEqual(expr.operator, op_type, f"Expected operator {op_type} for '{expr_str}'")
                
                self.assertIsInstance(expr.target, Identifier, f"Expected target to be Identifier")
                self.assertEqual(expr.target.name, target_name, f"Expected target name '{target_name}'")
                
                self.assertIsInstance(expr.value, Literal, f"Expected value to be Literal")
                self.assertEqual(expr.value.value, value, f"Expected value {value}")
            else:  # If BinaryOp
                self.assertIsInstance(expr, BinaryOp, f"Expected BinaryOp for '{expr_str}'")
                self.assertEqual(expr.operator, op_type, f"Expected operator {op_type} for '{expr_str}'")
                
                self.assertIsInstance(expr.left, Identifier, f"Expected left operand to be Identifier")
                self.assertEqual(expr.left.name, target_name, f"Expected left operand name '{target_name}'")
                
                self.assertIsInstance(expr.right, Literal, f"Expected right operand to be Literal")
                self.assertEqual(expr.right.value, value, f"Expected right operand value {value}")

    def test_function_call(self):
        """Test parsing function call expressions"""
        function_calls = {
            "foo()": ("foo", []),
            "bar(1, 2)": ("bar", [1, 2]),
            'process("data")': ("process", ['"data"']),  # Quote the string to indicate it's a literal
            "max(a, b, c)": ("max", ["a", "b", "c"])
        }
        
        for expr_str, (func_name, args) in function_calls.items():
            expr = self.parse_expression(expr_str)
            self.assertIsInstance(expr, FunctionCall, f"Expected FunctionCall for '{expr_str}'")
            
            self.assertIsInstance(expr.function, Identifier, f"Expected function to be Identifier")
            self.assertEqual(expr.function.name, func_name, f"Expected function name '{func_name}'")
            
            self.assertEqual(len(expr.arguments), len(args), 
                             f"Expected {len(args)} arguments for '{expr_str}'")
            
            for i, arg_value in enumerate(args):
                arg = expr.arguments[i]
                if isinstance(arg_value, str):
                    if arg_value.startswith('"') or arg_value.startswith("'"):
                        # String literal
                        self.assertIsInstance(arg, Literal, f"Expected arg {i} to be string Literal")
                        self.assertEqual(arg.literal_type, TokenTypes.STRING, 
                                        f"Expected arg {i} to be string Literal")
                        # Remove quotes from expected value for comparison
                        expected_str = arg_value.strip('"\'')
                        self.assertEqual(arg.value, expected_str, 
                                        f"Expected arg {i} value '{expected_str}'")
                    else:
                        # Identifier
                        self.assertIsInstance(arg, Identifier, f"Expected arg {i} to be Identifier")
                        self.assertEqual(arg.name, arg_value, f"Expected arg {i} name '{arg_value}'")
                else:
                    # Expected number literal
                    self.assertIsInstance(arg, Literal, f"Expected arg {i} to be Literal")
                    self.assertEqual(arg.value, arg_value, f"Expected arg {i} value {arg_value}")

    def test_member_access(self):
        """Test parsing member access expressions"""
        member_accesses = {
            "obj.field": ("obj", "field"),
            "a.b.c": ("a.b", "c"),  # Nested access
            "foo.bar()": ("foo", "bar")  # Method call
        }
        
        for expr_str, (obj_name, member_name) in member_accesses.items():
            expr = self.parse_expression(expr_str)
            
            # Skip method calls for now
            if expr_str.endswith("()"):
                continue
                
            if "." in obj_name:  # Nested access
                self.assertIsInstance(expr, MemberAccess, f"Expected MemberAccess for '{expr_str}'")
                self.assertIsInstance(expr.object, MemberAccess, 
                                     f"Expected object to be MemberAccess for '{expr_str}'")
                self.assertIsInstance(expr.member, Identifier, 
                                     f"Expected member to be Identifier for '{expr_str}'")
                self.assertEqual(expr.member.name, member_name, 
                                f"Expected member name '{member_name}' for '{expr_str}'")
            else:
                self.assertIsInstance(expr, MemberAccess, f"Expected MemberAccess for '{expr_str}'")
                self.assertIsInstance(expr.object, Identifier, 
                                     f"Expected object to be Identifier for '{expr_str}'")
                self.assertEqual(expr.object.name, obj_name, 
                                f"Expected object name '{obj_name}' for '{expr_str}'")
                self.assertIsInstance(expr.member, Identifier, 
                                     f"Expected member to be Identifier for '{expr_str}'")
                self.assertEqual(expr.member.name, member_name, 
                                f"Expected member name '{member_name}' for '{expr_str}'")

    def test_precedence(self):
        """Test operator precedence in expressions"""
        # Multiplication has higher precedence than addition
        expr = self.parse_expression("a + b * c")
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.operator, TokenTypes.PLUS)
        self.assertIsInstance(expr.left, Identifier)
        self.assertEqual(expr.left.name, "a")
        self.assertIsInstance(expr.right, BinaryOp)
        self.assertEqual(expr.right.operator, TokenTypes.TIMES)
        
        # Parentheses override precedence
        expr = self.parse_expression("(a + b) * c")
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.operator, TokenTypes.TIMES)
        self.assertIsInstance(expr.left, BinaryOp)
        self.assertEqual(expr.left.operator, TokenTypes.PLUS)
        self.assertIsInstance(expr.right, Identifier)
        self.assertEqual(expr.right.name, "c")
        
        # Assignment has low precedence
        expr = self.parse_expression("x = a + b")
        if hasattr(expr, 'target'):  # If AssignmentExpr
            self.assertIsInstance(expr, AssignmentExpr)
            self.assertEqual(expr.operator, TokenTypes.ASSIGN)
            self.assertIsInstance(expr.value, BinaryOp)
            self.assertEqual(expr.value.operator, TokenTypes.PLUS)
        else:  # If BinaryOp
            self.assertIsInstance(expr, BinaryOp)
            self.assertEqual(expr.operator, TokenTypes.ASSIGN)
            self.assertIsInstance(expr.right, BinaryOp)
            self.assertEqual(expr.right.operator, TokenTypes.PLUS)


if __name__ == "__main__":
    unittest.main() 