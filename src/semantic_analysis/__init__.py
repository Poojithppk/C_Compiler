"""
Semantic Analysis Module for NEXUS Language Compiler

This module implements the third phase of the NEXUS compiler:
Semantic Analysis.

Components:
- Symbol table management (semantic_symbols.py)
- Semantic analyzer (semantic.py)
- Visual Semantic Analysis GUI (semantic_gui.py)
"""

__version__ = "1.0.0"
__author__ = "Anjani & Poojith - B.Tech Final Year Project"

# Import main components for easy access
from .semantic_symbols import (
    SymbolTable, 
    Symbol, 
    Scope, 
    DataType, 
    SymbolKind, 
    TypeInfo,
    SemanticError,
    TypeMismatch,
    UndefinedSymbol,
    RedeclarationError
)
from .semantic import SemanticAnalyzer
from .semantic_gui import SemanticAnalysisGUI

# Public API
__all__ = [
    'SymbolTable',
    'Symbol',
    'Scope',
    'DataType',
    'SymbolKind',
    'TypeInfo',
    'SemanticAnalyzer',
    'SemanticAnalysisGUI',
    'SemanticError',
    'TypeMismatch',
    'UndefinedSymbol',
    'RedeclarationError'
]
