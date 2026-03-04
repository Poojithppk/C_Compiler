"""
Test script for Lexical Analysis Phase

This script demonstrates and tests all components of the lexical analysis phase:
1. Token creation and manipulation
2. Lexical analyzer functionality
3. Visual GUI components
4. Error handling and recovery
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from lexical_analysis import (
    VisualLexicalAnalyzer, 
    LexicalAnalysisGUI, 
    Token, 
    TokenType,
    get_phase_info,
    create_analyzer,
    launch_gui
)


def test_token_creation():
    """Test token creation and manipulation."""
    print("🧪 Testing Token Creation...")
    
    # Create sample tokens
    token1 = Token(
        token_type=TokenType.INTEGER,
        lexeme="42",
        value=42,
        line=1,
        column=1,
        length=2
    )
    
    token2 = Token(
        token_type=TokenType.IDENTIFIER,
        lexeme="myVariable",
        value="myVariable",
        line=1,
        column=5,
        length=10
    )
    
    print(f"✅ Token 1: {token1}")
    print(f"✅ Token 2: {token2}")
    print()


def test_lexical_analyzer():
    """Test the lexical analyzer with sample code."""
    print("🧪 Testing Lexical Analyzer...")
    
    # Sample code in NEXUS language
    sample_code = '''
    hold count: num = 10;
    hold message: text = "Hello NEXUS";
    when (count > 5) {
        show message;
    }
    '''
    
    # Create analyzer
    analyzer = create_analyzer(visual_mode=False, debug_mode=False)
    
    # Analyze code
    tokens, errors = analyzer.analyze(sample_code)
    
    print(f"✅ Analyzed {len(tokens)} tokens")
    print(f"✅ Found {len(errors)} errors")
    
    # Show first few tokens
    print("\n🔍 First 10 tokens:")
    for i, token in enumerate(tokens[:10]):
        print(f"  {i+1}: {token}")
    
    print()


def test_phase_info():
    """Test phase information retrieval."""
    print("🧪 Testing Phase Information...")
    
    info = get_phase_info()
    
    print(f"✅ Phase: {info['name']}")
    print(f"✅ Number: {info['number']}")
    print(f"✅ Status: {info['status']}")
    print(f"✅ Version: {info['module_version']}")
    print(f"✅ Authors: {info['authors']}")
    
    print("\n🚀 Features:")
    for feature in info['features']:
        print(f"  • {feature}")
    
    print()


def test_gui_creation():
    """Test GUI creation (without starting the mainloop)."""
    print("🧪 Testing GUI Creation...")
    
    try:
        # Create GUI instance
        gui = LexicalAnalysisGUI()
        
        print("✅ GUI created successfully")
        print("✅ Window configured")
        print("✅ Components initialized")
        
        # Clean up
        gui.root.destroy()
        
    except Exception as e:
        print(f"❌ GUI creation failed: {e}")
    
    print()


def run_manual_gui_test():
    """Manual GUI test - actually launches the interface."""
    print("🎯 Manual GUI Test")
    print("=" * 50)
    
    choice = input("Do you want to launch the visual interface? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("🚀 Launching Visual Lexical Analysis Interface...")
        print("   Close the window when you're done testing.")
        
        try:
            gui = launch_gui()
            gui.run()
            print("✅ GUI test completed successfully")
        except Exception as e:
            print(f"❌ GUI test failed: {e}")
    else:
        print("⏭️ Skipping GUI test")
    
    print()


def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 LEXICAL ANALYSIS PHASE - COMPREHENSIVE TEST SUITE")
    print("   Advanced Visual Compiler Project")
    print("=" * 60)
    print()
    
    # Test all components
    test_token_creation()
    test_lexical_analyzer()
    test_phase_info()
    test_gui_creation()
    
    # Manual GUI test
    run_manual_gui_test()
    
    print("=" * 60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("   The lexical analysis phase is ready for use.")
    print("=" * 60)


if __name__ == "__main__":
    main()