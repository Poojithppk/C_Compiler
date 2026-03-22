"""
Intermediate Code Generation Phase for NEXUS Compiler

This module provides intermediate code generation capabilities including:
- Three-address code (3AC) generation
- Control flow graph construction
- Data flow analysis
- Symbol handling for intermediate representation
"""

from .intermediate_gui import IntermediateCodeGUI
from .intermediate_code_generator import IntermediateCodeGenerator
from .intermediate_symbols import TACCode, InstructionType, ControlFlowGraph

__all__ = [
    'IntermediateCodeGUI',
    'IntermediateCodeGenerator',
    'TACCode',
    'InstructionType',
    'ControlFlowGraph'
]
