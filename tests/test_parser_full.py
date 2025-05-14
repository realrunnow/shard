#!/usr/bin/env python3
"""
Test cases for the full Shard parser.
"""

import unittest
import logging
from typing import List, Dict, Any

from src.shard.lexer import TokenTypes
from src.shard.ast_nodes import (
    Program, TypeDef, ShardDef, ImplDef, FunctionDef, VariableDef,
    ComponentInstantiation, Parameter
)
from tests.test_framework import ShardTestCase


class FullParserTestCase(ShardTestCase):
    """Test case for the full parser"""

    def test_empty_program(self):
        """Test parsing an empty program"""
        ast, messages = self.parse_source("")
        self.assert_no_errors(ast)
        self.assertIsInstance(ast, Program, "Expected Program")
        self.assertEqual(len(ast.declarations), 0, "Expected 0 declarations")

    def test_type_definition(self):
        """Test parsing type definitions"""
        # Simple type
        source = "type Point { x: float; y: float; }"
        ast, messages = self.parse_source(source)
        self.assert_no_errors(ast)
        self.assertIsInstance(ast, Program, "Expected Program")
        self.assertEqual(len(ast.declarations), 1, "Expected 1 declaration")
        self.assertIsInstance(ast.declarations[0], TypeDef, "Expected TypeDef")
        self.assertEqual(ast.declarations[0].name, "Point", "Expected name 'Point'")
        self.assertEqual(len(ast.declarations[0].members), 2, "Expected 2 members")
        
        # Type with inheritance
        source = "type Circle from Point { radius: float; }"
        ast, messages = self.parse_source(source)
        self.assert_no_errors(ast)
        self.assertIsInstance(ast, Program, "Expected Program")
        self.assertEqual(len(ast.declarations), 1, "Expected 1 declaration")
        self.assertIsInstance(ast.declarations[0], TypeDef, "Expected TypeDef")
        self.assertEqual(ast.declarations[0].name, "Circle", "Expected name 'Circle'")
        self.assertIsNotNone(ast.declarations[0].parents, "Expected parents")
        self.assertEqual(ast.declarations[0].parents[0], "Point", "Expected parent 'Point'")
        self.assertEqual(len(ast.declarations[0].members), 1, "Expected 1 member")
        
        # Type with methods
        source = """
        type Calculator {
            add(a: float, b: float) -> float {
                return a + b;
            }
            
            subtract(a: float, b: float) -> float {
                return a - b;
            }
        }
        """
        ast, messages = self.parse_source(source)
        self.assert_no_errors(ast)
        self.assertIsInstance(ast, Program, "Expected Program")
        self.assertEqual(len(ast.declarations), 1, "Expected 1 declaration")
        self.assertIsInstance(ast.declarations[0], TypeDef, "Expected TypeDef")
        self.assertEqual(ast.declarations[0].name, "Calculator", "Expected name 'Calculator'")
        self.assertEqual(len(ast.declarations[0].members), 2, "Expected 2 members")
        self.assertIsInstance(ast.declarations[0].members[0], FunctionDef, "Expected FunctionDef")
        self.assertIsInstance(ast.declarations[0].members[1], FunctionDef, "Expected FunctionDef")

    def test_shard_definition(self):
        """Test parsing shard definitions"""
        source = """
        shard Counter {
            pub count: int = 0;
            
            increment() {
                count = count + 1;
            }
            
            reset() {
                count = 0;
            }
        }
        """
        ast, messages = self.parse_source(source)
        self.assert_no_errors(ast)
        self.assertIsInstance(ast, Program, "Expected Program")
        self.assertEqual(len(ast.declarations), 1, "Expected 1 declaration")
        self.assertIsInstance(ast.declarations[0], ShardDef, "Expected ShardDef")
        self.assertEqual(ast.declarations[0].name, "Counter", "Expected name 'Counter'")
        self.assertEqual(len(ast.declarations[0].members), 3, "Expected 3 members")
        
        # Check field
        self.assertIsInstance(ast.declarations[0].members[0], VariableDef, "Expected VariableDef")
        self.assertEqual(ast.declarations[0].members[0].name, "count", "Expected field name 'count'")
        self.assertIn(TokenTypes.PUB, ast.declarations[0].members[0].modifiers, "Expected public modifier")
        
        # Check methods
        self.assertIsInstance(ast.declarations[0].members[1], FunctionDef, "Expected FunctionDef")
        self.assertEqual(ast.declarations[0].members[1].name, "increment", "Expected method name 'increment'")
        self.assertIsInstance(ast.declarations[0].members[2], FunctionDef, "Expected FunctionDef")
        self.assertEqual(ast.declarations[0].members[2].name, "reset", "Expected method name 'reset'")

    def test_impl_definition(self):
        """Test parsing impl definitions"""
        source = """
        impl Counter for Display {
            render() -> string {
                return "Count: " + count;
            }
        }
        """
        ast, messages = self.parse_source(source)
        self.assert_no_errors(ast)
        self.assertIsInstance(ast, Program, "Expected Program")
        self.assertEqual(len(ast.declarations), 1, "Expected 1 declaration")
        self.assertIsInstance(ast.declarations[0], ImplDef, "Expected ImplDef")
        self.assertEqual(ast.declarations[0].target_type, "Counter", "Expected target_type 'Counter'")
        self.assertEqual(ast.declarations[0].for_type, "Display", "Expected for_type 'Display'")
        self.assertEqual(len(ast.declarations[0].members), 1, "Expected 1 member")
        self.assertIsInstance(ast.declarations[0].members[0], FunctionDef, "Expected FunctionDef")
        self.assertEqual(ast.declarations[0].members[0].name, "render", "Expected method name 'render'")

    def test_function_definition(self):
        """Test parsing function definitions"""
        source = """
        calculate(a: float, b: float, op: string) -> float {
            if (op == "add") {
                return a + b;
            } else {
                if (op == "subtract") {
                    return a - b;
                } else {
                    return 0;
                }
            }
        }
        """
        ast, messages = self.parse_source(source)
        self.assert_no_errors(ast)
        self.assertIsInstance(ast, Program, "Expected Program")
        self.assertEqual(len(ast.declarations), 1, "Expected 1 declaration")
        self.assertIsInstance(ast.declarations[0], FunctionDef, "Expected FunctionDef")
        self.assertEqual(ast.declarations[0].name, "calculate", "Expected name 'calculate'")
        self.assertEqual(len(ast.declarations[0].params), 3, "Expected 3 parameters")
        self.assertEqual(ast.declarations[0].return_type, "float", "Expected return type 'float'")
        
        # Check parameters
        self.assertIsInstance(ast.declarations[0].params[0], Parameter, "Expected Parameter")
        self.assertEqual(ast.declarations[0].params[0].name, "a", "Expected parameter name 'a'")
        self.assertEqual(ast.declarations[0].params[0].param_type, "float", "Expected parameter type 'float'")
        
        self.assertIsInstance(ast.declarations[0].params[1], Parameter, "Expected Parameter")
        self.assertEqual(ast.declarations[0].params[1].name, "b", "Expected parameter name 'b'")
        self.assertEqual(ast.declarations[0].params[1].param_type, "float", "Expected parameter type 'float'")
        
        self.assertIsInstance(ast.declarations[0].params[2], Parameter, "Expected Parameter")
        self.assertEqual(ast.declarations[0].params[2].name, "op", "Expected parameter name 'op'")
        self.assertEqual(ast.declarations[0].params[2].param_type, "string", "Expected parameter type 'string'")

    def test_component_instantiation(self):
        """Test parsing component instantiations"""
        source = "Counter(initial = 5) as myCounter;"
        ast, messages = self.parse_source(source)
        self.assert_no_errors(ast)
        self.assertIsInstance(ast, Program, "Expected Program")
        self.assertEqual(len(ast.declarations), 1, "Expected 1 declaration")
        self.assertIsInstance(ast.declarations[0], ComponentInstantiation, "Expected ComponentInstantiation")
        self.assertEqual(ast.declarations[0].component_type, "Counter", "Expected component_type 'Counter'")
        self.assertEqual(ast.declarations[0].instance_name, "myCounter", "Expected instance_name 'myCounter'")
        self.assertEqual(len(ast.declarations[0].args), 1, "Expected 1 argument")

    def test_complex_program(self):
        """Test parsing a complex program"""
        # Use one of our existing test files
        ast, messages = self.parse_file("tests/test_files/complex.sd")
        self.assert_no_errors(ast)
        self.assertIsInstance(ast, Program, "Expected Program")
        self.assertTrue(len(ast.declarations) > 3, "Expected multiple declarations")
        
        # Check for specific declarations
        type_defs = [d for d in ast.declarations if isinstance(d, TypeDef)]
        self.assertTrue(len(type_defs) >= 1, "Expected at least 1 TypeDef")
        self.assertEqual(type_defs[0].name, "TestType", "Expected type name 'TestType'")
        
        shard_defs = [d for d in ast.declarations if isinstance(d, ShardDef)]
        self.assertTrue(len(shard_defs) >= 1, "Expected at least 1 ShardDef")
        self.assertEqual(shard_defs[0].name, "Counter", "Expected shard name 'Counter'")
        
        impl_defs = [d for d in ast.declarations if isinstance(d, ImplDef)]
        self.assertTrue(len(impl_defs) >= 1, "Expected at least 1 ImplDef")
        self.assertEqual(impl_defs[0].target_type, "Counter", "Expected impl target_type 'Counter'")
        self.assertEqual(impl_defs[0].for_type, "TestType", "Expected impl for_type 'TestType'")
        
        func_defs = [d for d in ast.declarations if isinstance(d, FunctionDef)]
        self.assertTrue(len(func_defs) >= 1, "Expected at least 1 FunctionDef")
        self.assertEqual(func_defs[0].name, "process", "Expected function name 'process'")
        
        comp_insts = [d for d in ast.declarations if isinstance(d, ComponentInstantiation)]
        self.assertTrue(len(comp_insts) >= 2, "Expected at least 2 ComponentInstantiation")
        comp_types = {comp.component_type for comp in comp_insts}
        self.assertIn("Counter", comp_types, "Expected component type 'Counter'")
        self.assertIn("TestType", comp_types, "Expected component type 'TestType'")

        # Log any parser messages
        if messages:
            for msg in messages:
                logging.debug(f"Parser message: {msg}")


if __name__ == "__main__":
    unittest.main() 