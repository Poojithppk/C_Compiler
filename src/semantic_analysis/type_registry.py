"""
Dynamic Type Registry for Semantic Analysis

This module provides dynamic registration and management of types, type checking rules,
and type conversion rules. No hardcoded type system - all types can be registered
and configured at runtime.
"""

from typing import Dict, List, Optional, Callable, Any, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field


class TypeCategory(Enum):
    """Categories of types in the language."""
    PRIMITIVE = "primitive"
    COMPOSITE = "composite"
    FUNCTION = "function"
    CUSTOM = "custom"
    GENERIC = "generic"


@dataclass
class TypeDefinition:
    """Defines a single type for dynamic registration."""
    name: str
    category: TypeCategory
    base_types: List[str] = field(default_factory=list)  # For inheritance
    is_numeric: bool = False
    is_comparable: bool = False
    default_value: Any = None
    size_bytes: int = 0  # 0 = unknown/variable
    description: str = ""
    properties: Dict[str, 'TypeDefinition'] = field(default_factory=dict)
    methods: Dict[str, 'FunctionSignature'] = field(default_factory=dict)


@dataclass
class FunctionSignature:
    """Defines a function signature for type validation."""
    name: str
    parameter_types: List[str]
    return_type: str
    is_builtin: bool = False


class TypeRegistry:
    """
    Dynamic registry for managing all types in a language.
    Supports type registration, checking, conversion, and inference.
    """
    
    def __init__(self):
        """Initialize the type registry."""
        self.types: Dict[str, TypeDefinition] = {}
        self.type_aliases: Dict[str, str] = {}  # name -> actual type
        self.compatibility_rules: Dict[Tuple[str, str], bool] = {}  # (from_type, to_type) -> is_compatible
        self.conversion_functions: Dict[Tuple[str, str], Callable] = {}  # (from_type, to_type) -> converter
        self.validation_rules: Dict[str, Callable[[Any], bool]] = {}  # type_name -> validator
        self.type_inference_rules: Dict[str, Callable[[Any], str]] = {}  # type_name -> inferrer
        self.operator_rules: Dict[Tuple[str, str, str], Callable] = {}  # (type, op, type) -> result_type
    
    def register_type(self, type_def: TypeDefinition) -> None:
        """Register a new type dynamically."""
        self.types[type_def.name] = type_def
    
    def register_primitive_type(self, name: str, is_numeric: bool = False,
                               is_comparable: bool = True, default_value: Any = None) -> None:
        """Register a primitive type."""
        type_def = TypeDefinition(
            name=name,
            category=TypeCategory.PRIMITIVE,
            is_numeric=is_numeric,
            is_comparable=is_comparable,
            default_value=default_value
        )
        self.register_type(type_def)
    
    def register_composite_type(self, name: str, properties: Dict[str, str]) -> None:
        """Register a composite/struct type."""
        properties_defs = {}
        for prop_name, prop_type in properties.items():
            if prop_type in self.types:
                properties_defs[prop_name] = self.types[prop_type]
        
        type_def = TypeDefinition(
            name=name,
            category=TypeCategory.COMPOSITE,
            properties=properties_defs
        )
        self.register_type(type_def)
    
    def register_type_alias(self, alias: str, actual_type: str) -> None:
        """Register a type alias."""
        if actual_type not in self.types:
            raise ValueError(f"Type '{actual_type}' does not exist")
        self.type_aliases[alias] = actual_type
    
    def resolve_type(self, type_name: str) -> Optional[TypeDefinition]:
        """Resolve a type, following aliases."""
        actual_name = self.type_aliases.get(type_name, type_name)
        return self.types.get(actual_name)
    
    def register_compatibility(self, from_type: str, to_type: str, 
                             compatible: bool = True) -> None:
        """Register type compatibility rule."""
        self.compatibility_rules[(from_type, to_type)] = compatible
    
    def is_compatible(self, from_type: str, to_type: str) -> bool:
        """Check if from_type is compatible with to_type."""
        # Same type is always compatible
        if from_type == to_type:
            return True
        
        # Check if explicit rule exists
        if (from_type, to_type) in self.compatibility_rules:
            return self.compatibility_rules[(from_type, to_type)]
        
        # Check if types are numeric (numeric types can usually be converted)
        from_def = self.resolve_type(from_type)
        to_def = self.resolve_type(to_type)
        
        if from_def and to_def and from_def.is_numeric and to_def.is_numeric:
            return True
        
        return False
    
    def register_conversion(self, from_type: str, to_type: str, 
                          converter: Callable[[Any], Any]) -> None:
        """Register a type conversion function."""
        self.conversion_functions[(from_type, to_type)] = converter
    
    def convert(self, value: Any, from_type: str, to_type: str) -> Any:
        """Convert value from one type to another."""
        if from_type == to_type:
            return value
        
        key = (from_type, to_type)
        if key in self.conversion_functions:
            return self.conversion_functions[key](value)
        
        # No conversion available
        return None
    
    def register_validation_rule(self, type_name: str, 
                                validator: Callable[[Any], bool]) -> None:
        """Register a validation rule for a type."""
        self.validation_rules[type_name] = validator
    
    def validate(self, value: Any, type_name: str) -> bool:
        """Validate a value for a specific type."""
        if type_name in self.validation_rules:
            return self.validation_rules[type_name](value)
        
        # Default validation based on type definition
        type_def = self.resolve_type(type_name)
        if type_def:
            # Basic validation based on type category
            if type_def.category == TypeCategory.PRIMITIVE:
                if type_name == 'int':
                    return isinstance(value, int) and not isinstance(value, bool)
                elif type_name == 'float' or type_name == 'decimal':
                    return isinstance(value, (int, float))
                elif type_name == 'str' or type_name == 'text':
                    return isinstance(value, str)
                elif type_name == 'bool' or type_name == 'flag':
                    return isinstance(value, bool)
        
        return True
    
    def register_operator_rule(self, type1: str, operator: str, type2: str,
                              result_type: str) -> None:
        """Register an operator rule for two types."""
        self.operator_rules[(type1, operator, type2)] = result_type
    
    def get_operator_result_type(self, type1: str, operator: str, type2: str) -> Optional[str]:
        """Get the result type of an operation between two types."""
        key = (type1, operator, type2)
        if key in self.operator_rules:
            return self.operator_rules[key]
        
        # Default rules for numeric types
        type1_def = self.resolve_type(type1)
        type2_def = self.resolve_type(type2)
        
        if type1_def and type2_def and type1_def.is_numeric and type2_def.is_numeric:
            if operator in ['+', '-', '*', '/']:
                # Return the more general type
                if type1 == 'float' or type2 == 'float' or \
                   type1 == 'decimal' or type2 == 'decimal':
                    return 'float'
                return 'int'
            elif operator in ['<', '>', '<=', '>=', '==', '!=']:
                return 'bool' if type1_def.is_comparable else None
        
        return None
    
    def load_default_types(self) -> None:
        """Load default primitive types for NEXUS language."""
        self.register_primitive_type('int', is_numeric=True, is_comparable=True, default_value=0)
        self.register_primitive_type('num', is_numeric=True, is_comparable=True, default_value=0)  # Alias
        self.register_primitive_type('float', is_numeric=True, is_comparable=True, default_value=0.0)
        self.register_primitive_type('decimal', is_numeric=True, is_comparable=True, default_value=0.0)
        self.register_primitive_type('str', is_numeric=False, is_comparable=True, default_value="")
        self.register_primitive_type('text', is_numeric=False, is_comparable=True, default_value="")
        self.register_primitive_type('bool', is_numeric=False, is_comparable=True, default_value=False)
        self.register_primitive_type('flag', is_numeric=False, is_comparable=True, default_value=False)
        self.register_primitive_type('null', is_numeric=False, is_comparable=False, default_value=None)
        
        # Register type aliases
        self.register_type_alias('num', 'int')
        self.register_type_alias('text', 'str')
        self.register_type_alias('decimal', 'float')
        self.register_type_alias('flag', 'bool')
    
    def load_default_compatibility_rules(self) -> None:
        """Load default type compatibility rules."""
        # Numeric compatibility
        self.register_compatibility('int', 'float', True)
        self.register_compatibility('int', 'str', True)
        self.register_compatibility('float', 'str', True)
        
        # Reverse conversions
        self.register_compatibility('float', 'int', False)
        self.register_compatibility('str', 'int', False)
        self.register_compatibility('str', 'float', False)
    
    def load_default_operator_rules(self) -> None:
        """Load default operator rules for types."""
        # Arithmetic operators
        for type_name in ['int', 'float']:
            for op in ['+', '-', '*', '/']:
                self.register_operator_rule(type_name, op, type_name, type_name)
        
        # String concatenation
        self.register_operator_rule('str', '+', 'str', 'str')
        
        # Comparison operators
        for type_name in ['int', 'float', 'str']:
            for op in ['<', '>', '<=', '>=', '==', '!=']:
                self.register_operator_rule(type_name, op, type_name, 'bool')
    
    def load_all_defaults(self) -> None:
        """Load all default types, compatibility rules, and operators."""
        self.load_default_types()
        self.load_default_compatibility_rules()
        self.load_default_operator_rules()
    
    def get_type_info(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a type."""
        type_def = self.resolve_type(type_name)
        if not type_def:
            return None
        
        return {
            'name': type_def.name,
            'category': type_def.category.value,
            'is_numeric': type_def.is_numeric,
            'is_comparable': type_def.is_comparable,
            'default_value': type_def.default_value,
            'size_bytes': type_def.size_bytes,
            'properties': list(type_def.properties.keys()),
            'methods': list(type_def.methods.keys()),
        }
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about registered types."""
        return {
            'total_types': len(self.types),
            'type_aliases': len(self.type_aliases),
            'compatibility_rules': len(self.compatibility_rules),
            'conversion_functions': len(self.conversion_functions),
            'validation_rules': len(self.validation_rules),
            'operator_rules': len(self.operator_rules),
        }
