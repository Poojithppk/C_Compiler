#!/usr/bin/env python3
"""
Test script to verify lexical to syntax analysis workflow
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_lexical_to_syntax_workflow():
    """Test the complete workflow from lexical to syntax analysis"""
    print("🔧 Testing Lexical → Syntax Analysis Workflow")
    print("=" * 50)
    
    # Step 1: Test lexical analysis standalone
    print("\n📍 Step 1: Testing Lexical Analysis...")
    
    try:
        from src.lexical_analysis.lexer import VisualLexicalAnalyzer
        
        # Sample NEXUS code
        sample_code = """
        hold x = 42;
        show x;
        func add(a: num, b: num) -> num {
            return a + b;
        }
        """
        
        lexer = VisualLexicalAnalyzer(visual_mode=False)
        tokens, errors = lexer.analyze(sample_code)
        
        print(f"   ✅ Lexical Analysis: {len(tokens)} tokens, {len(errors)} errors")
        
        # Step 2: Test syntax analysis with tokens
        print("\n📍 Step 2: Testing Syntax Analysis with Tokens...")
        
        from src.syntax_analysis.parser import Parser
        
        parser = Parser(tokens, debug_mode=False)
        ast = parser.parse()
        
        print(f"   ✅ Syntax Analysis: AST generated with {len(ast.statements)} statements")
        print(f"   ✅ Parser errors: {len(parser.errors)}")
        
        # Step 3: Test GUI integration
        print("\n📍 Step 3: Testing GUI Integration...")
        
        import tkinter as tk
        from src.syntax_analysis.syntax_gui import SyntaxAnalysisGUI
        
        # Create a temporary root for testing
        test_root = tk.Tk()
        test_root.withdraw()  # Hide the window
        
        syntax_gui = SyntaxAnalysisGUI(test_root)
        
        # Test token loading method
        syntax_gui.load_tokens_from_lexical(tokens, errors)
        
        print(f"   ✅ GUI Integration: {len(syntax_gui.current_tokens)} tokens loaded")
        print(f"   ✅ Lexical errors in GUI: {len(syntax_gui.lexical_errors)}")
        
        test_root.destroy()
        
        print("\n🎉 All tests passed! Workflow is functional.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_lexical_to_syntax_workflow()