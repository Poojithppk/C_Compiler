"""Test script for secure statement parsing."""

from src.compiler.lexer import lex_analysis_test
from src.syntax_analysis.parser import SyntaxAnalyzer

# Test secure statement cases
test_code = '''
function calculateArea(radius: float) {
    secure validate(radius > 0);
    return 3.14 * radius * radius;
}

function processRadius(value: float) -> float {
    secure {
        validate(value > 0);
        sanitize(value);
    }
    return value * value;
}
'''

print("Testing secure statement parsing:\n")
print("Code to parse:")
print(test_code)
print("\n" + "="*40)

# Perform lexical analysis
tokens, errors = lex_analysis_test(test_code, detailed=False)
if errors:
    print(f"Lexical errors: {errors}")
else:
    print(f"✓ Lexical analysis successful - {len(tokens)} tokens found")

# Truncate excessive lexing output for cleaner display
if len(tokens) > 0:
    print("\nProceeding with syntax analysis...")
    
    # Perform syntax analysis
    parser = SyntaxAnalyzer(tokens)
    ast, errors = parser.parse()
    
    if errors:
        print(f"\nParsing errors ({len(errors)}):")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")
    else:
        print("✓ Syntax analysis successful!")
        print(f"✓ AST generated with root type: {type(ast).__name__}")
        
        # Count nodes by type
        from collections import Counter
        def count_nodes(node):
            counts = Counter()
            counts[type(node).__name__] += 1
            
            for attr_name in dir(node):
                if not attr_name.startswith('_') and hasattr(node, attr_name):
                    attr = getattr(node, attr_name)
                    if hasattr(attr, 'accept'):  # AST node
                        subcounts = count_nodes(attr)
                        counts.update(subcounts)
                    elif isinstance(attr, list):
                        for item in attr:
                            if hasattr(item, 'accept'):  # AST node
                                subcounts = count_nodes(item)
                                counts.update(subcounts)
            return counts
        
        if ast:
            node_counts = count_nodes(ast)
            print(f"\nAST node breakdown:")
            for node_type, count in node_counts.most_common():
                print(f"  {node_type}: {count}")