#!/usr/bin/env python3
"""Debug script to inspect AST structure and TAC generation for Program 3"""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator

program_code = """
result = 0
if (result < 10) then
    print "Less Than Ten"
else
    print "Not Less"
end
"""

# Phase 1: Lexical Analysis  
print("PHASE 1: LEXICAL")
lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, lex_errors = lexer.analyze(program_code)
print(f"✓ {len(tokens)} tokens")

# Phase 2: Syntax Analysis
print("\nPHASE 2: SYNTAX")
parser = Parser(tokens)
ast = parser.parse()
print(f"✓ AST generated")

# Phase 3: Semantic Analysis
print("\nPHASE 3: SEMANTIC")
from semantic_analysis.semantic import SemanticAnalyzer
semantic = SemanticAnalyzer(visual_mode=False)
success, errors, _ = semantic.analyze(ast)
print(f"✓ Semantic analysis passed: {success}")

# Phase 4: Intermediate Code
print("\nPHASE 4: TAC GENERATION")
print("-" * 40)

# Inspect AST before TAC generation
def inspect_node(node, depth=0):
    indent = "  " * depth
    node_type = type(node).__name__
    print(f"{indent}{node_type}", end="")
    
    # Print key attributes
    attrs = []
    if hasattr(node, 'value'):
        attrs.append(f"value={node.value}")
    if hasattr(node, 'operator'):
        attrs.append(f"op={node.operator}")
    
    if attrs:
        print(f" ({', '.join(attrs)})\n", end="")
    else:
        print()
    
    # Recursively inspect children
    if hasattr(node, 'statements') and isinstance(node.statements, (list, tuple)):
        for stmt in node.statements:
            inspect_node(stmt, depth + 1)
    if hasattr(node, 'condition'):
        print(f"{indent}[condition]:")
        inspect_node(node.condition, depth + 1)
    if hasattr(node, 'then_branch'):
        print(f"{indent}[then]:")
        if hasattr(node.then_branch, 'statements'):
            for stmt in node.then_branch.statements:
                inspect_node(stmt, depth + 1)
        else:
            inspect_node(node.then_branch, depth + 1)
    if hasattr(node, 'else_branch') and node.else_branch:
        print(f"{indent}[else]:")
        if hasattr(node.else_branch, 'statements'):
            for stmt in node.else_branch.statements:
                inspect_node(stmt, depth + 1)
        else:
            inspect_node(node.else_branch, depth + 1)
    if hasattr(node, 'left'):
        print(f"{indent}[left]:")
        inspect_node(node.left, depth + 1)
    if hasattr(node, 'right'):
        print(f"{indent}[right]:")
        inspect_node(node.right, depth + 1)
    if hasattr(node, 'expression') and not hasattr(node, 'statements'):
        print(f"{indent}[expr]:")
        inspect_node(node.expression, depth + 1)

print("\nAST Structure:")
inspect_node(ast)

# Only generate TAC if AST looks good
print("\nGenerating TAC...")
tac_gen = IntermediateCodeGenerator(visual_mode=False)
success, tac_code, errors = tac_gen.generate(ast)

print(f"TAC Generation Result:")
print(f"  Success: {success}")
print(f"  Errors: {errors}")
print(f"  Instructions: {len(tac_code.instructions)}")

if tac_code.instructions:
    print("\nTAC Instructions:")
    for i, instr in enumerate(tac_code.instructions):
        print(f"  {i}: {instr}")
else:
    print("\n⚠️  No TAC instructions generated!")
    print(f"  TAC Code object type: {type(tac_code)}")
    print(f"  TAC has errors: {len(tac_code.errors) > 0}")
    if tac_code.errors:
        print(f"  Errors: {tac_code.errors}")
