#!/usr/bin/env python3
"""
Debug parser output
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from syntax_analysis.ast_printer import ASTPrinter

# Sample code
code = """
hold num1 = 5;
hold num2 = 10;
hold total = num1 + num2;
show total;
"""

print("Input code:")
print(code)
print("=" * 60)

# Lexical Analysis
lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, lex_errors = lexer.analyze(code)

print(f"\nTokens generated: {len(tokens)}")
for i, token in enumerate(tokens[:15]):  # Show first 15
    print(f"  {i}: {token.token_type.name:15} '{token.lexeme}'")

print("\n" + "=" * 60)

# Syntax Analysis
parser = Parser(tokens, debug_mode=True)
ast = parser.parse()

print("\nAST Structure:")
print(f"  Root node type: {type(ast).__name__}")
print(f"  Statements: {len(ast.statements)}")

if ast.statements:
    print("\nStatement details:")
    for i, stmt in enumerate(ast.statements):
        print(f"  [{i}] {type(stmt).__name__}")
        if hasattr(stmt, 'name'):
            print(f"      name: {stmt.name}")
        if hasattr(stmt, 'initializer'):
            print(f"      initializer: {type(stmt.initializer).__name__ if stmt.initializer else 'None'}")
        if hasattr(stmt, 'expression'):
            print(f"      expression: {type(stmt.expression).__name__ if stmt.expression else 'None'}")

print("\n" + "=" * 60)
print("✅ Debug complete")
