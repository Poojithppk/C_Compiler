"""
Visual Lexical Analyzer for Custom Compiler

This module implements a comprehensive lexical analyzer with:
1. Visual token highlighting and step-by-step animation
2. Error recovery and suggestion system
3. Security-aware token detection
4. Interactive debugging capabilities
"""

import re
import sys
import time
from typing import List, Optional, Tuple, Iterator, Callable
from dataclasses import dataclass
from pathlib import Path

from .tokens import Token, TokenType, KEYWORDS, OPERATORS, PUNCTUATION, LexicalError


@dataclass
class LexerState:
    """Tracks the current state of the lexical analyzer."""
    source: str
    position: int
    line: int
    column: int
    tokens: List[Token]
    errors: List[LexicalError]
    current_char: Optional[str]
    visual_mode: bool = False


class VisualLexicalAnalyzer:
    """
    Comprehensive Lexical Analyzer with Visual Capabilities
    
    Features:
    - Token-by-token visualization
    - Error recovery with suggestions
    - Security-aware analysis
    - Interactive debugging
    """
    
    def __init__(self, visual_mode: bool = True, debug_mode: bool = False):
        self.visual_mode = visual_mode
        self.debug_mode = debug_mode
        self.state = None
        self.visual_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        
    def set_visual_callback(self, callback: Callable):
        """Set callback function for visual updates."""
        self.visual_callback = callback
        
    def set_error_callback(self, callback: Callable):
        """Set callback function for error handling."""
        self.error_callback = callback
        
    def analyze(self, source_code: str) -> Tuple[List[Token], List[LexicalError]]:
        """
        Main method to perform lexical analysis with visual feedback.
        
        Args:
            source_code: The source code to analyze
            
        Returns:
            Tuple of (tokens, errors)
        """
        self.state = LexerState(
            source=source_code,
            position=0,
            line=1,
            column=1,
            tokens=[],
            errors=[],
            current_char=source_code[0] if source_code else None,
            visual_mode=self.visual_mode
        )
        
        print("🚀 Starting Lexical Analysis...")
        print("=" * 50)
        
        while not self._is_at_end():
            try:
                self._scan_token()
                if self.visual_mode:
                    self._visual_update()
                    time.sleep(0.1)  # Small delay for visual effect
            except LexicalError as e:
                self.state.errors.append(e)
                if self.error_callback:
                    suggestion = self.error_callback(e)
                    if suggestion:
                        print(f"✅ Applied suggestion: {suggestion}")
                self._recover_from_error()
                
        # Add EOF token
        self.state.tokens.append(Token(
            TokenType.EOF, "", None, 
            self.state.line, self.state.column, 0
        ))
        
        self._print_summary()
        return self.state.tokens, self.state.errors
    
    def _scan_token(self):
        """Scan and identify the next token."""
        self._skip_whitespace()
        
        if self._is_at_end():
            return
            
        start_pos = self.state.position
        start_col = self.state.column
        char = self._advance()
        
        # Numbers (Integer and Float)
        if char.isdigit():
            self._scan_number(start_pos, start_col)
            
        # Identifiers and Keywords
        elif char.isalpha() or char == '_':
            self._scan_identifier(start_pos, start_col)
            
        # String literals
        elif char in ['"', "'"]:
            self._scan_string(start_pos, start_col, char)
            
        # Comments
        elif char == '/' and self._peek() == '/':
            self._scan_comment()
            
        # Multi-character operators
        elif char in '=!<>&|+-*':
            self._scan_operator(start_pos, start_col, char)
            
        # Single character tokens
        elif char in PUNCTUATION:
            self._create_token(PUNCTUATION[char], char, char, start_col)
            
        # Newlines
        elif char == '\n':
            self._create_token(TokenType.NEWLINE, char, None, start_col)
            self.state.line += 1
            self.state.column = 1
            
        else:
            # Unknown character - create error but try to recover
            error = LexicalError(
                f"Unexpected character: '{char}'", 
                self.state.line, 
                start_col
            )
            self.state.errors.append(error)
            print(f"❌ {error}")
    
    def _scan_number(self, start_pos: int, start_col: int):
        """Scan integer or floating-point number."""
        while self._peek() and self._peek().isdigit():
            self._advance()
            
        # Check for decimal point
        if self._peek() == '.' and self._peek_next() and self._peek_next().isdigit():
            self._advance()  # consume '.'
            while self._peek() and self._peek().isdigit():
                self._advance()
                
            # Create float token
            lexeme = self.state.source[start_pos:self.state.position]
            value = float(lexeme)
            self._create_token(TokenType.FLOAT, lexeme, value, start_col)
        else:
            # Create integer token
            lexeme = self.state.source[start_pos:self.state.position]
            value = int(lexeme)
            self._create_token(TokenType.INTEGER, lexeme, value, start_col)
            
    def _scan_identifier(self, start_pos: int, start_col: int):
        """Scan identifier or keyword."""
        while (self._peek() and 
               (self._peek().isalnum() or self._peek() in ['_'])):
            self._advance()
            
        lexeme = self.state.source[start_pos:self.state.position]
        
        # Check if it's a keyword
        token_type = KEYWORDS.get(lexeme.lower(), TokenType.IDENTIFIER)
        
        # Handle boolean values
        if token_type == TokenType.TRUE:
            value = True
        elif token_type == TokenType.FALSE:
            value = False
        elif token_type == TokenType.NULL:
            value = None
        else:
            value = lexeme
            
        self._create_token(token_type, lexeme, value, start_col)
        
    def _scan_string(self, start_pos: int, start_col: int, quote_char: str):
        """Scan string literal."""
        value = ""
        
        while self._peek() and self._peek() != quote_char:
            if self._peek() == '\n':
                self.state.line += 1
                self.state.column = 1
            elif self._peek() == '\\':
                # Handle escape sequences
                self._advance()  # consume backslash
                escaped_char = self._advance()
                if escaped_char in ['n', 't', 'r', '\\', '"', "'"]:
                    escape_map = {'n': '\n', 't': '\t', 'r': '\r', 
                                '\\': '\\', '"': '"', "'": "'"}
                    value += escape_map.get(escaped_char, escaped_char)
                else:
                    value += escaped_char
            else:
                value += self._advance()
                
        if self._peek() == quote_char:
            self._advance()  # consume closing quote
            lexeme = self.state.source[start_pos:self.state.position]
            self._create_token(TokenType.STRING, lexeme, value, start_col)
        else:
            raise LexicalError(
                f"Unterminated string literal", 
                self.state.line, 
                start_col
            )
    
    def _scan_comment(self):
        """Scan single-line comment."""
        start_col = self.state.column - 1
        comment_text = ""
        
        # Skip the '//'
        self._advance()
        
        while self._peek() and self._peek() != '\n':
            comment_text += self._advance()
            
        self._create_token(TokenType.COMMENT, f"//{comment_text}", comment_text, start_col)
        
    def _scan_operator(self, start_pos: int, start_col: int, first_char: str):
        """Scan single or multi-character operators."""
        # Check for multi-character operators
        if self._peek():
            two_char = first_char + self._peek()
            if two_char in OPERATORS:
                self._advance()  # consume second character
                self._create_token(OPERATORS[two_char], two_char, two_char, start_col)
                return
                
        # Single character operator
        if first_char in OPERATORS:
            self._create_token(OPERATORS[first_char], first_char, first_char, start_col)
        else:
            raise LexicalError(
                f"Unknown operator: '{first_char}'", 
                self.state.line, 
                start_col
            )
    
    def _create_token(self, token_type: TokenType, lexeme: str, value: any, start_col: int):
        """Create a new token and add it to the token list."""
        token = Token(
            token_type=token_type,
            lexeme=lexeme,
            value=value,
            line=self.state.line,
            column=start_col,
            length=len(lexeme)
        )
        self.state.tokens.append(token)
        
        if self.visual_mode:
            print(f"🔍 Found: {token}")
            
    def _skip_whitespace(self):
        """Skip whitespace characters (except newlines)."""
        while (self._peek() and 
               self._peek() in [' ', '\t', '\r'] and 
               self._peek() != '\n'):
            self._advance()
    
    def _advance(self) -> str:
        """Advance to the next character and return current."""
        if self._is_at_end():
            return '\0'
            
        char = self.state.current_char
        self.state.position += 1
        self.state.column += 1
        
        if self.state.position < len(self.state.source):
            self.state.current_char = self.state.source[self.state.position]
        else:
            self.state.current_char = None
            
        return char
    
    def _peek(self) -> Optional[str]:
        """Look at the next character without consuming it."""
        if self.state.position >= len(self.state.source):
            return None
        return self.state.source[self.state.position]
    
    def _peek_next(self) -> Optional[str]:
        """Look two characters ahead."""
        if self.state.position + 1 >= len(self.state.source):
            return None
        return self.state.source[self.state.position + 1]
    
    def _is_at_end(self) -> bool:
        """Check if we've reached the end of source."""
        return self.state.position >= len(self.state.source)
    
    def _recover_from_error(self):
        """Attempt to recover from lexical errors."""
        # Simple recovery: skip current character and continue
        if not self._is_at_end():
            self._advance()
            
    def _visual_update(self):
        """Update visual display if callback is set."""
        if self.visual_callback and self.state.tokens:
            self.visual_callback(self.state.tokens[-1], self.state)
            
    def _print_summary(self):
        """Print analysis summary."""
        print("\n" + "=" * 50)
        print("🎯 Lexical Analysis Complete!")
        print(f"📊 Tokens found: {len(self.state.tokens)}")
        print(f"❌ Errors: {len(self.state.errors)}")
        
        if self.state.errors:
            print("\n🔍 Error Details:")
            for error in self.state.errors:
                print(f"  - {error}")
                
        print("\n🏷️  Token Summary:")
        token_counts = {}
        for token in self.state.tokens:
            token_type = token.token_type.name
            token_counts[token_type] = token_counts.get(token_type, 0) + 1
            
        for token_type, count in sorted(token_counts.items()):
            print(f"  {token_type}: {count}")


def test_lexical_analyzer():
    """Test function to demonstrate the lexical analyzer."""
    
    # Sample code in our custom language
    sample_code = '''
    // This is a test program
    var x: int = 42;
    var message: string = "Hello, World!";
    var pi: float = 3.14159;
    var isValid: bool = true;
    
    func calculateArea(radius: float) -> float {
        secure validate(radius > 0);
        return pi * radius ** 2;
    }
    
    if (x >= 10 && isValid) {
        print(message);
    } else {
        print("Invalid input");
    }
    '''
    
    print("🧪 Testing Lexical Analyzer")
    print("=" * 50)
    print("📝 Source Code:")
    print(sample_code)
    print("\n" + "=" * 50)
    
    # Create and run analyzer
    analyzer = VisualLexicalAnalyzer(visual_mode=True, debug_mode=True)
    tokens, errors = analyzer.analyze(sample_code)
    
    return tokens, errors


if __name__ == "__main__":
    test_lexical_analyzer()