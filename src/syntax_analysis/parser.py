"""
Recursive Descent Parser for NEXUS Language

This module implements a recursive descent parser that converts a stream of tokens
into an Abstract Syntax Tree (AST) according to the NEXUS language grammar.

Features:
- Error recovery and reporting
- Security-aware parsing
- Visual parsing support
- Step-by-step parsing mode
"""

from typing import List, Optional, Union, Callable, Any
from lexical_analysis.tokens import Token, TokenType, LexicalError
from syntax_analysis.ast_nodes import *
from syntax_analysis.grammar import *
import logging


class ParseError(Exception):
    """Exception raised when parsing fails."""
    
    def __init__(self, message: str, token: Token, expected: Optional[List[str]] = None):
        self.message = message
        self.token = token
        self.expected = expected
        super().__init__(f"Parse Error at line {token.line}, column {token.column}: {message}")


class Parser:
    """
    Recursive Descent Parser for NEXUS Language.
    
    Uses predictive parsing with error recovery to build an AST from tokens.
    """
    
    def __init__(self, tokens: List[Token], debug_mode: bool = False):
        self.tokens = tokens
        self.current = 0
        self.debug_mode = debug_mode
        self.errors: List[ParseError] = []
        self.warnings: List[str] = []
        
        # Parsing state
        self.in_function = False
        self.in_loop = False
        self.in_secure_block = False
        self.loop_depth = 0
        
        # Step-by-step parsing support
        self.step_mode = False
        self.parse_steps: List[dict] = []
        self.step_callback: Optional[Callable] = None
        
        # Error recovery state
        self.panic_mode = False
        self.recovered_errors = 0
        
        # Skip initial whitespace
        self._skip_whitespace()
    
    def enable_step_mode(self, callback: Optional[Callable] = None) -> None:
        """Enable step-by-step parsing with optional callback."""
        self.step_mode = True
        self.step_callback = callback
    
    def disable_step_mode(self) -> None:
        """Disable step-by-step parsing."""
        self.step_mode = False
        self.step_callback = None
    
    # =====================
    # CORE PARSING METHODS
    # =====================
    
    def parse(self) -> ProgramNode:
        """Parse the entire program and return the root AST node."""
        try:
            if self.debug_mode:
                print("🚀 Starting parser...")
            
            self._record_step("parse", "Starting program parsing")
            program = self._parse_program()
            
            if self.errors:
                self._log_errors()
            
            if self.debug_mode:
                print(f"✅ Parsing completed with {len(self.errors)} errors")
            
            return program
            
        except Exception as e:
            error = ParseError(f"Unexpected parser error: {str(e)}", self._current_token())
            self.errors.append(error)
            raise error
    
    def _parse_program(self) -> ProgramNode:
        """Parse the root program production."""
        statements = []
        
        while not self._is_at_end():
            try:
                stmt = self._parse_declaration()
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                self.errors.append(e)
                self._synchronize()
        
        return ProgramNode(statements=statements)
    
    # =========================
    # DECLARATION PARSING
    # =========================
    
    def _parse_declaration(self) -> Optional[ASTNode]:
        """Parse declarations (variables, constants, functions) or statements."""
        try:
            self._record_step("declaration", f"Parsing declaration at: {self._current_token().lexeme}")
            
            if self._match(TokenType.VAR):        # hold
                return self._parse_var_declaration()
            elif self._match(TokenType.CONST):    # fixed
                return self._parse_const_declaration()
            elif self._match(TokenType.FUNC):     # func
                return self._parse_function_declaration()
            else:
                return self._parse_statement()
                
        except ParseError as e:
            self.errors.append(e)
            self._synchronize()
            return None
    
    def _parse_var_declaration(self) -> VarDeclarationNode:
        """Parse variable declaration: hold x = 5;"""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.lexeme
        
        # Optional type annotation
        data_type = None
        if self._match(TokenType.COLON):
            type_token = self._consume_type("Expected type annotation")
            data_type = type_token.lexeme
        
        # Optional initialization
        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._parse_expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        
        return VarDeclarationNode(
            name=name,
            data_type=data_type,
            initializer=initializer,
            is_constant=False,
            line=name_token.line,
            column=name_token.column
        )
    
    def _parse_const_declaration(self) -> VarDeclarationNode:
        """Parse constant declaration: fixed x = 5;"""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected constant name")
        name = name_token.lexeme
        
        # Optional type annotation
        data_type = None
        if self._match(TokenType.COLON):
            type_token = self._consume_type("Expected type annotation")
            data_type = type_token.lexeme
        
        # Mandatory initialization for constants
        self._consume(TokenType.ASSIGN, "Expected '=' in constant declaration")
        initializer = self._parse_expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after constant declaration")
        
        return VarDeclarationNode(
            name=name,
            data_type=data_type,
            initializer=initializer,
            is_constant=True,
            line=name_token.line,
            column=name_token.column
        )
    
    def _parse_function_declaration(self) -> FunctionDeclarationNode:
        """Parse function declaration: func name(params) -> type { body }"""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.lexeme
        
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after function name")
        
        # Parse parameters
        parameters = []
        if not self._check(TokenType.RIGHT_PAREN):
            parameters = self._parse_parameters()
        
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        
        # Optional return type
        return_type = None
        if self._match(TokenType.ARROW):
            type_token = self._consume_type("Expected return type")
            return_type = type_token.lexeme
        
        # Function body
        old_in_function = self.in_function
        self.in_function = True
        
        body = self._parse_block()
        
        self.in_function = old_in_function
        
        return FunctionDeclarationNode(
            name=name,
            parameters=parameters,
            return_type=return_type,
            body=body,
            line=name_token.line,
            column=name_token.column
        )
    
    def _parse_parameters(self) -> List[ParameterNode]:
        """Parse function parameters: name: type, name: type"""
        parameters = []
        
        # First parameter
        param_token = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
        self._consume(TokenType.COLON, "Expected ':' after parameter name")
        type_token = self._consume_type("Expected parameter type")
        
        parameters.append(ParameterNode(
            name=param_token.lexeme,
            data_type=type_token.lexeme,
            line=param_token.line,
            column=param_token.column
        ))
        
        # Additional parameters
        while self._match(TokenType.COMMA):
            param_token = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
            self._consume(TokenType.COLON, "Expected ':' after parameter name")
            type_token = self._consume_type("Expected parameter type")
            
            parameters.append(ParameterNode(
                name=param_token.lexeme,
                data_type=type_token.lexeme,
                line=param_token.line,
                column=param_token.column
            ))
        
        return parameters
    
    # =========================
    # STATEMENT PARSING
    # =========================
    
    def _parse_statement(self) -> ASTNode:
        """Parse statements."""
        self._record_step("statement", f"Parsing statement at: {self._current_token().lexeme}")
        
        if self._match(TokenType.PRINT):          # show
            return self._parse_print_statement()
        elif self._match(TokenType.RETURN):      # return
            return self._parse_return_statement()
        elif self._match(TokenType.IF):          # when
            return self._parse_if_statement()
        elif self._match(TokenType.WHILE):       # repeat
            return self._parse_while_statement()
        elif self._match(TokenType.FOR):         # cycle
            return self._parse_for_statement()
        elif self._match(TokenType.BREAK):       # stop
            return self._parse_break_statement()
        elif self._match(TokenType.CONTINUE):    # skip
            return self._parse_continue_statement()
        elif self._match(TokenType.LEFT_BRACE):  # {
            return self._parse_block()
        elif self._match(TokenType.SECURE):      # secure
            return self._parse_secure_statement()
        else:
            return self._parse_expression_statement()
    
    def _parse_print_statement(self) -> PrintStatementNode:
        """Parse print statement: show expression;"""
        token = self._previous()
        expr = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after print statement")
        
        return PrintStatementNode(expr, token.line, token.column)
    
    def _parse_return_statement(self) -> ReturnStatementNode:
        """Parse return statement: return expression?;"""
        token = self._previous()
        
        if not self.in_function:
            self.warnings.append(f"Return statement outside function at line {token.line}")
        
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self._parse_expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after return statement")
        
        return ReturnStatementNode(
            value=value,
            line=token.line,
            column=token.column
        )
    
    def _parse_if_statement(self) -> IfStatementNode:
        """Parse if statement: when (expr) stmt otherwise stmt"""
        token = self._previous()
        
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'when'")
        condition = self._parse_expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after condition")
        
        then_branch = self._parse_statement()
        
        else_branch = None
        if self._match(TokenType.ELSE):  # otherwise
            else_branch = self._parse_statement()
        
        return IfStatementNode(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
            line=token.line,
            column=token.column
        )
    
    def _parse_while_statement(self) -> WhileStatementNode:
        """Parse while statement: repeat (expr) stmt"""
        token = self._previous()
        
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'repeat'")
        condition = self._parse_expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after condition")
        
        # Enter loop context
        old_in_loop = self.in_loop
        old_loop_depth = self.loop_depth
        self.in_loop = True
        self.loop_depth += 1
        
        body = self._parse_statement()
        
        # Restore loop context
        self.in_loop = old_in_loop
        self.loop_depth = old_loop_depth
        
        return WhileStatementNode(
            condition=condition,
            body=body,
            line=token.line,
            column=token.column
        )
    
    def _parse_for_statement(self) -> ForStatementNode:
        """Parse for statement: cycle (init; condition; increment) stmt"""
        token = self._previous()
        
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'cycle'")
        
        # Initializer
        initializer = None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._parse_var_declaration()
        else:
            initializer = self._parse_expression_statement()
        
        # Condition
        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after loop condition")
        
        # Increment
        increment = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._parse_expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses")
        
        # Body
        old_in_loop = self.in_loop
        old_loop_depth = self.loop_depth
        self.in_loop = True
        self.loop_depth += 1
        
        body = self._parse_statement()
        
        self.in_loop = old_in_loop
        self.loop_depth = old_loop_depth
        
        return ForStatementNode(
            initializer=initializer,
            condition=condition,
            increment=increment,
            body=body,
            line=token.line,
            column=token.column
        )
    
    def _parse_break_statement(self) -> BreakStatementNode:
        """Parse break statement: stop;"""
        token = self._previous()
        
        if not self.in_loop:
            self.warnings.append(f"Break statement outside loop at line {token.line}")
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after 'stop'")
        
        return BreakStatementNode(line=token.line, column=token.column)
    
    def _parse_continue_statement(self) -> ContinueStatementNode:
        """Parse continue statement: skip;"""
        token = self._previous()
        
        if not self.in_loop:
            self.warnings.append(f"Continue statement outside loop at line {token.line}")
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after 'skip'")
        
        return ContinueStatementNode(line=token.line, column=token.column)
    
    def _parse_block(self) -> BlockNode:
        """Parse block statement: { statements }"""
        statements = []
        
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._parse_declaration()
            if stmt:
                statements.append(stmt)
        
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        
        return BlockNode(statements=statements)
    
    def _parse_secure_statement(self) -> ASTNode:
        """Parse secure statement: secure { ... } or secure validate(...); or secure expression;"""
        token = self._previous()
        
        # Check if it's a secure block: secure { ... }
        if self._check(TokenType.LEFT_BRACE):
            self._advance()  # consume '{'
            
            old_in_secure = self.in_secure_block
            self.in_secure_block = True
            
            body = self._parse_block()
            
            self.in_secure_block = old_in_secure
            
            return SecureBlockNode(body=body, line=token.line, column=token.column)
        
        # Otherwise, it's a secure statement: secure expression;
        else:
            old_in_secure = self.in_secure_block
            self.in_secure_block = True
            
            # Parse the expression (could be validate, sanitize, or other)
            expr = self._parse_expression()
            self._consume(TokenType.SEMICOLON, "Expected ';' after secure statement")
            
            self.in_secure_block = old_in_secure
            
            # Wrap the expression in a SecureBlockNode with a single expression statement
            expr_stmt = ExpressionStatementNode(expression=expr)
            block = BlockNode(statements=[expr_stmt])
            return SecureBlockNode(body=block, line=token.line, column=token.column)
    
    def _parse_expression_statement(self) -> ExpressionStatementNode:
        """Parse expression statement: expression;"""
        expr = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after expression")
        
        return ExpressionStatementNode(expression=expr)
    
    # =========================
    # EXPRESSION PARSING
    # =========================
    
    def _parse_expression(self) -> ASTNode:
        """Parse expression (assignment level)."""
        self._record_step("expression", f"Parsing expression at: {self._current_token().lexeme}")
        return self._parse_assignment()
    
    def _parse_assignment(self) -> ASTNode:
        """Parse assignment: identifier = expression"""
        expr = self._parse_logical_or()
        
        if self._match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, 
                      TokenType.MINUS_ASSIGN, TokenType.MULT_ASSIGN, TokenType.DIV_ASSIGN):
            operator = self._previous()
            value = self._parse_assignment()
            
            if isinstance(expr, IdentifierNode):
                return AssignmentExpressionNode(
                    name=expr.name,
                    operator=operator,
                    value=value,
                    line=operator.line,
                    column=operator.column
                )
            else:
                raise ParseError("Invalid assignment target", operator)
        
        return expr
    
    def _parse_logical_or(self) -> ASTNode:
        """Parse logical OR: expr || expr"""
        expr = self._parse_logical_and()
        
        while self._match(TokenType.OR) or self._match_keyword("or"):
            operator = self._previous()
            right = self._parse_logical_and()
            expr = BinaryExpressionNode(left=expr, operator=operator, right=right)
        
        return expr
    
    def _parse_logical_and(self) -> ASTNode:
        """Parse logical AND: expr && expr"""
        expr = self._parse_equality()
        
        while self._match(TokenType.AND) or self._match_keyword("and"):
            operator = self._previous()
            right = self._parse_equality()
            expr = BinaryExpressionNode(left=expr, operator=operator, right=right)
        
        return expr
    
    def _parse_equality(self) -> ASTNode:
        """Parse equality: expr == expr, expr != expr"""
        expr = self._parse_comparison()
        
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self._previous()
            right = self._parse_comparison()
            expr = BinaryExpressionNode(left=expr, operator=operator, right=right)
        
        return expr
    
    def _parse_comparison(self) -> ASTNode:
        """Parse comparison: expr > expr, expr >= expr, etc."""
        expr = self._parse_term()
        
        while self._match(TokenType.GREATER_THAN, TokenType.GREATER_EQUAL,
                          TokenType.LESS_THAN, TokenType.LESS_EQUAL):
            operator = self._previous()
            right = self._parse_term()
            expr = BinaryExpressionNode(left=expr, operator=operator, right=right)
        
        return expr
    
    def _parse_term(self) -> ASTNode:
        """Parse term: expr + expr, expr - expr"""
        expr = self._parse_factor()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self._parse_factor()
            expr = BinaryExpressionNode(left=expr, operator=operator, right=right)
        
        return expr
    
    def _parse_factor(self) -> ASTNode:
        """Parse factor: expr * expr, expr / expr, expr % expr"""
        expr = self._parse_unary()
        
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self._previous()
            right = self._parse_unary()
            expr = BinaryExpressionNode(left=expr, operator=operator, right=right)
        
        return expr
    
    def _parse_unary(self) -> ASTNode:
        """Parse unary: -expr, +expr, !expr, not expr"""
        if self._match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS) or self._match_keyword("not"):
            operator = self._previous()
            operand = self._parse_unary()
            return UnaryExpressionNode(operator=operator, operand=operand)
        
        return self._parse_power()
    
    def _parse_power(self) -> ASTNode:
        """Parse power: expr ** expr (right-associative)"""
        expr = self._parse_call()
        
        if self._match(TokenType.POWER):
            operator = self._previous()
            # Right associative: a ** b ** c = a ** (b ** c)
            right = self._parse_power()
            expr = BinaryExpressionNode(left=expr, operator=operator, right=right)
        
        return expr
    
    def _parse_call(self) -> ASTNode:
        """Parse function call: expr(args)"""
        expr = self._parse_primary()
        
        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._parse_function_call(expr)
            else:
                break
        
        return expr
    
    def _parse_function_call(self, callee: ASTNode) -> CallExpressionNode:
        """Parse function call arguments."""
        arguments = []
        
        if not self._check(TokenType.RIGHT_PAREN):
            arguments.append(self._parse_expression())
            while self._match(TokenType.COMMA):
                arguments.append(self._parse_expression())
        
        paren = self._consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
        
        return CallExpressionNode(
            callee=callee,
            arguments=arguments,
            line=paren.line,
            column=paren.column
        )
    
    def _parse_primary(self) -> ASTNode:
        """Parse primary expressions."""
        token = self._current_token()
        
        # Security expressions
        if self._match(TokenType.VALIDATE):
            return self._parse_validate_expression()
        elif self._match(TokenType.SANITIZE):
            return self._parse_sanitize_expression()
        
        # Literals
        elif self._match(TokenType.TRUE):
            prev_token = self._previous()
            return LiteralNode(True, TokenType.TRUE, prev_token.line, prev_token.column)
        elif self._match(TokenType.FALSE):
            prev_token = self._previous()
            return LiteralNode(False, TokenType.FALSE, prev_token.line, prev_token.column)
        elif self._match(TokenType.NULL):
            prev_token = self._previous()
            return LiteralNode(None, TokenType.NULL, prev_token.line, prev_token.column)
        elif self._match(TokenType.INTEGER):
            prev_token = self._previous()
            return LiteralNode(prev_token.value, TokenType.INTEGER, prev_token.line, prev_token.column)
        elif self._match(TokenType.FLOAT):
            prev_token = self._previous()
            return LiteralNode(prev_token.value, TokenType.FLOAT, prev_token.line, prev_token.column)
        elif self._match(TokenType.STRING):
            prev_token = self._previous()
            return LiteralNode(prev_token.value, TokenType.STRING, prev_token.line, prev_token.column)
        
        # Identifiers
        elif self._match(TokenType.IDENTIFIER):
            prev_token = self._previous()
            return IdentifierNode(prev_token.lexeme, prev_token.line, prev_token.column)
        
        # Grouped expressions
        elif self._match(TokenType.LEFT_PAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return GroupingExpressionNode(expression=expr, line=token.line, column=token.column)
        
        # Error handling
        else:
            raise ParseError(
                f"Unexpected token '{token.lexeme}'",
                token,
                EXPECTED_TOKENS['expression_start']
            )
    
    def _parse_validate_expression(self) -> ValidateExpressionNode:
        """Parse validate expression: validate(expr, condition?)"""
        token = self._previous()
        
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'validate'")
        expression = self._parse_expression()
        
        condition = None
        if self._match(TokenType.COMMA):
            condition = self._parse_expression()
        
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after validate expression")
        
        return ValidateExpressionNode(
            expression=expression,
            condition=condition,
            line=token.line,
            column=token.column
        )
    
    def _parse_sanitize_expression(self) -> SanitizeExpressionNode:
        """Parse sanitize expression: sanitize(expr)"""
        token = self._previous()
        
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'sanitize'")
        expression = self._parse_expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after sanitize expression")
        
        return SanitizeExpressionNode(
            expression=expression,
            line=token.line,
            column=token.column
        )
    
    # =========================
    # UTILITY METHODS
    # =========================
    
    def _match(self, *token_types) -> bool:
        """Check if current token matches any of the given types."""
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _match_keyword(self, keyword: str) -> bool:
        """Check if current token is a specific keyword."""
        if self._current_token().lexeme == keyword:
            self._advance()
            return True
        return False
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type."""
        if self._is_at_end():
            return False
        return self._current_token().token_type == token_type
    
    def _advance(self) -> Token:
        """Move to next token and return previous."""
        if not self._is_at_end():
            self.current += 1
        self._skip_whitespace()
        return self._previous()
    
    def _skip_whitespace(self):
        """Skip over whitespace tokens like newlines and comments."""
        while (self.current < len(self.tokens) and 
               self.tokens[self.current].token_type in (TokenType.NEWLINE, TokenType.COMMENT)):
            self.current += 1
    
    def _is_at_end(self) -> bool:
        """Check if we've reached end of tokens."""
        return self.current >= len(self.tokens) or (
            self.current < len(self.tokens) and 
            self.tokens[self.current].token_type == TokenType.EOF
        )
    
    def _current_token(self) -> Token:
        """Get current token, skipping whitespace."""
        self._skip_whitespace()
        if self.current >= len(self.tokens):
            # Return EOF token
            return Token(TokenType.EOF, "", None, 0, 0, 0)
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """Get previous token."""
        if self.current > 0:
            return self.tokens[self.current - 1]
        return self.tokens[0]
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise error."""
        if self._check(token_type):
            return self._advance()
        
        current = self._current_token()
        raise ParseError(message, current, [token_type.name])
    
    def _consume_type(self, message: str) -> Token:
        """Consume a type token (num, decimal, text, flag)."""
        if self._match(TokenType.INT, TokenType.FLOAT_TYPE, TokenType.STRING_TYPE, TokenType.BOOL):
            return self._previous()
        
        current = self._current_token()
        raise ParseError(message, current, EXPECTED_TOKENS['type_keywords'])
    
    def _synchronize(self) -> None:
        """Synchronize parser state after error for recovery."""
        self._advance()
        
        while not self._is_at_end():
            if self._previous().token_type == TokenType.SEMICOLON:
                return
            
            if self._current_token().lexeme in SYNC_TOKENS:
                return
            
            self._advance()
    
    def _record_step(self, rule: str, description: str) -> None:
        """Record parsing step for visual debugging."""
        # Always record steps for debugging/visualization
        step = {
            'rule': rule,
            'description': description,
            'position': self.current,
            'token': self._current_token().lexeme if not self._is_at_end() else 'EOF',
            'line': self._current_token().line if not self._is_at_end() else 0,
            'column': self._current_token().column if not self._is_at_end() else 0
        }
        self.parse_steps.append(step)
        
        if self.step_mode and self.step_callback:
            self.step_callback(step)
    
    def _log_errors(self) -> None:
        """Log all parsing errors."""
        if self.debug_mode:
            print(f"\n📊 Parsing Report:")
            print(f"   • Errors: {len(self.errors)}")
            print(f"   • Warnings: {len(self.warnings)}")
            
            if self.errors:
                print("\n❌ Errors:")
                for error in self.errors:
                    print(f"   • {error}")
            
            if self.warnings:
                print("\n⚠️ Warnings:")
                for warning in self.warnings:
                    print(f"   • {warning}")
    
    def get_parse_steps(self) -> List[dict]:
        """Get recorded parsing steps."""
        return self.parse_steps.copy()
    
    def get_errors(self) -> List[ParseError]:
        """Get parsing errors."""
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """Get parsing warnings."""
        return self.warnings.copy()
    
    def has_errors(self) -> bool:
        """Check if parsing had errors."""
        return len(self.errors) > 0