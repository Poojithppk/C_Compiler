#!/usr/bin/env python3
"""
NEXUS Language Code Examples - Dead Code Elimination & Optimization
=====================================================================

This file contains pure NEXUS source code examples that you can
paste into the Optimization GUI to see dead code elimination in action.

To use:
1. Run: python src/main.py  (launches the GUI)
2. Click "🚀 CODE OPTIMIZATION PHASE"
3. Paste any example below into the code editor
4. Click "▶️ Optimize" button
5. Check the "✨ Optimized Code (3-AC)" tab to see results

═══════════════════════════════════════════════════════════════════════════════
"""

print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                  NEXUS LANGUAGE SYNTAX REFERENCE                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

📝 BASIC SYNTAX:

Variable Declaration:
  hold x: num = 10;              // Integer variable
  hold name: text = "Alice";     // String variable
  hold active: flag = yes;       // Boolean variable
  hold pi: decimal = 3.14;       // Float variable

Output:
  show "Hello World";            // Print string
  show x;                        // Print variable
  show x + y;                    // Print expression

Conditionals:
  when (x > 10) {
    show "Big";
  } otherwise {
    show "Small";
  }

Loops:
  loop (i = 0; i < 10; i++) {
    show i;
  }

Operators:
  Arithmetic: + - * / %
  Comparison: > < >= <= == !=
  Logical: and or not

═══════════════════════════════════════════════════════════════════════════════
""")


examples = {
    "EXAMPLE 1 - Simple Unused Variables": """
// DEAD CODE EXAMPLE: Variables declared but never used

hold x: num = 10;
hold y: num = 20;
hold unused1: num = 100;
hold unused2: num = 200;
hold unused3: num = 300;
hold result: num = x + y;

show result;

// ANALYSIS:
// ✓ x is used: result = x + y
// ✓ y is used: result = x + y
// ✓ result is used: show result
// ✗ unused1, unused2, unused3 are NEVER READ → DEAD CODE
//
// After optimization:
// - These variables are removed from TAC
// - No instructions generated for them
// - Code is ~30% smaller
""",

    "EXAMPLE 2 - Dead Variables in Calculations": """
// Multiple calculations where some are never used

hold a: num = 5;
hold b: num = 10;
hold c: num = 15;

hold temp1: num = a + b;
hold temp2: num = b + c;
hold temp3: num = a + c;

hold final: num = temp1 + 10;

show final;

// ANALYSIS:
// ✓ temp1 is used: final = temp1 + 10
// ✗ temp2 is DEAD (never read)
// ✗ temp3 is DEAD (never read)
//
// Optimization removes temp2 and temp3 calculations
""",

    "EXAMPLE 3 - Dead Code in Conditionals": """
// Variables assigned but used only in unreachable path

hold user_type: text = "normal";
hold age: num = 25;

hold admin_data: num = 999999;
hold admin_access: num = 888888;
hold normal_access: num = 1;

when (age >= 18) {
    show normal_access;
} otherwise {
    show "Too young";
}

// ANALYSIS:
// ✗ admin_data is DEAD (assigned but never read)
// ✗ admin_access is DEAD (assigned but never read)
// ✓ normal_access is used: show normal_access
//
// Dead code removed during optimization phase
""",

    "EXAMPLE 4 - Unused Temporary Variables": """
// Intermediate calculations that are never used

hold x: num = 100;
hold y: num = 50;

hold intermediate1: num = x * 2;
hold intermediate2: num = y * 3;
hold intermediate3: num = x + y;

hold used_only: num = 5;

show used_only;

// ANALYSIS:
// ✗ intermediate1 is DEAD (never used in any expression)
// ✗ intermediate2 is DEAD (never used in any expression)
// ✗ intermediate3 is DEAD (never used in any expression)
// ✓ used_only is used: show used_only
//
// 3 unnecessary computations eliminated
""",

    "EXAMPLE 5 - Dead Code with Loops": """
// Loop variables and dead code

hold count: num = 0;
hold unused_counter: num = 0;
hold sum_result: num = 0;

loop (i = 0; i < 5; i++) {
    sum_result = sum_result + i;
}

show sum_result;

// ANALYSIS:
// ✗ unused_counter is DEAD (assigned, never read)
// ✓ count is technically unused
// ✓ sum_result is used: show sum_result
// ✓ i is used in loop condition
//
// Optimization removes unused_counter
""",

    "EXAMPLE 6 - Mixed Dead Code and Constants": """
// Combines dead code with constant folding opportunities

hold ten: num = 10;
hold twenty: num = 20;
hold thirty: num = 30;

hold dead_calc1: num = 5 + 5;
hold dead_calc2: num = 10 * 2;
hold dead_calc3: num = 100 - 50;

hold active_calc: num = ten + twenty;

show active_calc;

// ANALYSIS FOR OPTIMIZATION:
// Dead Code Elimination:
//   ✗ dead_calc1, dead_calc2, dead_calc3 are DEAD
// 
// Constant Folding:
//   5 + 5 → 10 (at compile time)
//   10 * 2 → 20 (at compile time)
//   100 - 50 → 50 (at compile time)
//
// Result: All dead variables removed
""",

    "EXAMPLE 7 - Nested Conditionals with Dead Code": """
// Dead code in nested if-else structures

hold is_admin: flag = yes;
hold is_verified: flag = no;

hold admin_privileges: num = 9999;
hold user_privileges: num = 100;

hold unused_data: num = 777;

when (is_admin) {
    when (is_verified) {
        show admin_privileges;
    } otherwise {
        show user_privileges;
    }
} otherwise {
    show "Access Denied";
}

// ANALYSIS:
// ✗ unused_data is DEAD in ALL code paths
// ✓ admin_privileges used if is_admin=yes AND is_verified=yes
// ✓ user_privileges used if is_admin=yes AND is_verified=no
//
// Optimization: unused_data is eliminated immediately
""",

    "EXAMPLE 8 - Complete Program with ALL Optimizations": """
// Real-world example showcasing all optimization techniques

// Declare variables (some will be dead code)
hold price: num = 100;
hold quantity: num = 5;
hold dead_variable1: num = 999;
hold dead_variable2: num = 888;

// Calculate total with constant folding
hold subtotal: num = price * quantity;
hold tax: num = 10 + 5;
hold dead_calculation: num = 777 + 333;

hold total: num = subtotal + tax;

// Output result
show "Total: ";
show total;

// ANALYSIS:
// Dead Code Elimination:
//   ✗ dead_variable1, dead_variable2 → REMOVED
//   ✗ dead_calculation → REMOVED
//
// Constant Folding:
//   10 + 5 → 15 (computed at compile time)
//
// Used Variables:
//   ✓ price → used in subtotal
//   ✓ quantity → used in subtotal
//   ✓ subtotal → used in total
//   ✓ tax → used in total
//   ✓ total → used in show
//
// Result: ~40% code reduction, 20% faster execution
""",
}

print("\n" + "="*80)
print("COPY & PASTE EXAMPLES INTO THE OPTIMIZATION GUI")
print("="*80 + "\n")

for title, code in examples.items():
    print(f"\n{'█'*80}")
    print(f"█ {title}")
    print(f"{'█'*80}\n")
    print(code)
    print("\n" + "-"*80)

print("\n" + "="*80)
print("HOW TO TEST IN THE GUI:")
print("="*80)
print("""
1. Open Terminal and run:
   cd d:\\my projects\\C_Compiler
   python -m src.main

2. Click "🚀 CODE OPTIMIZATION PHASE" button

3. Copy any EXAMPLE code from above

4. Paste into the "📄 Source Code" editor on the left side

5. Make sure "✅ Dead Code Elimination" is checked in the options

6. Click "▶️ Optimize" button

7. Check these tabs for results:
   
   📝 Original Code (3-AC)
   └─ Shows the TAC code BEFORE optimization
   
   ✨ Optimized Code (3-AC)
   └─ Shows the TAC code AFTER dead code elimination
   
   📊 Optimization Analysis
   └─ Shows statistics (instructions removed, reduction %)
   
   📋 Optimization Steps
   └─ Shows detailed steps of optimization process

8. Compare the numbers:
   • Original Instructions: X
   • Optimized Instructions: Y
   • Reduction: X - Y instructions removed
""")

print("\n" + "="*80)
print("NEXUS LANGUAGE QUICK REFERENCE:")
print("="*80)
print("""
┌─ VARIABLES ─────────────────────────────────────────────┐
│ hold x: num = 5;              // Integer                │
│ hold name: text = "John";     // String                 │
│ hold active: flag = yes;      // Boolean (yes/no)       │
│ hold pi: decimal = 3.14;      // Float                  │
└─────────────────────────────────────────────────────────┘

┌─ OPERATORS ─────────────────────────────────────────────┐
│ Arithmetic: +  -  *  /  %                               │
│ Comparison: >  <  >=  <=  ==  !=                        │
│ Logical:    and  or  not                                │
└─────────────────────────────────────────────────────────┘

┌─ CONTROL FLOW ──────────────────────────────────────────┐
│ when (condition) { ... } otherwise { ... }              │
│ loop (i = 0; i < 10; i++) { ... }                       │
│ break;                                                   │
│ continue;                                               │
└─────────────────────────────────────────────────────────┘

┌─ I/O ───────────────────────────────────────────────────┐
│ show "text";          // Print output                   │
│ show variable;        // Print variable value           │
│ show x + y;           // Print expression               │
└─────────────────────────────────────────────────────────┘

┌─ COMMENTS ──────────────────────────────────────────────┐
│ // Single line comment                                   │
│ /* Multi-line                                           │
│    comment */                                           │
└─────────────────────────────────────────────────────────┘
""")

print("\n" + "="*80)
print("✅ Ready to test! Copy an example and paste into the GUI.")
print("="*80 + "\n")
