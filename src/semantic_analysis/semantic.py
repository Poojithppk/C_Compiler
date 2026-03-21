"""
Semantic Analyzer for the NEXUS Compiler

This module performs semantic analysis on the Abstract Syntax Tree,
including type checking, symbol table management, and validation.
"""

from typing import List, Optional, Dict, Any, Tuple
import sys
from pathlib import Path

from .semantic_symbols import (
    SymbolTable, DataType, SymbolKind, TypeInfo, SemanticError, 
    UndefinedSymbol, TypeMismatch, RedeclarationError
)

# Try to import AST nodes from syntax analysis
try:
    from syntax_analysis.ast_nodes import (
    ASTNode, ProgramNode, VarDeclarationNode, FunctionDeclarationNode,
    PrintStatementNode, IdentifierNode, LiteralNode
)
except ImportError:
    # Fallback if importing from different location
    ASTNode = None


class SemanticAnalyzer:
    """
    Semantic analyzer for AST validation and type checking.
    
    Performs:
    - Symbol table management
    - Type checking
    - Scope validation
    - Variable usage analysis
    - Function call validation
    """
    
    def __init__(self, visual_mode: bool = True):
        self.symbol_table = SymbolTable()
        self.visual_mode = visual_mode
        self.analysis_steps: List[Dict[str, Any]] = []
        self.current_function: Optional[str] = None
        self.visual_callback = None
        self.error_callback = None
        
        # Statistics
        self.total_symbols = 0
        self.total_errors = 0
        self.total_warnings = 0
        
    def set_visual_callback(self, callback):
        """Set callback for visual updates during analysis."""
        self.visual_callback = callback
        
    def set_error_callback(self, callback):
        """Set callback for error reporting."""
        self.error_callback = callback
        
    def analyze(self, ast: ASTNode) -> Tuple[bool, List[str], List[str]]:
        """
        Perform semantic analysis on the AST.
        
        Returns:
            Tuple of (success: bool, errors: List[str], warnings: List[str])
        """
        try:
            self.analysis_steps = []
            self.symbol_table = SymbolTable()
            
            # Build symbol table and perform type checking
            self._visit(ast)
            
            # Collect results
            errors = self.symbol_table.get_all_errors()
            warnings = self.symbol_table.get_all_warnings()
            
            self.total_errors = len(errors)
            self.total_warnings = len(warnings)
            
            if self.visual_mode and self.error_callback and errors:
                for error in errors:
                    self.error_callback(error)
                    
            return len(errors) == 0, errors, warnings
            
        except SemanticError as e:
            error_msg = str(e)
            self.symbol_table.add_error(error_msg)
            if self.error_callback:
                self.error_callback(error_msg)
            return False, [error_msg], []
            
    def _visit(self, node: ASTNode) -> Any:
        """Visit an AST node and perform semantic analysis."""
        if node is None:
            return None
            
        # Get node type
        node_type = type(node).__name__
        
        # Route to appropriate visitor method
        method_name = f"_visit_{node_type}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            # Generic visit for unknown node types
            return self._visit_generic(node)
            
    def _visit_generic(self, node: ASTNode) -> Any:
        """Generic visitor for unknown node types."""
        node_type = type(node).__name__
        
        # Try to extract useful info from the node
        if hasattr(node, '__dict__'):
            node_dict = node.__dict__
            
            # Log this node type for debugging
            self._record_step("Node Visit", f"Processing {node_type}")
            
            # Visit children if they exist
            if hasattr(node, 'children') and node.children:
                for child in node.children:
                    self._visit(child)
            
            # Handle common node attributes
            if hasattr(node, 'declarations'):
                for decl in node.declarations:
                    self._visit(decl)
            
            if hasattr(node, 'statements'):
                for stmt in node.statements:
                    self._visit(stmt)
            
            if hasattr(node, 'body') and node.body:
                self._visit(node.body)
        
        return None
        
    def _visit_ProgramNode(self, node) -> None:
        """Visit a program node."""
        statements = node.statements if hasattr(node, 'statements') else []
        self._record_step("Analysis Started", f"Analyzing program with {len(statements)} statements")
        
        # Visit all statements
        for statement in statements:
            self._visit(statement)
            
        self._record_step("Analysis Complete", 
                         f"Total symbols: {self.total_symbols}, Errors: {self.total_errors}")
        
    def _visit_VarDeclarationNode(self, node) -> None:
        """Visit a variable declaration."""
        try:
            var_name = node.name if hasattr(node, 'name') else "unknown"
            line_num = node.line if hasattr(node, 'line') else 0
            
            # Determine type
            var_type = self._parse_type(node)
            
            # If type is unknown, try to infer from initializer
            if var_type == DataType.UNKNOWN and hasattr(node, 'initializer') and node.initializer:
                var_type = self._infer_expression_type(node.initializer)
            
            type_info = TypeInfo(base_type=var_type)
            
            # Declare in current scope
            success, error = self.symbol_table.declare(
                var_name, 
                SymbolKind.VARIABLE, 
                type_info, 
                line_num
            )
            
            if success:
                self.total_symbols += 1
                
                # Mark as initialized if it has an initializer
                if hasattr(node, 'initializer') and node.initializer:
                    self.symbol_table.initialize_symbol(var_name)
                
                self._record_step(
                    "Variable Declared",
                    f"Variable '{var_name}' declared as {var_type.value} at line {line_num}"
                )
            else:
                self._record_step("Error", error)
                
        except Exception as e:
            error_msg = f"Error declaring variable: {str(e)}"
            self.symbol_table.add_error(error_msg)
            self._record_step("Error", error_msg)
            
    def _visit_FunctionDeclarationNode(self, node) -> None:
        """Visit a function declaration."""
        try:
            func_name = node.name if hasattr(node, 'name') else "unknown"
            line_num = node.line if hasattr(node, 'line') else 0
            
            # Declare function in symbol table
            return_type = self._parse_type(node)
            type_info = TypeInfo(base_type=return_type)
            
            success, error = self.symbol_table.declare(
                func_name,
                SymbolKind.FUNCTION,
                type_info,
                line_num
            )
            
            if success:
                self._record_step(
                    "Function Declared",
                    f"Function '{func_name}' declared at line {line_num}"
                )
                self.total_symbols += 1
                
                # Enter function scope
                self.current_function = func_name
                self.symbol_table.enter_scope("function")
                
                # Process parameters if they exist
                if hasattr(node, 'parameters') and node.parameters:
                    for param in node.parameters:
                        self._visit(param)
                        
                # Process function body
                if hasattr(node, 'body') and node.body:
                    self._visit(node.body)
                    
                # Exit function scope
                self.symbol_table.exit_scope()
                self.current_function = None
            else:
                self._record_step("Error", error)
                
        except Exception as e:
            error_msg = f"Error declaring function: {str(e)}"
            self.symbol_table.add_error(error_msg)
            self._record_step("Error", error_msg)
            
    def _visit_ParameterNode(self, node) -> None:
        """Visit a parameter declaration."""
        try:
            param_name = node.name if hasattr(node, 'name') else "unknown"
            line_num = node.line if hasattr(node, 'line') else 0
            
            param_type = self._parse_type(node)
            type_info = TypeInfo(base_type=param_type)
            
            success, error = self.symbol_table.declare(
                param_name,
                SymbolKind.PARAMETER,
                type_info,
                line_num
            )
            
            if success:
                self._record_step(
                    "Parameter Declared",
                    f"Parameter '{param_name}' declared as {param_type.value}"
                )
                self.total_symbols += 1
                # Mark parameter as initialized
                self.symbol_table.initialize_symbol(param_name)
            else:
                self._record_step("Error", error)
                
        except Exception as e:
            error_msg = f"Error declaring parameter: {str(e)}"
            self.symbol_table.add_error(error_msg)
            self._record_step("Error", error_msg)
            
    def _visit_ID(self, node) -> None:
        """Visit an identifier usage."""
        try:
            name = node.value if hasattr(node, 'value') else str(node)
            line_num = node.line if hasattr(node, 'line') else 0
            
            # Check if symbol is defined
            symbol = self.symbol_table.lookup(name)
            if not symbol:
                error = f"Line {line_num}: Undefined symbol '{name}'"
                self.symbol_table.add_error(error)
                self._record_step("Undefined Symbol", error)
                raise UndefinedSymbol(error)
            else:
                self._record_step(
                    "Symbol Found",
                    f"Using symbol '{name}' (defined at line {symbol.line_number})"
                )
                
        except UndefinedSymbol:
            pass  # Already recorded
        except Exception as e:
            error_msg = f"Error visiting identifier: {str(e)}"
            self._record_step("Error", error_msg)
    
    def _visit_AssignmentNode(self, node) -> None:
        """Visit an assignment statement."""
        try:
            # Get variable name
            target_name = None
            if hasattr(node, 'target'):
                if hasattr(node.target, 'name'):
                    target_name = node.target.name
                elif hasattr(node.target, 'value'):
                    target_name = node.target.value
            
            if not target_name:
                target_name = "unknown"
            
            line_num = node.line if hasattr(node, 'line') else 0
            
            # Check if target variable exists
            symbol = self.symbol_table.lookup(target_name)
            if not symbol:
                error = f"Line {line_num}: Undefined symbol '{target_name}' in assignment"
                self.symbol_table.add_error(error)
                self._record_step("Assignment Error", error)
            else:
                # Mark as initialized
                self.symbol_table.initialize_symbol(target_name)
                self._record_step(
                    "Assignment",
                    f"Variable '{target_name}' assigned at line {line_num}"
                )
            
            # Visit value expression if present
            if hasattr(node, 'value') and node.value:
                self._visit(node.value)
                
        except Exception as e:
            error_msg = f"Error in assignment: {str(e)}"
            self.symbol_table.add_error(error_msg)
            self._record_step("Error", error_msg)
    
    def _visit_BinaryOpNode(self, node) -> None:
        """Visit a binary operation (expression)."""
        try:
            # Visit left operand
            if hasattr(node, 'left'):
                self._visit(node.left)
            
            # Visit right operand
            if hasattr(node, 'right'):
                self._visit(node.right)
        except Exception as e:
            error_msg = f"Error in binary operation: {str(e)}"
            self._record_step("Error", error_msg)
    
    def _visit_CallNode(self, node) -> None:
        """Visit a function call."""
        try:
            func_name = None
            if hasattr(node, 'callee'):
                if hasattr(node.callee, 'name'):
                    func_name = node.callee.name
                elif hasattr(node.callee, 'value'):
                    func_name = node.callee.value
            
            if not func_name:
                func_name = "unknown"
            
            line_num = node.line if hasattr(node, 'line') else 0
            
            # Check if function is defined
            symbol = self.symbol_table.lookup(func_name)
            if not symbol:
                error = f"Line {line_num}: Undefined function '{func_name}'"
                self.symbol_table.add_error(error)
                self._record_step("Undefined Function", error)
            elif symbol.kind != SymbolKind.FUNCTION and symbol.kind != SymbolKind.PROCEDURE:
                error = f"Line {line_num}: '{func_name}' is not a function"
                self.symbol_table.add_error(error)
                self._record_step("Type Error", error)
            else:
                self._record_step(
                    "Function Call",
                    f"Calling function '{func_name}' at line {line_num}"
                )
            
            # Visit arguments
            if hasattr(node, 'arguments') and node.arguments:
                for arg in node.arguments:
                    self._visit(arg)
                    
        except Exception as e:
            error_msg = f"Error in function call: {str(e)}"
            self._record_step("Error", error_msg)
    
    def _visit_PrintStatementNode(self, node) -> None:
        """Visit a print/show statement."""
        try:
            # Visit the expression being printed
            if hasattr(node, 'expression') and node.expression:
                self._visit(node.expression)
            
            self._record_step("Print Statement", "Processing print/show statement")
            
        except Exception as e:
            error_msg = f"Error in print statement: {str(e)}"
            self._record_step("Error", error_msg)
    
    def _visit_BinaryExpressionNode(self, node) -> DataType:
        """Visit a binary expression and infer its type."""
        try:
            # Infer types of both operands
            left_type = self._infer_expression_type(node.left) if hasattr(node, 'left') else DataType.UNKNOWN
            right_type = self._infer_expression_type(node.right) if hasattr(node, 'right') else DataType.UNKNOWN
            
            # Determine result type based on operator and operand types
            if left_type == DataType.INT and right_type == DataType.INT:
                return DataType.INT
            elif (left_type in (DataType.INT, DataType.FLOAT) and 
                  right_type in (DataType.INT, DataType.FLOAT)):
                return DataType.FLOAT
            elif left_type == DataType.STRING or right_type == DataType.STRING:
                # String concatenation
                return DataType.STRING
            else:
                return DataType.UNKNOWN
                
        except Exception as e:
            error_msg = f"Error inferring binary expression type: {str(e)}"
            self._record_step("Error", error_msg)
            return DataType.UNKNOWN
    
    def _visit_LiteralNode(self, node) -> DataType:
        """Visit a literal and infer its type."""
        try:
            if hasattr(node, 'value'):
                return TypeInfo.infer_from_value(str(node.value))
            return DataType.UNKNOWN
        except Exception as e:
            error_msg = f"Error inferring literal type: {str(e)}"
            self._record_step("Error", error_msg)
            return DataType.UNKNOWN
    
    def _infer_expression_type(self, expr_node) -> DataType:
        """Recursively infer the type of an expression."""
        if expr_node is None:
            return DataType.UNKNOWN
        
        node_type = type(expr_node).__name__
        
        if node_type == 'BinaryExpressionNode':
            return self._visit_BinaryExpressionNode(expr_node)
        elif node_type == 'LiteralNode':
            return self._visit_LiteralNode(expr_node)
        elif node_type == 'IdentifierNode':
            # Look up the variable to get its type
            var_name = expr_node.name if hasattr(expr_node, 'name') else None
            if var_name:
                symbol = self.symbol_table.lookup(var_name)
                if symbol:
                    return symbol.type_info.base_type
            return DataType.UNKNOWN
        elif node_type == 'UnaryExpressionNode':
            # For unary expressions, return the operand type
            if hasattr(expr_node, 'operand'):
                return self._infer_expression_type(expr_node.operand)
            return DataType.UNKNOWN
        else:
            # Try to infer from value attribute (for literals)
            if hasattr(expr_node, 'value'):
                return TypeInfo.infer_from_value(str(expr_node.value))
            return DataType.UNKNOWN
    
    def _visit_IdentifierNode(self, node) -> None:
        """Visit an identifier node."""
        try:
            name = node.name if hasattr(node, 'name') else "unknown"
            line_num = node.line if hasattr(node, 'line') else 0
            
            # Check if symbol is defined
            symbol = self.symbol_table.lookup(name)
            if not symbol:
                error = f"Line {line_num}: Undefined symbol '{name}'"
                self.symbol_table.add_error(error)
                self._record_step("Undefined Symbol", error)
            else:
                self._record_step(
                    "Symbol Found",
                    f"Using symbol '{name}' (defined at line {symbol.line_number})"
                )
                
        except Exception as e:
            error_msg = f"Error visiting identifier: {str(e)}"
            self._record_step("Error", error_msg)
    
    def _parse_type(self, node) -> DataType:
        """Parse type information from an AST node."""
        try:
            # Check for type attribute (from AST node)
            type_str = None
            
            if hasattr(node, 'type'):
                type_str = str(node.type).lower()
            elif hasattr(node, 'data_type'):
                type_str = str(node.data_type).lower()
            elif hasattr(node, 'type_name'):
                type_str = str(node.type_name).lower()
            
            if not type_str:
                return DataType.UNKNOWN
            
            # Map NEXUS language types to DataType
            # NEXUS types: num (int), decimal (float), text (string), flag (bool)
            if 'num' in type_str or 'int' in type_str or 'integer' in type_str:
                return DataType.INT
            elif 'decimal' in type_str or 'float' in type_str or 'real' in type_str:
                return DataType.FLOAT
            elif 'text' in type_str or 'string' in type_str or 'char' in type_str:
                return DataType.STRING
            elif 'flag' in type_str or 'bool' in type_str or 'boolean' in type_str:
                return DataType.BOOLEAN
            elif 'void' in type_str:
                return DataType.VOID
            else:
                return DataType.UNKNOWN
        except:
            return DataType.UNKNOWN
            
    def _record_step(self, step_type: str, description: str) -> None:
        """Record an analysis step for visualization."""
        step = {
            'type': step_type,
            'description': description,
            'symbol_count': self.total_symbols,
            'error_count': len(self.symbol_table.get_all_errors()),
            'warning_count': len(self.symbol_table.get_all_warnings())
        }
        self.analysis_steps.append(step)
        
        if self.visual_mode and self.visual_callback:
            self.visual_callback(step)
            
    def get_symbol_table(self) -> SymbolTable:
        """Get the symbol table."""
        return self.symbol_table
        
    def get_analysis_steps(self) -> List[Dict[str, Any]]:
        """Get all analysis steps."""
        return self.analysis_steps.copy()
        
    def get_statistics(self) -> Dict[str, int]:
        """Get analysis statistics."""
        return {
            'total_symbols': self.total_symbols,
            'total_errors': self.total_errors,
            'total_warnings': self.total_warnings,
            'scopes': len(self.symbol_table.scopes)
        }
