"""
Symbol Table and Type System for Semantic Analysis

This module defines the symbol table, symbol types, scopes, and type checking
for the semantic analysis phase of the compiler.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime


class DataType(Enum):
    """Supported data types in the language."""
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "bool"
    VOID = "void"
    ARRAY = "array"
    UNKNOWN = "unknown"


class SymbolKind(Enum):
    """Types of symbols that can be in the symbol table."""
    VARIABLE = "variable"
    FUNCTION = "function"
    PROCEDURE = "procedure"
    CONSTANT = "constant"
    PARAMETER = "parameter"
    CLASS = "class"
    STRUCT = "struct"


@dataclass
class TypeInfo:
    """Type information for symbols."""
    base_type: DataType
    is_array: bool = False
    array_size: Optional[int] = None
    is_pointer: bool = False
    is_const: bool = False
    
    def __str__(self) -> str:
        result = self.base_type.value
        if self.is_const:
            result = f"const {result}"
        if self.is_pointer:
            result += "*"
        if self.is_array:
            if self.array_size:
                result += f"[{self.array_size}]"
            else:
                result += "[]"
        return result
    
    @staticmethod
    def infer_from_value(value: str) -> DataType:
        """Infer data type from literal value."""
        if not value:
            return DataType.UNKNOWN
        
        value_lower = value.lower().strip()
        
        # Check for boolean
        if value_lower in ('yes', 'no', 'true', 'false'):
            return DataType.BOOLEAN
        
        # Check for null
        if value_lower in ('null', 'none'):
            return DataType.UNKNOWN
        
        # Check for string (quoted)
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return DataType.STRING
        
        # Check for number
        try:
            # Try integer
            if '.' not in value:
                int(value)
                return DataType.INT
            else:
                # Try float
                float(value)
                return DataType.FLOAT
        except ValueError:
            pass
        
        return DataType.UNKNOWN


@dataclass
class Symbol:
    """Represents a symbol in the symbol table."""
    name: str
    kind: SymbolKind
    type_info: TypeInfo
    line_number: int
    scope_level: int
    initialized: bool = False
    parameters: List['Symbol'] = field(default_factory=list)
    declarations_history: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.name} ({self.kind.value}): {self.type_info}"


class Scope:
    """Represents a scope level in the symbol table."""
    
    def __init__(self, level: int, scope_type: str = "block"):
        self.level = level
        self.scope_type = scope_type  # "global", "function", "block", "class"
        self.symbols: Dict[str, Symbol] = {}
        self.created_at = datetime.now()
        
    def insert(self, symbol: Symbol) -> bool:
        """Insert a symbol into this scope."""
        if symbol.name in self.symbols:
            return False  # Symbol already exists
        self.symbols[symbol.name] = symbol
        return True
        
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol in this scope (not parent scopes)."""
        return self.symbols.get(name, None)
        
    def get_all_symbols(self) -> List[Symbol]:
        """Get all symbols in this scope."""
        return list(self.symbols.values())
        
    def __str__(self) -> str:
        return f"Scope Level {self.level} ({self.scope_type}) - {len(self.symbols)} symbols"


class SymbolTable:
    """Main symbol table for managing scopes and symbols throughout the program."""
    
    def __init__(self):
        self.scopes: List[Scope] = []
        self.current_scope_level = 0
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Initialize global scope
        self.enter_scope("global")
        
    def enter_scope(self, scope_type: str = "block") -> None:
        """Enter a new scope level."""
        new_scope = Scope(self.current_scope_level, scope_type)
        self.scopes.append(new_scope)
        self.current_scope_level += 1
        
    def exit_scope(self) -> Optional[Scope]:
        """Exit the current scope."""
        if len(self.scopes) > 1:  # Keep at least global scope
            self.current_scope_level -= 1
            return self.scopes.pop()
        return None
        
    def declare(self, name: str, kind: SymbolKind, type_info: TypeInfo, 
                line_number: int) -> Tuple[bool, Optional[str]]:
        """Declare a symbol in the current scope."""
        current_scope = self.scopes[-1]
        
        # Check for redeclaration in same scope
        if current_scope.lookup(name):
            error = f"Line {line_number}: Symbol '{name}' already declared in this scope"
            self.errors.append(error)
            return False, error
            
        symbol = Symbol(
            name=name,
            kind=kind,
            type_info=type_info,
            line_number=line_number,
            scope_level=self.current_scope_level - 1
        )
        
        current_scope.insert(symbol)
        return True, None
        
    def lookup(self, name: str) -> Optional[Symbol]:
        """Look up a symbol, searching from current scope upwards."""
        # Search from current scope backwards to global
        for i in range(len(self.scopes) - 1, -1, -1):
            symbol = self.scopes[i].lookup(name)
            if symbol:
                return symbol
        return None
        
    def lookup_current(self, name: str) -> Optional[Symbol]:
        """Look up in current scope only."""
        if self.scopes:
            return self.scopes[-1].lookup(name)
        return None
        
    def initialize_symbol(self, name: str) -> bool:
        """Mark a symbol as initialized."""
        symbol = self.lookup(name)
        if symbol:
            symbol.initialized = True
            return True
        return False
        
    def add_error(self, error: str) -> None:
        """Add a semantic error."""
        self.errors.append(error)
        
    def add_warning(self, warning: str) -> None:
        """Add a semantic warning."""
        self.warnings.append(warning)
        
    def get_current_scope(self) -> Scope:
        """Get the current scope."""
        if self.scopes:
            return self.scopes[-1]
        return self.scopes[0]  # Global scope
        
    def get_scope_chain(self) -> List[Scope]:
        """Get the complete scope chain."""
        return self.scopes.copy()
        
    def get_all_errors(self) -> List[str]:
        """Get all semantic errors."""
        return self.errors.copy()
        
    def get_all_warnings(self) -> List[str]:
        """Get all semantic warnings."""
        return self.warnings.copy()
        
    def __str__(self) -> str:
        result = "SYMBOL TABLE\n"
        result += "=" * 60 + "\n"
        for scope in self.scopes:
            result += f"\n{scope}\n"
            result += "-" * 60 + "\n"
            for symbol in scope.get_all_symbols():
                result += f"  {symbol}\n"
        return result


class SemanticError(Exception):
    """Raised when a semantic error is encountered."""
    pass


class TypeMismatch(SemanticError):
    """Raised when there's a type mismatch."""
    pass


class UndefinedSymbol(SemanticError):
    """Raised when a symbol is used before being defined."""
    pass


class RedeclarationError(SemanticError):
    """Raised when a symbol is redeclared."""
    pass
