#!/usr/bin/env python3
"""
Test script to verify secure statement parsing fix
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser

def test_secure_parsing():
    """Test the secure statement parsing fix"""
    
    test_cases = [
        ("Secure block syntax", """
secure {
    validate(x > 0);
    show "valid";
}
        """),
        ("Secure statement syntax", """
secure validate(radius > 0);
        """),
        ("Function with secure statement", """
func calculateArea(radius: decimal) -> decimal {
    secure validate(radius > 0);
    return pi * radius ^ 2;
}
        """),
    ]
    
    print("🔧 Testing Secure Statement Parsing")
    print("=" * 50)
    
    for name, source in test_cases:
        print(f"\n📍 {name}")
        print(f"Source: {source.strip()}")
        
        # Step 1: Lexical Analysis
        lexer = VisualLexicalAnalyzer(visual_mode=False)
        tokens, errors = lexer.analyze(source)
        
        print(f"   Tokens: {len(tokens)}")
        print(f"   Lexical errors: {len(errors)}")
        
        if errors:
            print("   ❌ Lexical errors found, skipping")
            continue
        
        # Step 2: Syntax Analysis
        parser = Parser(tokens, debug_mode=False)
        
        try:
            ast = parser.parse()
            
            print(f"   ✅ Parse completed")
            print(f"   Parser errors: {len(parser.errors)}")
            
            if parser.errors:
                print("   Parser errors:")
                for error in parser.errors:
                    print(f"     {error}")
            else:
                print("   🎉 No parser errors!")
                
        except Exception as e:
            print(f"   ❌ Parse failed: {e}")

if __name__ == "__main__":
    test_secure_parsing()