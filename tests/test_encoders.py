#!/usr/bin/env python3
"""
Test cases for AST encoders.
"""

import unittest
import json
from src.shard.ast_nodes import (
    Program, TypeDef, ShardDef, ImplDef, FunctionDef, VariableDef,
    ComponentInstantiation, Literal, Identifier, FunctionCall, BinaryOp, 
    AssignmentExpr, MemberAccess, ExpressionStatement, ReturnStatement, Parameter,
    If, While, UnaryOp
)
from src.shard.encoders import encode_ast_as_json, encode_ast_as_alt
from src.shard.lexer.tokens import TokenTypes

class EncodersTestCase(unittest.TestCase):
    """Test cases for AST encoders"""
    
    def test_encode_if_statement(self):
        """Test encoding an if statement"""
        # Create a simple if statement
        if_stmt = If(
            condition=BinaryOp(
                left=Identifier(name="x"),
                operator=TokenTypes.EQ,
                right=Literal(value=42, literal_type=TokenTypes.INTEGER)
            ),
            then_block=[
                ExpressionStatement(expr=AssignmentExpr(
                    target=Identifier(name="y"),
                    operator=TokenTypes.ASSIGN,
                    value=Literal(value=1, literal_type=TokenTypes.INTEGER)
                ))
            ],
            else_block=[
                ExpressionStatement(expr=AssignmentExpr(
                    target=Identifier(name="y"),
                    operator=TokenTypes.ASSIGN,
                    value=Literal(value=0, literal_type=TokenTypes.INTEGER)
                ))
            ]
        )
        
        # Test alt encoding
        alt_output = encode_ast_as_alt(if_stmt)
        self.assertIn("if (x EQ 42)", alt_output)
        self.assertIn("y ASSIGN 1;", alt_output)
        self.assertIn("else {", alt_output)
        self.assertIn("y ASSIGN 0;", alt_output)
        
        # Test JSON encoding
        json_output = encode_ast_as_json(if_stmt)
        data = json.loads(json_output)
        self.assertEqual(data["type"], "If")
        self.assertEqual(data["condition"]["type"], "BinaryOp")
        self.assertEqual(data["condition"]["operator"], "EQ")
        self.assertEqual(len(data["then_block"]), 1)
        self.assertEqual(len(data["else_block"]), 1)

    def test_encode_while_statement(self):
        """Test encoding a while statement"""
        # Create a simple while statement
        while_stmt = While(
            condition=BinaryOp(
                left=Identifier(name="i"),
                operator=TokenTypes.LT,
                right=Literal(value=10, literal_type=TokenTypes.INTEGER)
            ),
            body=[
                ExpressionStatement(expr=AssignmentExpr(
                    target=Identifier(name="i"),
                    operator=TokenTypes.PLUS_ASSIGN,
                    value=Literal(value=1, literal_type=TokenTypes.INTEGER)
                ))
            ]
        )
        
        # Test alt encoding
        alt_output = encode_ast_as_alt(while_stmt)
        self.assertIn("while (i LT 10)", alt_output)
        self.assertIn("i PLUS_ASSIGN 1;", alt_output)
        
        # Test JSON encoding
        json_output = encode_ast_as_json(while_stmt)
        data = json.loads(json_output)
        self.assertEqual(data["type"], "While")
        self.assertEqual(data["condition"]["type"], "BinaryOp")
        self.assertEqual(data["condition"]["operator"], "LT")
        self.assertEqual(len(data["body"]), 1)
        self.assertEqual(data["body"][0]["expr"]["operator"], "PLUS_ASSIGN")

    def test_encode_unary_op(self):
        """Test encoding a unary operation"""
        # Create a unary operation
        unary_op = UnaryOp(
            operator=TokenTypes.MINUS,
            operand=Literal(value=42, literal_type=TokenTypes.INTEGER)
        )
        
        # Test alt encoding
        alt_output = encode_ast_as_alt(unary_op)
        self.assertEqual(alt_output.strip(), "MINUS 42")
        
        # Test JSON encoding
        json_output = encode_ast_as_json(unary_op)
        data = json.loads(json_output)
        self.assertEqual(data["type"], "UnaryOp")
        self.assertEqual(data["operator"], "MINUS")
        self.assertEqual(data["operand"]["value"], 42)
    
    def test_encode_complex_program(self):
        """Test encoding a complex program with all node types"""
        program = Program(
            [
                TypeDef(
                    modifiers=[TokenTypes.PUB],
                    name="Counter",
                    parents=None,
                    members=[
                        VariableDef(
                            modifiers=[TokenTypes.PRIV],
                            name="count",
                            type_name="int",
                            value=Literal(value=0, literal_type=TokenTypes.INTEGER)
                        ),
                        FunctionDef(
                            modifiers=[TokenTypes.PUB],
                            name="increment",
                            params=[
                                Parameter(
                                    modifiers=[],
                                    name="step",
                                    param_type="int",
                                    default_value=Literal(value=1, literal_type=TokenTypes.INTEGER)
                                )
                            ],
                            return_type=None,
                            body=[
                                ExpressionStatement(
                                    expr=AssignmentExpr(
                                            target=Identifier(name="count"),
                                        operator=TokenTypes.PLUS_ASSIGN,
                                        value=Identifier(name="step")
                                        )
                                ),
                                If(
                                    condition=BinaryOp(
                                        left=Identifier(name="count"),
                                        operator=TokenTypes.GT,
                                        right=Literal(value=100, literal_type=TokenTypes.INTEGER)
                                    ),
                                    then_block=[
                                        ExpressionStatement(
                                            expr=AssignmentExpr(
                                                target=Identifier(name="count"),
                        operator=TokenTypes.ASSIGN,
                                                value=Literal(value=100, literal_type=TokenTypes.INTEGER)
                    )
            )
                                    ],
                                    else_block=None
                                )
                            ]
                        )
                    ]
                ),
                ImplDef(
                    modifiers=[],
                    target_type="Counter",
                    for_type="Printable",
                    members=[
                        FunctionDef(
                            modifiers=[],
                            name="toString",
                            params=[],
                            return_type="string",
                            body=[
                                ReturnStatement(
                                    value=BinaryOp(
                                        left=Literal(value="Count: ", literal_type=TokenTypes.STRING),
                                        operator=TokenTypes.PLUS,
                                        right=FunctionCall(
                                            function=Identifier(name="toString"),
                                            arguments=[Identifier(name="count")]
                                        )
                                    )
                                )
                            ]
                        )
                    ]
                ),
                ComponentInstantiation(
                    component_type="Counter",
                    instance_name="myCounter",
                    args=[
                        AssignmentExpr(
                            target=Identifier(name="step"),
                            operator=TokenTypes.ASSIGN,
                            value=Literal(value=5, literal_type=TokenTypes.INTEGER)
                        )
                    ]
                )
            ]
        )
        
        # Encode the program
        json_output = encode_ast_as_json(program)
        alt_output = encode_ast_as_alt(program)

        # Expected alt output string
        expected_alt_output = (
            "Program:\n"
            "    PUB Type Counter {\n"
            "            PRIV count: int = 0\n"
            "            PUB increment( step: int = 1) {\n"
            "                        count PLUS_ASSIGN step;\n"
            "                        if (count GT 100) {\n"
            "                            count ASSIGN 100;\n"
            "                        }\n"
            "                    }\n"
            "        }\n"
            "    impl Counter for Printable {\n"
            "             toString() -> string {\n"
            "                        return \"Count: \" PLUS toString(count);\n"
            "                    }\n"
            "        }\n"
            "    Counter(step ASSIGN 5) as myCounter\n"
        )

  
        # Check JSON output (basic structure check)
        try:
            data = json.loads(json_output)
            self.assertEqual(data["type"], "Program")
            self.assertIsInstance(data["declarations"], list)
            self.assertEqual(len(data["declarations"]), 3) # TypeDef, ImplDef, ComponentInstantiation
        except json.JSONDecodeError:
            self.fail("JSON output is not valid JSON")

if __name__ == "__main__":
    unittest.main() 