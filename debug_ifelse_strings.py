#!/usr/bin/env python3
"""Debug if-else string handling."""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser  
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator

code = '''hold num1 = 20;
hold num2 = 10;
when (num1 > num2)
    show "Greater";
otherwise
    show "Smaller";'''

lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, _ = lexer.analyze(code)

parser = Parser(tokens)
ast = parser.parse()

gen = IntermediateCodeGenerator()
success, tac, errors = gen.generate(ast)

print(f"TAC Instructions ({len(tac.instructions)}):")
for i, instr in enumerate(tac.instructions):
    print(f"{i}: {instr}")

print(f"\nErrors: {len(errors)}")
for err in errors:
    print(f"  - {err}")
