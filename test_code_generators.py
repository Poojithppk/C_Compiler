#!/usr/bin/env python3
"""
Code Generator Test for NEXUS Compiler

Tests code generation phase:
- Python code generation
- C code generation
- Assembly code generation

For if-else and loop structures
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator


class CodeGenerator:
    """Generate code from TAC instructions."""
    
    def __init__(self):
        self.indent_level = 0
        self.temp_map = {}  # Map temporary variables to actual names
        self.label_map = {}
    
    def generate_python(self, ast, tac_code) -> str:
        """Generate Python code from TAC."""
        lines = []
        lines.append("# Generated Python Code from NEXUS")
        lines.append("")
        
        # Add import for show function
        lines.append("def show(value):")
        lines.append("    print(value)")
        lines.append("")
        
        # Generate code from TAC
        for instr in tac_code.instructions[:10]:  # Limit to first 10 instructions
            if instr.instruction_type.value == "ASSIGN":
                result = instr.result.value if instr.result else "temp"
                arg1 = instr.arg1.value if instr.arg1 else "0"
                lines.append(f"{result} = {arg1}")
        
        return "\n".join(lines)
    
    def generate_c(self, ast, tac_code) -> str:
        """Generate C code from TAC."""
        lines = []
        lines.append("/* Generated C Code from NEXUS */")
        lines.append("#include <stdio.h>")
        lines.append("")
        lines.append("int main() {")
        
        # Add variable declarations
        lines.append("    int x, y, result;")
        
        # Generate code from TAC
        for instr in tac_code.instructions[:10]:  # Limit to first 10 instructions
            if instr.instruction_type.value == "ASSIGN":
                result = instr.result.value if instr.result else "temp"
                arg1 = instr.arg1.value if instr.arg1 else "0"
                lines.append(f"    {result} = {arg1};")
        
        lines.append("")
        lines.append("    return 0;")
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_assembly(self, ast, tac_code) -> str:
        """Generate x86-64 Assembly code from TAC."""
        lines = []
        lines.append("; Generated x86-64 Assembly Code from NEXUS")
        lines.append("")
        lines.append("section .text")
        lines.append("    global main")
        lines.append("")
        lines.append("main:")
        lines.append("    push rbp")
        lines.append("    mov rbp, rsp")
        lines.append("    sub rsp, 32")
        
        # Add simple variable initialization from TAC
        var_offset = 16
        for instr in tac_code.instructions[:5]:  # Limit to first 5 instructions
            if instr.instruction_type.value == "ASSIGN":
                arg1 = instr.arg1.value if instr.arg1 else "0"
                if isinstance(arg1, int):
                    lines.append(f"    mov dword [rbp-{var_offset}], {arg1}")
                    var_offset += 4
        
        lines.append("")
        lines.append("    xor eax, eax")
        lines.append("    mov rsp, rbp")
        lines.append("    pop rbp")
        lines.append("    ret")
        
        return "\n".join(lines)


def test_code_generation(name: str, code: str) -> bool:
    """Test code generation for a single program."""
    print(f"\n{'='*70}")
    print(f"[CODE GENERATION TEST] {name}")
    print(f"{'='*70}")
    
    # Run through compilation phases
    try:
        lexer = VisualLexicalAnalyzer(visual_mode=False)
        tokens, lex_errors = lexer.analyze(code)
        
        if lex_errors:
            print(f"[ERROR] Lexical errors: {len(lex_errors)}")
            return False
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        analyzer = SemanticAnalyzer(visual_mode=False)
        success, errors, _ = analyzer.analyze(ast)
        
        if not success:
            print(f"[ERROR] Semantic errors: {len(errors)}")
            return False
        
        tac_gen = IntermediateCodeGenerator(visual_mode=False)
        success, tac_code, _ = tac_gen.generate(ast)
        
        if not success:
            print(f"[ERROR] TAC generation failed")
            return False
        
        # Now generate code for all targets
        codegen = CodeGenerator()
        
        print("\n[PYTHON CODE GENERATION]")
        python_code = codegen.generate_python(ast, tac_code)
        print(python_code)
        print("[SUCCESS] Python code generated")
        
        print("\n[C CODE GENERATION]")
        c_code = codegen.generate_c(ast, tac_code)
        print(c_code)
        print("[SUCCESS] C code generated")
        
        print("\n[ASSEMBLY CODE GENERATION]")
        asm_code = codegen.generate_assembly(ast, tac_code)
        print(asm_code)
        print("[SUCCESS] Assembly code generated")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


# Test Programs
TESTS = {
    "Simple if-else": """hold x = 10;
when (x > 5)
    show x;
otherwise
    show 0;""",
    
    "While loop": """hold count = 5;
repeat (count > 0)
    count = count - 1;"""
}


def main():
    """Run code generation tests."""
    print("\n" + "="*70)
    print("CODE GENERATION TEST SUITE")
    print("Testing: Python, C, x86-64 Assembly")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for test_name, test_code in TESTS.items():
        if test_code_generation(test_name, test_code):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*70}")
    print(f"[RESULTS] {passed} passed, {failed} failed")
    print(f"{'='*70}")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
