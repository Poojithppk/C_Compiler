"""
Lexical Analysis Module for Advanced Visual Compiler

This module contains all components related to the lexical analysis phase:
- Token definitions and types
- Visual lexical analyzer with step-by-step processing
- Interactive GUI for visual token analysis
- Error recovery and suggestion systems
"""

__version__ = "1.0.0"
__author__ = "Anjani & Poojith - B.Tech Final Year Project"

# Import main components for easy access
from .tokens import Token, TokenType, KEYWORDS, OPERATORS, PUNCTUATION, LexicalError
from .lexer import VisualLexicalAnalyzer, LexerState
from .lexical_gui import LexicalAnalysisGUI

# Public API
__all__ = [
    # Token-related exports
    'Token', 
    'TokenType', 
    'KEYWORDS', 
    'OPERATORS', 
    'PUNCTUATION', 
    'LexicalError',
    
    # Analyzer exports
    'VisualLexicalAnalyzer',
    'LexerState',
    
    # GUI exports
    'LexicalAnalysisGUI'
]

# Module information
PHASE_NAME = "Lexical Analysis Phase"
PHASE_NUMBER = 1
PHASE_STATUS = "🟢 COMPLETE"
FEATURES = [
    "Visual token highlighting and step-by-step animation",
    "Comprehensive token recognition (keywords, operators, literals)",
    "Error recovery with intelligent suggestions",
    "Real-time syntax highlighting",
    "Interactive debugging capabilities",
    "Security-aware token detection"
]

def get_phase_info():
    """Get information about the lexical analysis phase."""
    return {
        'name': PHASE_NAME,
        'number': PHASE_NUMBER,
        'status': PHASE_STATUS,
        'features': FEATURES,
        'module_version': __version__,
        'authors': __author__
    }

def create_analyzer(visual_mode=True, debug_mode=False):
    """
    Factory function to create a lexical analyzer instance.
    
    Args:
        visual_mode (bool): Enable visual feedback
        debug_mode (bool): Enable debug output
        
    Returns:
        VisualLexicalAnalyzer: Configured analyzer instance
    """
    return VisualLexicalAnalyzer(visual_mode=visual_mode, debug_mode=debug_mode)

def launch_gui():
    """
    Launch the visual lexical analysis interface.
    
    Returns:
        LexicalAnalysisGUI: GUI instance
    """
    return LexicalAnalysisGUI()

# Quick access functions
analyze = create_analyzer
gui = launch_gui