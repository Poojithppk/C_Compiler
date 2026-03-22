"""Debug script to trace ExpressionStatementNode handling."""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator

# Program 4 test code - simpler test
test_code = """
hold count = 10;
repeat (count > 0)
{
    show count;
    count = count - 1;
}
"""

print("=" * 70)
print("TRACING EXPRESSION STATEMENT HANDLING")
print("=" * 70)

lexer = VisualLexicalAnalyzer()
tokens, _ = lexer.analyze(test_code)

parser = Parser(tokens)
ast = parser.parse()

semantic_analyzer = SemanticAnalyzer()
semantic_analyzer.analyze(ast)

# Create TAC generator with tracing
tac_gen = IntermediateCodeGenerator()

# Patch the _visit_ExpressionStatementNode to trace calls
original_visit_expr = tac_gen._visit_ExpressionStatementNode

def traced_visit_expr(node):
    print(f"\n>>> _visit_ExpressionStatementNode called")
    print(f"    node type: {node.__class__.__name__}")
    if hasattr(node, 'expression'):
        print(f"    expression type: {node.expression.__class__.__name__}")
    result = original_visit_expr(node)
    print(f"    result: {result}")
    return result

tac_gen._visit_ExpressionStatementNode = traced_visit_expr

# Also patch _visit_AssignmentNode
original_visit_assign = tac_gen._visit_AssignmentNode

def traced_visit_assign(node):
    print(f"\n>>> _visit_AssignmentNode called")
    if hasattr(node, 'target'):
        target_name = node.target.name if hasattr(node.target, 'name') else "unknown"
        print(f"    target: {target_name}")
    if hasattr(node, 'value'):
        print(f"    value type: {node.value.__class__.__name__}")
    result = original_visit_assign(node)
    print(f"    result: {result}")
    return result

tac_gen._visit_AssignmentNode = traced_visit_assign

# Patch _visit_BlockNode
original_visit_block = tac_gen._visit_BlockNode

def traced_visit_block(node):
    print(f"\n>>> _visit_BlockNode called")
    if hasattr(node, 'statements'):
        print(f"    contains {len(node.statements)} statements")
        for i, stmt in enumerate(node.statements):
            print(f"      {i}: {stmt.__class__.__name__}")
    result = original_visit_block(node)
    return result

tac_gen._visit_BlockNode = traced_visit_block

success, tac_code, errors = tac_gen.generate(ast)

print("\n" + "=" * 70)
print("FINAL TAC OUTPUT")
print("=" * 70)
for i, instr in enumerate(tac_code.instructions):
    print(f"{i:2d}: {instr}")
