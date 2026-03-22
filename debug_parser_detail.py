#!/usr/bin/env python3
"""Debug parser output in detail"""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser

program_code = """
result = 0
if (result < 10) then
    print "Less Than Ten"
else
    print "Not Less"
end
"""

# Lex
lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, _ = lexer.analyze(program_code)

# Parse
parser = Parser(tokens)
ast = parser.parse()

# Detailed inspection
print("AST Type:", type(ast).__name__)
print("AST Dir:", [x for x in dir(ast) if not x.startswith('_')])
print("\nAST Attributes:")
for attr in dir(ast):
    if not attr.startswith('_'):
        try:
            val = getattr(ast, attr)
            if not callable(val):
                print(f"  {attr}: {val}")
        except:
            pass

if hasattr(ast, 'statements'):
    print(f"\nstatements: {ast.statements}")
    print(f"statements type: {type(ast.statements)}")
    print(f"statements length: {len(ast.statements) if ast.statements else 'None'}")
    
    if ast.statements:
        for i, stmt in enumerate(ast.statements):
            print(f"\n  Statement {i}: {type(stmt).__name__}")
            print(f"    Attributes: {[x for x in dir(stmt) if not x.startswith('_')]}")
