#!/usr/bin/env python3
"""Test if the parser works with a simpler if-else structure"""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser

# Try different versions of the if-else code
test_cases = [
    # Original 
    """
result = 0
if (result < 10) then
    print "Less Than Ten"
else
    print "Not Less"
end
""",
    # Without leading newline
    """result = 0
if (result < 10) then
    print "Less Than Ten"
else
    print "Not Less"
end""",
    # Simple assignment only
    """result = 0""",
    # Simple if-else without assignment first
    """if (5 < 10) then
    print "Yes"
else
    print "No"
end"""
]

for test_idx, code in enumerate(test_cases):
    print(f"\n{'='*60}")
    print(f"TEST CASE {test_idx + 1}")
    print(f"{'='*60}")
    print("Code:")
    print(code)
    print("\nParsing...")
    
    try:
        lexer = VisualLexicalAnalyzer(visual_mode=False)
        tokens, errors = lexer.analyze(code)
        
        if errors:
            print(f"  ✗ Lexical errors: {errors}")
            continue
            
        print(f"  ✓ {len(tokens)} tokens generated")
        
        # Show first few tokens
        print("  Tokens (first 10):")
        for i, tok in enumerate(tokens[:10]):
            print(f"    {i}: {tok.type.name} = {repr(tok.value)}")
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        if hasattr(ast, 'statements') and ast.statements:
            print(f"  ✓ {len(ast.statements)} statements parsed")
            for i, stmt in enumerate(ast.statements[:3]):
                print(f"    {i}: {type(stmt).__name__}")
        else:
            print(f"  ✗ No statements parsed (empty)")
            
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        import traceback
        traceback.print_exc()
