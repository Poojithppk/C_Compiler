#!/usr/bin/env python3
"""
Simple test script to debug syntax analysis
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.lexical_analysis.lexer import VisualLexicalAnalyzer
from src.syntax_analysis.parser import Parser
from src.syntax_analysis.ast_printer import ASTPrinter

# Simple test
def test_simple_literal():
    print("=== Testing Simple Literal ===")
    source_code = 'show 42;'
    
    # Tokenize
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens, errors = lexer.analyze(source_code)
    
    print(f"Tokens: {[t.token_type.name for t in tokens]}")
    
    if errors:
        print(f"Lexer errors: {errors}")
        return
    
    # Parse
    parser = Parser(tokens, debug_mode=True)
    try:
        ast = parser.parse()
        print("Parse successful!")
        
        # Print AST
        printer = ASTPrinter()
        ast_str = printer.print_ast(ast)
        print("\nAST:")
        print(ast_str)
        
    except Exception as e:
        print(f"Parse failed: {e}")
        import traceback
        traceback.print_exc()

def test_simple_assignment():
    print("\n=== Testing Simple Assignment ===")
    source_code = 'x = 42;'
    
    # Tokenize
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens, errors = lexer.analyze(source_code)
    
    print(f"Tokens: {[t.token_type.name for t in tokens]}")
    
    if errors:
        print(f"Lexer errors: {errors}")
        return
    
    # Parse
    parser = Parser(tokens, debug_mode=True)
    try:
        ast = parser.parse()
        print("Parse successful!")
        
        # Print AST
        printer = ASTPrinter()
        ast_str = printer.print_ast(ast)
        print("\nAST:")
        print(ast_str)
        
    except Exception as e:
        print(f"Parse failed: {e}")
        import traceback
        traceback.print_exc()

def test_simple_function():
    print("\n=== Testing Simple Function ===")
    source_code = '''
    func add(a: num, b: num) -> num {
        return a + b;
    }
    '''
    
    # Tokenize
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens, errors = lexer.analyze(source_code)
    
    print(f"Token count: {len(tokens)}")
    
    if errors:
        print(f"Lexer errors: {errors}")
        return
    
    # Parse
    parser = Parser(tokens, debug_mode=True)
    try:
        ast = parser.parse()
        print("Parse successful!")
        
        # Print AST
        printer = ASTPrinter()
        ast_str = printer.print_ast(ast)
        print("\nAST:")
        print(ast_str)
        
    except Exception as e:
        print(f"Parse failed: {e}")
        import traceback
        traceback.print_exc()

def test_variable_declaration():
    print("\n=== Testing Variable Declaration ===")
    source_code = 'hold x = 42;'
    
    # Tokenize
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens, errors = lexer.analyze(source_code)
    
    print(f"Tokens: {[t.token_type.name for t in tokens]}")
    
    if errors:
        print(f"Lexer errors: {errors}")
        return
    
    # Parse
    parser = Parser(tokens, debug_mode=True)
    try:
        ast = parser.parse()
        print("Parse successful!")
        
        # Print AST
        printer = ASTPrinter()
        ast_str = printer.print_ast(ast)
        print("\nAST:")
        print(ast_str)
        
    except Exception as e:
        print(f"Parse failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_literal()
    test_simple_assignment()
    test_variable_declaration()
    test_simple_function()