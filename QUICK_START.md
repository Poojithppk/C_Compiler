# 🚀 QUICK START GUIDE - Semantic Analysis Phase

## 30-Second Setup

Your semantic analyzer is ready to use! No additional setup needed.

---

## 🎯 Test It Now

### Option 1: Quick Single Phase Test
```bash
1. Run: python src/main.py
2. Click: 🎯 SEMANTIC ANALYSIS button
3. Click: 📋 Load Sample (or paste code)
4. Click: 🔍 Analyze
5. View: Results in multiple tabs
```

### Option 2: Full Workflow Test
```bash
1. Run: python src/main.py
2. Click: 🔄 LEXICAL → SYNTAX → SEMANTIC
3. Follow prompts through all 3 phases
4. See complete compilation in action
```

---

## 📝 What You'll See

### When Analysis Completes:
```
✅ 📋 Symbol Table Tab
   - All declared symbols listed
   - Organized by scope
   - Shows type information

✅ 🔍 Scope Hierarchy Tab
   - Nested scope structure
   - Global → Function → Block
   - Symbol counts per scope

✅ 🔷 Type Analysis Tab
   - Symbols grouped by type
   - INT, FLOAT, STRING, BOOL assignments
   - Array and pointer information

✅ ⚠️ Errors & Warnings Tab
   - Any semantic errors found
   - Variable usage issues
   - Type mismatches

✅ 📊 Analysis Steps Tab
   - Real-time trace of analysis
   - Symbol counting progress
   - Error detection timeline
```

---

## 🧪 Sample Code Included

The GUI has built-in test code:

```nexus
function int main() {
    int x = 10
    float y = 3.14
    string message = "Hello"
    
    int result = add(x, 5)
    print(result)
    
    return 0
}

function int add(int a, int b) {
    int sum = a + b
    return sum
}

function void display(string text) {
    print(text)
}
```

**Expected Results**:
- ✅ 6 symbols total
- ✅ 4 scopes (global, main, add, display)
- ✅ No errors
- ✅ All symbols valid

---

## 📂 What Was Created

```
New Folder: src/semantic_analysis/
├── semantic_symbols.py     (Symbol table system)
├── semantic.py             (Core analyzer)
├── semantic_gui.py         (Visual interface)
├── __init__.py             (Module exports)
├── README.md               (Documentation)
└── PHASE_3_COMPLETE.md     (Status)

Updated: src/main.py
Added: SEMANTIC_ANALYZER_COMPLETE.md
Added: IMPLEMENTATION_GUIDE.md
Added: QUICK_START.md (this file)
```

---

## 🎮 GUI Controls

### Main Buttons
- **🔍 Analyze** - Start semantic analysis
- **⏮️ Reset** - Clear all results

### Settings
- **Animation Speed** - Slow/Medium/Fast/Instant
- **Auto Mode** - Automatic or manual stepping

### File Operations
- **📁 Load File** - Open code from file
- **💾 Save File** - Save code to file
- **🔄 Clear** - Clear editor
- **📋 Load Sample** - Load test code

---

## 🔄 Workflow Options

### Sequential Mode (Best for Learning)
```
Main Dashboard
    ↓
Click: "🔄 LEXICAL → SYNTAX → SEMANTIC"
    ↓
Phase 1: Lexical Analysis
    Sees: Tokenization process
    Result: Tokens generated
    ↓
    Choose: Yes → Continue?
    ↓
Phase 2: Syntax Analysis
    Sees: Parsing process
    Result: AST generated
    ↓
    Choose: Yes → Continue?
    ↓
Phase 3: Semantic Analysis ← NEW!
    Sees: Symbol table building
    Result: Symbols validated
    Type checking complete
    ↓
Final Result: All 3 phases complete!
```

### Individual Phase Mode (Good for Testing)
```
Main Dashboard
    ↓
Click: "🎯 SEMANTIC ANALYSIS"
    ↓
Enter/Load Code
    ↓
Click: "🔍 Analyze"
    ↓
View: 6 Analysis Tabs
    ↓
Test Complete
```

---

## 🐛 Common Test Cases

### Test 1: Simple Variables
```nexus
int x = 5
float y = 3.14
string name = "Alice"
```
✅ Should see: 3 symbols in global scope

### Test 2: Function with Parameters
```nexus
function int add(int a, int b) {
    int result = a + b
    return result
}
```
✅ Should see: 1 function + 3 symbols (2 params + 1 local)

### Test 3: Multiple Scopes
```nexus
int global_var = 10

function void doSomething() {
    int local_var = 20
}
```
✅ Should see: 2 scopes with 2 symbols total

### Test 4: Error Case (Undefined Symbol)
```nexus
function int test() {
    int x = undefined_var
    return x
}
```
⚠️ Should see: Error "undefined_var" undefined

---

## 📊 Status Check

### Verify Installation
1. Check folder exists: `src/semantic_analysis/`
2. Check files:
   - `__init__.py` ✓
   - `semantic_symbols.py` ✓
   - `semantic.py` ✓
   - `semantic_gui.py` ✓
   - `README.md` ✓

3. Check main.py updated: Look for `SemanticAnalysisGUI` import ✓

4. Run: `python src/main.py` and see:
   - Dashboard loads ✓
   - Semantic button visible ✓
   - Sequential button updated ✓

---

## 🎯 What Semantic Analysis Does

**Phase 3 performs critical validation:**

1. **Symbol Table Building**
   - Tracks all variable declarations
   - Records function signatures
   - Manages scope nesting

2. **Type Checking**
   - Verifies type assignments
   - Checks function calls
   - Validates operations

3. **Scope Validation**
   - Ensures symbols defined before use
   - Detects undefined variables
   - Prevents redeclaration

4. **Error Detection**
   - Reports semantic errors
   - Generates warnings
   - Provides line numbers

5. **Visualization**
   - Shows symbol table contents
   - Displays scope hierarchy
   - Lists type information
   - Shows all errors

---

## 🔗 Integration with Other Phases

### How It Works Together
```
Phase 1: Lexical Analysis
├── Input: Raw source code
├── Output: Tokens
└── Passes to: Phase 2

Phase 2: Syntax Analysis
├── Input: Tokens from Phase 1
├── Output: AST (Abstract Syntax Tree)
└── Passes to: Phase 3

Phase 3: Semantic Analysis ← YOU ARE HERE
├── Input: AST from Phase 2
├── Output: Validated AST + Symbol Table
├── Checks: Type safety, scope validity
└── Next: Phase 4 (Intermediate Code)
```

---

## 💡 Tips & Tricks

### For Better Analysis
- Use clear variable names (helps error messages)
- Declare variables before use
- Check type matching in functions
- Use functions with type signatures

### For Debugging
- Use "Load Sample" to see working code
- Check each tab for different information
- Look at Analysis Steps for trace
- Use speed controls to slow down

### For Learning
- Read symbols as they're declared
- Watch scope entry/exit
- Track type assignments
- See error detection in action

---

## 📞 Where to Find Help

### Documentation Files
- **README.md** - Detailed phase info: `src/semantic_analysis/README.md`
- **Implementation Guide** - Integration details: `IMPLEMENTATION_GUIDE.md`
- **Completion Summary** - Full overview: `SEMANTIC_ANALYZER_COMPLETE.md`

### In Code
- Docstrings on all classes
- Comments on complex logic
- Type hints throughout

### Quick Reference
```python
# Import
from semantic_analysis import SemanticAnalyzer, SemanticAnalysisGUI

# Use analyzer
analyzer = SemanticAnalyzer()
success, errors, warnings = analyzer.analyze(ast)
symbol_table = analyzer.get_symbol_table()

# Launch GUI
import tkinter as tk
root = tk.Tk()
gui = SemanticAnalysisGUI(root)
root.mainloop()
```

---

## ✅ Verification Checklist

- [ ] Run `python src/main.py` successfully
- [ ] See semantic analysis button (✅ READY)
- [ ] Click semantic analysis button
- [ ] Load sample code
- [ ] Run analysis
- [ ] See symbol table populated
- [ ] View all 6 tabs
- [ ] No errors shown (valid sample)
- [ ] Try full workflow (3 phases)
- [ ] All working correctly!

---

## 🎉 You're All Set!

The semantic analysis phase is **ready to use** with:
- ✅ Professional GUI with 6 tabs
- ✅ Symbol table management
- ✅ Type checking
- ✅ Scope validation
- ✅ Error detection
- ✅ Full workflow integration

**Next**: Try it now with `python src/main.py`!

---

## 📈 Project Progress

```
Compiler Phases Completed:

Phase 1: ✅ LEXICAL ANALYSIS
Phase 2: ✅ SYNTAX ANALYSIS
Phase 3: ✅ SEMANTIC ANALYSIS ← JUST ADDED!
Phase 4: 🚧 Intermediate Code Generation (next)
Phase 5: 🚧 Optimization
Phase 6: 🚧 Code Generation

Overall Progress: 50% (3/6 phases complete)
```

---

## 🚀 Ready? Let's Go!

```bash
# Terminal command
python src/main.py

# Then click: 🎯 SEMANTIC ANALYSIS
# Then click: 🔍 Analyze
# Then check: All 6 tabs for results!
```

**Enjoy your new semantic analyzer! 🎊**
