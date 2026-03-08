#!/usr/bin/env python3
"""
Targeted test script to verify AST node constructor fixes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from syntax_analysis.ast_printer import ASTPrinter

def test_constructs():
    """Test various constructs to verify AST node constructors work"""
    test_cases = [
        ("Simple assignment", "x = 42;"),
        ("Variable declaration", "hold x = 42;"),
        ("Print statement", "show 'hello';"),
        ("Multiple statements", "x = 10; y = 20; show x;"),
    ]
    
    for name, source in test_cases:
        print(f"\n=== {name} ===")
        print(f"Source: {source}")
        
        # Tokenize
        lexer = VisualLexicalAnalyzer(visual_mode=False)
        tokens, errors = lexer.analyze(source)
        
        if errors:
            print(f"❌ Lexer errors: {errors}")
            continue
        
        # Parse
        parser = Parser(tokens, debug_mode=False)
        try:
            ast = parser.parse()
            if parser.errors:
                print(f"⚠️  Parse warnings: {len(parser.errors)} errors")
                for error in parser.errors[:3]:  # Show first 3 errors
                    print(f"    {error}")
            else:
                print("✅ Parse successful!")
            
            # Print AST
            if ast and ast.statements:
                printer = ASTPrinter()
                ast_str = printer.print_ast(ast)
                print("AST:")
                print(ast_str)
            else:
                print("⚠️  No statements parsed")
                
        except Exception as e:
            print(f"❌ Parse failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_constructs()