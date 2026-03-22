# Intermediate Code Generation Phase - NEXUS Compiler

## Overview

The Intermediate Code Generation phase is responsible for converting the Abstract Syntax Tree (AST) produced by the Semantic Analysis phase into intermediate code representation. This phase bridges high-level semantic analysis and low-level code generation.

## Features

### 1. Three-Address Code (3AC) Generation
- Converts AST nodes into simple three-address instructions
- Each instruction has at most three operands: `result = arg1 op arg2`
- Generates temporary variables for intermediate results
- Clear, linear representation of program logic

### 2. Instruction Types
The generator supports the following instruction types:

**Arithmetic Operations:**
- `ADD`: Addition
- `SUB`: Subtraction
- `MUL`: Multiplication
- `DIV`: Division
- `MOD`: Modulo

**Memory Operations:**
- `LOAD`: Load value from memory
- `STORE`: Store value to memory
- `LOAD_ARR`: Load from array
- `STORE_ARR`: Store to array

**Control Flow:**
- `JUMP`: Unconditional jump
- `JUMP_IF_TRUE`: Conditional jump (true)
- `JUMP_IF_FALSE`: Conditional jump (false)
- `LABEL`: Label definition
- `RETURN`: Function return

**Function Operations:**
- `FUNC_BEGIN`: Function start label
- `FUNC_END`: Function end label
- `CALL`: Function call
- `PARAM`: Parameter passing

**I/O Operations:**
- `READ`: Read input
- `WRITE`: Write output
- `ASSIGN`: Variable assignment

### 3. Control Flow Graph (CFG)
- Automatically builds CFG from generated 3AC
- Identifies basic blocks (straight-line code)
- Tracks successor and predecessor relationships
- Foundation for optimization and code generation

### 4. Symbol Table Tracking
- Maintains variable and function declarations
- Tracks variable initialization status
- Records type information for each symbol

### 5. Basic Optimizations
- Dead code elimination analysis
- Instruction reachability analysis
- Foundation for advanced optimizations in future phases

## Input/Output

### Input
The phase takes as input:
1. **Lexical Tokens** - From the Lexical Analysis phase
2. **Abstract Syntax Tree (AST)** - From the Syntax Analysis phase
3. **Semantic Information** - From the Semantic Analysis phase

### Output
The phase produces:
1. **Three-Address Code (TAC)** - Linear sequence of instructions
2. **Control Flow Graph (CFG)** - Block-based representation
3. **Symbol Table** - Variable and function definitions
4. **Error/Warning Report** - Issues found during generation

## Usage

### Standalone Usage
```python
from intermediate_code import IntermediateCodeGenerator
from syntax_analysis.ast_nodes import ASTNode

# Create generator
generator = IntermediateCodeGenerator(visual_mode=True)

# Set callbacks for visual updates
generator.set_visual_callback(lambda step: print(step['description']))
generator.set_error_callback(lambda err: print(f"Error: {err}"))

# Generate from AST
success, tac_code, errors = generator.generate(ast)

# Access results
if success:
    print(tac_code.get_instructions_text())
```

### With Full Pipeline
The IntermediateCodeGUI automatically handles all four phases:
1. Lexical Analysis
2. Syntax Analysis
3. Semantic Analysis
4. Intermediate Code Generation

## Data Structures

### TACInstruction
Represents a single three-address code instruction:
```python
@dataclass
class TACInstruction:
    instruction_type: InstructionType    # Type of instruction
    result: Optional[Operand]            # Target operand
    arg1: Optional[Operand]              # First argument
    arg2: Optional[Operand]              # Second argument
    label: Optional[str]                 # Optional label
    line_number: int                     # Position in code
```

### BasicBlock
Represents a sequence of instructions with single entry and exit:
```python
@dataclass
class BasicBlock:
    id: str                              # Block identifier (B0, B1, ...)
    instructions: List[TACInstruction]   # Instructions in block
    predecessors: List[BasicBlock]       # Incoming blocks
    successors: List[BasicBlock]         # Outgoing blocks
```

### ControlFlowGraph
Represents the overall program structure:
```python
class ControlFlowGraph:
    blocks: Dict[str, BasicBlock]        # All blocks
    entry_block: BasicBlock              # Program entry
    exit_block: BasicBlock               # Program exit
```

## Visual Interface

The IntermediateCodeGUI provides five tabs:

1. **3-Address Code Tab**
   - Shows the generated three-address code
   - Each instruction clearly labeled
   - Result, arg1, arg2 operands visible

2. **Control Flow Graph Tab**
   - Displays basic blocks
   - Shows successor relationships
   - Input/output per block

3. **Generation Steps Tab**
   - Step-by-step generation process
   - Instruction counts per step
   - Error/warning progression

4. **Statistics Tab**
   - Total instructions generated
   - Temporary variable count
   - Label count
   - Block count

5. **Errors & Warnings Tab**
   - All generation-time errors
   - Warnings and information
   - Quick issue identification

## Example

Given source code:
```nexus
num x;
num y;
num result;

result = x + y;
show result;
```

Generated TAC:
```
FUNC_BEGIN: main_begin
ASSIGN t=x a1=0
ASSIGN t=y a1=0
ADD t=t0 a1=x a2=y
ASSIGN t=result a1=t0
WRITE a1=result
FUNC_END: main_end
```

## Error Handling

The phase provides comprehensive error handling:
- **IntermediateCodeError** - Base exception class
- **UndefinedVariable** - Reference to undefined variable
- **InvalidInstruction** - Malformed or invalid instruction

All errors are collected and reported without halting generation when possible.

## Integration

The phase integrates seamlessly with:
- **Semantic Analysis** - Uses AST and semantic information
- **Optimization Phase** - Provides TAC for optimization
- **Code Generation** - TAC serves as input for final code generation

## Next Steps

The generated intermediate code is used for:
1. **Optimization Phase** - Apply optimization techniques on TAC
2. **Code Generation** - Convert TAC to target language (Python, C, Java, Assembly)
3. **Analysis** - Perform data flow and control flow analysis

## Status

✅ **COMPLETE** - Phase 4 is fully implemented with:
- Three-address code generation
- Control flow graph construction
- Symbol table management
- Basic optimization framework
- Comprehensive GUI visualization
