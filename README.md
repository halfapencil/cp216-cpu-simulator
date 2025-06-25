# ARMv7 and Thumb Simulator Design Document

## To run program
- Set the file path in the instructions variable, isnide the main function, to the location of the binary source file you want to use. Premade test files are available for quick use (called 'test', 'test_2', 'test_3').
- Run the ArmSimulator.py file with Python 3. 

## Product Requirements

### Read ARM/Thumb Machine Code File
- The simulator reads a binary file containing ARM (32-bit) or Thumb (16-bit) machine code instructions.
- ARM instructions are 4 bytes (32 bits) each, stored sequentially. The first 4 bytes represent the first instruction, the next 4 bytes the second, and so on.
- Thumb instructions are 2 bytes (16 bits) each, stored sequentially when in Thumb mode.
- The first instruction is loaded at memory address 0x00.
- The simulator detects ARM or Thumb mode based on a mode flag (e.g., set by a special instruction or file header) or by analyzing instruction length.

### Decode Machine Code
- Each machine code word (32-bit for ARM, 16-bit for Thumb) is decoded into its corresponding ARM or Thumb assembly instruction.
- The decoder identifies the instruction type (opcode) and extracts operands (e.g., registers, immediate values).

### Execute Instructions
- The simulator executes the decoded instruction, which may involve:
  - Modifying register values.
  - Updating memory locations (e.g., via LDR/STR).
  - Performing arithmetic or logical operations (e.g., ADD, SUB, AND).
  - Updating the program counter (e.g., via B instructions).
- Instructions are executed in a pipelined manner with fetch, decode, and execute stages.

### Supported Instructions
The simulator supports the following 15 instructions (covering both ARM and Thumb formats):
1. **MOV**: Move a value or register content to a register.
2. **ADD**: Add two register values or a register and immediate value.
3. **SUB**: Subtract a register or immediate value from a register.
4. **MUL**: Multiply two register values.
5. **LDR**: Load a value from memory into a register.
6. **STR**: Store a register value into memory.
7. **CMP**: Compare two registers or a register and immediate, setting condition flags.
8. **B**: Branch (unconditional) to a specified address.
9. **BEQ**: Branch if equal (conditional).
10. **BNE**: Branch if not equal (conditional).
11. **BGT**: Branch if greater than (conditional).
12. **AND**: Perform bitwise AND on two registers.
13. **ORR**: Perform bitwise OR on two registers.
14. **EOR**: Perform bitwise XOR on two registers.
15. **LSL**: Logical shift left on a register value.

## Simulator Architecture
The simulator is implemented in Python as a modular program with object-oriented design. Each component is represented as a class.

### Stage (Instruction Execution Cycle)
- Emulates the fetch-decode-execute pipeline.
- Coordinates the Program Counter, Memory, Decoder, Executor, and ALU.
- Pipeline stages:
  1. **Fetch**: Retrieves the instruction at the Program Counter (PC) address from Main Memory.
  2. **Decode**: Passes the instruction to the Decoder to translate into assembly format.
  3. **Execute**: Sends the decoded instruction to the Executor for processing.
- Loops until all instructions are executed or a halt condition is met.

### Program Memory Load
- Loads the binary file into Main Memory.
- ARM instructions (32-bit) are stored as 4-byte words; Thumb instructions (16-bit) as 2-byte words.
- The first instruction is stored at address 0x00.
- Each instruction occupies a unique memory cell.
- The simulator checks the mode (ARM or Thumb) to determine instruction size (4 or 2 bytes).

### Main Memory
- Represented as a 2D Python list with 1024 rows (arbitrary but sufficient for simulation).
- Matrix dimensions: 1024 x 2.
  - Column 1: Memory address (32-bit, starting at 0x00, incrementing by 4 for ARM or 2 for Thumb).
  - Column 2: Binary instruction or data value (32-bit for ARM, 16-bit for Thumb, or data).
- Functions:
  - `store_mem_cell(cell_value)`: Stores a binary value at the next available address; returns the address.
  - `edit_mem_cell(cell_addr, cell_value)`: Updates the value at the specified address.
  - `load_mem_cell(cell_addr)`: Returns the binary value at the given address.
  - `del_mem_cell(cell_addr)`: Clears the value at the specified address.

### Registers
- Emulates ARMv7's 16 registers (r0–r15) as a 2D Python list (16 x 2).
  - Column 1: Register identifier (e.g., r0, r1, ..., r15).
  - Column 2: 32-bit binary value.
- General-purpose registers: r0–r12.
- Special registers:
  - r13: Stack Pointer (SP).
  - r14: Link Register (LR).
  - r15: Program Counter (PC), initialized to 0x00, incremented by 4 (ARM) or 2 (Thumb) per cycle.
- Additional register:
  - **Instruction Register (IR)**: Stores the current instruction’s opcode and operands during decoding.
  - **Condition Flags**: Stores flags (e.g., Zero, Negative) for CMP and conditional branches.

### Decoder
- Converts binary instructions into assembly format.
- Process:
  1. Identifies ARM (32-bit) or Thumb (16-bit) based on mode and instruction length.
  2. Extracts the opcode using a lookup table (hash map) mapping binary patterns to instruction names (e.g., 1110... for MOV in ARM).
  3. Parses operands (registers, immediates, offsets) based on instruction format.
  4. Returns a tuple: (instruction_name, operands).
- Supports both ARM and Thumb instruction formats (refer to ARMv7 reference manual for bit fields).

### Executor
- Executes the decoded instruction by:
  - Performing arithmetic/logical operations via the ALU (e.g., ADD, SUB, AND).
  - Updating registers or memory (e.g., MOV, LDR, STR).
  - Modifying the PC for branches (B, BEQ, BNE, BGT).
  - Setting condition flags for CMP.
- Coordinates with Main Memory and Registers for data access.

### Arithmetic Logic Unit (ALU)
- Performs arithmetic and logical operations:
  - Arithmetic: ADD, SUB, MUL.
  - Logical: AND, ORR, EOR, LSL.
  - Comparison: CMP (sets condition flags).
- Inputs: Two operands (registers or immediate values).
- Outputs: Result stored in a register or condition flags updated.

### Control Unit
- Manages the pipeline by coordinating fetch, decode, and execute stages.
- Handles mode switching (ARM vs. Thumb) based on branch instructions or mode flags.
- Ensures proper sequencing and handles exceptions (e.g., invalid instructions).

## Implementation Details
- **Language**: Python 3.
- **Error Handling**:
  - Validates binary file format and instruction integrity.
  - Reports invalid opcodes or malformed instructions.
- **Instruction Formats**:
  - ARM: 32-bit, based on ARMv7 reference manual (e.g., opcode in bits 31–28, operands vary).
  - Thumb: 16-bit, based on Thumb instruction set (e.g., opcode in bits 15–10).
- **Sample Input File**:
