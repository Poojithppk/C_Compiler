#!/usr/bin/env python3
"""Test code generation for Program 2 complex expression."""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser  
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator
from targets.code_generation_gui import CodeGenerationGUI

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

analyzer = SemanticAnalyzer()
analyzer.analyze(ast)

gen = IntermediateCodeGenerator()
success, tac, errors = gen.generate(ast)

print(f"✓ TAC Generation: {len(tac.instructions)} instructions, {len(errors)} errors")

# Create code generator
code_gen = CodeGenerationGUI()
code_gen.tac_code = tac

# Generate Python code
python_code = code_gen._generate_python_code()
print(f"\n=== PYTHON CODE ({len(python_code)} chars) ===")
print(python_code[:500])
if len(python_code) > 500:
    print("...")
    print(python_code[-300:])

# Generate C code
c_code = code_gen._generate_c_code()
print(f"\n=== C CODE ({len(c_code)} chars) ===")
print(c_code[:500])
if len(c_code) > 500:
    print("...")
    print(c_code[-300:])

# Check for undefined temporaries in generated code
import re
undefined = []
all_assigns = re.findall(r'(\w+)\s*=\s', python_code)
all_uses = re.findall(r'[^=]\s*(\w+)[\s;)]', python_code)
for var in all_uses:
    if not var[0].isdigit() and var not in all_assigns:
        undefined.append(var)

if undefined:
    print(f"\n❌ Undefined variables in generated code: {set(undefined)}")
else:
    print(f"\n✅ All generated code looks valid!")
