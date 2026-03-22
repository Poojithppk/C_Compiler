#!/usr/bin/env python3
"""Debug string literal values in AST."""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser  

code = 'show "Greater";'

lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, _ = lexer.analyze(code)

print(f"Token values:")
for t in tokens:
    if hasattr(t, 'value'):
        print(f"  {t.type}: value={repr(t.value)}")

parser = Parser(tokens)
ast = parser.parse()

# Print AST structure with details
def print_ast(node, indent=0):
    spaces = "  " * indent
    print(f"{spaces}{type(node).__name__}", end="")
    if hasattr(node, 'value'):
        print(f" value={repr(node.value)}", end="")
    if hasattr(node, 'expression'):
        print()
        print(f"{spaces}  .expression:")
        print_ast(node.expression, indent+2)
    elif hasattr(node, 'statements'):
        print()
        for stmt in node.statements:
            print_ast(stmt, indent+1)
    else:
        print()

print("\nAST:")
print_ast(ast)

