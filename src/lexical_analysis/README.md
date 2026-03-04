# Lexical Analysis Phase Documentation

## Overview

The Lexical Analysis Phase is the first and foundational phase of our Advanced Visual Compiler. It converts source code written in our custom programming language into a stream of tokens that can be processed by subsequent compiler phases.

## 🎯 Features

### Core Functionality
- **Token Recognition**: Recognizes all language constructs including:
  - Keywords (`var`, `func`, `if`, `while`, etc.)
  - Operators (`+`, `-`, `==`, `&&`, etc.)
  - Literals (integers, floats, strings, booleans)
  - Identifiers and symbols
  - Comments and special tokens

### Visual Capabilities
- **Step-by-Step Animation**: Watch tokens being identified one by one
- **Real-Time Highlighting**: Source code highlighting as tokens are processed
- **Interactive Token Table**: Detailed view of all identified tokens
- **Error Visualization**: Clear display of lexical errors with suggestions

### Advanced Features
- **Error Recovery**: Intelligent error detection and recovery mechanisms
- **Security-Aware Tokens**: Special recognition for security keywords
- **Multi-Mode Analysis**: Both automatic and step-by-step analysis modes
- **Export Capabilities**: Save and load source code files

## 📁 File Structure

```
lexical_analysis/
├── __init__.py              # Module initialization and exports
├── tokens.py                # Token definitions and types
├── lexer.py                 # Core lexical analyzer engine
├── lexical_gui.py           # Visual interface for lexical analysis
├── test_lexical.py          # Comprehensive test suite
└── README.md                # This documentation file
```

## 🚀 Quick Start

### 1. Basic Token Analysis

```python
from lexical_analysis import create_analyzer

# Create analyzer
analyzer = create_analyzer(visual_mode=False)

# Analyze source code
source_code = '''
var x: int = 42;
var message: string = "Hello World";
'''

tokens, errors = analyzer.analyze(source_code)

# Display results
for token in tokens:
    print(token)
```

### 2. Visual Interface

```python
from lexical_analysis import launch_gui

# Launch the visual interface
gui = launch_gui()
gui.run()
```

### 3. Using Main Application

```python
# Run from the main application
python src/main.py
# Then select "🔍 LEXICAL ANALYSIS" phase
```

## 🔧 Token Types

Our custom language supports the following token types:

### Literals
- `INTEGER`: Whole numbers (e.g., `42`, `100`)
- `FLOAT`: Decimal numbers (e.g., `3.14`, `2.5`)
- `STRING`: Text literals (e.g., `"Hello"`, `'World'`)
- `BOOLEAN`: True/false values

### Keywords
- **Control Flow**: `if`, `else`, `elif`, `while`, `for`, `break`, `continue`
- **Functions**: `func`, `return`
- **Variables**: `var`, `const`
- **Types**: `int`, `float`, `string`, `bool`
- **Security**: `secure`, `validate`, `sanitize`

### Operators
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`, `**`
- **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical**: `&&`, `||`, `!`
- **Assignment**: `=`, `+=`, `-=`, `*=`, `/=`

### Punctuation
- **Brackets**: `(`, `)`, `{`, `}`, `[`, `]`
- **Separators**: `;`, `,`, `.`, `:`, `->`

## 🎮 Visual Interface Guide

### Main Tabs

1. **📝 Source Code Editor**
   - Write or load source code
   - Real-time syntax highlighting
   - Line numbering
   - File operations (load/save)

2. **🏷️ Token Visualization**
   - Live token stream display
   - Detailed token information
   - Interactive token selection
   - Current token highlighting

3. **📊 Analysis Results**
   - Statistical summary
   - Error details and suggestions
   - Token distribution analysis

### Control Panel

- **🚀 Start Analysis**: Begin lexical analysis
- **👆 Step Forward**: Move through tokens one by one (Step Mode)
- **🔄 Reset**: Clear all analysis data
- **Analysis Modes**:
  - **Step Mode**: Manual token-by-token progression
  - **Auto Mode**: Automatic analysis with animation

## 🔍 Sample Language Code

```javascript
// Sample Program in Our Custom Language
var x: int = 42;
var message: string = "Hello, Compiler!";
var pi: float = 3.14159;
var isActive: bool = true;

// Function with security validation
func calculateArea(radius: float) -> float {
    secure validate(radius > 0);
    return pi * radius ** 2;
}

// Conditional with logical operators
if (x >= 10 && isActive) {
    print(message);
    var result: float = calculateArea(5.0);
} else {
    print("Conditions not met");
}

// Loop example
for (var i: int = 0; i < 5; i++) {
    print("Iteration: " + i);
}
```

## 🧪 Testing

### Run Comprehensive Tests

```bash
cd src/lexical_analysis
python test_lexical.py
```

### Test Components

1. **Token Creation Test**: Verify token objects work correctly
2. **Analyzer Test**: Test lexical analysis on sample code
3. **Phase Info Test**: Verify module information
4. **GUI Creation Test**: Test interface initialization
5. **Manual GUI Test**: Interactive testing option

## 🐛 Error Handling

The lexical analyzer includes robust error handling:

### Error Types
- **Unexpected Characters**: Unknown symbols in source code
- **Unterminated Strings**: Missing closing quotes
- **Invalid Numbers**: Malformed numeric literals
- **Unknown Operators**: Unrecognized operator sequences

### Recovery Mechanisms
- **Character Skipping**: Skip invalid characters and continue
- **Synchronization**: Find next valid token boundary
- **Error Reporting**: Detailed error messages with line/column info
- **Suggestion System**: Context-aware correction suggestions

## 📊 Output Format

### Token Structure
Each token contains:
- **Type**: TokenType enum value
- **Lexeme**: Original text from source
- **Value**: Processed value (for literals)
- **Line**: Line number in source
- **Column**: Column position
- **Length**: Character length

### Example Output
```
Token(INTEGER, '42', 42, Line: 1, Col: 12)
Token(IDENTIFIER, 'myVar', myVar, Line: 1, Col: 15)
Token(ASSIGN, '=', =, Line: 1, Col: 21)
```

## 🔗 Integration

### With Other Phases
The lexical analysis phase outputs tokens that feed into:
- **Syntax Analysis**: Uses tokens to build parse trees
- **Semantic Analysis**: Processes identifiers and types
- **Code Generation**: Converts tokens to target languages

### API Usage
```python
# For other compiler phases
from lexical_analysis import VisualLexicalAnalyzer, TokenType

analyzer = VisualLexicalAnalyzer(visual_mode=False)
tokens, errors = analyzer.analyze(source_code)

# Filter tokens by type
keywords = [t for t in tokens if t.token_type in keyword_types]
identifiers = [t for t in tokens if t.token_type == TokenType.IDENTIFIER]
```

## 🎯 Next Steps

After completing lexical analysis:

1. **Phase 2**: Syntax Analysis (Parse Tree Generation)
2. **Phase 3**: Semantic Analysis (Type Checking)
3. **Phase 4**: Intermediate Code Generation
4. **Phase 5**: Optimization
5. **Phase 6**: Multi-Target Code Generation

## 👥 Authors

- **Anjani**: Core Compiler Logic, Backend, Optimization
- **Poojith**: UI, Visualization, Testing, Documentation

---

**Status**: ✅ Complete and Ready for Use  
**Version**: 1.0.0  
**Last Updated**: March 5, 2026