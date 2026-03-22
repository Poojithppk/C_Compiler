#!/usr/bin/env python3
"""Debug script to inspect complex AST structure."""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser  

code = 'hold expr = (a + b) * c; show expr;'

lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, _ = lexer.analyze(code)

parser = Parser(tokens)
ast = parser.parse()

def print_node(node, indent=0):
    spaces = "  " * indent
    print(f"{spaces}{type(node).__name__}", end="")
    
    if hasattr(node, 'value'):
        print(f" (value={node.value})", end="")
    if hasattr(node, 'name'):
        print(f" (name={node.name})", end="")
    if hasattr(node, 'operator'):
        print(f" (op={node.operator})", end="")
    
    print()
    
    if hasattr(node, 'statements'):
        for stmt in node.statements:
            print_node(stmt, indent+1)
    if hasattr(node, 'expression'):
        print(f"{spaces}  .expression:")
        print_node(node.expression, indent+2)  
    if hasattr(node, 'initializer'):
        print(f"{spaces}  .initializer:")
        print_node(node.initializer, indent+2)
    if hasattr(node, 'left'):
        print(f"{spaces}  .left:")
        print_node(node.left, indent+2)
    if hasattr(node, 'right'):
        print(f"{spaces}  .right:")
        print_node(node.right, indent+2)

print("AST STRUCTURE:")
print_node(ast)
