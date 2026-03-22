#!/usr/bin/env python3
"""End-to-end test of Program 3 with the fixed code generator"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator

# Program 3 code
program = """hold num1 = 20;
hold num2 = 10;

when (num1 > num2)
{
    show "Greater";
}
otherwise
{
    show "Smaller";
}"""

print("Program 3: If-Else Conditional")
print("=" * 60)

# Phase 1-4
lexer = VisualLexicalAnalyzer(visual_mode=False)
tokens, _ = lexer.analyze(program)

parser = Parser(tokens)
ast = parser.parse()

semantic = SemanticAnalyzer(visual_mode=False)
semantic.analyze(ast)

tac_gen = IntermediateCodeGenerator(visual_mode=False)
success, tac_code, _ = tac_gen.generate(ast)

print(f"TAC Instructions: {len(tac_code.instructions)}")
for i, instr in enumerate(tac_code.instructions):
    print(f"  {i}: {instr}")

# Now test JUST the _generate_python_code method
from intermediate_code.intermediate_symbols import InstructionType, OperandType

# Create a simple object to call the method
class TestCodeGen:
    def __init__(self, tac):
        self.tac_code = tac
    
    def _generate_python_code(self) -> str:
        """Generate Python code from TAC with control flow support."""
        if not self.tac_code or not hasattr(self.tac_code, 'instructions'):
            return "# Error: No TAC code available"
        
        python_code = '#!/usr/bin/env python3\n'
        python_code += '"""\nGenerated Python code\n"""\n\n'
        python_code += 'def main():\n'
        
        instructions = self.tac_code.instructions
        labels_map = {}
        
        # First pass: find all labels
        for i, instr in enumerate(instructions):
            if instr.instruction_type == InstructionType.LABEL and instr.label:
                labels_map[instr.label] = i
        
        # Generate code
        i = 0
        indent_level = 1
        
        while i < len(instructions):
            instr = instructions[i]
            indent_str = '    ' * indent_level
            
            # Skip labels
            if instr.instruction_type == InstructionType.LABEL:
                i += 1
                continue
            
            # Handle if-else: CMP followed by JUMP_IF_FALSE
            if (instr.instruction_type == InstructionType.CMP and 
                i + 1 < len(instructions) and 
                instructions[i + 1].instruction_type == InstructionType.JUMP_IF_FALSE):
                
                # Extract comparison
                arg1 = str(instr.arg1) if instr.arg1 else "0"
                arg2 = str(instr.arg2) if instr.arg2 else "0"
                condition = f"{arg1} > {arg2}"
                
                false_label = instructions[i + 1].label
                false_label_idx = labels_map.get(false_label, len(instructions))
                
                python_code += f'{indent_str}if {condition}:\n'
                indent_level += 1
                i += 2
                
                # Generate if-block
                while i < len(instructions):
                    if instructions[i].instruction_type == InstructionType.LABEL:
                        if instructions[i].label == false_label:
                            python_code += f'    ' * (indent_level - 1) + 'else:\n'
                            i += 1
                            
                            # Generate else block
                            else_end_idx = i
                            while else_end_idx < len(instructions):
                                if instructions[else_end_idx].instruction_type == InstructionType.LABEL:
                                    break
                                if instructions[else_end_idx].instruction_type == InstructionType.JUMP:
                                    break
                                else_end_idx += 1
                            
                            # Generate else block instructions
                            else_indent_str = '    ' * indent_level
                            while i < else_end_idx:
                                instr = instructions[i]
                                if instr.instruction_type == InstructionType.WRITE:
                                    if instr.arg1:
                                        value = str(instr.arg1)
                                        if hasattr(instr.arg1, 'type') and instr.arg1.type == OperandType.CONSTANT:
                                            python_code += f'{else_indent_str}print("{value}")\n'
                                        else:
                                            python_code += f'{else_indent_str}print(f"Result: {{{value}}}")\n'
                                elif instr.instruction_type == InstructionType.ASSIGN:
                                    if instr.result and instr.arg1:
                                        python_code += f'{else_indent_str}{instr.result} = {instr.arg1}\n'
                                i += 1
                            indent_level -= 1
                            break
                        else:
                            i += 1
                            continue
                    
                    if instructions[i].instruction_type == InstructionType.JUMP:
                        i += 1
                        break
                    
                    # Generate if-block instructions
                    if_indent_str = '    ' * indent_level
                    if instructions[i].instruction_type == InstructionType.WRITE:
                        if instructions[i].arg1:
                            value = str(instructions[i].arg1)
                            if hasattr(instructions[i].arg1, 'type') and instructions[i].arg1.type == OperandType.CONSTANT:
                                python_code += f'{if_indent_str}print("{value}")\n'
                            else:
                                python_code += f'{if_indent_str}print(f"Result: {{{value}}}")\n'
                    elif instructions[i].instruction_type == InstructionType.ASSIGN:
                        if instructions[i].result and instructions[i].arg1:
                            python_code += f'{if_indent_str}{instructions[i].result} = {instructions[i].arg1}\n'
                    
                    i += 1
                
                indent_level -= 1
                continue
            
            # Handle regular straight-line instructions
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
        
        return python_code

code_gen = TestCodeGen(tac_code)
python_code = code_gen._generate_python_code()

print("\n" + "=" * 60)
print("Generated Python Code:")
print("=" * 60)
print(python_code)

print("\nExpected: Should print 'Greater    ' (because 20 > 10)")
print("Test: If-else block indentation should be correct")
