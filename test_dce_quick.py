#!/usr/bin/env python3
"""
QUICK TEST: Dead Code Elimination - Before & After
====================================================

Run this immediately to see dead code elimination in action:

    python test_dce_quick.py

Shows real TAC code with and without dead code elimination.
"""

import sys
sys.path.insert(0, 'src')

from lexical_analysis.lexer import VisualLexicalAnalyzer
from syntax_analysis.parser import Parser
from semantic_analysis.semantic import SemanticAnalyzer
from intermediate_code.intermediate_code_generator import IntermediateCodeGenerator
import re


def print_header(text):
    print("\n" + "╔" + "═"*78 + "╗")
    print("║ " + text.center(76) + " ║")
    print("╚" + "═"*78 + "╝")


def print_subsection(text):
    print("\n" + "▶ " + text)
    print("  " + "─"*76)


# ═══════════════════════════════════════════════════════════════════════════════

print_header("DEAD CODE ELIMINATION DEMO")

# Test Program
nexus_code = """
hold unused1: num = 100;
hold unused2: num = 200;
hold x: num = 10;
hold y: num = 20;
hold dead_sum: num = 999;
hold result: num = x + y;
show result;
"""

print_subsection("1. NEXUS SOURCE CODE (Input)")
print(nexus_code)

try:
    # Phase 1-4: Parse to TAC
    lexer = VisualLexicalAnalyzer(visual_mode=False)
    tokens = lexer.tokenize(nexus_code)
    
    parser = Parser(tokens, visual_mode=False)
    ast = parser.parse_program()
    
    semantic_analyzer = SemanticAnalyzer(visual_mode=False)
    sem_result = semantic_analyzer.analyze(ast)
    
    tac_generator = IntermediateCodeGenerator(visual_mode=False)
    tac_code = tac_generator.generate(ast, sem_result.symbol_table)
    
    original_instr = [str(i).strip() for i in tac_code.instructions]
    
    print_subsection("2. BEFORE OPTIMIZATION (Raw TAC)")
    print(f"📊 Total Instructions: {len(original_instr)}\n")
    for i, instr in enumerate(original_instr, 1):
        print(f"   {i:2}. {instr}")
    
    # Identify used variables
    print_subsection("3. ANALYZING VARIABLE USAGE")
    used_vars = set()
    for instr in original_instr:
        operand_match = re.findall(r'a[0-9]=(\w+)', instr)
        for var in operand_match:
            used_vars.add(var)
        write_match = re.match(r'WRITE\s+a1=(\w+)', instr)
        if write_match:
            used_vars.add(write_match.group(1))
    
    print(f"   Variables that are USED: {used_vars}")
    
    # Dead code elimination
    cleaned = []
    for instr in original_instr:
        assign_match = re.match(r'ASSIGN\s+t=(\w+)\s+a1=', instr)
        if assign_match:
            var_name = assign_match.group(1)
            if var_name in used_vars or var_name.startswith('t'):
                cleaned.append(instr)
                print(f"   ✓ KEEP: {instr}")
            else:
                print(f"   ✗ REMOVE: {instr} (unused: {var_name})")
        else:
            cleaned.append(instr)
    
    print_subsection("4. AFTER OPTIMIZATION (Dead Code Eliminated)")
    print(f"📊 Total Instructions: {len(cleaned)}\n")
    for i, instr in enumerate(cleaned, 1):
        print(f"   {i:2}. {instr}")
    
    # Results
    print_subsection("5. OPTIMIZATION RESULTS")
    reduction = len(original_instr) - len(cleaned)
    percentage = round(100 * reduction / len(original_instr), 1) if len(original_instr) > 0 else 0
    
    print(f"   Original:  {len(original_instr)} instructions")
    print(f"   Optimized: {len(cleaned)} instructions")
    print(f"   Removed:   {reduction} instructions")
    print(f"   Reduction: {percentage}%")
    
    if reduction > 0:
        print(f"\n   ✅ DEAD CODE ELIMINATION SUCCESSFUL!")
        print(f"   📈 {percentage}% code size reduction achieved")
    else:
        print(f"\n   ℹ️  No dead code found in this example")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print_header("✅ DEAD CODE ELIMINATION TEST COMPLETE")
