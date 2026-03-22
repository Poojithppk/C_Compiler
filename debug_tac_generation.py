#!/usr/bin/env python3
"""
Debug Intermediate Code Generation for if-else and loops
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator


def debug_tac(name: str, code: str):
    """Debug TAC generation for a code snippet."""
    print(f"\n{'='*70}")
    print(f"[DEBUG] {name}")
    print(f"{'='*70}\n")
    print(f"[CODE]\n{code}\n")
    
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens, lex_errors = lexer.analyze(code)
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    analyzer = SemanticAnalyzer(visual_mode=False)
    analyzer.analyze(ast)
    
    tac_gen = IntermediateCodeGenerator(visual_mode=False)
    success, tac_code, errors = tac_gen.generate(ast)
    
    print(f"[AST] {type(ast).__name__}")
    if hasattr(ast, 'statements'):
        for i, stmt in enumerate(ast.statements):
            print(f"  Statement {i}: {type(stmt).__name__}")
            if hasattr(stmt, 'condition'):
                print(f"    Has condition: {hasattr(stmt, 'condition')}")
            if hasattr(stmt, 'then_branch'):
                print(f"    Has then_branch: {hasattr(stmt, 'then_branch')}")
            if hasattr(stmt, 'else_branch'):
                print(f"    Has else_branch: {hasattr(stmt, 'else_branch')}")
    
    print(f"\n[TAC INSTRUCTIONS] Total: {len(tac_code.instructions)}")
    for i, instr in enumerate(tac_code.instructions):
        print(f"  {i}: {instr.instruction_type.value:15} | {instr}")
    
    print(f"\n[SUMMARY]")
    print(f"  Instructions: {len(tac_code.instructions)}")
    print(f"  Labels created: {tac_code.label_counter}")
    print(f"  Temporaries: {tac_code.temp_counter}")
    print(f"  Errors: {len(errors)}")


# Test cases
debug_tac("IF-ELSE Statement", """hold x = 10;
when (x > 5)
    show x;
otherwise
    show 0;""")

debug_tac("WHILE Loop", """hold count = 5;
repeat (count > 0)
{
    show count;
    count = count - 1;
}""")

debug_tac("IF-ELIF-ELSE", """hold grade = 85;
when (grade >= 90)
    show 1;
otherwise when (grade >= 80)
    show 2;
otherwise
    show 3;""")
