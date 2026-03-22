#!/usr/bin/env python3
"""
Test script for nested if-elif-else code generation
This tests Program 3 variant with nested conditions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import tkinter as tk
from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator
from targets.code_generation_gui import CodeGenerationGUI

# Nested if-elif-else test program
nexus_code = """
hold a = 10;
hold b = 5;
hold c = 3;
hold value = a + b * c;
when (value > 20)
{
    show "Large value";
}
otherwise
{
    when (value > 10)
    {
        show "Medium value";
    }
    otherwise
    {
        show "Small value";
    }
}
"""

print("=" * 70)
print("NESTED IF-ELIF-ELSE TEST PROGRAM")
print("=" * 70)
print("\nNEXUS Code:")
print("-" * 70)
print(nexus_code)
print("-" * 70)

try:
    # Phase 1: Lexical Analysis
    print("\n[PHASE 1] LEXICAL ANALYSIS")
    lexer = VisualLexicalAnalyzer(visual_mode=False, debug_mode=False)
    tokens, lex_errors = lexer.analyze(nexus_code)
    print(f"✓ Generated {len(tokens)} tokens")
    if lex_errors:
        print(f"⚠ {len(lex_errors)} lexical errors detected")
    
    # Phase 2: Syntax Analysis
    print("\n[PHASE 2] SYNTAX ANALYSIS")
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"✓ AST generated successfully")
    
    # Phase 3: Semantic Analysis
    print("\n[PHASE 3] SEMANTIC ANALYSIS")
    semantic = SemanticAnalyzer()
    semantic.analyze(ast)
    print(f"✓ Semantic analysis passed")
    
    # Phase 4: Intermediate Code Generation
    print("\n[PHASE 4] INTERMEDIATE CODE GENERATION (TAC)")
    tac_gen = IntermediateCodeGenerator()
    tac_instructions = tac_gen.generate(ast)
    print(f"✓ Generated {len(tac_instructions)} TAC instructions")
    print("\nTAC Instructions:")
    print("-" * 70)
    for i, instr in enumerate(tac_instructions):
        print(f"{i}: {instr}")
    print("-" * 70)
    
    # Phase 5: Code Generation
    print("\n[PHASE 5] CODE GENERATION")
    
    # Create a tkinter root for CodeGenerationGUI
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    code_gen = CodeGenerationGUI(root)
    code_gen.tac_code = tac_instructions[1]  # The TACCode object is at index 1
    
    # Python
    print("\n>>> PYTHON CODE GENERATION:")
    print("-" * 70)
    python_code = code_gen._generate_python_code()
    print(python_code)
    print("-" * 70)
    
    # C
    print("\n>>> C CODE GENERATION:")
    print("-" * 70)
    c_code = code_gen._generate_c_code()
    print(c_code)
    print("-" * 70)
    
    # Assembly
    print("\n>>> ASSEMBLY CODE GENERATION:")
    print("-" * 70)
    asm_code = code_gen._generate_assembly_code()
    print(asm_code)
    print("-" * 70)
    
    print("\n" + "=" * 70)
    print("TEST COMPLETED")
    print("=" * 70)
    
    root.destroy()  # Clean up
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
