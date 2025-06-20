# ARMv7 and Thumb Simulator Design Document

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

### Display Results
- After each instruction execution, the simulator displays:
  - The current instruction (in assembly format) with an ARM or Thumb indicator.
  - Updated register values (r0–r15), with the modified register highlighted in red and the Program Counter (r15) with a light green background flashing on each new instruction.
  - Modified or accessed memory locations, highlighted in red, with a searchable address input to view specific cells.
- The simulator supports two modes:
  - Step-by-step: Displays each instruction, register, and memory state; user presses "Next Instruction" to proceed.
  - Full execution: Runs all instructions and displays the final state with "Continue to End of Program."

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

## GUI Design
The simulator features a graphical user interface (GUI) similar to CPULator, with the following components:

### User Interface 
![image](https://github.com/user-attachments/assets/5dbf1004-c9a7-4129-8a26-15717bfa59ce)


### Register Display
- **Headline**: "Register Contents"
- Displays all 16 registers (r0–r15) in a compact table (reduced height compared to memory table).
  - Columns: Register name (e.g., r0, r1, ..., r15), Value (32-bit binary or decimal).
  - The register being modified is highlighted in red.
  - The Program Counter (r15) has a light green background that flashes each time a new instruction is executed.

### Memory Display
- **Headline**: "Memory Contents"
- Displays the main memory in a table.
  - Columns: Mem Addr (hexadecimal), Value (binary or data).
  - The current memory cell being modified or accessed is highlighted in red.
- **Headline**: "Search Memory Address"
- Includes a text input box to enter a memory address (hexadecimal) and display the corresponding cell's value.

### Instruction Display
- **Headline**: "Current Instruction"
- Shows the current binary string (16/32-bit) being accessed, e.g., "0000 0000 0000 0000".
- Displays the decoded instruction, e.g., "mov r1, r2".
- Includes indicators:
  - A red square next to "ARM" when in ARM mode.
  - A red square next to "THUMB" when in Thumb mode (only one is active at a time).

### File Input Area
- **Headline**: "Upload Source File"
- Contains a "Choose file" button to select and upload a binary instruction file.
- Once uploaded, the file is loaded into memory to start the simulation.

### Control Buttons
- **Headline**: "Simulation Controls"
- Includes the following buttons:
  - "Next Instruction": Advances to the next instruction step-by-step.
  - "Continue to End of Program": Executes all remaining instructions and displays the final state.
  - "Start Simulation": Initiates the simulation after a file is uploaded.

## Implementation Details
- **Language**: Python 3 (with a GUI framework like Tkinter or PyQt).
- **Interface**: Graphical user interface as described above.
- **Error Handling**:
  - Validates binary file format and instruction integrity.
  - Reports invalid opcodes or malformed instructions.
- **Instruction Formats**:
  - ARM: 32-bit, based on ARMv7 reference manual (e.g., opcode in bits 31–28, operands vary).
  - Thumb: 16-bit, based on Thumb instruction set (e.g., opcode in bits 15–10).
- **Sample Input File**:
  ```
  11100010100000010010000000000011  ; ARM: ADD r1, r2, r3
  11100011101000000000000000000001  ; ARM: MOV r0, #1
  01000010000001010000              ; Thumb: ADD r5, r1
  0100001011000100                  ; Thumb: MOV r4, r3
  ```
