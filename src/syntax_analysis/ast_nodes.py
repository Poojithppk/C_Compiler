"""
Abstract Syntax Tree Node Definitions for NEXUS Language

This module defines all AST node types for the NEXUS programming language.
Each node represents a syntactic construct in the language.
"""

from abc import ABC, abstractmethod
from typing import List, Any, Optional, Union
from dataclasses import dataclass
from lexical_analysis.tokens import Token, TokenType


# Base AST Node
class ASTNode(ABC):
    """Base class for all AST nodes."""
    
    def __init__(self, line: int = 0, column: int = 0):
        self.line = line
        self.column = column
        self.parent: Optional['ASTNode'] = None
        self.children: List['ASTNode'] = []
    
    @abstractmethod
    def accept(self, visitor) -> Any:
        """Accept a visitor for the visitor pattern."""
        pass
    
    def add_child(self, child: 'ASTNode') -> None:
        """Add a child node."""
        child.parent = self
        self.children.append(child)
    
    def __str__(self) -> str:
        return self.__class__.__name__


# Program Structure
@dataclass
class ProgramNode(ASTNode):
    """Root node representing the entire program."""
    statements: List[ASTNode]
    
    def accept(self, visitor) -> Any:
        return visitor.visit_program(self)


@dataclass 
class BlockNode(ASTNode):
    """Block of statements enclosed in braces."""
    statements: List[ASTNode]
    
    def accept(self, visitor) -> Any:
        return visitor.visit_block(self)


# Declarations
class VarDeclarationNode(ASTNode):
    """Variable declaration: hold x = 5;"""
    
    def __init__(self, name: str, data_type: Optional[str], initializer: Optional[ASTNode], 
                 is_constant: bool = False, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.data_type = data_type
        self.initializer = initializer
        self.is_constant = is_constant
    
    def accept(self, visitor) -> Any:
        return visitor.visit_var_declaration(self)


@dataclass
class FunctionDeclarationNode(ASTNode):
    """Function declaration: func add(x: num, y: num) -> num { ... }"""
    name: str
    parameters: List['ParameterNode']
    return_type: Optional[str]
    body: BlockNode
    
    def accept(self, visitor) -> Any:
        return visitor.visit_function_declaration(self)


class ParameterNode(ASTNode):
    """Function parameter: x: num"""
    
    def __init__(self, name: str, data_type: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.data_type = data_type
    
    def accept(self, visitor) -> Any:
        return visitor.visit_parameter(self)


# Statements  
class ExpressionStatementNode(ASTNode):
    """Expression used as statement."""
    
    def __init__(self, expression: ASTNode, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expression = expression
    
    def accept(self, visitor) -> Any:
        return visitor.visit_expression_statement(self)


class ReturnStatementNode(ASTNode):
    """Return statement: return expression;"""
    
    def __init__(self, value: Optional[ASTNode], line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value
    
    def accept(self, visitor) -> Any:
        return visitor.visit_return_statement(self)


@dataclass
class IfStatementNode(ASTNode):
    """If statement: when (condition) { ... } otherwise { ... }"""
    condition: ASTNode
    then_branch: ASTNode
    else_branch: Optional[ASTNode]
    line: int = 0
    column: int = 0
    
    def accept(self, visitor) -> Any:
        return visitor.visit_if_statement(self)


@dataclass
class WhileStatementNode(ASTNode):
    """While loop: repeat (condition) { ... }"""
    condition: ASTNode
    body: ASTNode
    line: int = 0
    column: int = 0
    
    def accept(self, visitor) -> Any:
        return visitor.visit_while_statement(self)


@dataclass
class ForStatementNode(ASTNode):
    """For loop: cycle (init; condition; update) { ... }"""
    initializer: Optional[ASTNode]
    condition: Optional[ASTNode]
    increment: Optional[ASTNode]
    body: ASTNode
    line: int = 0
    column: int = 0
    
    def accept(self, visitor) -> Any:
        return visitor.visit_for_statement(self)


@dataclass
class BreakStatementNode(ASTNode):
    """Break statement: stop;"""
    line: int = 0
    column: int = 0
    
    def accept(self, visitor) -> Any:
        return visitor.visit_break_statement(self)


@dataclass
class ContinueStatementNode(ASTNode):
    """Continue statement: skip;"""
    line: int = 0
    column: int = 0
    
    def accept(self, visitor) -> Any:
        return visitor.visit_continue_statement(self)


class PrintStatementNode(ASTNode):
    """Print statement: show expression;"""
    
    def __init__(self, expression: ASTNode, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expression = expression
    
    def accept(self, visitor) -> Any:
        return visitor.visit_print_statement(self)


# Expressions
@dataclass
class BinaryExpressionNode(ASTNode):
    """Binary expression: left operator right"""
    left: ASTNode
    operator: Token
    right: ASTNode
    
    def accept(self, visitor) -> Any:
        return visitor.visit_binary_expression(self)


@dataclass
class UnaryExpressionNode(ASTNode):
    """Unary expression: operator operand"""
    operator: Token
    operand: ASTNode
    
    def accept(self, visitor) -> Any:
        return visitor.visit_unary_expression(self)


class AssignmentExpressionNode(ASTNode):
    """Assignment expression: name = value"""
    
    def __init__(self, name: str, operator: Token, value: ASTNode, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.operator = operator  # =, +=, -=, etc.
        self.value = value
    
    def accept(self, visitor) -> Any:
        return visitor.visit_assignment_expression(self)


class CallExpressionNode(ASTNode):
    """Function call: name(arguments)"""
    
    def __init__(self, callee: ASTNode, arguments: List[ASTNode], line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.callee = callee
        self.arguments = arguments
    
    def accept(self, visitor) -> Any:
        return visitor.visit_call_expression(self)


@dataclass
class GroupingExpressionNode(ASTNode):
    """Grouped expression: (expression)"""
    expression: ASTNode
    line: int = 0
    column: int = 0
    
    def accept(self, visitor) -> Any:
        return visitor.visit_grouping_expression(self)


# Primary Expressions
class IdentifierNode(ASTNode):
    """Variable reference"""
    
    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
    
    def accept(self, visitor) -> Any:
        return visitor.visit_identifier(self)


class LiteralNode(ASTNode):
    """Literal value: number, string, boolean"""
    
    def __init__(self, value: Any, token_type: TokenType, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value
        self.token_type = token_type
    
    def accept(self, visitor) -> Any:
        return visitor.visit_literal(self)


# Security-Aware Nodes
@dataclass
class SecureBlockNode(ASTNode):
    """Secure block: secure { ... }"""
    body: BlockNode
    line: int = 0
    column: int = 0
    
    def accept(self, visitor) -> Any:
        return visitor.visit_secure_block(self)


class ValidateExpressionNode(ASTNode):
    """Validate expression: validate(expression, condition)"""
    
    def __init__(self, expression: ASTNode, condition: Optional[ASTNode], line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expression = expression
        self.condition = condition
    
    def accept(self, visitor) -> Any:
        return visitor.visit_validate_expression(self)


class SanitizeExpressionNode(ASTNode):
    """Sanitize expression: sanitize(expression)"""
    
    def __init__(self, expression: ASTNode, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expression = expression
    
    def accept(self, visitor) -> Any:
        return visitor.visit_sanitize_expression(self)


# Error Recovery Node
@dataclass
class ErrorNode(ASTNode):
    """Error recovery node for malformed syntax"""
    message: str
    token: Optional[Token]
    
    def accept(self, visitor) -> Any:
        return visitor.visit_error(self)


# Visitor Pattern Interface
class ASTVisitor(ABC):
    """Visitor interface for AST traversal."""
    
    @abstractmethod
    def visit_program(self, node: ProgramNode) -> Any:
        pass
    
    @abstractmethod
    def visit_block(self, node: BlockNode) -> Any:
        pass
    
    @abstractmethod
    def visit_var_declaration(self, node: VarDeclarationNode) -> Any:
        pass
    
    @abstractmethod
    def visit_function_declaration(self, node: FunctionDeclarationNode) -> Any:
        pass
    
    @abstractmethod
    def visit_parameter(self, node: ParameterNode) -> Any:
        pass
    
    @abstractmethod
    def visit_expression_statement(self, node: ExpressionStatementNode) -> Any:
        pass
    
    @abstractmethod
    def visit_return_statement(self, node: ReturnStatementNode) -> Any:
        pass
    
    @abstractmethod
    def visit_if_statement(self, node: IfStatementNode) -> Any:
        pass
    
    @abstractmethod
    def visit_while_statement(self, node: WhileStatementNode) -> Any:
        pass
    
    @abstractmethod
    def visit_for_statement(self, node: ForStatementNode) -> Any:
        pass
    
    @abstractmethod
    def visit_break_statement(self, node: BreakStatementNode) -> Any:
        pass
    
    @abstractmethod
    def visit_continue_statement(self, node: ContinueStatementNode) -> Any:
        pass
    
    @abstractmethod
    def visit_print_statement(self, node: PrintStatementNode) -> Any:
        pass
    
    @abstractmethod
    def visit_binary_expression(self, node: BinaryExpressionNode) -> Any:
        pass
    
    @abstractmethod
    def visit_unary_expression(self, node: UnaryExpressionNode) -> Any:
        pass
    
    @abstractmethod
    def visit_assignment_expression(self, node: AssignmentExpressionNode) -> Any:
        pass
    
    @abstractmethod
    def visit_call_expression(self, node: CallExpressionNode) -> Any:
        pass
    
    @abstractmethod
    def visit_grouping_expression(self, node: GroupingExpressionNode) -> Any:
        pass
    
    @abstractmethod
    def visit_identifier(self, node: IdentifierNode) -> Any:
        pass
    
    @abstractmethod
    def visit_literal(self, node: LiteralNode) -> Any:
        pass
    
    @abstractmethod
    def visit_secure_block(self, node: SecureBlockNode) -> Any:
        pass
    
    @abstractmethod
    def visit_validate_expression(self, node: ValidateExpressionNode) -> Any:
        pass
    
    @abstractmethod
    def visit_sanitize_expression(self, node: SanitizeExpressionNode) -> Any:
        pass
    
    @abstractmethod
    def visit_error(self, node: ErrorNode) -> Any:
        pass