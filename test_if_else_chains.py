#!/usr/bin/env python3
"""
Test if-elif-else chain parsing in NEXUS compiler
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer

# Test 1: Simple if-else
print("=" * 60)
print("[TEST 1] Simple if-else")
print("=" * 60)

code1 = """
hold x = 10;
when (x > 5)
    show x;
otherwise
    show 0;
"""

try:
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens, lex_errors = lexer.analyze(code1)
    parser = Parser(tokens)
    ast = parser.parse()
    print("[SUCCESS] if-else parsed correctly")
except Exception as e:
    print(f"[ERROR] Failed: {e}")

# Test 2: if-elif-else chain
print("\n" + "=" * 60)
print("[TEST 2] if-elif-else chain")
print("=" * 60)

code2 = """
hold x = 5;
when (x > 10)
    show 1;
otherwise when (x > 5)
    show 2;
otherwise
    show 3;
"""

try:
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens, lex_errors = lexer.analyze(code2)
    
    if lex_errors:
        print(f"[ERROR] Lexical errors: {len(lex_errors)}")
        for err in lex_errors:
            print(f"  {err}")
    else:
        print(f"[INFO] Tokens: {len(tokens)}")
        parser = Parser(tokens)
        ast = parser.parse()
        print("[SUCCESS] if-elif-else chain parsed correctly")
except Exception as e:
    print(f"[ERROR] Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Multiple elif clauses
print("\n" + "=" * 60)
print("[TEST 3] Multiple elif clauses")
print("=" * 60)

code3 = """
hold grade = 85;
when (grade >= 90)
    show 1;
otherwise when (grade >= 80)
    show 2;
otherwise when (grade >= 70)
    show 3;
otherwise
    show 4;
"""

try:
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens, lex_errors = lexer.analyze(code3)
    
    if lex_errors:
        print(f"[ERROR] Lexical errors: {len(lex_errors)}")
    else:
        parser = Parser(tokens)
        ast = parser.parse()
        print("[SUCCESS] Multiple elif clauses parsed correctly")
except Exception as e:
    print(f"[ERROR] Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Nested if-else
print("\n" + "=" * 60)
print("[TEST 4] Nested if-else")
print("=" * 60)

code4 = """
hold x = 10;
hold y = 20;
when (x > 5)
    when (y > 15)
        show 1;
    otherwise
        show 2;
otherwise
    show 3;
"""

try:
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens, lex_errors = lexer.analyze(code4)
    
    if lex_errors:
        print(f"[ERROR] Lexical errors: {len(lex_errors)}")
    else:
        parser = Parser(tokens)
        ast = parser.parse()
        print("[SUCCESS] Nested if-else parsed correctly")
except Exception as e:
    print(f"[ERROR] Failed: {e}")

print("\n" + "=" * 60)
print("[INFO] IF-ELSE CHAIN TESTING COMPLETE")
print("=" * 60)
