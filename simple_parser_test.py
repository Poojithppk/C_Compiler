#!/usr/bin/env python3
"""Simple test of parser output"""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser

code1 = "result = 0;"
code2 = """result = 0;
if (result < 10) then
    print "Less";
else
    print "More";
end;"""

for label, code in [("SIMPLE", code1), ("IF-ELSE", code2)]:
    print(f"\n{label} TEST:")
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens, _ = lexer.analyze(code)
    print(f"  Tokens: {len(tokens)}")
    
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"  AST type: {type(ast).__name__}")
    print(f"  Statements: {len(ast.statements) if hasattr(ast, 'statements') else 'N/A'}")
    
    # Check for parser errors
    if parser.has_errors():
        print(f"  Parser errors: {parser.get_errors()}")
    else:
        print(f"  No parser errors")
    
    if hasattr(ast, 'statements') and ast.statements:
        for i, stmt in enumerate(ast.statements):
            print(f"    {i}: {type(stmt).__name__}")
