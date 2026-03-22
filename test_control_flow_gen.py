#!/usr/bin/env python3
"""Test control flow code generation directly"""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator
from intermediate_code.intermediate_symbols import InstructionType, OperandType, Operand

# Program 3 with correct NEXUS syntax
program_code = """hold num1 = 20;
hold num2 = 10;

when (num1 > num2)
{
    show "Greater";
}
otherwise
{
    show "Smaller";
}"""

print("=" * 60)
print("PROGRAM 3: Testing Control Flow Code Generation")
print("=" * 60)

# Phase 1-4: Lex, Parse, Semantic, TAC
lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, _ = lexer.analyze(program_code)

parser = Parser(tokens)
ast = parser.parse()

semantic = SemanticAnalyzer(visual_mode=False)
semantic.analyze(ast)

tac_gen = IntermediateCodeGenerator(visual_mode=False)
success, tac_code, _ = tac_gen.generate(ast)

print(f"\nTAC Instructions ({len(tac_code.instructions)}):")
for i, instr in enumerate(tac_code.instructions):
    print(f"  {i}: {instr}")

# Now manually implement the control flow code generation
print("\n" + "=" * 60)
print("TESTING CONTROL FLOW CODE GENERATION")
print("=" * 60)

python_code = '#!/usr/bin/env python3\n'
python_code += '"""\nGenerated Python code\n"""\n\n'
python_code += 'def main():\n'

instructions = tac_code.instructions
labels_map = {}

# First pass: map labels
for i, instr in enumerate(instructions):
    if instr.instruction_type == InstructionType.LABEL and instr.label:
        labels_map[instr.label] = i

print(f"Label map: {labels_map}")

# Second pass: generate code with control flow support
i = 0
indent_level = 1

while i < len(instructions):
    instr = instructions[i]
    indent_str = '    ' * indent_level
    
    # Skip labels
    if instr.instruction_type == InstructionType.LABEL:
        print(f"\nFound label at {i}: {instr.label}")
        i += 1
        continue
    
    # Handle CMP + JUMP_IF_FALSE pattern for if-else
    if (instr.instruction_type == InstructionType.CMP and 
        i + 1 < len(instructions) and 
        instructions[i + 1].instruction_type == InstructionType.JUMP_IF_FALSE):
        
        print(f"\nFound if-else pattern at instruction {i}")
        
        # Get jump target
        false_label_instr = instructions[i + 1]
        false_label = false_label_instr.label
        false_label_idx = labels_map.get(false_label, len(instructions))
        
        print(f"  False label: {false_label} (index {false_label_idx})")
        
        # Get comparison operands  
        arg1 = str(instr.arg1) if instr.arg1 else "0"
        arg2 = str(instr.arg2) if instr.arg2 else "0"
        condition = f"{arg1} > {arg2}"  # Assume greater-than
        
        python_code += f'{indent_str}if {condition}:\n'
        indent_level += 1
        i += 2  # Skip CMP and JUMP_IF_FALSE
        
        # Generate if-block
        print(f"  Collecting if-block from {i}...")
        while i < len(instructions):
            curr_instr = instructions[i]
            
            # Check if we reached the false label
            if curr_instr.instruction_type == InstructionType.LABEL:
                if curr_instr.label == false_label:
                    print(f"  Found else label at {i}")
                    python_code += f'    ' * (indent_level - 1) + 'else:\n'
                    indent_level = indent_level  # Stay at same indent
                    i += 1
                    
                    # Generate else block
                    else_end_idx = i
                    while else_end_idx < len(instructions):
                        if instructions[else_end_idx].instruction_type == InstructionType.LABEL:
                            break
                        else_end_idx += 1
                    
                    print(f"  Collecting else-block from {i} to {else_end_idx}...")
                    while i < else_end_idx:
                        elif_instr = instructions[i]
                        
                        if elif_instr.instruction_type == InstructionType.WRITE:
                            if elif_instr.arg1:
                                value = str(elif_instr.arg1)
                                if hasattr(elif_instr.arg1, 'type') and elif_instr.arg1.type == OperandType.CONSTANT:
                                    python_code += f'{indent_str}print("{value}")\n'
                                else:
                                    python_code += f'{indent_str}print(f"Result: {{{value}}}")\n'
                        elif elif_instr.instruction_type == InstructionType.ASSIGN:
                            if elif_instr.result and elif_instr.arg1:
                                python_code += f'{indent_str}{elif_instr.result} = {elif_instr.arg1}\n'
                        
                        i += 1
                    
                    indent_level -= 1
                    break
                else:
                    i += 1
                    continue
            
            # Generate if-block instruction
            if curr_instr.instruction_type == InstructionType.WRITE:
                if curr_instr.arg1:
                    value = str(curr_instr.arg1)
                    if hasattr(curr_instr.arg1, 'type') and curr_instr.arg1.type == OperandType.CONSTANT:
                        python_code += f'{indent_str}print("{value}")\n'
                    else:
                        python_code += f'{indent_str}print(f"Result: {{{value}}}")\n'
            elif curr_instr.instruction_type == InstructionType.ASSIGN:
                if curr_instr.result and curr_instr.arg1:
                    python_code += f'{indent_str}{curr_instr.result} = {curr_instr.arg1}\n'
            
            i += 1
        
        indent_level -= 1
        continue
    
    # Regular straight-line instructions
    if instr.instruction_type == InstructionType.ASSIGN:
        if instr.result and instr.arg1:
            python_code += f'{indent_str}{instr.result} = {instr.arg1}\n'
    elif instr.instruction_type == InstructionType.WRITE:
        if instr.arg1:
            value = str(instr.arg1)
            if hasattr(instr.arg1, 'type') and instr.arg1.type == OperandType.CONSTANT:
                python_code += f'{indent_str}print("{value}")\n'
            else:
                python_code += f'{indent_str}print(f"Result: {{{value}}}")\n'
    
    i += 1

python_code += '    return 0\n\n'
python_code += 'if __name__ == "__main__":\n'
python_code += '    main()\n'

print("\n" + "=" * 60)
print("GENERATED PYTHON CODE:")
print("=" * 60)
print(python_code)

print("\n" + "=" * 60)
print("EXPECTED OUTPUT:")
print("Greater")
print("=" * 60)
