#!/usr/bin/env python3
"""Test Program 3 (If-Else) with updated control flow code generator"""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator
from targets.code_generation_gui import CodeGenerationGUI

# Program 3: If-Else Statement
program_code = """
result = 0
if (result < 10) then
    print "Less Than Ten"
else
    print "Not Less"
end
"""

print("=" * 60)
print("PROGRAM 3: If-Else Statement")
print("=" * 60)
print(f"Source Code:\n{program_code}\n")

# Phase 1: Lexical Analysis
print("PHASE 1: LEXICAL ANALYSIS")
print("-" * 40)
lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, lex_errors = lexer.analyze(program_code)
if lex_errors:
    print(f"✗ Lexical errors: {len(lex_errors)}")
    for err in lex_errors:
        print(f"  {err}")
    sys.exit(1)
print(f"✓ Tokens generated: {len(tokens)}")
for i, token in enumerate(tokens):
    print(f"  {i}: {token}")

# Phase 2: Syntax Analysis
print("\nPHASE 2: SYNTAX ANALYSIS")
print("-" * 40)
parser = Parser(tokens)
try:
    ast = parser.parse()
    print("✓ AST generated successfully")
    print(f"  Root: {type(ast).__name__}")
    if hasattr(ast, 'statements'):
        for i, stmt in enumerate(ast.statements):
            print(f"    {i}: {type(stmt).__name__}")
except Exception as e:
    print(f"✗ Syntax error: {e}")
    sys.exit(1)

# Phase 3: Semantic Analysis
print("\nPHASE 3: SEMANTIC ANALYSIS")
print("-" * 40)
semantic = SemanticAnalyzer(visual_mode=False)
success, errors, _ = semantic.analyze(ast)
if not success:
    print(f"✗ Semantic errors: {len(errors)}")
    for err in errors:
        print(f"  {err}")
    sys.exit(1)
print("✓ Semantic analysis successful")

# Phase 4: Intermediate Code Generation
print("\nPHASE 4: INTERMEDIATE CODE GENERATION")
print("-" * 40)
try:
    tac_gen = IntermediateCodeGenerator(visual_mode=False)
    success, tac_code, _ = tac_gen.generate(ast)
    if not success or not tac_code:
        print("✗ TAC generation failed")
        print(f"  Success: {success}")
        print(f"  TAC code object: {tac_code}")
        if tac_code:
            print(f"  Has instructions attr: {hasattr(tac_code, 'instructions')}")
            if hasattr(tac_code, 'instructions'):
                print(f"  Instructions: {tac_code.instructions}")
        sys.exit(1)
    
    if not tac_code.instructions:
        print(f"⚠️ TAC has NO instructions (empty)")
        print(f"  TAC object type: {type(tac_code)}")
        print(f"  TAC object attributes: {dir(tac_code)}")
    else:
        print(f"✓ TAC generated with {len(tac_code.instructions)} instructions")
        for i, instr in enumerate(tac_code.instructions):
            print(f"  {i}: {instr}")
except Exception as e:
    print(f"✗ TAC generation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Phase 5: Code Generation
print("\nPHASE 5: CODE GENERATION")
print("-" * 40)
try:
    # Check if we have any TAC instructions
    if not tac_code.instructions:
        print("⚠️ Skipping code generation - no TAC instructions")
        sys.exit(1)
    
    code_gen = CodeGenerationGUI(root=None)
    code_gen.tac_code = tac_code
    
    # Generate Python code
    python_code = code_gen._generate_python_code()
    print("✓ Python code generated:")
    print(python_code)
    print("\n" + "=" * 60)
    print("EXPECTED OUTPUT:")
    print("Less Than Ten")
    print("=" * 60)
except Exception as e:
    print(f"✗ Code generation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
