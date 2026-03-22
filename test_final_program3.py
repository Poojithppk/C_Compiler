#!/usr/bin/env python3
"""Test that control flow code generation works correctly"""

import sys
import os
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator
import tkinter as tk
from targets.code_generation_gui import CodeGenerationGUI

# Program 3
program = """hold num1 = 20;
hold num2 = 10;

when (num1 > num2)
{
    show "Greater";
}
otherwise
{
    show "Smaller";
}"""

print("=" * 70)
print("Program 3: If-Else Conditional - Full Pipeline Test")
print("=" * 70)

# Phases 1-4
lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, _ = lexer.analyze(program)

parser = Parser(tokens)
ast = parser.parse()

semantic = SemanticAnalyzer(visual_mode=False)
semantic.analyze(ast)

tac_gen = IntermediateCodeGenerator(visual_mode=False)
success, tac_code, _ = tac_gen.generate(ast)

print(f"\nTAC Instructions: {len(tac_code.instructions)}")
for i, instr in enumerate(tac_code.instructions):
    print(f"  {i}: {instr}")

# Create a minimal Tkinter window to satisfy CodeGenerationGUI
root = tk.Tk()
root.withdraw()  # Hide the window

try:
    # Create code generator
    code_gen = CodeGenerationGUI(root=root)
    code_gen.tac_code = tac_code
    
    # Generate Python code
    python_code = code_gen._generate_python_code()
    
    print("\n" + "=" * 70)
    print("Generated Python Code:")
    print("=" * 70)
    print(python_code)
    
    # Check if output is correct
    print("\n" + "=" * 70)
    print("VALIDATION:")
    print("=" * 70)
    
    checks = [
        ("Has if statement", "if num1 > num2:" in python_code),
        ("Has proper if-indent", "        print(\"Greater\")" in python_code),
        ("Has else statement", "    else:" in python_code),
        ("Has proper else-indent", "        print(\"Smaller\")" in python_code),
        ("Not both prints outside", "    print(\"Smaller\")\n" not in python_code.replace("        print(\"Smaller\")", "")),
    ]
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
    
    all_pass = all(r for _, r in checks)
    print(f"\n{'='*70}")
    if all_pass:
        print("✅ ALL CHECKS PASSED - Control flow code generation working correctly!")
    else:
        print("❌ Some checks failed - see above")
    print("="*70)

finally:
    root.destroy()
