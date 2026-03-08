"""
Test Suite for NEXUS Language Syntax Analysis

This module contains comprehensive test cases for the syntax analysis phase,
including valid programs, error cases, and edge cases.
"""

import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.lexical_analysis.lexer import VisualLexicalAnalyzer
from src.lexical_analysis.tokens import Token, TokenType
from src.syntax_analysis.parser import Parser, ParseError
from src.syntax_analysis.ast_nodes import *
from src.syntax_analysis.ast_printer import ASTPrinter


class TestSyntaxAnalysis(unittest.TestCase):
    """Test cases for syntax analysis functionality."""
    
    def setUp(self):
        """Setup test environment."""
        self.lexer = VisualLexicalAnalyzer(visual_mode=False)
        self.parser = None
        self.ast_printer = ASTPrinter()
    
    def _parse_code(self, source_code: str) -> ProgramNode:
        """Helper method to parse source code and return AST."""
        tokens, errors = self.lexer.analyze(source_code)
        self.parser = Parser(tokens, debug_mode=True)
        return self.parser.parse()
    
    def _parse_expression(self, source_code: str) -> ASTNode:
        """Helper method to parse a single expression."""
        # Wrap expression in a minimal program
        full_code = f"show {source_code};"
        ast = self._parse_code(full_code)
        
        # Extract the expression from the print statement
        if (ast.statements and 
            isinstance(ast.statements[0], PrintStatementNode)):
            return ast.statements[0].expression
        
        self.fail(f"Failed to parse expression: {source_code}")
    
    def test_empty_program(self):
        """Test parsing empty program."""
        ast = self._parse_code("")
        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(len(ast.statements), 0)
    
    # ======================
    # DECLARATION TESTS
    # ======================
    
    def test_variable_declaration_simple(self):
        """Test simple variable declaration."""
        ast = self._parse_code("hold x;")
        
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, VarDeclarationNode)
        self.assertEqual(stmt.name, "x")
        self.assertIsNone(stmt.data_type)
        self.assertIsNone(stmt.initializer)
        self.assertFalse(stmt.is_constant)
    
    def test_variable_declaration_with_type(self):
        """Test variable declaration with type annotation."""
        ast = self._parse_code("hold count: num;")
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, VarDeclarationNode)
        self.assertEqual(stmt.name, "count")
        self.assertEqual(stmt.data_type, "num")
        self.assertIsNone(stmt.initializer)
    
    def test_variable_declaration_with_initializer(self):
        """Test variable declaration with initializer."""
        ast = self._parse_code("hold x = 42;")
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, VarDeclarationNode)
        self.assertEqual(stmt.name, "x")
        self.assertIsNotNone(stmt.initializer)
        self.assertIsInstance(stmt.initializer, LiteralNode)
        self.assertEqual(stmt.initializer.value, 42)
    
    def test_variable_declaration_full(self):
        """Test full variable declaration with type and initializer."""
        ast = self._parse_code("hold pi: decimal = 3.14159;")
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, VarDeclarationNode)
        self.assertEqual(stmt.name, "pi")
        self.assertEqual(stmt.data_type, "decimal")
        self.assertIsNotNone(stmt.initializer)
        self.assertEqual(stmt.initializer.value, 3.14159)
    
    def test_constant_declaration(self):
        """Test constant declaration."""
        ast = self._parse_code("fixed MAX_SIZE = 100;")
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, VarDeclarationNode)
        self.assertEqual(stmt.name, "MAX_SIZE")
        self.assertTrue(stmt.is_constant)
        self.assertIsNotNone(stmt.initializer)
    
    def test_function_declaration_simple(self):
        """Test simple function declaration."""
        ast = self._parse_code("""
        func greet() {
            show "Hello!";
        }
        """)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, FunctionDeclarationNode)
        self.assertEqual(stmt.name, "greet")
        self.assertEqual(len(stmt.parameters), 0)
        self.assertIsNone(stmt.return_type)
        self.assertIsInstance(stmt.body, BlockNode)
    
    def test_function_declaration_with_parameters(self):
        """Test function declaration with parameters."""
        ast = self._parse_code("""
        func add(a: num, b: num) {
            return a + b;
        }
        """)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, FunctionDeclarationNode)
        self.assertEqual(stmt.name, "add")
        self.assertEqual(len(stmt.parameters), 2)
        
        # Check parameters
        param1 = stmt.parameters[0]
        self.assertEqual(param1.name, "a")
        self.assertEqual(param1.data_type, "num")
        
        param2 = stmt.parameters[1]
        self.assertEqual(param2.name, "b")
        self.assertEqual(param2.data_type, "num")
    
    def test_function_declaration_with_return_type(self):
        """Test function declaration with return type."""
        ast = self._parse_code("""
        func multiply(x: num, y: num) -> num {
            return x * y;
        }
        """)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, FunctionDeclarationNode)
        self.assertEqual(stmt.return_type, "num")
    
    # ======================
    # STATEMENT TESTS
    # ======================
    
    def test_print_statement(self):
        """Test print statement."""
        ast = self._parse_code('show "Hello World!";')
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, PrintStatementNode)
        self.assertIsInstance(stmt.expression, LiteralNode)
        self.assertEqual(stmt.expression.value, "Hello World!")
    
    def test_return_statement(self):
        """Test return statement."""
        ast = self._parse_code("""
        func test() {
            return 42;
        }
        """)
        
        func_body = ast.statements[0].body
        return_stmt = func_body.statements[0]
        self.assertIsInstance(return_stmt, ReturnStatementNode)
        self.assertIsInstance(return_stmt.value, LiteralNode)
        self.assertEqual(return_stmt.value.value, 42)
    
    def test_return_statement_empty(self):
        """Test empty return statement."""
        ast = self._parse_code("""
        func test() {
            return;
        }
        """)
        
        func_body = ast.statements[0].body
        return_stmt = func_body.statements[0]
        self.assertIsInstance(return_stmt, ReturnStatementNode)
        self.assertIsNone(return_stmt.value)
    
    def test_if_statement_simple(self):
        """Test simple if statement."""
        ast = self._parse_code("""
        when (x > 0) {
            show "positive";
        }
        """)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, IfStatementNode)
        self.assertIsInstance(stmt.condition, BinaryExpressionNode)
        self.assertIsInstance(stmt.then_branch, BlockNode)
        self.assertIsNone(stmt.else_branch)
    
    def test_if_else_statement(self):
        """Test if-else statement."""
        ast = self._parse_code("""
        when (x > 0) {
            show "positive";
        } otherwise {
            show "not positive";
        }
        """)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, IfStatementNode)
        self.assertIsNotNone(stmt.else_branch)
        self.assertIsInstance(stmt.else_branch, BlockNode)
    
    def test_while_statement(self):
        """Test while statement."""
        ast = self._parse_code("""
        repeat (i < 10) {
            i = i + 1;
        }
        """)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, WhileStatementNode)
        self.assertIsInstance(stmt.condition, BinaryExpressionNode)
        self.assertIsInstance(stmt.body, BlockNode)
    
    def test_for_statement(self):
        """Test for statement."""
        ast = self._parse_code("""
        cycle (hold i: num = 0; i < 10; i = i + 1) {
            show i;
        }
        """)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, ForStatementNode)
        self.assertIsInstance(stmt.initializer, VarDeclarationNode)
        self.assertIsInstance(stmt.condition, BinaryExpressionNode)
        self.assertIsInstance(stmt.increment, AssignmentExpressionNode)
        self.assertIsInstance(stmt.body, BlockNode)
    
    def test_break_continue_statements(self):
        """Test break and continue statements."""
        ast = self._parse_code("""
        repeat (yes) {
            when (x == 0) {
                skip;
            }
            when (x < 0) {
                stop;
            }
            x = x - 1;
        }
        """)
        
        while_stmt = ast.statements[0]
        block = while_stmt.body
        
        # Check skip (continue) statement
        skip_stmt = block.statements[0].then_branch.statements[0]
        self.assertIsInstance(skip_stmt, ContinueStatementNode)
        
        # Check stop (break) statement
        stop_stmt = block.statements[1].then_branch.statements[0]
        self.assertIsInstance(stop_stmt, BreakStatementNode)
    
    def test_secure_block(self):
        """Test secure block statement."""
        ast = self._parse_code("""
        secure {
            hold sensitiveData: text = "secret";
            show validate(sensitiveData, sensitiveData != null);
        }
        """)
        
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, SecureBlockNode)
        self.assertIsInstance(stmt.body, BlockNode)
        self.assertEqual(len(stmt.body.statements), 2)
    
    # ======================
    # EXPRESSION TESTS
    # ======================
    
    def test_literal_expressions(self):
        """Test literal value expressions."""
        # Integer
        expr = self._parse_expression("42")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 42)
        self.assertEqual(expr.token_type, TokenType.INTEGER)
        
        # Float
        expr = self._parse_expression("3.14159")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, 3.14159)
        self.assertEqual(expr.token_type, TokenType.FLOAT)
        
        # String
        expr = self._parse_expression('"Hello World"')
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, "Hello World")
        self.assertEqual(expr.token_type, TokenType.STRING)
        
        # Boolean
        expr = self._parse_expression("yes")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, True)
        self.assertEqual(expr.token_type, TokenType.TRUE)
        
        expr = self._parse_expression("no")
        self.assertIsInstance(expr, LiteralNode)
        self.assertEqual(expr.value, False)
        self.assertEqual(expr.token_type, TokenType.FALSE)
        
        # Null
        expr = self._parse_expression("null")
        self.assertIsInstance(expr, LiteralNode)
        self.assertIsNone(expr.value)
        self.assertEqual(expr.token_type, TokenType.NULL)
    
    def test_identifier_expression(self):
        """Test identifier expressions."""
        expr = self._parse_expression("myVariable")
        self.assertIsInstance(expr, IdentifierNode)
        self.assertEqual(expr.name, "myVariable")
    
    def test_binary_expressions(self):
        """Test binary expressions."""
        # Arithmetic
        expr = self._parse_expression("a + b")
        self.assertIsInstance(expr, BinaryExpressionNode)
        self.assertEqual(expr.operator.lexeme, "+")
        self.assertIsInstance(expr.left, IdentifierNode)
        self.assertIsInstance(expr.right, IdentifierNode)
        
        # Comparison
        expr = self._parse_expression("x > 10")
        self.assertIsInstance(expr, BinaryExpressionNode)
        self.assertEqual(expr.operator.lexeme, ">")
        
        # Logical
        expr = self._parse_expression("a and b")
        self.assertIsInstance(expr, BinaryExpressionNode)
        self.assertEqual(expr.operator.lexeme, "and")
    
    def test_unary_expressions(self):
        """Test unary expressions."""
        # Negation
        expr = self._parse_expression("-x")
        self.assertIsInstance(expr, UnaryExpressionNode)
        self.assertEqual(expr.operator.lexeme, "-")
        self.assertIsInstance(expr.operand, IdentifierNode)
        
        # Logical NOT
        expr = self._parse_expression("not isValid")
        self.assertIsInstance(expr, UnaryExpressionNode)
        self.assertEqual(expr.operator.lexeme, "not")
    
    def test_assignment_expressions(self):
        """Test assignment expressions."""
        ast = self._parse_code("x = 42;")
        
        expr_stmt = ast.statements[0]
        self.assertIsInstance(expr_stmt, ExpressionStatementNode)
        
        assign_expr = expr_stmt.expression
        self.assertIsInstance(assign_expr, AssignmentExpressionNode)
        self.assertEqual(assign_expr.name, "x")
        self.assertEqual(assign_expr.operator.lexeme, "=")
        self.assertIsInstance(assign_expr.value, LiteralNode)
    
    def test_compound_assignment(self):
        """Test compound assignment operators."""
        ast = self._parse_code("x += 5;")
        
        assign_expr = ast.statements[0].expression
        self.assertIsInstance(assign_expr, AssignmentExpressionNode)
        self.assertEqual(assign_expr.operator.lexeme, "+=")
    
    def test_function_call(self):
        """Test function call expressions."""
        expr = self._parse_expression("add(2, 3)")
        self.assertIsInstance(expr, CallExpressionNode)
        self.assertIsInstance(expr.callee, IdentifierNode)
        self.assertEqual(expr.callee.name, "add")
        self.assertEqual(len(expr.arguments), 2)
    
    def test_grouping_expression(self):
        """Test parenthesized expressions."""
        expr = self._parse_expression("(a + b)")
        self.assertIsInstance(expr, GroupingExpressionNode)
        self.assertIsInstance(expr.expression, BinaryExpressionNode)
    
    def test_operator_precedence(self):
        """Test operator precedence."""
        # a + b * c should be parsed as a + (b * c)
        expr = self._parse_expression("a + b * c")
        self.assertIsInstance(expr, BinaryExpressionNode)
        self.assertEqual(expr.operator.lexeme, "+")
        self.assertIsInstance(expr.left, IdentifierNode)
        self.assertIsInstance(expr.right, BinaryExpressionNode)
        self.assertEqual(expr.right.operator.lexeme, "*")
    
    def test_right_associativity(self):
        """Test right-associative operators."""
        # a ** b ** c should be parsed as a ** (b ** c)
        expr = self._parse_expression("a ** b ** c")
        self.assertIsInstance(expr, BinaryExpressionNode)
        self.assertEqual(expr.operator.lexeme, "**")
        self.assertIsInstance(expr.left, IdentifierNode)
        self.assertIsInstance(expr.right, BinaryExpressionNode)
        self.assertEqual(expr.right.operator.lexeme, "**")
    
    # ======================
    # SECURITY FEATURE TESTS
    # ======================
    
    def test_validate_expression(self):
        """Test validate expressions."""
        expr = self._parse_expression("validate(userInput)")
        self.assertIsInstance(expr, ValidateExpressionNode)
        self.assertIsInstance(expr.expression, IdentifierNode)
        self.assertIsNone(expr.condition)
        
        # With condition
        expr = self._parse_expression("validate(x, x > 0)")
        self.assertIsInstance(expr, ValidateExpressionNode)
        self.assertIsNotNone(expr.condition)
        self.assertIsInstance(expr.condition, BinaryExpressionNode)
    
    def test_sanitize_expression(self):
        """Test sanitize expressions."""
        expr = self._parse_expression("sanitize(userInput)")
        self.assertIsInstance(expr, SanitizeExpressionNode)
        self.assertIsInstance(expr.expression, IdentifierNode)
    
    # ======================
    # COMPLEX PROGRAM TESTS
    # ======================
    
    def test_complex_program(self):
        """Test parsing a complex program."""
        complex_code = """
        // Secure calculator program
        secure {
            hold x: num = 10;
            fixed PI: decimal = 3.14159;
            
            func calculate(a: num, b: num) -> num {
                when (validate(a, a > 0) and validate(b, b > 0)) {
                    return sanitize(a + b * PI);
                } otherwise {
                    return 0;
                }
            }
            
            hold result: num = calculate(x, 5);
            show "Result: " + result;
            
            cycle (hold i: num = 0; i < 3; i = i + 1) {
                when (i == 1) {
                    skip;
                }
                show "Number: " + i;
            }
        }
        """
        
        ast = self._parse_code(complex_code)
        self.assertIsInstance(ast, ProgramNode)
        self.assertEqual(len(ast.statements), 1)
        self.assertIsInstance(ast.statements[0], SecureBlockNode)
        
        # Verify the secure block contains multiple statements
        secure_block = ast.statements[0].body
        self.assertGreater(len(secure_block.statements), 4)
    
    # ======================
    # ERROR HANDLING TESTS
    # ======================
    
    def test_syntax_error_recovery(self):
        """Test error recovery in parsing."""
        # Invalid syntax that should generate errors but continue parsing
        code = """
        hold x = ;  // Missing expression
        hold y = 42;  // Valid statement after error
        """
        
        try:
            ast = self._parse_code(code)
            # Parser should have errors but still produce an AST
            self.assertTrue(self.parser.has_errors())
            errors = self.parser.get_errors()
            self.assertGreater(len(errors), 0)
        except ParseError:
            # Expected behavior - parser may throw on unrecoverable errors
            pass
    
    def test_missing_semicolon_error(self):
        """Test missing semicolon error."""
        with self.assertRaises(ParseError):
            self._parse_code("hold x = 42")  # Missing semicolon
    
    def test_unmatched_parentheses(self):
        """Test unmatched parentheses error."""
        with self.assertRaises(ParseError):
            self._parse_code("show (2 + 3;")  # Missing closing paren
    
    def test_invalid_assignment_target(self):
        """Test invalid assignment target error."""
        with self.assertRaises(ParseError):
            self._parse_code("42 = x;")  # Can't assign to literal
    
    def test_unexpected_token(self):
        """Test unexpected token handling."""
        with self.assertRaises(ParseError):
            self._parse_code("hold 42 x;") 
    
    # ======================
    # UTILITY TESTS
    # ======================
    
    def test_ast_printer(self):
        """Test AST printer functionality."""
        ast = self._parse_code("hold x: num = 42;")
        
        # Test that AST can be printed
        ast_str = self.ast_printer.print_ast(ast)
        self.assertIsInstance(ast_str, str)
        self.assertIn("Program", ast_str)
        self.assertIn("VariableDeclaration", ast_str)
        self.assertIn("x", ast_str)
    
    def test_parser_debug_mode(self):
        """Test parser debug mode."""
        tokens = self.lexer.tokenize("hold x = 42;")
        parser = Parser(tokens, debug_mode=True)
        
        # Parse with debug output
        ast = parser.parse()
        self.assertIsInstance(ast, ProgramNode)
    
    def test_step_mode_parsing(self):
        """Test step-by-step parsing mode."""
        tokens = self.lexer.tokenize("hold x = 42;")
        parser = Parser(tokens, debug_mode=False)
        
        steps = []
        
        def step_callback(step_info):
            steps.append(step_info)
        
        parser.enable_step_mode(step_callback)
        ast = parser.parse()
        
        # Verify steps were recorded
        self.assertGreater(len(steps), 0)
        for step in steps:
            self.assertIn('rule', step)
            self.assertIn('description', step)


class TestGrammarRules(unittest.TestCase):
    """Test specific grammar rule implementations."""
    
    def setUp(self):
        """Setup test environment."""
        self.lexer = VisualLexicalAnalyzer(visual_mode=False)
    
    def _parse_rule(self, rule_name: str, source_code: str):
        """Helper to test specific grammar rules."""
        tokens, lex_errors = self.lexer.analyze(source_code)
        parser = Parser(tokens, debug_mode=True)
        
        # Parse the entire program
        try:
            ast = parser.parse()
            return ast, parser.get_errors()
        except ParseError as e:
            return None, [e]
    
    def test_type_annotations(self):
        """Test all type annotation variants."""
        test_cases = [
            "hold x: num;",
            "hold y: decimal;", 
            "hold name: text;",
            "hold isValid: flag;"
        ]
        
        for code in test_cases:
            ast, errors = self._parse_rule("type", code)
            self.assertEqual(len(errors), 0, f"Failed to parse: {code}")
    
    def test_all_operators(self):
        """Test all binary operators."""
        operators = [
            "+", "-", "*", "/", "%", "**",
            "<", "<=", ">", ">=", "==", "!=",
            "and", "or", "&&", "||"
        ]
        
        for op in operators:
            code = f"show a {op} b;"
            ast, errors = self._parse_rule("binary_op", code)
            self.assertEqual(len(errors), 0, f"Failed to parse operator: {op}")


def run_tests():
    """Run all syntax analysis tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSyntaxAnalysis))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestGrammarRules))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    if result.wasSuccessful():
        print("\n🎉 All syntax analysis tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()