"""
Syntax Analysis Module for NEXUS Language Compiler

This module implements the second phase of the NEXUS compiler:
Syntax Analysis (Parsing).

Components:
- AST Node definitions (ast_nodes.py)
- Recursive Descent Parser (parser.py)
- Visual Syntax Analysis GUI (syntax_gui.py)
- AST Printer utilities (ast_printer.py)
"""

__version__ = "1.0.0"
__author__ = "Anjani & Poojith - B.Tech Final Year Project"

# Import main components for easy access
from .ast_nodes import *
from .parser import Parser, ParseError
from .syntax_gui import SyntaxAnalysisGUI
from .ast_printer import ASTPrinter

# Public API
__all__ = [
    'Parser',
    'ParseError', 
    'SyntaxAnalysisGUI',
    'ASTPrinter'
]