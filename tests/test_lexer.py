#!/usr/bin/env python3
"""
Test cases for the Shard lexer.
"""

import unittest
from typing import List, Dict, Any

from src.shard.lexer import Lexer, TokenTypes, Token
from tests.test_framework import ShardTestCase


class LexerTestCase(ShardTestCase):
    """Test case for the lexer component"""

    def test_empty_input(self):
        """Test lexer on empty input"""
        tokens = self.tokenize_source("")
        self.assertEqual(len(tokens), 0, "Empty input should produce no tokens")

    def test_whitespace(self):
        """Test lexer on whitespace input"""
        tokens = self.tokenize_source("  \t\n   \r\n")
        self.assertEqual(len(tokens), 0, "Whitespace should produce no tokens")

    def test_comments(self):
        """Test lexer on comments"""
        tokens = self.tokenize_source("// This is a comment\n// Another comment")
        self.assertEqual(len(tokens), 0, "Comments should produce no tokens")

    def test_keywords(self):
        """Test lexer on language keywords"""
        keywords = {
            "type": TokenTypes.TYPE,
            "shard": TokenTypes.SHARD,
            "impl": TokenTypes.IMPL,
            "for": TokenTypes.FOR,
            "if": TokenTypes.IF,
            "else": TokenTypes.ELSE,
            "while": TokenTypes.WHILE,
            "return": TokenTypes.RETURN,
            "pub": TokenTypes.PUB,
            "priv": TokenTypes.PRIV,
            "internal": TokenTypes.INTERNAL,
            "open": TokenTypes.OPEN,
            "const": TokenTypes.CONST,
            "mut": TokenTypes.MUT,
            "pure": TokenTypes.PURE,
            "impure": TokenTypes.IMPURE,
            "meta": TokenTypes.META,
            "bus": TokenTypes.BUS,
            "on": TokenTypes.ON,
            "as": TokenTypes.AS
        }
        
        for keyword, token_type in keywords.items():
            tokens = self.tokenize_source(keyword)
            self.assertEqual(len(tokens), 1, f"Expected 1 token for '{keyword}'")
            self.assertEqual(tokens[0].type, token_type, f"Expected token type {token_type} for '{keyword}'")
            self.assertEqual(tokens[0].value, keyword, f"Expected token value '{keyword}'")

    def test_identifiers(self):
        """Test lexer on identifiers"""
        identifiers = ["abc", "x", "variable_name", "snake_case", "camelCase", "PascalCase", "_underscore"]
        
        for ident in identifiers:
            tokens = self.tokenize_source(ident)
            self.assertEqual(len(tokens), 1, f"Expected 1 token for '{ident}'")
            self.assertEqual(tokens[0].type, TokenTypes.IDENT, f"Expected token type IDENT for '{ident}'")
            self.assertEqual(tokens[0].value, ident, f"Expected token value '{ident}'")

    def test_literals(self):
        """Test lexer on literal values"""
        literals = {
            "123": (TokenTypes.INTEGER, 123),
            "0": (TokenTypes.INTEGER, 0),
            "3.14": (TokenTypes.FLOAT, 3.14),
            "0.5": (TokenTypes.FLOAT, 0.5),
            '"string"': (TokenTypes.STRING, "string"),
            '"hello world"': (TokenTypes.STRING, "hello world"),
            "true": (TokenTypes.BOOL, True),
            "false": (TokenTypes.BOOL, False)
        }
        
        for literal, (token_type, expected_value) in literals.items():
            tokens = self.tokenize_source(literal)
            self.assertEqual(len(tokens), 1, f"Expected 1 token for '{literal}'")
            self.assertEqual(tokens[0].type, token_type, f"Expected token type {token_type} for '{literal}'")
            self.assertEqual(tokens[0].value, expected_value, f"Expected token value {expected_value} for '{literal}'")

    def test_operators(self):
        """Test lexer on operators"""
        operators = {
            "+": TokenTypes.PLUS,
            "-": TokenTypes.MINUS,
            "*": TokenTypes.TIMES,
            "/": TokenTypes.DIVIDE,
            "=": TokenTypes.ASSIGN,
            "==": TokenTypes.EQ,
            "!=": TokenTypes.NE,
            "<": TokenTypes.LT,
            ">": TokenTypes.GT,
            "<=": TokenTypes.LE,
            ">=": TokenTypes.GE,
            "+=": TokenTypes.PLUS_ASSIGN,
            "-=": TokenTypes.MINUS_ASSIGN,
            "*=": TokenTypes.TIMES_ASSIGN,
            "/=": TokenTypes.DIVIDE_ASSIGN,
            "->": TokenTypes.ARROW
        }
        
        for operator, token_type in operators.items():
            tokens = self.tokenize_source(operator)
            self.assertEqual(len(tokens), 1, f"Expected 1 token for '{operator}'")
            self.assertEqual(tokens[0].type, token_type, f"Expected token type {token_type} for '{operator}'")
            self.assertEqual(tokens[0].value, operator, f"Expected token value '{operator}'")

    def test_punctuation(self):
        """Test lexer on punctuation"""
        punctuation = {
            ";": TokenTypes.SEMICOLON,
            ":": TokenTypes.COLON,
            ",": TokenTypes.COMMA,
            ".": TokenTypes.DOT,
            "(": TokenTypes.LPAREN,
            ")": TokenTypes.RPAREN,
            "{": TokenTypes.LBRACE,
            "}": TokenTypes.RBRACE
        }
        
        for punct, token_type in punctuation.items():
            tokens = self.tokenize_source(punct)
            self.assertEqual(len(tokens), 1, f"Expected 1 token for '{punct}'")
            self.assertEqual(tokens[0].type, token_type, f"Expected token type {token_type} for '{punct}'")
            self.assertEqual(tokens[0].value, punct, f"Expected token value '{punct}'")

    def test_complete_program(self):
        """Test lexer on a complete program"""
        program = """
        // This is a comment
        type Test {
            x: int;
            y: float = 3.14;
            
            init() {
                print("Hello");
            }
        }
        """
        
        tokens = self.tokenize_source(program)
        expected_token_types = [
            TokenTypes.TYPE,
            TokenTypes.IDENT,  # Test
            TokenTypes.LBRACE,
            TokenTypes.IDENT,  # x
            TokenTypes.COLON,
            TokenTypes.IDENT,  # int
            TokenTypes.SEMICOLON,
            TokenTypes.IDENT,  # y
            TokenTypes.COLON,
            TokenTypes.IDENT,  # float
            TokenTypes.ASSIGN,
            TokenTypes.FLOAT,  # 3.14
            TokenTypes.SEMICOLON,
            TokenTypes.IDENT,  # init
            TokenTypes.LPAREN,
            TokenTypes.RPAREN,
            TokenTypes.LBRACE,
            TokenTypes.IDENT,  # print
            TokenTypes.LPAREN,
            TokenTypes.STRING,  # "Hello"
            TokenTypes.RPAREN,
            TokenTypes.SEMICOLON,
            TokenTypes.RBRACE,
            TokenTypes.RBRACE
        ]
        
        self.assertEqual(len(tokens), len(expected_token_types), 
                         "Expected number of tokens doesn't match actual")
        
        for i, (token, expected_type) in enumerate(zip(tokens, expected_token_types)):
            self.assertEqual(token.type, expected_type, 
                             f"Token {i} type mismatch: {token.type} != {expected_type}")


if __name__ == "__main__":
    unittest.main() 