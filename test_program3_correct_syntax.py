#!/usr/bin/env python3
"""Test Program 3 with correct NEXUS syntax"""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator
from targets.code_generation_gui import CodeGenerationGUI

# Program 3 with correct NEXUS syntax
program_code = """hold num1 = 20;
hold num2 = 10;

when (num1 > num2)
{
    show "Greater";
}
otherwise
{
    show "Smaller";
}"""

print("=" * 60)
print("PROGRAM 3: If-Else Conditional")
print("=" * 60)
print(f"Source Code:\n{program_code}\n")

# Phase 1: Lexical Analysis
print("PHASE 1: LEXICAL ANALYSIS")
print("-" * 40)
lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, lex_errors = lexer.analyze(program_code)
if lex_errors:
    print(f"✗ Lexical errors: {lex_errors}")
    sys.exit(1)
print(f"✓ Tokens generated: {len(tokens)}")

# Phase 2: Syntax Analysis
print("\nPHASE 2: SYNTAX ANALYSIS")
print("-" * 40)
parser = Parser(tokens)
ast = parser.parse()
if parser.has_errors():
    print(f"✗ Parser errors: {parser.get_errors()}")
    sys.exit(1)
print("✓ AST generated successfully")
print(f"  Statements: {len(ast.statements) if hasattr(ast, 'statements') else 0}")

# Phase 3: Semantic Analysis
print("\nPHASE 3: SEMANTIC ANALYSIS")
print("-" * 40)
semantic = SemanticAnalyzer(visual_mode=False)
success, errors, _ = semantic.analyze(ast)
if not success:
    print(f"✗ Semantic errors: {errors}")
    sys.exit(1)
print("✓ Semantic analysis successful")

# Phase 4: Intermediate Code Generation
print("\nPHASE 4: INTERMEDIATE CODE GENERATION")
print("-" * 40)
tac_gen = IntermediateCodeGenerator(visual_mode=False)
success, tac_code, _ = tac_gen.generate(ast)
if not success or not tac_code.instructions:
    print("✗ TAC generation failed or empty")
    sys.exit(1)
print(f"✓ TAC generated with {len(tac_code.instructions)} instructions")
for i, instr in enumerate(tac_code.instructions):
    print(f"  {i}: {instr}")

# Phase 5: Code Generation
print("\nPHASE 5: CODE GENERATION")
print("-" * 40)
try:
    # Create a complete mock object for CodeGenerationGUI
    class MockRoot:
        def __getattr__(self, name):
            # Return a no-op lambda for any method call
            return lambda *args, **kwargs: None
    
    code_gen = CodeGenerationGUI(root=MockRoot())
    code_gen.tac_code = tac_code
    
    python_code = code_gen._generate_python_code()
    print("✓ Python code generated:")
    print(python_code)
except Exception as e:
    print(f"✗ Code generation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("EXPECTED OUTPUT:")
print("Greater")
print("=" * 60)
