"""
Dynamic Token Registry for Lexical Analysis

This module provides dynamic registration and management of tokens, keywords,
operators, and punctuation. No hardcoding - all token definitions can be
registered at runtime and configured through configuration objects.
"""

from typing import Dict, List, Optional, Callable, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from .tokens import TokenType


@dataclass
class TokenDefinition:
    """Defines a single token for dynamic registration."""
    token_type: TokenType
    lexeme: str
    priority: int = 0  # Higher priority = checked first
    is_keyword: bool = False
    is_operator: bool = False
    is_punctuation: bool = False
    validator: Optional[Callable[[str], bool]] = None  # Custom validation
    processor: Optional[Callable[[str], any]] = None    # Custom processing


class TokenRegistry:
    """
    Dynamic registry for managing all token definitions.
    Supports registration, lookup, and configuration of tokens.
    """
    
    def __init__(self):
        """Initialize the token registry."""
        self.keywords: Dict[str, TokenType] = {}
        self.operators: Dict[str, TokenType] = {}
        self.punctuation: Dict[str, TokenType] = {}
        self.definitions: Dict[str, TokenDefinition] = {}
        self.operator_priority: Dict[str, int] = {}  # Longest match first
        self.validation_rules: Dict[TokenType, Callable] = {}
        self.processing_hooks: Dict[TokenType, Callable] = {}
    
    def register_keyword(self, lexeme: str, token_type: TokenType, 
                        priority: int = 100) -> None:
        """Register a keyword dynamically."""
        self.keywords[lexeme] = token_type
        self.definitions[lexeme] = TokenDefinition(
            token_type=token_type,
            lexeme=lexeme,
            priority=priority,
            is_keyword=True
        )
    
    def register_operator(self, lexeme: str, token_type: TokenType, 
                         priority: int = 0) -> None:
        """Register an operator dynamically."""
        self.operators[lexeme] = token_type
        self.operator_priority[lexeme] = priority
        self.definitions[lexeme] = TokenDefinition(
            token_type=token_type,
            lexeme=lexeme,
            priority=priority,
            is_operator=True
        )
    
    def register_punctuation(self, lexeme: str, token_type: TokenType) -> None:
        """Register a punctuation mark dynamically."""
        self.punctuation[lexeme] = token_type
        self.definitions[lexeme] = TokenDefinition(
            token_type=token_type,
            lexeme=lexeme,
            is_punctuation=True
        )
    
    def register_validation_rule(self, token_type: TokenType, 
                                 validator: Callable[[str], bool]) -> None:
        """Register a validation rule for a token type."""
        self.validation_rules[token_type] = validator
    
    def register_processing_hook(self, token_type: TokenType, 
                                processor: Callable[[str], any]) -> None:
        """Register a processing hook for a token type."""
        self.processing_hooks[token_type] = processor
    
    def get_keyword(self, lexeme: str) -> Optional[TokenType]:
        """Get keyword token type by lexeme."""
        return self.keywords.get(lexeme.lower())
    
    def get_operator(self, lexeme: str) -> Optional[TokenType]:
        """Get operator token type by lexeme."""
        return self.operators.get(lexeme)
    
    def get_punctuation(self, lexeme: str) -> Optional[TokenType]:
        """Get punctuation token type by lexeme."""
        return self.punctuation.get(lexeme)
    
    def is_keyword(self, lexeme: str) -> bool:
        """Check if lexeme is a registered keyword."""
        return lexeme.lower() in self.keywords
    
    def is_operator(self, lexeme: str) -> bool:
        """Check if lexeme is a registered operator."""
        return lexeme in self.operators
    
    def is_punctuation(self, lexeme: str) -> bool:
        """Check if lexeme is a registered punctuation."""
        return lexeme in self.punctuation
    
    def get_longest_operator_match(self, text: str, start_pos: int) -> Optional[Tuple[str, TokenType]]:
        """
        Get the longest matching operator starting at position.
        Uses greedy matching - checks longer operators first.
        """
        # Sort operators by length (longest first)
        sorted_ops = sorted(self.operators.keys(), key=len, reverse=True)
        
        for op in sorted_ops:
            if text[start_pos:].startswith(op):
                return (op, self.operators[op])
        
        return None
    
    def validate_token(self, token_type: TokenType, value: str) -> bool:
        """Validate token value using registered rules."""
        if token_type in self.validation_rules:
            return self.validation_rules[token_type](value)
        return True
    
    def process_token(self, token_type: TokenType, value: str) -> any:
        """Process token value using registered hooks."""
        if token_type in self.processing_hooks:
            return self.processing_hooks[token_type](value)
        return value
    
    def get_keywords_for_type(self, token_type: TokenType) -> List[str]:
        """Get all keywords registered for a specific token type."""
        return [k for k, v in self.keywords.items() if v == token_type]
    
    def load_default_keywords(self) -> None:
        """Load default NEXUS language keywords."""
        default_keywords = {
            'hold': TokenType.VAR,
            'fixed': TokenType.CONST,
            'num': TokenType.INT,
            'decimal': TokenType.FLOAT_TYPE,
            'text': TokenType.STRING_TYPE,
            'flag': TokenType.BOOL,
            'func': TokenType.FUNC,
            'return': TokenType.RETURN,
            'when': TokenType.IF,
            'otherwise': TokenType.ELSE,
            'otherwise when': TokenType.ELIF,
            'repeat': TokenType.WHILE,
            'cycle': TokenType.FOR,
            'stop': TokenType.BREAK,
            'skip': TokenType.CONTINUE,
            'choose': TokenType.SWITCH,
            'option': TokenType.CASE,
            'default': TokenType.DEFAULT,
            'yes': TokenType.TRUE,
            'no': TokenType.FALSE,
            'null': TokenType.NULL,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            'show': TokenType.PRINT,
            'ask': TokenType.INPUT,
            'secure': TokenType.SECURE,
            'validate': TokenType.VALIDATE,
            'sanitize': TokenType.SANITIZE,
            'toNumber': TokenType.TO_NUMBER,
            'toDecimal': TokenType.TO_DECIMAL,
            'toString': TokenType.TO_STRING,
            'toBoolean': TokenType.TO_BOOLEAN,
            'isNumber': TokenType.IS_NUMBER,
            'length': TokenType.LENGTH,
            'uppercase': TokenType.UPPERCASE,
            'lowercase': TokenType.LOWERCASE,
            'trim': TokenType.TRIM,
            'substring': TokenType.SUBSTRING,
            'format': TokenType.FORMAT,
        }
        
        for keyword, token_type in default_keywords.items():
            self.register_keyword(keyword, token_type)
    
    def load_default_operators(self) -> None:
        """Load default operators."""
        default_operators = {
            '**': TokenType.POWER,  # Priority: Longer match first
            '+=': TokenType.PLUS_ASSIGN,
            '-=': TokenType.MINUS_ASSIGN,
            '*=': TokenType.MULT_ASSIGN,
            '/=': TokenType.DIV_ASSIGN,
            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
            '&&': TokenType.AND,
            '||': TokenType.OR,
            '->': TokenType.ARROW,
            '::': TokenType.DOUBLE_COLON,
            # Single character operators (lower priority)
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '^': TokenType.POWER,
            '=': TokenType.ASSIGN,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '!': TokenType.NOT,
        }
        
        for i, (op, token_type) in enumerate(default_operators.items()):
            priority = len(op)  # Longer operators have higher priority
            self.register_operator(op, token_type, priority=priority)
    
    def load_default_punctuation(self) -> None:
        """Load default punctuation marks."""
        default_punctuation = {
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            ':': TokenType.COLON,
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
        }
        
        for punct, token_type in default_punctuation.items():
            self.register_punctuation(punct, token_type)
    
    def load_all_defaults(self) -> None:
        """Load all default tokens (keywords, operators, punctuation)."""
        self.load_default_keywords()
        self.load_default_operators()
        self.load_default_punctuation()
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about registered tokens."""
        return {
            'total_keywords': len(self.keywords),
            'total_operators': len(self.operators),
            'total_punctuation': len(self.punctuation),
            'total_definitions': len(self.definitions),
            'validation_rules': len(self.validation_rules),
            'processing_hooks': len(self.processing_hooks),
        }
