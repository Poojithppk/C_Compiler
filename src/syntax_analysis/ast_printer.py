"""
AST Pretty Printer for NEXUS Language

This module provides formatted text representation of Abstract Syntax Trees
for debugging and visualization purposes.
"""

from typing import Any, List
from syntax_analysis.ast_nodes import *


class ASTPrinter:
    """Pretty printer for AST nodes using the visitor pattern."""
    
    def __init__(self):
        self.indent_level = 0
        self.indent_size = 2
        self.output = []
    
    def print_ast(self, node: ASTNode) -> str:
        """Print the entire AST as formatted text."""
        self.output.clear()
        self.indent_level = 0
        
        if node:
            node.accept(self)
        else:
            self.output.append("(empty AST)")
        
        return '\n'.join(self.output)
    
    def _indent(self) -> str:
        """Get current indentation string."""
        return ' ' * (self.indent_level * self.indent_size)
    
    def _print_line(self, text: str) -> None:
        """Print a line with proper indentation."""
        self.output.append(self._indent() + text)
    
    def _enter_scope(self) -> None:
        """Increase indentation level."""
        self.indent_level += 1
    
    def _exit_scope(self) -> None:
        """Decrease indentation level."""
        self.indent_level = max(0, self.indent_level - 1)
    
    def _format_location(self, node: ASTNode) -> str:
        """Format source location info."""
        if hasattr(node, 'line') and hasattr(node, 'column'):
            return f" @{node.line}:{node.column}"
        return ""
    
    # =====================
    # VISITOR IMPLEMENTATIONS
    # =====================
    
    def visit_program(self, node: ProgramNode) -> Any:
        """Visit program node."""
        self._print_line(f"Program{self._format_location(node)}")
        self._enter_scope()
        
        if node.statements:
            for i, stmt in enumerate(node.statements):
                self._print_line(f"Statement[{i}]:")
                self._enter_scope()
                stmt.accept(self)
                self._exit_scope()
        else:
            self._print_line("(no statements)")
        
        self._exit_scope()
    
    def visit_block(self, node: BlockNode) -> Any:
        """Visit block node."""
        self._print_line(f"Block{self._format_location(node)}")
        self._enter_scope()
        
        if node.statements:
            for i, stmt in enumerate(node.statements):
                self._print_line(f"Statement[{i}]:")
                self._enter_scope()
                stmt.accept(self)
                self._exit_scope()
        else:
            self._print_line("(empty block)")
        
        self._exit_scope()
    
    def visit_var_declaration(self, node: VarDeclarationNode) -> Any:
        """Visit variable declaration node."""
        decl_type = "Constant" if node.is_constant else "Variable"
        type_info = f": {node.data_type}" if node.data_type else ""
        
        self._print_line(f"{decl_type}Declaration '{node.name}'{type_info}{self._format_location(node)}")
        
        if node.initializer:
            self._enter_scope()
            self._print_line("Initializer:")
            self._enter_scope()
            node.initializer.accept(self)
            self._exit_scope()
            self._exit_scope()
    
    def visit_function_declaration(self, node: FunctionDeclarationNode) -> Any:
        """Visit function declaration node."""
        return_type = f" -> {node.return_type}" if node.return_type else ""
        
        self._print_line(f"FunctionDeclaration '{node.name}'{return_type}{self._format_location(node)}")
        self._enter_scope()
        
        # Parameters
        if node.parameters:
            self._print_line("Parameters:")
            self._enter_scope()
            for i, param in enumerate(node.parameters):
                self._print_line(f"Parameter[{i}]:")
                self._enter_scope()
                param.accept(self)
                self._exit_scope()
            self._exit_scope()
        else:
            self._print_line("Parameters: (none)")
        
        # Body
        self._print_line("Body:")
        self._enter_scope()
        node.body.accept(self)
        self._exit_scope()
        
        self._exit_scope()
    
    def visit_parameter(self, node: ParameterNode) -> Any:
        """Visit parameter node."""
        self._print_line(f"Parameter '{node.name}': {node.data_type}{self._format_location(node)}")
    
    def visit_expression_statement(self, node: ExpressionStatementNode) -> Any:
        """Visit expression statement node."""
        self._print_line(f"ExpressionStatement{self._format_location(node)}")
        self._enter_scope()
        node.expression.accept(self)
        self._exit_scope()
    
    def visit_return_statement(self, node: ReturnStatementNode) -> Any:
        """Visit return statement node."""
        self._print_line(f"ReturnStatement{self._format_location(node)}")
        
        if node.value:
            self._enter_scope()
            self._print_line("Value:")
            self._enter_scope()
            node.value.accept(self)
            self._exit_scope()
            self._exit_scope()
    
    def visit_if_statement(self, node: IfStatementNode) -> Any:
        """Visit if statement node."""
        self._print_line(f"IfStatement{self._format_location(node)}")
        self._enter_scope()
        
        # Condition
        self._print_line("Condition:")
        self._enter_scope()
        node.condition.accept(self)
        self._exit_scope()
        
        # Then branch
        self._print_line("ThenBranch:")
        self._enter_scope()
        node.then_branch.accept(self)
        self._exit_scope()
        
        # Else branch
        if node.else_branch:
            self._print_line("ElseBranch:")
            self._enter_scope()
            node.else_branch.accept(self)
            self._exit_scope()
        
        self._exit_scope()
    
    def visit_while_statement(self, node: WhileStatementNode) -> Any:
        """Visit while statement node."""
        self._print_line(f"WhileStatement{self._format_location(node)}")
        self._enter_scope()
        
        # Condition
        self._print_line("Condition:")
        self._enter_scope()
        node.condition.accept(self)
        self._exit_scope()
        
        # Body
        self._print_line("Body:")
        self._enter_scope()
        node.body.accept(self)
        self._exit_scope()
        
        self._exit_scope()
    
    def visit_for_statement(self, node: ForStatementNode) -> Any:
        """Visit for statement node."""
        self._print_line(f"ForStatement{self._format_location(node)}")
        self._enter_scope()
        
        # Initializer
        if node.initializer:
            self._print_line("Initializer:")
            self._enter_scope()
            node.initializer.accept(self)
            self._exit_scope()
        else:
            self._print_line("Initializer: (none)")
        
        # Condition
        if node.condition:
            self._print_line("Condition:")
            self._enter_scope()
            node.condition.accept(self)
            self._exit_scope()
        else:
            self._print_line("Condition: (none)")
        
        # Increment
        if node.increment:
            self._print_line("Increment:")
            self._enter_scope()
            node.increment.accept(self)
            self._exit_scope()
        else:
            self._print_line("Increment: (none)")
        
        # Body
        self._print_line("Body:")
        self._enter_scope()
        node.body.accept(self)
        self._exit_scope()
        
        self._exit_scope()
    
    def visit_break_statement(self, node: BreakStatementNode) -> Any:
        """Visit break statement node."""
        self._print_line(f"BreakStatement{self._format_location(node)}")
    
    def visit_continue_statement(self, node: ContinueStatementNode) -> Any:
        """Visit continue statement node."""
        self._print_line(f"ContinueStatement{self._format_location(node)}")
    
    def visit_print_statement(self, node: PrintStatementNode) -> Any:
        """Visit print statement node."""
        self._print_line(f"PrintStatement{self._format_location(node)}")
        self._enter_scope()
        node.expression.accept(self)
        self._exit_scope()
    
    def visit_binary_expression(self, node: BinaryExpressionNode) -> Any:
        """Visit binary expression node."""
        self._print_line(f"BinaryExpression '{node.operator.lexeme}'{self._format_location(node)}")
        self._enter_scope()
        
        # Left operand
        self._print_line("Left:")
        self._enter_scope()
        node.left.accept(self)
        self._exit_scope()
        
        # Right operand
        self._print_line("Right:")
        self._enter_scope()
        node.right.accept(self)
        self._exit_scope()
        
        self._exit_scope()
    
    def visit_unary_expression(self, node: UnaryExpressionNode) -> Any:
        """Visit unary expression node."""
        self._print_line(f"UnaryExpression '{node.operator.lexeme}'{self._format_location(node)}")
        self._enter_scope()
        
        # Operand
        self._print_line("Operand:")
        self._enter_scope()
        node.operand.accept(self)
        self._exit_scope()
        
        self._exit_scope()
    
    def visit_assignment_expression(self, node: AssignmentExpressionNode) -> Any:
        """Visit assignment expression node."""
        self._print_line(f"AssignmentExpression '{node.name}' {node.operator.lexeme}{self._format_location(node)}")
        self._enter_scope()
        
        # Value
        self._print_line("Value:")
        self._enter_scope()
        node.value.accept(self)
        self._exit_scope()
        
        self._exit_scope()
    
    def visit_call_expression(self, node: CallExpressionNode) -> Any:
        """Visit function call expression node."""
        self._print_line(f"CallExpression{self._format_location(node)}")
        self._enter_scope()
        
        # Callee
        self._print_line("Callee:")
        self._enter_scope()
        node.callee.accept(self)
        self._exit_scope()
        
        # Arguments
        if node.arguments:
            self._print_line("Arguments:")
            self._enter_scope()
            for i, arg in enumerate(node.arguments):
                self._print_line(f"Argument[{i}]:")
                self._enter_scope()
                arg.accept(self)
                self._exit_scope()
            self._exit_scope()
        else:
            self._print_line("Arguments: (none)")
        
        self._exit_scope()
    
    def visit_grouping_expression(self, node: GroupingExpressionNode) -> Any:
        """Visit grouping expression node."""
        self._print_line(f"GroupingExpression{self._format_location(node)}")
        self._enter_scope()
        node.expression.accept(self)
        self._exit_scope()
    
    def visit_identifier(self, node: IdentifierNode) -> Any:
        """Visit identifier node."""
        self._print_line(f"Identifier '{node.name}'{self._format_location(node)}")
    
    def visit_literal(self, node: LiteralNode) -> Any:
        """Visit literal node."""
        value_str = repr(node.value) if isinstance(node.value, str) else str(node.value)
        type_str = node.token_type.name
        self._print_line(f"Literal {value_str} ({type_str}){self._format_location(node)}")
    
    def visit_secure_block(self, node: SecureBlockNode) -> Any:
        """Visit secure block node."""
        self._print_line(f"SecureBlock{self._format_location(node)}")
        self._enter_scope()
        node.body.accept(self)
        self._exit_scope()
    
    def visit_validate_expression(self, node: ValidateExpressionNode) -> Any:
        """Visit validate expression node."""
        self._print_line(f"ValidateExpression{self._format_location(node)}")
        self._enter_scope()
        
        # Expression
        self._print_line("Expression:")
        self._enter_scope()
        node.expression.accept(self)
        self._exit_scope()
        
        # Condition (optional)
        if node.condition:
            self._print_line("Condition:")
            self._enter_scope()
            node.condition.accept(self)
            self._exit_scope()
        
        self._exit_scope()
    
    def visit_sanitize_expression(self, node: SanitizeExpressionNode) -> Any:
        """Visit sanitize expression node."""
        self._print_line(f"SanitizeExpression{self._format_location(node)}")
        self._enter_scope()
        node.expression.accept(self)
        self._exit_scope()
    
    def visit_error(self, node: ErrorNode) -> Any:
        """Visit error recovery node."""
        token_info = f" token='{node.token.lexeme}'" if node.token else ""
        self._print_line(f"ErrorNode '{node.message}'{token_info}{self._format_location(node)}")


class ASTPrinterCompact:
    """Compact AST printer for single-line representation."""
    
    def print_ast(self, node: ASTNode) -> str:
        """Print AST in compact form."""
        if not node:
            return "(empty)"
        
        return self._visit_node(node)
    
    def _visit_node(self, node: ASTNode) -> str:
        """Visit any AST node and return compact representation."""
        if isinstance(node, ProgramNode):
            statements = [self._visit_node(stmt) for stmt in node.statements]
            return f"Program({'; '.join(statements)})"
        
        elif isinstance(node, VarDeclarationNode):
            const_prefix = "const " if node.is_constant else ""
            type_suffix = f": {node.data_type}" if node.data_type else ""
            init_suffix = f" = {self._visit_node(node.initializer)}" if node.initializer else ""
            return f"{const_prefix}{node.name}{type_suffix}{init_suffix}"
        
        elif isinstance(node, FunctionDeclarationNode):
            params = [f"{p.name}: {p.data_type}" for p in node.parameters]
            return_type = f" -> {node.return_type}" if node.return_type else ""
            return f"func {node.name}({', '.join(params)}){return_type} {{ ... }}"
        
        elif isinstance(node, BinaryExpressionNode):
            left = self._visit_node(node.left)
            right = self._visit_node(node.right)
            return f"({left} {node.operator.lexeme} {right})"
        
        elif isinstance(node, UnaryExpressionNode):
            operand = self._visit_node(node.operand)
            return f"({node.operator.lexeme}{operand})"
        
        elif isinstance(node, AssignmentExpressionNode):
            value = self._visit_node(node.value)
            return f"{node.name} {node.operator.lexeme} {value}"
        
        elif isinstance(node, CallExpressionNode):
            callee = self._visit_node(node.callee)
            args = [self._visit_node(arg) for arg in node.arguments]
            return f"{callee}({', '.join(args)})"
        
        elif isinstance(node, IdentifierNode):
            return node.name
        
        elif isinstance(node, LiteralNode):
            if isinstance(node.value, str):
                return f'"{node.value}"'
            return str(node.value)
        
        elif isinstance(node, IfStatementNode):
            condition = self._visit_node(node.condition)
            then_branch = self._visit_node(node.then_branch)
            else_part = f" else {self._visit_node(node.else_branch)}" if node.else_branch else ""
            return f"if ({condition}) {then_branch}{else_part}"
        
        elif isinstance(node, WhileStatementNode):
            condition = self._visit_node(node.condition)
            body = self._visit_node(node.body)
            return f"while ({condition}) {body}"
        
        elif isinstance(node, PrintStatementNode):
            expr = self._visit_node(node.expression)
            return f"print({expr})"
        
        elif isinstance(node, BlockNode):
            statements = [self._visit_node(stmt) for stmt in node.statements]
            return f"{{ {'; '.join(statements)} }}"
        
        else:
            return node.__class__.__name__


class ASTGraphvizPrinter:
    """Generate Graphviz DOT format for AST visualization."""
    
    def __init__(self):
        self.node_counter = 0
        self.dot_lines = []
        self.nodes = {}
    
    def print_ast(self, node: ASTNode) -> str:
        """Generate DOT format representation of AST."""
        self.node_counter = 0
        self.dot_lines.clear()
        self.nodes.clear()
        
        self.dot_lines.append("digraph AST {")
        self.dot_lines.append("  rankdir=TB;")
        self.dot_lines.append("  node [shape=box, style=filled, fontname=\"Arial\"];")
        
        if node:
            self._visit_node(node, None)
        
        self.dot_lines.append("}")
        return '\n'.join(self.dot_lines)
    
    def _visit_node(self, node: ASTNode, parent_id: Optional[int]) -> int:
        """Visit node and create DOT representation."""
        node_id = self.node_counter
        self.node_counter += 1
        
        # Node label and color
        label = self._get_node_label(node)
        color = self._get_node_color(node)
        
        # Create node
        self.dot_lines.append(f'  {node_id} [label="{label}", fillcolor="{color}"];')
        
        # Connect to parent
        if parent_id is not None:
            self.dot_lines.append(f'  {parent_id} -> {node_id};')
        
        # Visit children
        children = self._get_children(node)
        for child in children:
            if child:
                self._visit_node(child, node_id)
        
        return node_id
    
    def _get_node_label(self, node: ASTNode) -> str:
        """Get display label for node."""
        if isinstance(node, VarDeclarationNode):
            const_prefix = "const " if node.is_constant else "var "
            return f"{const_prefix}{node.name}"
        elif isinstance(node, FunctionDeclarationNode):
            return f"func {node.name}"
        elif isinstance(node, BinaryExpressionNode):
            return f"Binary\\n{node.operator.lexeme}"
        elif isinstance(node, UnaryExpressionNode):
            return f"Unary\\n{node.operator.lexeme}"
        elif isinstance(node, AssignmentExpressionNode):
            return f"Assign\\n{node.operator.lexeme}"
        elif isinstance(node, IdentifierNode):
            return f"ID\\n{node.name}"
        elif isinstance(node, LiteralNode):
            value_str = str(node.value)[:10]  # Truncate long values
            return f"Literal\\n{value_str}"
        elif isinstance(node, CallExpressionNode):
            return "Call"
        elif isinstance(node, IfStatementNode):
            return "If"
        elif isinstance(node, WhileStatementNode):
            return "While"
        elif isinstance(node, ForStatementNode):
            return "For"
        elif isinstance(node, PrintStatementNode):
            return "Print"
        elif isinstance(node, BlockNode):
            return "Block"
        elif isinstance(node, SecureBlockNode):
            return "Secure\\nBlock"
        else:
            return node.__class__.__name__.replace("Node", "")
    
    def _get_node_color(self, node: ASTNode) -> str:
        """Get color for node type."""
        if isinstance(node, (VarDeclarationNode, FunctionDeclarationNode)):
            return "lightblue"
        elif isinstance(node, (BinaryExpressionNode, UnaryExpressionNode, AssignmentExpressionNode)):
            return "lightgreen"
        elif isinstance(node, (IfStatementNode, WhileStatementNode, ForStatementNode)):
            return "lightyellow"
        elif isinstance(node, (IdentifierNode, LiteralNode)):
            return "lightsalmon"
        elif isinstance(node, (CallExpressionNode, PrintStatementNode)):
            return "lightcyan"
        elif isinstance(node, (BlockNode, SecureBlockNode)):
            return "lightgray"
        else:
            return "white"
    
    def _get_children(self, node: ASTNode) -> List[Optional[ASTNode]]:
        """Get child nodes in order."""
        children = []
        
        if isinstance(node, ProgramNode):
            children.extend(node.statements)
        elif isinstance(node, BlockNode):
            children.extend(node.statements)
        elif isinstance(node, VarDeclarationNode):
            if node.initializer:
                children.append(node.initializer)
        elif isinstance(node, FunctionDeclarationNode):
            children.extend(node.parameters)
            children.append(node.body)
        elif isinstance(node, BinaryExpressionNode):
            children.extend([node.left, node.right])
        elif isinstance(node, UnaryExpressionNode):
            children.append(node.operand)
        elif isinstance(node, AssignmentExpressionNode):
            children.append(node.value)
        elif isinstance(node, CallExpressionNode):
            children.append(node.callee)
            children.extend(node.arguments)
        elif isinstance(node, IfStatementNode):
            children.append(node.condition)
            children.append(node.then_branch)
            if node.else_branch:
                children.append(node.else_branch)
        elif isinstance(node, WhileStatementNode):
            children.extend([node.condition, node.body])
        elif isinstance(node, ForStatementNode):
            if node.initializer:
                children.append(node.initializer)
            if node.condition:
                children.append(node.condition)
            if node.increment:
                children.append(node.increment)
            children.append(node.body)
        elif isinstance(node, PrintStatementNode):
            children.append(node.expression)
        elif isinstance(node, SecureBlockNode):
            children.append(node.body)
        elif isinstance(node, ValidateExpressionNode):
            children.append(node.expression)
            if node.condition:
                children.append(node.condition)
        elif isinstance(node, SanitizeExpressionNode):
            children.append(node.expression)
        elif isinstance(node, ExpressionStatementNode):
            children.append(node.expression)
        elif isinstance(node, GroupingExpressionNode):
            children.append(node.expression)
        elif isinstance(node, ReturnStatementNode):
            if node.value:
                children.append(node.value)
        
        return children