#!/usr/bin/env python3
"""Debug code generation issues."""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser  
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator

code = '''hold a = 5;
hold b = 3;
hold c = 8;
hold d = 2;
hold e = 7;
hold f = 4;
hold g = 6;
hold h = 9;
hold i = 10;
hold j = 11;
hold expr = ((a + b * c - d) * (e + f * g - h)) + (i * j - a * b + c * d) - (e + f + g) * (h + i * (j + a * (b + c * (d - e))));
show expr;'''

lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, _ = lexer.analyze(code)

parser = Parser(tokens)
ast = parser.parse()

gen = IntermediateCodeGenerator()
success, tac, errors = gen.generate(ast)

print(f"TAC Generation: Success={success}, Errors={len(errors)}")
if errors:
    print("\nErrors:")
    for err in errors[:10]:
        print(f"  - {err}")

print(f"\n\nAll {len(tac.instructions)} TAC Instructions:")
for i, instr in enumerate(tac.instructions):
    print(f"{i:2d}: {instr}")

# Check for undefined temp usage
print("\n\nChecking for undefined temporaries:")
defined_temps = set()
undefined_usage = []

for i, instr in enumerate(tac.instructions):
    s = str(instr)
    # Extract result (defined)
    if "t=" in s:
        for part in s.split():
            if part.startswith("t="):
                temp = part[2:]
                defined_temps.add(temp)
    
    # Extract usage  
    for part in s.split():
        if part.startswith("a1=t") or part.startswith("a2=t"):
            temp = part[3:]  # Get temp name
            if temp not in defined_temps:
                undefined_usage.append(f"Instr {i}: {s} uses undefined temp {temp}")

if undefined_usage:
    print(f"Found {len(undefined_usage)} undefined usages:")
    for undef in undefined_usage[:10]:
        print(f"  {undef}")
else:
    print("No undefined temporaries found ✓")
