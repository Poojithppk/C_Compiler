"""Debug script to analyze Program 4 TAC generation issues."""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator
import json

# Program 4 test code
program4_code = """
hold count = 10;
repeat (count > 0)
{
    show count;
    count = count - 1;
}
"""

print("=" * 70)
print("PROGRAM 4 TAC GENERATION DEBUG")
print("=" * 70)

# Phase 1: Lexical Analysis
print("\n1. LEXICAL ANALYSIS")
print("-" * 70)
lexer = VisualLexicalAnalyzer()
tokens, lex_errors = lexer.analyze(program4_code)
print(f"Tokens generated: {len(tokens)}")
for token in tokens[:20]:  # Show first 20
    print(f"  {token}")

# Phase 2: Syntax Analysis
print("\n2. SYNTAX ANALYSIS")
print("-" * 70)
parser = Parser(tokens)
ast = parser.parse()
print(f"AST generated successfully")

# Print AST structure
def print_ast(node, indent=0):
    prefix = "  " * indent
    if hasattr(node, '__class__'):
        class_name = node.__class__.__name__
        print(f"{prefix}{class_name}")
        
        # Print important attributes
        if hasattr(node, 'name'):
            print(f"{prefix}  name: {node.name}")
        if hasattr(node, 'operator'):
            print(f"{prefix}  operator: {node.operator}")
        
        # Recursively print children
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                print_ast(stmt, indent + 1)
        if hasattr(node, 'body'):
            if isinstance(node.body, list):
                for item in node.body:
                    print_ast(item, indent + 1)
            else:
                print_ast(node.body, indent + 1)
        if hasattr(node, 'condition'):
            print(f"{prefix}  condition:")
            print_ast(node.condition, indent + 2)

print("AST Structure:")
print_ast(ast)

# Phase 3: Semantic Analysis
print("\n3. SEMANTIC ANALYSIS")
print("-" * 70)
semantic_analyzer = SemanticAnalyzer()
success = semantic_analyzer.analyze(ast)
print(f"Semantic analysis: {'SUCCESS' if success else 'FAILED'}")
if not success:
    for error in semantic_analyzer.errors:
        print(f"  Error: {error}")

# Phase 4: Intermediate Code Generation
print("\n4. INTERMEDIATE CODE GENERATION (TAC)")
print("-" * 70)
tac_gen = IntermediateCodeGenerator()
success, tac_code, errors = tac_gen.generate(ast)

print(f"TAC generation: {'SUCCESS' if success else 'FAILED'}")
print(f"Total instructions: {len(tac_code.instructions)}")
print(f"Errors: {len(tac_code.errors)}, Warnings: {len(tac_code.warnings)}")

print("\nTAC Instructions:")
for i, instr in enumerate(tac_code.instructions):
    print(f"{i:2d}: {instr}")

print("\nDetailed Instruction Analysis:")
for i, instr in enumerate(tac_code.instructions):
    print(f"\n{i:2d}: {instr.instruction_type.value}")
    print(f"    label: {instr.label}")
    print(f"    result: {instr.result}")
    print(f"    arg1: {instr.arg1}")
    print(f"    arg2: {instr.arg2}")

print("\n" + "=" * 70)
print("LOOKING FOR ASSIGNMENT TO count")
print("=" * 70)
assign_count = [instr for instr in tac_code.instructions 
                if instr.instruction_type.value == "ASSIGN" and 
                   hasattr(instr.result, 'value') and 
                   instr.result.value == "count"]
print(f"Found {len(assign_count)} ASSIGN instructions to 'count':")
for instr in assign_count:
    print(f"  {instr}")

print("\n" + "=" * 70)
print("LOOKING FOR SUBTRACTION (SUB) INSTRUCTIONS")
print("=" * 70)
sub_instrs = [instr for instr in tac_code.instructions 
              if instr.instruction_type.value == "SUB"]
print(f"Found {len(sub_instrs)} SUB instructions:")
for instr in sub_instrs:
    print(f"  {instr}")

print("\n" + "=" * 70)
print("CHECKING LOOP BODY STATEMENTS IN AST")
print("=" * 70)

# Navigate to while/repeat statement
def find_loop(node):
    if hasattr(node, '__class__'):
        if 'While' in node.__class__.__name__ or 'Repeat' in node.__class__.__name__:
            return node
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                result = find_loop(stmt)
                if result:
                    return result
    return None

loop_node = find_loop(ast)
if loop_node:
    print(f"Loop node found: {loop_node.__class__.__name__}")
    if hasattr(loop_node, 'body'):
        print(f"Loop body type: {type(loop_node.body)}")
        if isinstance(loop_node.body, list):
            print(f"Loop body has {len(loop_node.body)} items")
            for i, item in enumerate(loop_node.body):
                print(f"  {i}: {item.__class__.__name__}")
        else:
            print(f"Loop body object: {loop_node.body.__class__.__name__}")
            if hasattr(loop_node.body, 'statements'):
                print(f"  Contains {len(loop_node.body.statements)} statements")
                for i, stmt in enumerate(loop_node.body.statements):
                    print(f"    {i}: {stmt.__class__.__name__}")
else:
    print("No loop node found in AST!")
