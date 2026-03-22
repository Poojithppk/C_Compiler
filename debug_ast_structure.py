#!/usr/bin/env python3
"""Debug script to inspect AST structure for binary expressions."""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser  
from syntax_analysis.ast_printer import ASTPrinter

code = 'hold expr = a * b; show expr;'

lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, _ = lexer.analyze(code)

parser = Parser(tokens)
ast = parser.parse()

# Print AST structure
try:
    printer = ASTPrinter()
    ast_out = printer.print_ast(ast)
    print(ast_out)
except:
    # Fallback simple printer
    def print_node(node, indent=0):
        spaces = "  " * indent
        print(f"{spaces}{type(node).__name__}")
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                print_node(stmt, indent+1)
        if hasattr(node, 'expression'):
            print_node(node.expression, indent+1)  
        if hasattr(node, 'left'):
            print(f"{spaces}  .left:")
            print_node(node.left, indent+2)
        if hasattr(node, 'operator'):
            print(f"{spaces}  .operator: {node.operator}")
        if hasattr(node, 'right'):
            print(f"{spaces}  .right:")
            print_node(node.right, indent+2)
        if hasattr(node, 'value'):
            print(f"{spaces}  .value: {node.value}")
        if hasattr(node, 'name'):
            print(f"{spaces}  .name: {node.name}")
    
    print_node(ast)
