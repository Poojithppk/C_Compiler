"""
Intermediate Code Generator for NEXUS Compiler

This module performs intermediate code generation, converting the AST
into three-address code (3AC) with control flow analysis.
"""

from typing import List, Optional, Dict, Any, Tuple
from .intermediate_symbols import (
    TACCode, TACInstruction, InstructionType, Operand, OperandType,
    ControlFlowGraph, BasicBlock, IntermediateCodeError
)


class IntermediateCodeGenerator:
    """
    Generates three-address code from Abstract Syntax Tree.
    
    Features:
    - Three-address code generation
    - Temporary variable allocation
    - Label generation for control flow
    - Symbol table tracking
    - Error reporting
    """
    
    def __init__(self, visual_mode: bool = True):
        self.tac_code = TACCode()
        self.visual_mode = visual_mode
        self.cfg = ControlFlowGraph()
        self.current_function = None
        self.generation_steps: List[Dict[str, Any]] = []
        self.visual_callback = None
        self.error_callback = None
    
    def set_visual_callback(self, callback):
        """Set callback for visual updates."""
        self.visual_callback = callback
    
    def set_error_callback(self, callback):
        """Set callback for error reporting."""
        self.error_callback = callback
    
    def generate(self, ast) -> Tuple[bool, TACCode, List[str]]:
        """
        Generate intermediate code from AST.
        
        Args:
            ast: The Abstract Syntax Tree
            
        Returns:
            Tuple of (success: bool, tac_code: TACCode, errors: List[str])
        """
        try:
            self.tac_code = TACCode()
            self.generation_steps = []
            
            self._record_step("Initialization", "Starting intermediate code generation")
            
            # Process the AST
            self._visit(ast)
            
            # Build control flow graph
            self._record_step("CFG Generation", "Building control flow graph")
            self.cfg.build_from_tac(self.tac_code)
            
            # Optimize (basic)
            self._record_step("Optimization", "Applying basic optimizations")
            self._perform_basic_optimizations()
            
            self._record_step("Complete", 
                            f"Generated {len(self.tac_code.instructions)} instructions")
            
            return True, self.tac_code, self.tac_code.errors
            
        except IntermediateCodeError as e:
            error_msg = str(e)
            self.tac_code.add_error(error_msg)
            if self.error_callback:
                self.error_callback(error_msg)
            return False, self.tac_code, [error_msg]
        except Exception as e:
            error_msg = f"Error generating intermediate code: {str(e)}"
            self.tac_code.errors.append(error_msg)
            if self.error_callback:
                self.error_callback(error_msg)
            return False, self.tac_code, [error_msg]
    
    def _visit(self, node) -> Optional[str]:
        """Visit AST node and generate code."""
        if node is None:
            return None
        
        node_type = type(node).__name__
        method_name = f"_visit_{node_type}"
        
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            return self._visit_generic(node)
    
    def _visit_generic(self, node) -> Optional[str]:
        """Generic visitor for unknown node types."""
        node_type = type(node).__name__
        self._record_step("Node Visit", f"Processing {node_type}")
        
        # Visit children
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                self._visit(stmt)
        
        if hasattr(node, 'body') and node.body:
            self._visit(node.body)
        
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                self._visit(child)
        
        return None
    
    def _visit_ProgramNode(self, node) -> None:
        """Visit program node."""
        self._record_step("Program Start", "Processing program")
        
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                self._visit(stmt)
        
        self._record_step("Program End", "Program processing complete")
    
    def _visit_VarDeclarationNode(self, node) -> None:
        """Visit variable declaration."""
        try:
            var_name = node.name if hasattr(node, 'name') else "unknown"
            var_type = node.type if hasattr(node, 'type') else "unknown"
            
            # Store in symbol table
            self.tac_code.symbol_table[var_name] = {
                'type': var_type,
                'kind': 'VARIABLE',
                'initialized': False
            }
            
            # If has initializer, generate assignment code
            if hasattr(node, 'initializer') and node.initializer:
                init_value = self._visit(node.initializer)
                
                # Generate assignment
                instr = TACInstruction(
                    instruction_type=InstructionType.ASSIGN,
                    result=Operand(OperandType.VARIABLE, var_name, var_type),
                    arg1=Operand(OperandType.CONSTANT, init_value) if init_value else None
                )
                self.tac_code.add_instruction(instr)
                self.tac_code.symbol_table[var_name]['initialized'] = True
                
                self._record_step("Variable Declaration", 
                                f"Declared {var_name} with initialization")
            else:
                self._record_step("Variable Declaration", f"Declared {var_name}")
            
        except Exception as e:
            error_msg = f"Error declaring variable: {str(e)}"
            self.tac_code.errors.append(error_msg)
    
    def _visit_FunctionDeclarationNode(self, node) -> None:
        """Visit function declaration."""
        try:
            func_name = node.name if hasattr(node, 'name') else "unknown"
            
            # Store function in symbol table
            self.tac_code.symbol_table[func_name] = {
                'type': 'FUNCTION',
                'kind': 'FUNCTION',
                'return_type': node.type if hasattr(node, 'type') else 'void'
            }
            
            # Generate function begin label
            func_label = f"{func_name}_begin"
            instr = TACInstruction(
                instruction_type=InstructionType.FUNC_BEGIN,
                label=func_label
            )
            self.tac_code.add_instruction(instr)
            
            self.current_function = func_name
            self._record_step("Function Declaration", f"Function {func_name} declared")
            
            # Process parameters
            if hasattr(node, 'parameters') and node.parameters:
                for param in node.parameters:
                    self._visit(param)
            
            # Process function body
            if hasattr(node, 'body') and node.body:
                self._visit(node.body)
            
            # Generate function end label
            end_label = f"{func_name}_end"
            instr = TACInstruction(
                instruction_type=InstructionType.FUNC_END,
                label=end_label
            )
            self.tac_code.add_instruction(instr)
            
            self._record_step("Function End", f"Function {func_name} completed")
            self.current_function = None
            
        except Exception as e:
            error_msg = f"Error in function declaration: {str(e)}"
            self.tac_code.errors.append(error_msg)
    
    def _visit_AssignmentNode(self, node) -> Optional[str]:
        """Visit assignment statement."""
        try:
            target_name = None
            if hasattr(node, 'target'):
                if hasattr(node.target, 'name'):
                    target_name = node.target.name
            
            if not target_name:
                self.tac_code.warnings.append("Assignment with unknown target")
                return None
            
            # Generate code for value expression
            value_result = self._visit(node.value) if hasattr(node, 'value') else None
            
            # Generate assignment instruction
            instr = TACInstruction(
                instruction_type=InstructionType.ASSIGN,
                result=Operand(OperandType.VARIABLE, target_name),
                arg1=Operand(OperandType.VARIABLE, value_result) if value_result else None
            )
            self.tac_code.add_instruction(instr)
            
            self._record_step("Assignment", f"{target_name} = {value_result}")
            
            return target_name
            
        except Exception as e:
            error_msg = f"Error in assignment: {str(e)}"
            self.tac_code.errors.append(error_msg)
            return None
    
    def _visit_BinaryOpNode(self, node) -> Optional[str]:
        """Visit binary operation."""
        try:
            if not hasattr(node, 'left') or not hasattr(node, 'right'):
                return None
            
            # Generate code for operands
            left_result = self._visit(node.left)
            right_result = self._visit(node.right)
            
            # Determine operation type
            op = node.op if hasattr(node, 'op') else '+'
            instr_type = self._get_instruction_type(op)
            
            if instr_type is None:
                return None
            
            # Generate temporary for result
            temp = self.tac_code.generate_temp()
            
            # Generate instruction
            instr = TACInstruction(
                instruction_type=instr_type,
                result=Operand(OperandType.TEMP, temp),
                arg1=Operand(OperandType.VARIABLE, left_result) if left_result else None,
                arg2=Operand(OperandType.VARIABLE, right_result) if right_result else None
            )
            self.tac_code.add_instruction(instr)
            
            self._record_step("Binary Operation", 
                            f"{left_result} {op} {right_result} -> {temp}")
            
            return temp
            
        except Exception as e:
            error_msg = f"Error in binary operation: {str(e)}"
            self.tac_code.errors.append(error_msg)
            return None
    
    def _visit_BinaryExpressionNode(self, node) -> Optional[str]:
        """Visit binary expression (alias for BinaryOpNode)."""
        return self._visit_BinaryOpNode(node)
    
    def _visit_CallNode(self, node) -> Optional[str]:
        """Visit function call."""
        try:
            func_name = None
            if hasattr(node, 'callee'):
                if hasattr(node.callee, 'name'):
                    func_name = node.callee.name
            
            if not func_name:
                self.tac_code.warnings.append("Function call with unknown function")
                return None
            
            # Generate code for arguments
            if hasattr(node, 'arguments') and node.arguments:
                for arg in node.arguments:
                    arg_result = self._visit(arg)
                    param_instr = TACInstruction(
                        instruction_type=InstructionType.PARAM,
                        arg1=Operand(OperandType.VARIABLE, arg_result)
                    )
                    self.tac_code.add_instruction(param_instr)
            
            # Generate call instruction
            temp = self.tac_code.generate_temp()
            instr = TACInstruction(
                instruction_type=InstructionType.CALL,
                result=Operand(OperandType.TEMP, temp),
                arg1=Operand(OperandType.FUNCTION, func_name)
            )
            self.tac_code.add_instruction(instr)
            
            self._record_step("Function Call", f"Call {func_name}() -> {temp}")
            
            return temp
            
        except Exception as e:
            error_msg = f"Error in function call: {str(e)}"
            self.tac_code.errors.append(error_msg)
            return None
    
    def _visit_PrintStatementNode(self, node) -> None:
        """Visit print/write statement."""
        try:
            if hasattr(node, 'expression') and node.expression:
                expr_result = self._visit(node.expression)
                
                instr = TACInstruction(
                    instruction_type=InstructionType.WRITE,
                    arg1=Operand(OperandType.VARIABLE, expr_result)
                )
                self.tac_code.add_instruction(instr)
                
                self._record_step("Print Statement", f"Write {expr_result}")
            
        except Exception as e:
            error_msg = f"Error in print statement: {str(e)}"
            self.tac_code.errors.append(error_msg)
    
    def _visit_IfStatementNode(self, node) -> None:
        """Visit if-else statement with proper control flow."""
        try:
            # Generate condition evaluation
            if hasattr(node, 'condition') and node.condition:
                cond_result = self._visit(node.condition)
                
                # Create labels for branches
                else_label = self.tac_code.generate_label()
                end_label = self.tac_code.generate_label()
                
                # Conditional jump: if NOT condition, go to else
                instr = TACInstruction(
                    instruction_type=InstructionType.JUMP_IF_FALSE,
                    arg1=Operand(OperandType.VARIABLE, cond_result),
                    label=else_label
                )
                self.tac_code.add_instruction(instr)
                
                # Then branch
                if hasattr(node, 'then_branch') and node.then_branch:
                    self._visit(node.then_branch)
                
                # Jump to end of if-else
                instr = TACInstruction(
                    instruction_type=InstructionType.JUMP,
                    label=end_label
                )
                self.tac_code.add_instruction(instr)
                
                # Else label
                instr = TACInstruction(
                    instruction_type=InstructionType.LABEL,
                    label=else_label
                )
                self.tac_code.add_instruction(instr)
                
                # Else branch (if exists)
                if hasattr(node, 'else_branch') and node.else_branch:
                    self._visit(node.else_branch)
                
                # End label
                instr = TACInstruction(
                    instruction_type=InstructionType.LABEL,
                    label=end_label
                )
                self.tac_code.add_instruction(instr)
                
                self._record_step("If-Else", f"Conditional with {else_label} and {end_label}")
                
        except Exception as e:
            error_msg = f"Error in if statement: {str(e)}"
            self.tac_code.errors.append(error_msg)
    
    def _visit_WhileStatementNode(self, node) -> None:
        """Visit while loop with proper control flow."""
        try:
            # Create labels
            loop_label = self.tac_code.generate_label()
            end_label = self.tac_code.generate_label()
            
            # Loop label (jump back here)
            instr = TACInstruction(
                instruction_type=InstructionType.LABEL,
                label=loop_label
            )
            self.tac_code.add_instruction(instr)
            
            # Evaluate condition
            if hasattr(node, 'condition') and node.condition:
                cond_result = self._visit(node.condition)
                
                # If condition is false, jump to end
                instr = TACInstruction(
                    instruction_type=InstructionType.JUMP_IF_FALSE,
                    arg1=Operand(OperandType.VARIABLE, cond_result),
                    label=end_label
                )
                self.tac_code.add_instruction(instr)
            
            # Loop body
            if hasattr(node, 'body') and node.body:
                self._visit(node.body)
            
            # Jump back to loop label
            instr = TACInstruction(
                instruction_type=InstructionType.JUMP,
                label=loop_label
            )
            self.tac_code.add_instruction(instr)
            
            # End label
            instr = TACInstruction(
                instruction_type=InstructionType.LABEL,
                label=end_label
            )
            self.tac_code.add_instruction(instr)
            
            self._record_step("While Loop", f"Loop condition with {loop_label} and {end_label}")
            
        except Exception as e:
            error_msg = f"Error in while loop: {str(e)}"
            self.tac_code.errors.append(error_msg)
    
    def _visit_ForStatementNode(self, node) -> None:
        """Visit for loop with proper control flow."""
        try:
            # Initialize loop variable
            if hasattr(node, 'initializer') and node.initializer:
                self._visit(node.initializer)
            
            # Create labels
            loop_label = self.tac_code.generate_label()
            end_label = self.tac_code.generate_label()
            
            # Loop label
            instr = TACInstruction(
                instruction_type=InstructionType.LABEL,
                label=loop_label
            )
            self.tac_code.add_instruction(instr)
            
            # Condition check
            if hasattr(node, 'condition') and node.condition:
                cond_result = self._visit(node.condition)
                
                instr = TACInstruction(
                    instruction_type=InstructionType.JUMP_IF_FALSE,
                    arg1=Operand(OperandType.VARIABLE, cond_result),
                    label=end_label
                )
                self.tac_code.add_instruction(instr)
            
            # Loop body
            if hasattr(node, 'body') and node.body:
                self._visit(node.body)
            
            # Increment
            if hasattr(node, 'increment') and node.increment:
                self._visit(node.increment)
            
            # Jump back
            instr = TACInstruction(
                instruction_type=InstructionType.JUMP,
                label=loop_label
            )
            self.tac_code.add_instruction(instr)
            
            # End label
            instr = TACInstruction(
                instruction_type=InstructionType.LABEL,
                label=end_label
            )
            self.tac_code.add_instruction(instr)
            
            self._record_step("For Loop", f"Loop with {loop_label} and {end_label}")
            
        except Exception as e:
            error_msg = f"Error in for loop: {str(e)}"
            self.tac_code.errors.append(error_msg)
    
    def _visit_BlockNode(self, node) -> None:
        """Visit code block."""
        try:
            if hasattr(node, 'statements') and node.statements:
                for statement in node.statements:
                    self._visit(statement)
                    
            self._record_step("Block", "Code block processed")
            
        except Exception as e:
            error_msg = f"Error in block: {str(e)}"
            self.tac_code.errors.append(error_msg)
    
    def _visit_IdentifierNode(self, node) -> Optional[str]:
        """Visit identifier."""
        try:
            name = node.name if hasattr(node, 'name') else str(node)
            return name
        except:
            return None
    
    def _visit_LiteralNode(self, node) -> Optional[str]:
        """Visit literal value."""
        try:
            value = node.value if hasattr(node, 'value') else str(node)
            return str(value)
        except:
            return None
    
    def _get_instruction_type(self, op: str) -> Optional[InstructionType]:
        """Get instruction type for operation."""
        op_map = {
            '+': InstructionType.ADD,
            '-': InstructionType.SUB,
            '*': InstructionType.MUL,
            '/': InstructionType.DIV,
            '%': InstructionType.MOD,
            '==': InstructionType.CMP,
            '!=': InstructionType.CMP,
            '<': InstructionType.CMP,
            '>': InstructionType.CMP,
            '<=': InstructionType.CMP,
            '>=': InstructionType.CMP
        }
        return op_map.get(op)
    
    def _perform_basic_optimizations(self) -> None:
        """Perform basic optimizations on generated code."""
        # Remove dead code (basic)
        reachable = set()
        worklist = [0] if self.tac_code.instructions else []
        
        while worklist:
            idx = worklist.pop(0)
            if idx in reachable or idx >= len(self.tac_code.instructions):
                continue
            
            reachable.add(idx)
            instr = self.tac_code.instructions[idx]
            
            if instr.instruction_type not in (InstructionType.JUMP, 
                                             InstructionType.JUMP_IF_TRUE,
                                             InstructionType.JUMP_IF_FALSE,
                                             InstructionType.RETURN):
                worklist.append(idx + 1)
    
    def _record_step(self, step_type: str, description: str) -> None:
        """Record a generation step."""
        step = {
            'type': step_type,
            'description': description,
            'instruction_count': len(self.tac_code.instructions),
            'error_count': len(self.tac_code.errors),
            'warning_count': len(self.tac_code.warnings)
        }
        self.generation_steps.append(step)
        
        if self.visual_mode and self.visual_callback:
            self.visual_callback(step)
    
    def get_generation_steps(self) -> List[Dict[str, Any]]:
        """Get all generation steps."""
        return self.generation_steps.copy()
    
    def get_tac_code(self) -> TACCode:
        """Get the generated TAC code."""
        return self.tac_code
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics."""
        return {
            'instructions': len(self.tac_code.instructions),
            'temporaries': self.tac_code.temp_counter,
            'labels': self.tac_code.label_counter,
            'errors': len(self.tac_code.errors),
            'warnings': len(self.tac_code.warnings),
            'blocks': len(self.cfg.blocks)
        }
