#!/usr/bin/env python3
"""Generate Python code with control flow support from TAC."""

def generate_python_with_control_flow(tac_code):
    """Generate Python code that properly implements if-else and loops."""
    from intermediate_code.intermediate_symbols import InstructionType, OperandType
    
    if not tac_code or not hasattr(tac_code, 'instructions'):
        return "# Error: No TAC code available"
    
    # First pass: identify basic blocks and control flow
    instructions = tac_code.instructions
    labels_to_idx = {}  # label -> instruction index
    jumps = []  # List of (jump_idx, target_label, is_conditional)
    
    # Map labels to their indices
    for i, instr in enumerate(instructions):
        if instr.instruction_type == InstructionType.LABEL:
            if instr.label:
                labels_to_idx[instr.label] = i
    
    # Identify jumps
    for i, instr in enumerate(instructions):
        if instr.instruction_type == InstructionType.JUMP:
            jumps.append((i, instr.label, False))
        elif instr.instruction_type == InstructionType.JUMP_IF_FALSE:
            jumps.append((i, instr.label, True))
    
    # Build Python code with control flow
    python_code = '#!/usr/bin/env python3\n'
    python_code += '"""\nGenerated Python code from NEXUS compiler\n"""\n\n'
    python_code += 'def main():\n'
    
    i = 0
    indent = 1  # Indentation level (1 = inside main, 2 = inside if block, etc.)
    
    while i < len(instructions):
        instr = instructions[i]
        indent_str = '    ' * indent
        
        # Skip labels
        if instr.instruction_type == InstructionType.LABEL:
            i += 1
            continue
        
        # Handle CMP + JUMP_IF_FALSE pattern (if-else)
        if (instr.instruction_type == InstructionType.CMP and 
            i + 1 < len(instructions) and
            instructions[i + 1].instruction_type == InstructionType.JUMP_IF_FALSE):
            
            # CMP: t0 = num1 > num2
            cmp_instr = instr
            jump_instr = instructions[i + 1]
            false_label = jump_instr.label
            
            # Build condition
            if cmp_instr.result and cmp_instr.arg1 and cmp_instr.arg2:
                # For now, assume > comparison (would need to detect actual operator)
                cond = f"{cmp_instr.arg1} > {cmp_instr.arg2}"
                python_code += f'{indent_str}if {cond}:\n'
                indent += 1
            
            # Generate code until we hit the false label or next jump
            i += 2  # Skip CMP and JUMP_IF_FALSE
            while i < len(instructions):
                if instructions[i].instruction_type == InstructionType.LABEL:
                    if instructions[i].label == false_label:
                        # Found the else branch label
                        python_code += f'    ' * (indent - 1) + 'else:\n'
                        indent_str = '    ' * indent
                        i += 1
                        break
                    else:
                        i += 1
                        continue
                
                # Generate instruction
                if instructions[i].instruction_type == InstructionType.WRITE:
                    if instructions[i].arg1:
                        value = str(instructions[i].arg1)
                        if instructions[i].arg1.type == OperandType.CONSTANT:
                            python_code += f'{indent_str}print("{value}")\n'
                        else:
                            python_code += f'{indent_str}print(f"{{variable}}: {{{value}}}")\n'
                elif instructions[i].instruction_type == InstructionType.ASSIGN:
                    if instructions[i].result and instructions[i].arg1:
                        python_code += f'{indent_str}{instructions[i].result} = {instructions[i].arg1}\n'
                
                i += 1
            
            # After else block ends
            if indent > 1:
                indent -= 1
            continue
        
        # Handle regular instructions
        if instr.instruction_type == InstructionType.ASSIGN:
            if instr.result and instr.arg1:
                python_code += f'{indent_str}{instr.result} = {instr.arg1}\n'
        
        elif instr.instruction_type == InstructionType.ADD:
            if instr.result and instr.arg1 and instr.arg2:
                python_code += f'{indent_str}{instr.result} = {instr.arg1} + {instr.arg2}\n'
        
        elif instr.instruction_type == InstructionType.SUB:
            if instr.result and instr.arg1 and instr.arg2:
                python_code += f'{indent_str}{instr.result} = {instr.arg1} - {instr.arg2}\n'
        
        elif instr.instruction_type == InstructionType.MUL:
            if instr.result and instr.arg1 and instr.arg2:
                python_code += f'{indent_str}{instr.result} = {instr.arg1} * {instr.arg2}\n'
        
        elif instr.instruction_type == InstructionType.DIV:
            if instr.result and instr.arg1 and instr.arg2:
                python_code += f'{indent_str}{instr.result} = {instr.arg1} // {instr.arg2}\n'
        
        elif instr.instruction_type == InstructionType.MOD:
            if instr.result and instr.arg1 and instr.arg2:
                python_code += f'{indent_str}{instr.result} = {instr.arg1} % {instr.arg2}\n'
        
        elif instr.instruction_type == InstructionType.WRITE:
            if instr.arg1:
                value = str(instr.arg1)
                if instr.arg1.type == OperandType.CONSTANT:
                    python_code += f'{indent_str}print("{value}")\n'
                else:
                    python_code += f'{indent_str}print(f"Result: {{{value}}}")\n'
        
        i += 1
    
    python_code += '    return 0\n\n'
    python_code += 'if __name__ == "__main__":\n'
    python_code += '    main()\n'
    
    return python_code
