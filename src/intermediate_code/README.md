# Intermediate Code Generation Phase

## Description

The Intermediate Code Generation phase is the fourth step in the NEXUS Compiler pipeline. It takes the Abstract Syntax Tree (AST) produced by the Semantic Analysis phase and generates three-address code (3AC), which is a low-level intermediate representation suitable for optimization and code generation.

## What It Does

### 1. Three-Address Code Generation
Converts AST nodes into simple, three-operand instructions that are easy to optimize and translate:
- Arithmetic operations (ADD, SUB, MUL, DIV, MOD)
- Assignment operations
- Function calls and returns
- Control flow (jumps, labels)
- Variable and memory operations

### 2. Temporary Variable Management
- Automatically generates temporary variables for intermediate results
- Maintains a counter for unique temporary variable names (t0, t1, t2, ...)
- Each temporary is distinct and trackable

### 3. Label Generation
- Creates unique labels for control flow destinations
- Labels for function entry/exit points
- Labels for jump targets

### 4. Control Flow Graph Construction
- Builds a graph representation of basic blocks
- Identifies block boundaries (labels, jumps)
- Tracks successor and predecessor relationships
- Forms the foundation for optimization and code generation

### 5. Symbol Table Management
- Tracks all variable and function declarations
- Records type information for each symbol
- Maintains initialization status

## Input

The phase receives:
1. **Lexical Tokens** - From Lexical Analysis (used for reference)
2. **Abstract Syntax Tree** - From Syntax Analysis
3. **Semantic Information** - From Semantic Analysis

## Output

The phase produces:
1. **Three-Address Code (TAC)** - Linear sequence of intermediate instructions
2. **Control Flow Graph (CFG)** - Block-based program representation
3. **Symbol Table** - Variable and function definitions
4. **Generation Steps** - Step-by-step visualization of the process
5. **Statistics** - Metrics about generated code
6. **Error/Warning Report** - Issues found during generation

## Visual Interface Features

### 📝 3-Address Code Tab
Shows the complete generated three-address code with clear instruction formatting.

### 🌳 Control Flow Graph Tab
Displays basic blocks and their connections, showing how execution flows through the program.

### 📊 Generation Steps Tab
Shows the step-by-step process of code generation with statistics at each step.

### 📈 Statistics Tab
Provides metrics including:
- Total instructions generated
- Number of temporary variables
- Number of labels created
- Number of basic blocks
- Count of errors and warnings

### ⚠️ Errors & Warnings Tab
Lists all issues found during generation, helping identify problems in the input code.

## Key Classes

### IntermediateCodeGenerator
Main class that performs the code generation:
- `generate(ast)` - Main generation method
- `set_visual_callback()` - For GUI updates
- `set_error_callback()` - For error reporting

### TACCode
Represents the complete intermediate code:
- `add_instruction()` - Adds TAC instruction
- `generate_temp()` - Creates temporary variable
- `generate_label()` - Creates label
- `get_instructions_text()` - Formatted code output

### TACInstruction
Single three-address code instruction:
- `instruction_type` - Type of operation
- `result` - Target operand
- `arg1`, `arg2` - Source operands
- `label` - Optional label
- `line_number` - Position in code

### ControlFlowGraph
Program structure representation:
- `create_block()` - Create new basic block
- `build_from_tac()` - Build graph from TAC
- `get_blocks_list()` - List all blocks

## Example

**Input Code:**
```nexus
num x;
num y;
num z;

z = x + y;
show z;
```

**Generated Three-Address Code:**
```
FUNC_BEGIN: main_begin
ASSIGN t=x a1=0
ASSIGN t=y a1=0
ASSIGN t=z a1=0
ADD t=t0 a1=x a2=y
ASSIGN t=z a1=t0
WRITE a1=z
FUNC_END: main_end
```

**Basic Blocks:**
```
Block: B0
────────────────────────────────
FUNC_BEGIN: main_begin
ASSIGN t=x a1=0
ASSIGN t=y a1=0
ASSIGN t=z a1=0
ADD t=t0 a1=x a2=y
Successors: []
```

## Integration with Other Phases

### ← Input from Semantic Analysis
Uses the AST produced by Semantic Analysis phase to ensure type correctness and symbol validity.

### Output to Optimization Phase →
The generated TAC serves as input to the Optimization phase for:
- Dead code elimination
- Common subexpression elimination
- Constant folding
- Loop optimization

### Output to Code Generation Phase →
The intermediate code and CFG are used by Code Generation to produce:
- Python code
- C code
- Java code
- Assembly code

## Performance Considerations

- **Linear Generation:** Code generation is O(n) where n is number of AST nodes
- **Efficient Temporaries:** Temporary variables are managed with simple counter
- **Basic Block Formation:** CFG construction is O(n) 
- **Storage:** Memory efficient representation suitable for large programs

## Error Handling

The phase gracefully handles errors:
- Undefined variable references
- Invalid instruction types
- Missing operands
- Type mismatches (when semantic info available)

All errors are collected and reported without interrupting generation.

## Next Steps

After Intermediate Code Generation:
1. **Optimization Phase** - Improve generated code
2. **Code Generation Phase** - Produce target language code
3. **Runtime/Testing** - Execute and validate generated code

## Status

✅ **FULLY IMPLEMENTED** - Phase 4 is complete with all features
