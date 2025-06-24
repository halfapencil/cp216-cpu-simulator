import sys

class ARMSimulator:
    def __init__(self):
        # Initialize 16 registers (R0-R15, R15 is PC)
        self.registers = [0] * 16
        # Initialize memory (1024 words, word-aligned)
        self.memory = [0] * 1024
        # Instruction mode: 0 for ARM, 1 for Thumb
        self.mode = 0
        # Condition flags
        self.flags = {'N': 0, 'Z': 0, 'C': 0, 'V': 0}
        # Track instruction sizes (32 or 16 bits)
        self.instr_sizes = []
        # Track modified memory indices
        self.modified_memory = set()

    def load_binary(self, filename):
        """Read text file with binary strings (0s and 1s) for ARM/Thumb instructions."""
        instructions = []
        self.instr_sizes = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()  # Remove whitespace
                if not line or line.startswith('#'):  # Skip empty or comment lines
                    continue
                # Remove spaces if present in binary string
                line = line.replace(' ', '')
                # Validate binary string
                if not all(c in '01' for c in line):
                    print(f"Invalid binary string: {line}")
                    continue
                # Check instruction length
                if len(line) not in (16, 32):
                    print(f"Invalid instruction length: {len(line)} bits in {line}")
                    continue
                # Convert binary string to integer
                try:
                    instr = int(line, 2)
                    instructions.append(instr)
                    self.instr_sizes.append(len(line))  # Store 32 or 16 bits
                except ValueError:
                    print(f"Error parsing binary string: {line}")
        return instructions

    def decode_arm(self, instr):
        """Decode a 32-bit ARM instruction."""
        cond = (instr >> 28) & 0xF
        opcode = (instr >> 21) & 0xF
        rd = (instr >> 12) & 0xF
        rn = (instr >> 16) & 0xF
        rm = instr & 0xF
        imm = instr & 0xFFF
        imm8 = instr & 0xFF
        offset = (instr & 0xFFFFFF) << 2  # Branch offset

        # Data Processing
        if (instr >> 25) & 0x7 == 0:  # Data Processing
            if opcode == 0x0:  # AND
                return f"AND R{rd}, R{rn}, R{rm}"
            elif opcode == 0x1:  # EOR
                return f"EOR R{rd}, R{rn}, R{rm}"
            elif opcode == 0x2:  # SUB
                return f"SUB R{rd}, R{rn}, R{rm}"
            elif opcode == 0x4:  # ADD
                return f"ADD R{rd}, R{rn}, R{rm}"
            elif opcode == 0xA:  # CMP
                return f"CMP R{rn}, R{rm}"
            elif opcode == 0xC:  # ORR
                return f"ORR R{rd}, R{rn}, R{rm}"
        elif (instr >> 25) & 0x7 == 0x1:  # Load/Store or MOV immediate
            if (instr >> 20) & 0x1:  # LDR
                return f"LDR R{rd}, [R{rn}, #{imm8}]"
            elif (instr >> 4) & 0xFF == 0xA:  # MOV immediate
                return f"MOV R{rd}, #{imm}"
            else:  # STR
                return f"STR R{rd}, [R{rn}, #{imm8}]"
        # Branch
        elif (instr >> 25) & 0x7 == 0x5:  # Branch
            # Sign-extend offset
            if offset & 0x2000000:
                offset -= 0x4000000
            return f"B {offset}"
        # BX
        elif (instr & 0x0FFFFFF0) == 0x012FFF10:  # BX pattern
            rm = instr & 0xF
            return f"BX R{rm}"
        return "UNKNOWN"

    def decode_thumb(self, instr):
        """Decode a 16-bit Thumb instruction."""
        opcode = (instr >> 10) & 0x3F
        rd = instr & 0x7
        rn = (instr >> 3) & 0x7
        rm = (instr >> 6) & 0x7
        imm = instr & 0xFF
        shift = (instr >> 6) & 0x1F

        # Thumb Instructions
        if (instr >> 13) == 0:  # Shift/ADD/SUB/MOV
            if (instr >> 11) & 0x3 == 0:  # LSL
                return f"LSL R{rd}, R{rn}, #{shift}"
            elif (instr >> 11) & 0x3 == 0x1:  # ADD/SUB
                if (instr >> 9) & 0x1:  # SUB
                    return f"SUB R{rd}, R{rn}, R{rm}"
                else:  # ADD
                    return f"ADD R{rd}, R{rn}, R{rm}"
            elif (instr >> 11) & 0x3 == 0x3:  # MOV
                return f"MOV R{rd}, #{imm}"
        elif (instr >> 11) == 0x1D:  # BX
            return f"BX R{rm}"
        return "UNKNOWN"

    def execute_arm(self, instr):
        """Execute a 32-bit ARM instruction."""
        opcode = (instr >> 21) & 0xF
        rd = (instr >> 12) & 0xF
        rn = (instr >> 16) & 0xF
        rm = instr & 0xF
        imm = instr & 0xFFF
        imm8 = instr & 0xFF
        offset = (instr & 0xFFFFFF) << 2

        # Data Processing
        if (instr >> 25) & 0x7 == 0:
            if opcode == 0x0:  # AND
                self.registers[rd] = self.registers[rn] & self.registers[rm]
                self.update_flags(self.registers[rd])
            elif opcode == 0x1:  # EOR
                self.registers[rd] = self.registers[rn] ^ self.registers[rm]
                self.update_flags(self.registers[rd])
            elif opcode == 0x2:  # SUB
                self.registers[rd] = self.registers[rn] - self.registers[rm]
                self.update_flags(self.registers[rd])
            elif opcode == 0x4:  # ADD
                self.registers[rd] = self.registers[rn] + self.registers[rm]
                self.update_flags(self.registers[rd])
            elif opcode == 0xA:  # CMP
                result = self.registers[rn] - self.registers[rm]
                self.update_flags(result)
            elif opcode == 0xC:  # ORR
                self.registers[rd] = self.registers[rn] | self.registers[rm]
                self.update_flags(self.registers[rd])
        # Load/Store or MOV immediate
        elif (instr >> 25) & 0x7 == 0x1:
            if (instr >> 4) & 0xFF == 0xA:  # MOV immediate
                self.registers[rd] = imm
                self.update_flags(self.registers[rd])
            else:
                addr = self.registers[rn] + imm8
                if addr >= 0 and addr < len(self.memory) * 4:
                    idx = addr // 4
                    if (instr >> 20) & 0x1:  # LDR
                        self.registers[rd] = self.memory[idx]
                    else:  # STR
                        self.memory[idx] = self.registers[rd]
                        self.modified_memory.add(idx)
        # Branch
        elif (instr >> 25) & 0x7 == 0x5:
            if offset & 0x2000000:
                offset -= 0x4000000
            self.registers[15] += offset + 8  # Account for pipeline
        # BX
        elif (instr & 0x0FFFFFF0) == 0x012FFF10:
            self.registers[15] = self.registers[rm] & 0xFFFFFFFE
            self.mode = 1 if self.registers[rm] & 0x1 else 0

    def execute_thumb(self, instr):
        """Execute a 16-bit Thumb instruction."""
        rd = instr & 0x7
        rn = (instr >> 3) & 0x7
        rm = (instr >> 6) & 0x7
        imm = instr & 0xFF
        shift = (instr >> 6) & 0x1F

        if (instr >> 13) == 0:
            if (instr >> 11) & 0x3 == 0:  # LSL
                self.registers[rd] = self.registers[rn] << shift
                self.update_flags(self.registers[rd])
            elif (instr >> 11) & 0x3 == 0x1:
                if (instr >> 9) & 0x1:  # SUB
                    self.registers[rd] = self.registers[rn] - self.registers[rm]
                    self.update_flags(self.registers[rd])
                else:  # ADD
                    self.registers[rd] = self.registers[rn] + self.registers[rm]
                    self.update_flags(self.registers[rd])
            elif (instr >> 11) & 0x3 == 0x3:  # MOV
                self.registers[rd] = imm
                self.update_flags(self.registers[rd])
        elif (instr >> 11) == 0x1D:  # BX
            self.registers[15] = self.registers[rm] & 0xFFFFFFFE
            self.mode = 1 if self.registers[rm] & 0x1 else 0

    def update_flags(self, result):
        """Update condition flags."""
        self.flags['Z'] = 1 if result == 0 else 0
        self.flags['N'] = 1 if result < 0 else 0
        self.flags['C'] = 0
        self.flags['V'] = 0

    def run(self, instructions):
        """Run the simulator."""
        self.registers[15] = 0  # Initialize PC
        while 0 <= self.registers[15] < sum((s // 8 for s in self.instr_sizes)):
            idx = 0
            byte_offset = 0
            # Find instruction index based on PC and instruction sizes
            for i, size in enumerate(self.instr_sizes):
                if byte_offset <= self.registers[15] < byte_offset + (size // 8):
                    idx = i
                    break
                byte_offset += size // 8
            if idx >= len(instructions):
                break
            instr = instructions[idx]
            # Format binary string
            binary = format(instr, '032b' if self.mode == 0 else '016b')
            # Add spaces every 4 bits for readability
            binary = ' '.join(binary[i:i+4] for i in range(0, len(binary), 4))
            instr_type = "ARM" if self.mode == 0 else "Thumb"
            decoded = self.decode_thumb(instr) if self.mode == 1 else self.decode_arm(instr)
            print(f"PC: {self.registers[15]:08x}, Binary: {binary}, Decoded: {decoded}")
            if self.mode == 1:
                self.execute_thumb(instr)
                if decoded.startswith("BX"):
                    continue  # BX may change PC/mode
                self.registers[15] += 2
            else:
                self.execute_arm(instr)
                self.registers[15] += 4
            print(f"Registers: {self.registers}")
            print(f"Flags: {self.flags}\n")

if __name__ == "__main__":
    sim = ARMSimulator()
    sim.mode = 0  # Start in ARM mode
    sim.registers[1] = 40 + 1  # Set R1 to Thumb start (40 bytes + 1 for Thumb mode)
    sim.registers[2] = 4       # Set R2 for STR/LDR (valid memory address)
    instructions = sim.load_binary("test") # <---- Put file adress of test file
    sim.run(instructions)