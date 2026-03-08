"""
NEXUS Language Grammar Definition

This file defines the complete grammar rules for the NEXUS programming language
using Extended Backus-Naur Form (EBNF) notation.

Grammar Productions:
"""

# ===============================
# NEXUS LANGUAGE GRAMMAR (EBNF)
# ===============================

NEXUS_GRAMMAR = """

program          → declaration* EOF

declaration      → varDecl
                 | constDecl  
                 | funcDecl
                 | statement

// Variable Declarations
varDecl          → "hold" IDENTIFIER ( ":" type )? ( "=" expression )? ";"
constDecl        → "fixed" IDENTIFIER ( ":" type )? "=" expression ";"

// Function Declarations
funcDecl         → "func" IDENTIFIER "(" parameters? ")" ( "->" type )? block
parameters       → parameter ( "," parameter )*
parameter        → IDENTIFIER ":" type

// Types
type             → "num" | "decimal" | "text" | "flag"

// Statements
statement        → exprStmt
                 | printStmt
                 | returnStmt
                 | ifStmt
                 | whileStmt
                 | forStmt
                 | breakStmt
                 | continueStmt
                 | block
                 | secureBlock

exprStmt         → expression ";"
printStmt        → "show" expression ";"
returnStmt       → "return" expression? ";"

// Control Flow
ifStmt           → "when" "(" expression ")" statement 
                   ( "otherwise" "when" "(" expression ")" statement )*
                   ( "otherwise" statement )?

whileStmt        → "repeat" "(" expression ")" statement
forStmt          → "cycle" "(" ( varDecl | exprStmt | ";" )
                              expression? ";"
                              expression? ")" statement

breakStmt        → "stop" ";"
continueStmt     → "skip" ";"

// Blocks
block            → "{" declaration* "}"
secureBlock      → "secure" "{" declaration* "}"

// Expressions (in order of precedence - lowest to highest)
expression       → assignment

assignment       → ( call "." )? IDENTIFIER assignOp assignment
                 | logicalOr

assignOp         → "=" | "+=" | "-=" | "*=" | "/="

logicalOr        → logicalAnd ( ( "or" | "||" ) logicalAnd )*
logicalAnd       → equality ( ( "and" | "&&" ) equality )*
equality         → comparison ( ( "!=" | "==" ) comparison )*
comparison       → term ( ( ">" | ">=" | "<" | "<=" ) term )*
term             → factor ( ( "-" | "+" ) factor )*
factor           → unary ( ( "/" | "*" | "%" ) unary )*
unary            → ( "not" | "!" | "-" | "+" ) unary | power
power            → call ( "**" call )*
call             → primary ( "(" arguments? ")" | "." IDENTIFIER )*
primary          → "yes" | "no" | "null" | NUMBER | STRING | IDENTIFIER 
                 | "(" expression ")" | securityExpr

// Security Expressions
securityExpr     → validateExpr | sanitizeExpr
validateExpr     → "validate" "(" expression ( "," expression )? ")"
sanitizeExpr     → "sanitize" "(" expression ")"

// Function Call Arguments
arguments        → expression ( "," expression )*

// Lexical Rules
NUMBER           → DIGIT+ ( "." DIGIT+ )?
STRING           → '"' ( [^"\\] | escape )* '"'
IDENTIFIER       → ALPHA ( ALPHA | DIGIT | "_" )*
ALPHA            → [a-zA-Z_]
DIGIT            → [0-9]

// Comments
COMMENT          → "//" [^\\n]* \\n

"""

# Operator Precedence (from highest to lowest)
PRECEDENCE_TABLE = {
    'CALL': 12,         # function(), array[]
    'POWER': 11,        # **
    'UNARY': 10,        # -, +, !, not
    'MULTIPLICATIVE': 9, # *, /, %
    'ADDITIVE': 8,      # +, -
    'COMPARISON': 7,    # <, <=, >, >=
    'EQUALITY': 6,      # ==, !=
    'LOGICAL_AND': 5,   # &&, and
    'LOGICAL_OR': 4,    # ||, or
    'ASSIGNMENT': 3,    # =, +=, -=, *=, /=
    'SEQUENCE': 2,      # ,
    'LOWEST': 1         # statement level
}

# Associativity rules
ASSOCIATIVITY = {
    'POWER': 'RIGHT',          # a ** b ** c = a ** (b ** c)
    'ASSIGNMENT': 'RIGHT',     # a = b = c = a = (b = c)
    'UNARY': 'RIGHT',         # !-x = !(-x)
    'DEFAULT': 'LEFT'         # Most operators are left-associative
}

# Binary operator mapping to precedence
BINARY_OPERATORS = {
    # Arithmetic
    '+': PRECEDENCE_TABLE['ADDITIVE'],
    '-': PRECEDENCE_TABLE['ADDITIVE'],
    '*': PRECEDENCE_TABLE['MULTIPLICATIVE'],
    '/': PRECEDENCE_TABLE['MULTIPLICATIVE'],
    '%': PRECEDENCE_TABLE['MULTIPLICATIVE'],
    '**': PRECEDENCE_TABLE['POWER'],
    
    # Comparison
    '<': PRECEDENCE_TABLE['COMPARISON'],
    '<=': PRECEDENCE_TABLE['COMPARISON'],
    '>': PRECEDENCE_TABLE['COMPARISON'],
    '>=': PRECEDENCE_TABLE['COMPARISON'],
    '==': PRECEDENCE_TABLE['EQUALITY'],
    '!=': PRECEDENCE_TABLE['EQUALITY'],
    
    # Logical
    'and': PRECEDENCE_TABLE['LOGICAL_AND'],
    '&&': PRECEDENCE_TABLE['LOGICAL_AND'],
    'or': PRECEDENCE_TABLE['LOGICAL_OR'],
    '||': PRECEDENCE_TABLE['LOGICAL_OR'],
    
    # Assignment
    '=': PRECEDENCE_TABLE['ASSIGNMENT'],
    '+=': PRECEDENCE_TABLE['ASSIGNMENT'],
    '-=': PRECEDENCE_TABLE['ASSIGNMENT'],
    '*=': PRECEDENCE_TABLE['ASSIGNMENT'],
    '/=': PRECEDENCE_TABLE['ASSIGNMENT'],
}

# Unary operator mapping
UNARY_OPERATORS = {
    '-': PRECEDENCE_TABLE['UNARY'],
    '+': PRECEDENCE_TABLE['UNARY'],
    '!': PRECEDENCE_TABLE['UNARY'],
    'not': PRECEDENCE_TABLE['UNARY'],
}

# Grammar rule descriptions for error messages
RULE_DESCRIPTIONS = {
    'program': 'program structure',
    'declaration': 'variable, constant, or function declaration',
    'statement': 'statement',
    'expression': 'expression',
    'primary': 'primary expression (identifier, literal, or grouped expression)',
    'block': 'code block',
    'parameters': 'function parameters',
    'arguments': 'function arguments',
    'type': 'type annotation',
}

# Expected tokens for each grammar rule (for error recovery)
EXPECTED_TOKENS = {
    'declaration_start': ['hold', 'fixed', 'func', 'when', 'repeat', 'cycle', 'show', 'return', 'stop', 'skip', '{', 'secure'],
    'expression_start': ['(', 'IDENTIFIER', 'NUMBER', 'STRING', 'yes', 'no', 'null', '-', '+', '!', 'not', 'validate', 'sanitize'],
    'statement_start': ['hold', 'fixed', 'show', 'return', 'when', 'repeat', 'cycle', 'stop', 'skip', '{', 'secure', 'IDENTIFIER', '('],
    'type_keywords': ['num', 'decimal', 'text', 'flag'],
    'literal_values': ['NUMBER', 'STRING', 'yes', 'no', 'null'],
    'binary_operators': ['+', '-', '*', '/', '%', '**', '<', '<=', '>', '>=', '==', '!=', 'and', '&&', 'or', '||'],
    'assignment_operators': ['=', '+=', '-=', '*=', '/='],
    'unary_operators': ['-', '+', '!', 'not'],
}

# First sets for each non-terminal (for predictive parsing)
FIRST_SETS = {
    'program': ['hold', 'fixed', 'func', 'when', 'repeat', 'cycle', 'show', 'return', 'stop', 'skip', '{', 'secure', 'IDENTIFIER', 'EOF'],
    'declaration': ['hold', 'fixed', 'func'],
    'statement': ['show', 'return', 'when', 'repeat', 'cycle', 'stop', 'skip', '{', 'secure', 'IDENTIFIER', '('],
    'expression': ['(', 'IDENTIFIER', 'NUMBER', 'STRING', 'yes', 'no', 'null', '-', '+', '!', 'not', 'validate', 'sanitize'],
    'block': ['{'],
    'secureBlock': ['secure'],
}

# Follow sets for each non-terminal (for error recovery)
FOLLOW_SETS = {
    'program': ['EOF'],
    'declaration': ['hold', 'fixed', 'func', 'when', 'repeat', 'cycle', 'show', 'return', 'stop', 'skip', '{', 'secure', 'IDENTIFIER', 'EOF', '}'],
    'statement': ['hold', 'fixed', 'func', 'when', 'repeat', 'cycle', 'show', 'return', 'stop', 'skip', '{', 'secure', 'IDENTIFIER', 'EOF', '}', 'otherwise'],
    'expression': [';', ')', '}', ',', 'otherwise'],
    'block': ['hold', 'fixed', 'func', 'when', 'repeat', 'cycle', 'show', 'return', 'stop', 'skip', '{', 'secure', 'IDENTIFIER', 'EOF', '}', 'otherwise'],
}

# Error recovery synchronization tokens
SYNC_TOKENS = [';', '}', 'hold', 'fixed', 'func', 'when', 'repeat', 'cycle', 'show', 'return', 'EOF']

# Grammar validation functions
def is_binary_operator(token_type_or_lexeme):
    """Check if a token represents a binary operator."""
    return token_type_or_lexeme in BINARY_OPERATORS

def is_unary_operator(token_type_or_lexeme):
    """Check if a token represents a unary operator.""" 
    return token_type_or_lexeme in UNARY_OPERATORS

def is_assignment_operator(token_type_or_lexeme):
    """Check if a token represents an assignment operator."""
    return token_type_or_lexeme in ['=', '+=', '-=', '*=', '/=']

def get_precedence(operator):
    """Get the precedence level of an operator."""
    return BINARY_OPERATORS.get(operator, 0)

def is_right_associative(operator):
    """Check if an operator is right-associative."""
    if operator in ['**', '=', '+=', '-=', '*=', '/=']:
        return True
    return False

def is_statement_start(token):
    """Check if a token can start a statement."""
    return token in EXPECTED_TOKENS['statement_start']

def is_expression_start(token):
    """Check if a token can start an expression."""
    return token in EXPECTED_TOKENS['expression_start']