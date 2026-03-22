"""
Intermediate Code Symbol Definitions for NEXUS Compiler

This module defines the data structures for intermediate code representation,
including three-address code (3AC), instructions, and control flow graphs.
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Set, Tuple
from dataclasses import dataclass, field


class InstructionType(Enum):
    """Types of intermediate code instructions."""
    # Arithmetic operations
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"
    
    # Assignment
    ASSIGN = "ASSIGN"
    
    # Comparison
    CMP = "CMP"
    
    # Control flow
    JUMP = "JUMP"
    JUMP_IF_TRUE = "JUMP_IF_TRUE"
    JUMP_IF_FALSE = "JUMP_IF_FALSE"
    CALL = "CALL"
    RETURN = "RETURN"
    LABEL = "LABEL"
    
    # Memory operations
    LOAD = "LOAD"
    STORE = "STORE"
    LOAD_ARR = "LOAD_ARR"
    STORE_ARR = "STORE_ARR"
    
    # I/O operations
    READ = "READ"
    WRITE = "WRITE"
    
    # Function operations
    FUNC_BEGIN = "FUNC_BEGIN"
    FUNC_END = "FUNC_END"
    PARAM = "PARAM"
    
    # Misc
    NOP = "NOP"


class OperandType(Enum):
    """Types of operands in 3AC."""
    CONSTANT = "CONSTANT"
    VARIABLE = "VARIABLE"
    TEMP = "TEMP"
    LABEL = "LABEL"
    FUNCTION = "FUNCTION"


@dataclass
class Operand:
    """Represents an operand in 3AC."""
    type: OperandType
    value: Any
    data_type: str = "unknown"
    
    def __repr__(self):
        if self.type == OperandType.CONSTANT:
            return str(self.value)
        return f"{self.value}"


@dataclass
class TACInstruction:
    """Represents a single three-address code instruction."""
    instruction_type: InstructionType
    result: Optional[Operand] = None
    arg1: Optional[Operand] = None
    arg2: Optional[Operand] = None
    label: Optional[str] = None
    line_number: int = 0
    
    def __repr__(self):
        """String representation of the instruction."""
        parts = []
        
        if self.label:
            parts.append(f"{self.label}:")
        
        parts.append(self.instruction_type.value)
        
        if self.result:
            parts.append(f"t={self.result}")
        
        if self.arg1:
            parts.append(f"a1={self.arg1}")
        
        if self.arg2:
            parts.append(f"a2={self.arg2}")
        
        return " ".join(parts)
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            'instruction_type': self.instruction_type.value,
            'result': str(self.result) if self.result else None,
            'arg1': str(self.arg1) if self.arg1 else None,
            'arg2': str(self.arg2) if self.arg2 else None,
            'label': self.label,
            'line_number': self.line_number
        }


@dataclass
class TACCode:
    """Represents the complete three-address code for a program."""
    instructions: List[TACInstruction] = field(default_factory=list)
    temp_counter: int = 0
    label_counter: int = 0
    symbol_table: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_instruction(self, instruction: TACInstruction) -> None:
        """Add an instruction to the code."""
        instruction.line_number = len(self.instructions)
        self.instructions.append(instruction)
    
    def generate_temp(self) -> str:
        """Generate a temporary variable name."""
        temp_name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp_name
    
    def generate_label(self) -> str:
        """Generate a label name."""
        label_name = f"L{self.label_counter}"
        self.label_counter += 1
        return label_name
    
    def get_instructions_text(self) -> str:
        """Get all instructions as formatted text."""
        lines = []
        for instr in self.instructions:
            lines.append(str(instr))
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'instructions': [instr.to_dict() for instr in self.instructions],
            'temp_counter': self.temp_counter,
            'label_counter': self.label_counter,
            'errors': self.errors,
            'warnings': self.warnings
        }


@dataclass
class BasicBlock:
    """Represents a basic block in control flow graph."""
    id: str
    instructions: List[TACInstruction] = field(default_factory=list)
    predecessors: List['BasicBlock'] = field(default_factory=list)
    successors: List['BasicBlock'] = field(default_factory=list)
    
    def add_instruction(self, instruction: TACInstruction) -> None:
        """Add instruction to block."""
        self.instructions.append(instruction)
    
    def add_successor(self, block: 'BasicBlock') -> None:
        """Add successor block."""
        if block not in self.successors:
            self.successors.append(block)
            if self not in block.predecessors:
                block.predecessors.append(self)
    
    def get_instructions_text(self) -> str:
        """Get block instructions as text."""
        return "\n".join(str(instr) for instr in self.instructions)


class ControlFlowGraph:
    """Represents the control flow graph of intermediate code."""
    
    def __init__(self):
        self.blocks: Dict[str, BasicBlock] = {}
        self.entry_block: Optional[BasicBlock] = None
        self.exit_block: Optional[BasicBlock] = None
        self.block_counter = 0
    
    def create_block(self) -> BasicBlock:
        """Create a new basic block."""
        block_id = f"B{self.block_counter}"
        self.block_counter += 1
        block = BasicBlock(block_id)
        self.blocks[block_id] = block
        
        if self.entry_block is None:
            self.entry_block = block
        
        return block
    
    def set_exit_block(self, block: BasicBlock) -> None:
        """Set the exit block."""
        self.exit_block = block
    
    def get_block(self, block_id: str) -> Optional[BasicBlock]:
        """Get a block by ID."""
        return self.blocks.get(block_id)
    
    def build_from_tac(self, tac_code: TACCode) -> None:
        """Build CFG from three-address code."""
        if not tac_code.instructions:
            self.entry_block = self.create_block()
            self.exit_block = self.entry_block
            return
        
        current_block = self.create_block()
        self.entry_block = current_block
        
        for instruction in tac_code.instructions:
            # Start new block on labels or after jumps
            if instruction.instruction_type in (InstructionType.LABEL, 
                                               InstructionType.JUMP,
                                               InstructionType.JUMP_IF_TRUE,
                                               InstructionType.JUMP_IF_FALSE):
                if current_block.instructions:
                    # Create new block for next instruction
                    new_block = self.create_block()
                    current_block.add_successor(new_block)
                    current_block = new_block
            
            current_block.add_instruction(instruction)
        
        self.exit_block = current_block
    
    def get_blocks_list(self) -> List[BasicBlock]:
        """Get all blocks in order."""
        return list(self.blocks.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'blocks': {
                block_id: {
                    'instructions': block.get_instructions_text(),
                    'successors': [s.id for s in block.successors]
                }
                for block_id, block in self.blocks.items()
            },
            'entry_block': self.entry_block.id if self.entry_block else None,
            'exit_block': self.exit_block.id if self.exit_block else None
        }


class IntermediateCodeError(Exception):
    """Exception for intermediate code generation errors."""
    pass


class UndefinedVariable(IntermediateCodeError):
    """Exception for undefined variable usage."""
    pass


class InvalidInstruction(IntermediateCodeError):
    """Exception for invalid instruction."""
    pass
