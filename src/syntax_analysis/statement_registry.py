"""
Dynamic Statement Registry for Syntax Analysis

This module provides dynamic registration and handling of statement types
(if-else, loops, etc.). Allows custom statement parsers to be registered
and executed based on statement type.
"""

from typing import Dict, Optional, Callable, List
from enum import Enum
from dataclasses import dataclass


class StatementType(Enum):
    """Types of statements supported by the parser."""
    IF = "if"
    ELIF = "elif"
    ELSE = "else"
    WHILE = "while"
    FOR = "for"
    SWITCH = "switch"
    BLOCK = "block"
    EXPRESSION = "expression"
    RETURN = "return"
    BREAK = "break"
    CONTINUE = "continue"
    VARIABLE_DECLARATION = "variable_declaration"
    FUNCTION_DECLARATION = "function_declaration"
    CUSTOM = "custom"


@dataclass
class StatementPattern:
    """Defines a statement pattern for parsing."""
    statement_type: StatementType
    keyword_token_type: any  # The token type that starts this statement
    lookahead_required: int = 0  # How many tokens to look ahead
    block_required: bool = False  # Does this statement require a block?
    condition_required: bool = False  # Does this statement have a condition?
    custom_parser: Optional[Callable] = None  # Custom parsing function


class StatementRegistry:
    """
    Dynamic registry for managing statement patterns and parsers.
    """
    
    def __init__(self):
        """Initialize the statement registry."""
        self.patterns: Dict[str, StatementPattern] = {}
        self.parsers: Dict[str, Callable] = {}
        self.statement_keywords: Dict[str, StatementType] = {}
    
    def register_statement(self, statement_type: StatementType, 
                          keyword: str, keyword_token_type: any,
                          parser: Callable,
                          block_required: bool = False,
                          condition_required: bool = False) -> None:
        """
        Register a new statement type dynamically.
        
        Args:
            statement_type: The statement type enum
            keyword: The keyword that triggers this statement (e.g., 'when', 'repeat')
            keyword_token_type: The token type for this keyword
            parser: The function that parses this statement
            block_required: Whether this statement requires a code block
            condition_required: Whether this statement has a condition
        """
        pattern = StatementPattern(
            statement_type=statement_type,
            keyword_token_type=keyword_token_type,
            block_required=block_required,
            condition_required=condition_required,
            custom_parser=parser
        )
        
        key = keyword.lower()
        self.patterns[key] = pattern
        self.parsers[key] = parser
        self.statement_keywords[key] = statement_type
    
    def get_statement_pattern(self, keyword: str) -> Optional[StatementPattern]:
        """Get the parser pattern for a keyword."""
        return self.patterns.get(keyword.lower())
    
    def get_parser(self, keyword: str) -> Optional[Callable]:
        """Get the parser function for a keyword."""
        return self.parsers.get(keyword.lower())
    
    def has_statement(self, keyword: str) -> bool:
        """Check if a statement type is registered."""
        return keyword.lower() in self.patterns
    
    def get_statement_type(self, keyword: str) -> Optional[StatementType]:
        """Get the statement type for a keyword."""
        return self.statement_keywords.get(keyword.lower())
    
    def is_control_structure(self, keyword: str) -> bool:
        """Check if a keyword represents a control structure."""
        stmt_type = self.get_statement_type(keyword)
        return stmt_type in [
            StatementType.IF, StatementType.ELIF, StatementType.ELSE,
            StatementType.WHILE, StatementType.FOR, StatementType.SWITCH
        ]
    
    def is_loop_structure(self, keyword: str) -> bool:
        """Check if a keyword represents a loop."""
        stmt_type = self.get_statement_type(keyword)
        return stmt_type in [StatementType.WHILE, StatementType.FOR]
    
    def get_control_structures(self) -> List[str]:
        """Get all registered control structure keywords."""
        return [k for k, v in self.statement_keywords.items() 
                if v in [StatementType.IF, StatementType.ELIF, StatementType.ELSE,
                        StatementType.WHILE, StatementType.FOR, StatementType.SWITCH]]
    
    def get_all_keywords(self) -> List[str]:
        """Get all registered statement keywords."""
        return list(self.statement_keywords.keys())
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about registered statements."""
        return {
            'total_patterns': len(self.patterns),
            'total_parsers': len(self.parsers),
            'control_structures': len(self.get_control_structures()),
            'loop_structures': len([k for k in self.statement_keywords 
                                   if self.is_loop_structure(k)]),
        }
