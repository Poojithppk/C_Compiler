"""
Token Types for Custom Compiler Language

This module defines all token types that the lexical analyzer will recognize.
Our custom language supports: variables, functions, conditionals, loops, arithmetic, 
logical operations, and security-aware programming constructs.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional


class TokenType(Enum):
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    
    # Keywords
    VAR = auto()           # Variable declaration
    CONST = auto()         # Constant declaration
    FUNC = auto()          # Function declaration
    RETURN = auto()        # Return statement
    IF = auto()            # Conditional
    ELSE = auto()          # Else clause
    ELIF = auto()          # Elif clause
    WHILE = auto()         # While loop
    FOR = auto()           # For loop
    BREAK = auto()         # Break statement
    CONTINUE = auto()      # Continue statement
    TRUE = auto()          # Boolean true
    FALSE = auto()         # Boolean false
    NULL = auto()          # Null value
    
    # Data Types
    INT = auto()           # Integer type
    FLOAT_TYPE = auto()    # Float type
    STRING_TYPE = auto()   # String type
    BOOL = auto()          # Boolean type
    
    # Operators
    PLUS = auto()          # +
    MINUS = auto()         # -
    MULTIPLY = auto()      # *
    DIVIDE = auto()        # /
    MODULO = auto()        # %
    POWER = auto()         # **
    
    # Assignment Operators
    ASSIGN = auto()        # =
    PLUS_ASSIGN = auto()   # +=
    MINUS_ASSIGN = auto()  # -=
    MULT_ASSIGN = auto()   # *=
    DIV_ASSIGN = auto()    # /=
    
    # Comparison Operators
    EQUAL = auto()         # ==
    NOT_EQUAL = auto()     # !=
    LESS_THAN = auto()     # <
    GREATER_THAN = auto()  # >
    LESS_EQUAL = auto()    # <=
    GREATER_EQUAL = auto() # >=
    
    # Logical Operators
    AND = auto()           # &&
    OR = auto()            # ||
    NOT = auto()           # !
    
    # Punctuation
    SEMICOLON = auto()     # ;
    COMMA = auto()         # ,
    DOT = auto()           # .
    COLON = auto()         # :
    
    # Brackets
    LEFT_PAREN = auto()    # (
    RIGHT_PAREN = auto()   # )
    LEFT_BRACE = auto()    # {
    RIGHT_BRACE = auto()   # }
    LEFT_BRACKET = auto()  # [
    RIGHT_BRACKET = auto() # ]
    
    # Security-Aware Keywords
    SECURE = auto()        # secure keyword for security contexts
    VALIDATE = auto()      # validate input
    SANITIZE = auto()      # sanitize data
    
    # Special Tokens
    NEWLINE = auto()       # \n
    EOF = auto()           # End of file
    ERROR = auto()         # Error token
    COMMENT = auto()       # Comments
    
    # Advanced Features
    ARROW = auto()         # -> for function returns
    DOUBLE_COLON = auto()  # :: for scope resolution


@dataclass
class Token:
    """
    Token data structure containing all information about a lexeme.
    """
    token_type: TokenType
    lexeme: str
    value: Any
    line: int
    column: int
    length: int
    
    def __str__(self) -> str:
        return f"Token({self.token_type.name}, '{self.lexeme}', {self.value}, Line: {self.line}, Col: {self.column})"
    
    def __repr__(self) -> str:
        return self.__str__()


class LexicalError(Exception):
    """Custom exception for lexical analysis errors."""
    
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexical Error at line {line}, column {column}: {message}")


# Keywords mapping for our custom language
KEYWORDS = {
    'var': TokenType.VAR,
    'const': TokenType.CONST,
    'func': TokenType.FUNC,
    'return': TokenType.RETURN,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'elif': TokenType.ELIF,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'null': TokenType.NULL,
    'int': TokenType.INT,
    'float': TokenType.FLOAT_TYPE,
    'string': TokenType.STRING_TYPE,
    'bool': TokenType.BOOL,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
    'secure': TokenType.SECURE,
    'validate': TokenType.VALIDATE,
    'sanitize': TokenType.SANITIZE,
}

# Operator mappings
OPERATORS = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '%': TokenType.MODULO,
    '**': TokenType.POWER,
    '=': TokenType.ASSIGN,
    '+=': TokenType.PLUS_ASSIGN,
    '-=': TokenType.MINUS_ASSIGN,
    '*=': TokenType.MULT_ASSIGN,
    '/=': TokenType.DIV_ASSIGN,
    '==': TokenType.EQUAL,
    '!=': TokenType.NOT_EQUAL,
    '<': TokenType.LESS_THAN,
    '>': TokenType.GREATER_THAN,
    '<=': TokenType.LESS_EQUAL,
    '>=': TokenType.GREATER_EQUAL,
    '&&': TokenType.AND,
    '||': TokenType.OR,
    '!': TokenType.NOT,
    '->': TokenType.ARROW,
    '::': TokenType.DOUBLE_COLON,
}

# Punctuation mappings
PUNCTUATION = {
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