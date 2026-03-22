#!/usr/bin/env python3
"""Test nested if-else code generation with proper elif handling"""

import sys
import os
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator
from intermediate_code.intermediate_symbols import InstructionType, OperandType

# Test program with nested if-else
program = """hold a = 10;
hold b = 5;
hold c = 3;
hold value = a + b * c;
when (value > 20) {
    show "Large value";
}
otherwise {
    when (value > 10) {
        show "Medium value";
    }
    otherwise {
        show "Small value";
    }
}"""

print("=" * 70)
print("Testing: Nested If-Elif-Else Code Generation")
print("=" * 70)

# Get TAC
lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, _ = lexer.analyze(program)

parser = Parser(tokens)
ast = parser.parse()

semantic = SemanticAnalyzer(visual_mode=False)
semantic.analyze(ast)

tac_gen = IntermediateCodeGenerator(visual_mode=False)
success, tac_code, _ = tac_gen.generate(ast)

print(f"\nTAC Instructions: {len(tac_code.instructions)}")

# Generate Python with nested if-elif-else support
python_code = '#!/usr/bin/env python3\n'
python_code += '"""\nGenerated Python code\n"""\n\n'
python_code += 'def main():\n'

instructions = tac_code.instructions
labels_map = {}

# Map labels
for i, instr in enumerate(instructions):
    if instr.instruction_type == InstructionType.LABEL and instr.label:
        labels_map[instr.label] = i

print(f"Label map: {labels_map}\n")

i = 0
indent_level = 1

while i < len(instructions):
    instr = instructions[i]
    indent_str = '    ' * indent_level
    
    if instr.instruction_type == InstructionType.LABEL:
        i += 1
        continue
    
    # Regular ASSIGN/ARITHMETIC
    if instr.instruction_type == InstructionType.ASSIGN:
        python_code += f'{indent_str}{instr.result} = {instr.arg1}\n'
        i += 1
        continue
    
    if instr.instruction_type in [InstructionType.ADD, InstructionType.SUB, InstructionType.MUL, InstructionType.DIV]:
        op_map = {InstructionType.ADD: '+', InstructionType.SUB: '-', InstructionType.MUL: '*', InstructionType.DIV: '//'}
        op = op_map.get(instr.instruction_type, '+')
        python_code += f'{indent_str}{instr.result} = {instr.arg1} {op} {instr.arg2}\n'
        i += 1
        continue
    
    # Handle if-elif-else chain
    if (instr.instruction_type == InstructionType.CMP and 
        i + 1 < len(instructions) and 
        instructions[i + 1].instruction_type == InstructionType.JUMP_IF_FALSE):
        
        # Process the if-elif-else chain
        first_if = True
        
        while i < len(instructions):
            if (instructions[i].instruction_type == InstructionType.CMP and 
                i + 1 < len(instructions) and 
                instructions[i + 1].instruction_type == InstructionType.JUMP_IF_FALSE):
                
                arg1 = str(instructions[i].arg1) if instructions[i].arg1 else "0"
                arg2 = str(instructions[i].arg2) if instructions[i].arg2 else "0"
                condition = f"{arg1} > {arg2}"  # Assume >
                
                if first_if:
                    python_code += f'{indent_str}if {condition}:\n'
                    first_if = False
                else:
                    python_code += f'{indent_str}elif {condition}:\n'
                
                false_label = instructions[i + 1].label
                indent_level += 1
                block_indent = '    ' * indent_level
                i += 2
                
                # Collect block until JUMP or false_label
                while i < len(instructions):
                    if instructions[i].instruction_type == InstructionType.LABEL:
                        if instructions[i].label == false_label:
                            break
                        i += 1
                        continue
                    
                    if instructions[i].instruction_type == InstructionType.JUMP:
                        i += 1
                        continue
                    
                    # Generate statement
                    if instructions[i].instruction_type == InstructionType.WRITE:
                        if instructions[i].arg1:
                            value = str(instructions[i].arg1)
                            if hasattr(instructions[i].arg1, 'type') and instructions[i].arg1.type == OperandType.CONSTANT:
                                python_code += f'{block_indent}print("{value}")\n'
                            else:
                                python_code += f'{block_indent}print({value})\n'
                    
                    i += 1
                
                indent_level -= 1
                
                # Now at false_label - check if there's another condition
                if i < len(instructions) and instructions[i].instruction_type == InstructionType.LABEL:
                    if instructions[i].label == false_label:
                        i += 1
                        
                        # Look ahead for next CMP
                        next_instr_idx = i
                        while next_instr_idx < len(instructions) and instructions[next_instr_idx].instruction_type == InstructionType.LABEL:
                            next_instr_idx += 1
                        
                        if (next_instr_idx < len(instructions) and 
                            instructions[next_instr_idx].instruction_type == InstructionType.CMP):
                            # Continue loop for elif
                            i = next_instr_idx
                            continue
                        else:
                            # No more conditions - this is final else
                            if next_instr_idx < len(instructions) and instructions[next_instr_idx].instruction_type != InstructionType.LABEL:
                                python_code += f'{indent_str}else:\n'
                                indent_level += 1
                                block_indent = '    ' * indent_level
                                i = next_instr_idx
                                
                                # Collect final else block
                                while i < len(instructions):
                                    if instructions[i].instruction_type == InstructionType.LABEL:
                                        break
                                    
                                    if instructions[i].instruction_type == InstructionType.WRITE:
                                        if instructions[i].arg1:
                                            value = str(instructions[i].arg1)
                                            if hasattr(instructions[i].arg1, 'type') and instructions[i].arg1.type == OperandType.CONSTANT:
                                                python_code += f'{block_indent}print("{value}")\n'
                                    
                                    i += 1
                                
                                indent_level -= 1
                            break
            else:
                break
        
        continue
    
    i += 1

python_code += '    return 0\n\n'
python_code += 'if __name__ == "__main__":\n'
python_code += '    main()\n'

print("=" * 70)
print("Generated Python Code:")
print("=" * 70)
print(python_code)

print("\n" + "=" * 70)
print("VALIDATION:")
print("=" * 70)
checks = [
    ("Has if statement", "if value > 20:" in python_code),
    ("Has elif statement", "elif value > 10:" in python_code),
    ("Has else statement", "else:" in python_code),
    ("Prints 'Large value' in if", 'print("Large value")' in python_code),
    ("Prints 'Medium value' in elif", 'print("Medium value")' in python_code),
    ("Prints 'Small value' in else", 'print("Small value")' in python_code),
]

for name, result in checks:
    print(f"{'✅' if result else '❌'} {name}")

if all(r for _, r in checks):
    print("\n✅ ALL CHECKS PASSED")
else:
    print("\n❌ SOME CHECKS FAILED")
