#!/usr/bin/env python3
"""
Quick test of the secure parsing fix
"""

import sys
sys.path.append('D:\\my projects\\C_Compiler\\src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser

# Test the exact problematic code
source = """func calculateArea(radius: decimal) -> decimal {
    secure validate(radius > 0);
    return pi * radius ^ 2;
}"""

print("Testing secure statement parsing fix...")
print(f"Source:\n{source}")
print()

# Lexical analysis
lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, errors = lexer.analyze(source)
print(f"Tokens: {len(tokens)}, Errors: {len(errors)}")

# Syntax analysis
parser = Parser(tokens, debug_mode=False)
try:
    ast = parser.parse()
    print(f"✅ Parse successful!")
    print(f"Parser errors: {len(parser.errors)}")
    
    if parser.errors:
        print("Errors:")
        for error in parser.errors:
            print(f"  {error}")
    else:
        print("🎉 No errors! Fix successful!")
        
except Exception as e:
    print(f"❌ Parse failed: {e}")