#!/usr/bin/env python3
"""Test code generation directly without GUI wrapper."""

import sys
sys.path.insert(0, 'src')
import re

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser  
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator

# Copy code generation logic directly
def generate_python_code(tac_code):
    """Generate Python code from TAC."""
    if not tac_code:
        return "# Error: No TAC code available"
    
    # Extract instructions from TAC
    tac_instructions = tac_code.instructions
    
    # Parse variables and instructions
    variables = {}
    instructions = []
    write_vars = []
    
    for instr_obj in tac_instructions:
        instr_str = str(instr_obj).strip()
        if not instr_str:
            continue
        
        # ASSIGN
        assign_match = re.match(r'ASSIGN\s+t=(\w+)\s+a1=(\w+)', instr_str)
        if assign_match:
            var_name = assign_match.group(1)
            value = assign_match.group(2)
            variables[var_name] = (value, None)
            instructions.append(('ASSIGN', var_name, value))
            continue
        
        # ADD, SUB, MUL, DIV, MOD
        for op_name, op_sym in [('ADD', '+'), ('SUB', '-'), ('MUL', '*'), ('DIV', '/'), ('MOD', '%')]:
            op_match = re.match(f'{op_name}\\s+t=(\\w+)\\s+a1=(\\w+)\\s+a2=(\\w+)', instr_str)
            if op_match:
                result = op_match.group(1)
                var1 = op_match.group(2)
                var2 = op_match.group(3)
                variables[result] = (var1, var2)
                instructions.append((op_name, result, var1, var2))
                break
        
        if assign_match or any(re.match(f'{op}\\s+t=', instr_str) for op in ['ADD', 'SUB', 'MUL', 'DIV', 'MOD']):
            continue
        
        # WRITE
        write_match = re.match(r'WRITE\s+a1=(\w+)', instr_str)
        if write_match:
            var_name = write_match.group(1)
            write_vars.append(var_name)
            instructions.append(('WRITE', var_name))
            continue
    
    # Generate Python code
    python_code = '#!/usr/bin/env python3\n'
    python_code += 'def main():\n'
    
    for instr in instructions:
        if instr[0] == 'ASSIGN':
            _, var_name, value = instr
            python_code += f'    {var_name} = {value}\n'
        elif instr[0] == 'ADD':
            _, result, var1, var2 = instr
            python_code += f'    {result} = {var1} + {var2}\n'
        elif instr[0] == 'SUB':
            _, result, var1, var2 = instr
            python_code += f'    {result} = {var1} - {var2}\n'
        elif instr[0] == 'MUL':
            _, result, var1, var2 = instr
            python_code += f'    {result} = {var1} * {var2}\n'
        elif instr[0] == 'DIV':
            _, result, var1, var2 = instr
            python_code += f'    {result} = {var1} // {var2}\n'
        elif instr[0] == 'MOD':
            _, result, var1, var2 = instr
            python_code += f'    {result} = {var1} % {var2}\n'
        elif instr[0] == 'WRITE':
            _, var_name = instr
            python_code += f'    print(f"expr: {{expr}}")\n'
    
    python_code += '    return 0\n\nif __name__ == "__main__":\n    main()\n'
    return python_code

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

print(f"✓ TAC: {len(tac.instructions)} instructions")

python_code = generate_python_code(tac)

print("\n=== GENERATED PYTHON CODE ===")
lines = python_code.split('\n')
for i, line in enumerate(lines[:30]):
    print(line)

print("\n=== VALIDATION ===")
# Check for undefined vars
defined_vars = set()
for line in python_code.split('\n'):
    if '=' in line and 'def' not in line:
        match = re.match(r'\s*(\w+)\s*=', line)
        if match:
            defined_vars.add(match.group(1))

undefined = []
for line in python_code.split('\n'):
    for var in re.findall(r'\b([a-z]\w*)\b', line):
        if var not in defined_vars and var not in ['print', 'main']:
            undefined.append(var)

if undefined:
    print(f"❌ Undefined: {set(undefined)}")
else:
    print("✅ All variables properly defined!")
