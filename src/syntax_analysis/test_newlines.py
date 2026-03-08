#!/usr/bin/env python3
"""
Test script to verify newline handling in parser
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from syntax_analysis.ast_printer import ASTPrinter

def test_newlines():
    """Test various constructs with newlines"""
    test_cases = [
        ("Multi-line variable declarations", """
hold x = 42;
hold y = 24;
show x;
        """),
        ("Function with newlines", """
func add(a: num, b: num) -> num {
    return a + b;
}
        """),
        ("Complex program", """
hold x = 10;

func calculate(val: num) -> num {
    hold result = val * 2;
    return result;
}

hold answer = calculate(x);
show answer;
        """),
    ]
    
    for name, source in test_cases:
        print(f"\n=== {name} ===")
        print(f"Source code:\n{source}")
        
        # Tokenize
        lexer = VisualLexicalAnalyzer(visual_mode=False)
        tokens, errors = lexer.analyze(source)
        
        print(f"Tokens generated: {len(tokens)}")
        print(f"Lexical errors: {len(errors)}")
        
        if errors:
            print("Lexer errors found, skipping syntax analysis")
            continue
        
        # Parse
        parser = Parser(tokens, debug_mode=False)
        try:
            ast = parser.parse()
            print(f"✅ Parse successful!")
            print(f"Parser errors: {len(parser.errors)}")
            
            if parser.errors:
                print("Parser errors:")
                for error in parser.errors:
                    print(f"  {error}")
            else:
                print("🎉 No parser errors!")
                
        except Exception as e:
            print(f"❌ Parse failed: {e}")

if __name__ == "__main__":
    test_newlines()