#!/usr/bin/env python3
"""
Test script to specifically verify the original newline parsing error is fixed
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser

def test_original_error():
    """Test the exact code that was causing the original parsing errors"""
    
    # This is similar to the sample code that was causing the newline errors
    problematic_code = """func calculateArea(radius: decimal) -> decimal {
    secure validate(radius > 0);
    return pi * radius ^ 2;
}"""
    
    print("🔧 Testing Original Newline Error Code")
    print("=" * 50)
    print(f"Source:\n{problematic_code}")
    print()
    
    # Step 1: Lexical Analysis
    print("📍 Step 1: Lexical Analysis")
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens, errors = lexer.analyze(problematic_code)
    
    print(f"   Tokens generated: {len(tokens)}")
    print(f"   Lexical errors: {len(errors)}")
    
    # Check for newline tokens
    newline_count = sum(1 for token in tokens if token.token_type.name == 'NEWLINE')
    print(f"   Newline tokens found: {newline_count}")
    
    if errors:
        print("❌ Lexical errors found:")
        for error in errors:
            print(f"   {error}")
        return False
    
    # Step 2: Syntax Analysis
    print("\n📍 Step 2: Syntax Analysis")
    parser = Parser(tokens, debug_mode=False)
    
    try:
        ast = parser.parse()
        
        print(f"   ✅ Parse completed")
        print(f"   Parser errors: {len(parser.errors)}")
        
        if parser.errors:
            print("   Parser errors found:")
            for error in parser.errors:
                print(f"     {error}")
            
            # Check if any are newline-related
            newline_errors = [err for err in parser.errors if "Unexpected token '\\n'" in str(err)]
            if newline_errors:
                print(f"   ❌ Found {len(newline_errors)} newline-related errors (STILL BROKEN)")
                return False
            else:
                print("   ✅ No newline-related errors (FIXED)")
                return True
        else:
            print("   🎉 No parser errors at all! (FULLY FIXED)")
            return True
            
    except Exception as e:
        print(f"   ❌ Parse failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_original_error()
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: Original newline parsing errors are FIXED!")
    else:
        print("❌ FAILURE: Newline parsing errors still exist")
    print("=" * 50)