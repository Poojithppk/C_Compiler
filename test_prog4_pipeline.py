"""Test Program 4 through the entire pipeline."""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator

# Program 4 test code
test_code = """
hold count = 10;
repeat (count > 0)
{
    show count;
    count = count - 1;
}
"""

print("=" * 70)
print("TESTING PROGRAM 4 - FULL PIPELINE")
print("=" * 70)

# Phases 1-4
lexer = VisualLexicalAnalyzer()
tokens, _ = lexer.analyze(test_code)

parser = Parser(tokens)
ast = parser.parse()

semantic = SemanticAnalyzer(visual_mode=False)
semantic.analyze(ast)

tac_gen = IntermediateCodeGenerator(visual_mode=False)
success, tac_code, _ = tac_gen.generate(ast)

print("\nTAC CODE:")
print("-" * 70)
for i, instr in enumerate(tac_code.instructions):
    print(f"{i:2d}: {instr}")

# Phase 5 - Code Generation
# Create a temporary GUI object just to access code generation methods
class TempCodeGen:
    def __init__(self):
        self.tac_code = tac_code
    
    def _detect_loop_ranges(self, instructions):
        from intermediate_code.intermediate_symbols import InstructionType
        
        labels_map = {}
        for i, instr in enumerate(instructions):
            if instr.instruction_type == InstructionType.LABEL and instr.label:
                labels_map[instr.label] = i
        
        loop_ranges = []
        for i, instr in enumerate(instructions):
            if instr.instruction_type == InstructionType.JUMP and instr.label:
                target_idx = labels_map.get(instr.label, -1)
                if target_idx >= 0 and target_idx < i:
                    loop_start_label = instr.label
                    loop_end_label = None
                    for j in range(i + 1, len(instructions)):
                        if instructions[j].instruction_type == InstructionType.LABEL:
                            loop_end_label = instructions[j].label
                            break
                    loop_ranges.append({
                        'start_label': loop_start_label,
                        'end_label': loop_end_label,
                        'start_idx': target_idx,
                        'jump_idx': i,
                        'end_idx': len(instructions) if loop_end_label is None else labels_map.get(loop_end_label, len(instructions))
                    })
        
        return loop_ranges
    
    def _is_loop_condition(self, cmp_idx, instructions, loop_ranges):
        for loop_info in loop_ranges:
            if cmp_idx >= loop_info['start_idx'] and cmp_idx <= loop_info['jump_idx']:
                return True, loop_info
        return False, None
    
    def _generate_python_block(self, instructions, labels_map, start_idx, end_idx, indent_level=1, is_elif=False, loop_ranges=None):
        from intermediate_code.intermediate_symbols import InstructionType, OperandType
        
        if loop_ranges is None:
            loop_ranges = []
        
        python_code = ''
        i = start_idx
        
        while i < end_idx:
            instr = instructions[i]
            indent_str = '    ' * indent_level
            
            if instr.instruction_type == InstructionType.LABEL:
                i += 1
                continue
            
            is_loop, loop_info = self._is_loop_condition(i, instructions, loop_ranges) if loop_ranges else (False, None)
            
            if (is_loop and instr.instruction_type == InstructionType.CMP and 
                i + 1 < len(instructions) and 
                instructions[i + 1].instruction_type == InstructionType.JUMP_IF_FALSE):
                
                arg1 = str(instr.arg1) if instr.arg1 else "0"
                arg2 = str(instr.arg2) if instr.arg2 else "0"
                condition = f"{arg1} > {arg2}"
                
                python_code += f'{indent_str}while {condition}:\n'
                i += 2
                
                loop_body_end = i
                while loop_body_end < len(instructions):
                    if (instructions[loop_body_end].instruction_type == InstructionType.JUMP and
                        instructions[loop_body_end].label in [loop_info['start_label']]):
                        break
                    loop_body_end += 1
                
                python_code += self._generate_python_block(instructions, labels_map, i, loop_body_end, indent_level + 1, loop_ranges=loop_ranges)
                i = loop_body_end
                
                if i < len(instructions) and instructions[i].instruction_type == InstructionType.JUMP:
                    i += 1
                
                continue
            
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
            
            elif instr.instruction_type == InstructionType.SUB:
                if instr.result and instr.arg1 and instr.arg2:
                    python_code += f'{indent_str}{instr.result} = {instr.arg1} - {instr.arg2}\n'
            
            i += 1
        
        return python_code
    
    def _generate_python_code(self):
        from intermediate_code.intermediate_symbols import InstructionType
        
        python_code = '#!/usr/bin/env python3\n'
        python_code += '"""\nGenerated Python code from NEXUS compiler\n"""\n\n'
        python_code += 'def main():\n'
        
        instructions = self.tac_code.instructions
        labels_map = {}
        
        for i, instr in enumerate(instructions):
            if instr.instruction_type == InstructionType.LABEL and instr.label:
                labels_map[instr.label] = i
        
        loop_ranges = self._detect_loop_ranges(instructions)
        
        python_code += self._generate_python_block(instructions, labels_map, 0, len(instructions), indent_level=1, loop_ranges=loop_ranges)
        
        python_code += '    return 0\n\n'
        python_code += 'if __name__ == "__main__":\n'
        python_code += '    main()\n'
        
        return python_code

gen = TempCodeGen()
python_code = gen._generate_python_code()

print("\nGENERATED PYTHON CODE:")
print("-" * 70)
print(python_code)

print("\n" + "=" * 70)
print("CODE GENERATION TEST COMPLETE")
print("=" * 70)
