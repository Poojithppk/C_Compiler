#!/usr/bin/env python3
"""
Direct test of semantic analysis pipeline
"""
import sys
import os

# Add src to path to allow absolute imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer

# Sample code
code = """
hold num1 = 5;
hold num2 = 10;
hold total = num1 + num2;
show total;
"""

print("=" * 60)
print("SEMANTIC ANALYSIS PIPELINE TEST")
print("=" * 60)

# Phase 1: Lexical Analysis
print("\n[1] LEXICAL ANALYSIS")
lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, lex_errors = lexer.analyze(code)
print(f"✅ Tokens: {len(tokens)}")
if lex_errors:
    print(f"❌ Errors: {len(lex_errors)}")
    for err in lex_errors:
        print(f"   - {err}")

# Phase 2: Syntax Analysis
print("\n[2] SYNTAX ANALYSIS")
try:
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"✅ AST Generated")
    print(f"   Program node type: {type(ast).__name__}")
    if hasattr(ast, 'statements'):
        print(f"   Statements: {len(ast.statements)}")
except Exception as e:
    print(f"❌ Syntax Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Phase 3: Semantic Analysis
print("\n[3] SEMANTIC ANALYSIS")
try:
    analyzer = SemanticAnalyzer(visual_mode=False)
    success, errors, warnings = analyzer.analyze(ast)
    print(f"✅ Analysis Complete")
    print(f"   Success: {success}")
    print(f"   Errors: {len(errors)}")
    print(f"   Warnings: {len(warnings)}")
    
    if errors:
        print("\n   Errors:")
        for err in errors:
            print(f"   - {err}")
    
    if warnings:
        print("\n   Warnings:")
        for warn in warnings:
            print(f"   - {warn}")
    
    # Display symbol table
    print(f"\n   Symbol Table:")
    sym_table = analyzer.get_symbol_table()
    for scope in sym_table.scopes:
        print(f"   Scope: {scope}")
        for name, symbol in scope.symbols.items():
            print(f"   - {name}: {symbol.kind} ({symbol.type_info})")
    
except Exception as e:
    print(f"❌ Semantic Analysis Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL PHASES COMPLETED SUCCESSFULLY")
print("=" * 60)
