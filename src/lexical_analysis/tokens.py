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
    VAR = auto()           # Variable declaration (hold)
    CONST = auto()         # Constant declaration (fixed)
    FUNC = auto()          # Function declaration
    RETURN = auto()        # Return statement
    IF = auto()            # Conditional (when)
    ELSE = auto()          # Else clause (otherwise)
    ELIF = auto()          # Elif clause (otherwise when)
    WHILE = auto()         # While loop (repeat)
    FOR = auto()           # For loop (cycle)
    BREAK = auto()         # Break statement (stop)
    CONTINUE = auto()      # Continue statement (skip)
    SWITCH = auto()        # Switch statement (choose)
    CASE = auto()          # Case statement (option)
    DEFAULT = auto()       # Default case
    TRUE = auto()          # Boolean true (yes)
    FALSE = auto()         # Boolean false (no)
    NULL = auto()          # Null value
    
    # I/O Operations
    PRINT = auto()         # Output statement (show)
    INPUT = auto()         # Input statement (ask)
    
    # Data Types
    INT = auto()           # Integer type (num)
    FLOAT_TYPE = auto()    # Decimal type (decimal)
    STRING_TYPE = auto()   # String type (text)
    BOOL = auto()          # Boolean type (flag)
    
    # Type Conversion Functions
    TO_NUMBER = auto()     # Convert to number (toNumber)
    TO_DECIMAL = auto()    # Convert to decimal (toDecimal)
    TO_STRING = auto()     # Convert to string (toString)
    TO_BOOLEAN = auto()    # Convert to boolean (toBoolean)
    IS_NUMBER = auto()     # Check if number (isNumber)
    
    # String Functions
    LENGTH = auto()        # String length function
    UPPERCASE = auto()     # Convert to uppercase
    LOWERCASE = auto()     # Convert to lowercase
    TRIM = auto()          # Trim whitespace
    SUBSTRING = auto()     # Extract substring
    FORMAT = auto()        # String formatting
    
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


# Keywords mapping for NEXUS programming language
KEYWORDS = {
    # Variable and constant declarations
    'hold': TokenType.VAR,           # Variable declaration
    'fixed': TokenType.CONST,        # Constant declaration
    
    # Data types
    'num': TokenType.INT,            # Integer type
    'decimal': TokenType.FLOAT_TYPE, # Decimal/float type
    'text': TokenType.STRING_TYPE,   # String type
    'flag': TokenType.BOOL,          # Boolean type
    
    # Function keywords
    'func': TokenType.FUNC,          # Function declaration
    'return': TokenType.RETURN,      # Return statement
    
    # Control flow
    'when': TokenType.IF,            # Conditional statement
    'otherwise': TokenType.ELSE,     # Else clause
    'otherwise when': TokenType.ELIF, # Elif clause
    
    # Loop keywords
    'repeat': TokenType.WHILE,       # While loop
    'cycle': TokenType.FOR,          # For loop
    'stop': TokenType.BREAK,         # Break statement
    'skip': TokenType.CONTINUE,      # Continue statement
    
    # Switch statement
    'choose': TokenType.SWITCH,      # Switch statement
    'option': TokenType.CASE,        # Case statement
    'default': TokenType.DEFAULT,    # Default case
    
    # Boolean values
    'yes': TokenType.TRUE,           # Boolean true
    'no': TokenType.FALSE,           # Boolean false
    'null': TokenType.NULL,          # Null value
    
    # Logical operators (as words)
    'and': TokenType.AND,            # Logical AND
    'or': TokenType.OR,              # Logical OR
    'not': TokenType.NOT,            # Logical NOT
    
    # I/O operations
    'show': TokenType.PRINT,         # Output statement
    'ask': TokenType.INPUT,          # Input statement
    
    # Security-aware keywords (keeping these unique)
    'secure': TokenType.SECURE,      # Security context
    'validate': TokenType.VALIDATE,  # Validate input
    'sanitize': TokenType.SANITIZE,  # Sanitize data
    
    # Type conversion functions
    'toNumber': TokenType.TO_NUMBER, # Convert to number
    'toDecimal': TokenType.TO_DECIMAL, # Convert to decimal
    'toString': TokenType.TO_STRING, # Convert to string
    'toBoolean': TokenType.TO_BOOLEAN, # Convert to boolean
    'isNumber': TokenType.IS_NUMBER, # Check if number
    
    # String functions
    'length': TokenType.LENGTH,      # String length function
    'uppercase': TokenType.UPPERCASE, # Convert to uppercase
    'lowercase': TokenType.LOWERCASE, # Convert to lowercase
    'trim': TokenType.TRIM,          # Trim whitespace
    'substring': TokenType.SUBSTRING, # Extract substring
    'format': TokenType.FORMAT,      # String formatting
}

# Operator mappings
OPERATORS = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '%': TokenType.MODULO,
    '^': TokenType.POWER,        # Exponentiation operator
    '**': TokenType.POWER,       # Alternative exponentiation
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