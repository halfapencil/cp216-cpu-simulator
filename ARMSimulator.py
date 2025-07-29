import sys
from CacheSim import CacheSim

class ARMSimulator:
    def __init__(self, blocksize=8, unified_size=32):
        self.registers = [0] * 16  # R0-R15, R15 is PC
        self.memory = [0] * 1024
        self.mode = 0  # 0 = ARM, 1 = Thumb
        self.flags = {'N': 0, 'Z': 0, 'C': 0, 'V': 0}
        self.instr_sizes = []
        self.modified_memory = set()
        self.cache = CacheSim(blocksize, unified_size)
        self.cache_enabled = True

    def load_binary(self, filename):
        instructions = []
        self.instr_sizes = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip().replace(' ', '')
                if not line or line.startswith('#'):
                    continue
                if not all(c in '01' for c in line):
                    continue
                if len(line) not in (16, 32):
                    continue
                try:
                    instr = int(line, 2)
                    instructions.append(instr)
                    self.instr_sizes.append(len(line))
                except ValueError:
                    continue
        return instructions

    def decode_arm(self, instr):
        cond = (instr >> 28) & 0xF
        opcode = (instr >> 21) & 0xF
        s_bit = (instr >> 20) & 0x1
        i_bit = (instr >> 25) & 0x1  # Immediate flag

        rd = (instr >> 12) & 0xF
        rn = (instr >> 16) & 0xF
        rm = instr & 0xF
        imm = instr & 0xFFF
        imm8 = instr & 0xFF
        offset = (instr & 0xFFFFFF) << 2

        # Data processing instructions
        if (instr >> 26) & 0b11 == 0b00:
            if opcode == 0x0:  # AND
                return f"AND R{rd}, R{rn}, #{imm}" if i_bit else f"AND R{rd}, R{rn}, R{rm}"
            elif opcode == 0x1:  # EOR
                return f"EOR R{rd}, R{rn}, #{imm}" if i_bit else f"EOR R{rd}, R{rn}, R{rm}"
            elif opcode == 0x2:  # SUB
                return f"SUB R{rd}, R{rn}, #{imm}" if i_bit else f"SUB R{rd}, R{rn}, R{rm}"
            elif opcode == 0x4:  # ADD
                return f"ADD R{rd}, R{rn}, #{imm}" if i_bit else f"ADD R{rd}, R{rn}, R{rm}"
            elif opcode == 0xA:  # CMP
                return f"CMP R{rn}, #{imm}" if i_bit else f"CMP R{rn}, R{rm}"
            elif opcode == 0xC:  # ORR
                return f"ORR R{rd}, R{rn}, #{imm}" if i_bit else f"ORR R{rd}, R{rn}, R{rm}"
            elif opcode == 0xD:  # MOV
                return f"MOV R{rd}, #{imm}" if i_bit else f"MOV R{rd}, R{rm}"

        # Load/Store instructions
        elif (instr >> 26) & 0b11 == 0b01:
            if (instr >> 20) & 0x1:  # LDR
                return f"LDR R{rd}, [R{rn}, #{imm8}]"
            else:  # STR
                return f"STR R{rd}, [R{rn}, #{imm8}]"

        # Branch
        elif (instr >> 25) & 0x7 == 0b101:
            if offset & 0x2000000:
                offset -= 0x4000000
            return f"B {offset}"

        # Branch and exchange
        elif (instr & 0x0FFFFFF0) == 0x012FFF10:
            rm = instr & 0xF
            return f"BX R{rm}"

        return "UNKNOWN"


    def decode_thumb(self, instr):
        opcode = (instr >> 10) & 0x3F
        rd = instr & 0x7
        rn = (instr >> 3) & 0x7
        rm = (instr >> 6) & 0x7
        imm = instr & 0xFF
        shift = (instr >> 6) & 0x1F
        if (instr >> 13) == 0:
            if (instr >> 11) & 0x3 == 0: return f"LSL R{rd}, R{rn}, #{shift}"
            elif (instr >> 11) & 0x3 == 0x1:
                if (instr >> 9) & 0x1: return f"SUB R{rd}, R{rn}, R{rm}"
                else: return f"ADD R{rd}, R{rn}, R{rm}"
            elif (instr >> 11) & 0x3 == 0x3: return f"MOV R{rd}, #{imm}"
        elif (instr >> 11) == 0x1D: return f"BX R{rm}"
        return "UNKNOWN"

    def execute_arm(self, instr):
        opcode = (instr >> 21) & 0xF
        rd = (instr >> 12) & 0xF
        rn = (instr >> 16) & 0xF
        rm = instr & 0xF
        imm = instr & 0xFFF
        imm8 = instr & 0xFF
        offset = (instr & 0xFFFFFF) << 2
        pc = self.registers[15]

        if (instr >> 25) & 0x7 == 0:
            if opcode == 0x0: self.registers[rd] = self.registers[rn] & self.registers[rm]
            elif opcode == 0x1: self.registers[rd] = self.registers[rn] ^ self.registers[rm]
            elif opcode == 0x2: self.registers[rd] = self.registers[rn] - self.registers[rm]
            elif opcode == 0x4: self.registers[rd] = self.registers[rn] + self.registers[rm]
            elif opcode == 0xA: self.update_flags(self.registers[rn] - self.registers[rm]); return
            elif opcode == 0xC: self.registers[rd] = self.registers[rn] | self.registers[rm]
            self.update_flags(self.registers[rd])

        elif (instr >> 25) & 0x7 == 0x1:
            addr = self.registers[rn] + imm8
            idx = addr // 4
            if (instr >> 20) & 0x1:  # LDR
                if self.cache_enabled: self.cache.access_data(pc, False)
                self.registers[rd] = self.memory[idx]
            else:  # STR
                if self.cache_enabled: self.cache.access_data(pc, True)
                self.memory[idx] = self.registers[rd]
                self.modified_memory.add(idx)

        elif (instr >> 25) & 0x7 == 0x5:
            if offset & 0x2000000: offset -= 0x4000000
            self.registers[15] += offset + 8

        elif (instr & 0x0FFFFFF0) == 0x012FFF10:
            self.registers[15] = self.registers[rm] & 0xFFFFFFFE
            self.mode = 1 if self.registers[rm] & 0x1 else 0

    def execute_thumb(self, instr):
        rd = instr & 0x7
        rn = (instr >> 3) & 0x7
        rm = (instr >> 6) & 0x7
        imm = instr & 0xFF
        shift = (instr >> 6) & 0x1F
        if (instr >> 13) == 0:
            if (instr >> 11) & 0x3 == 0: self.registers[rd] = self.registers[rn] << shift
            elif (instr >> 11) & 0x3 == 0x1:
                if (instr >> 9) & 0x1: self.registers[rd] = self.registers[rn] - self.registers[rm]
                else: self.registers[rd] = self.registers[rn] + self.registers[rm]
            elif (instr >> 11) & 0x3 == 0x3: self.registers[rd] = imm
            self.update_flags(self.registers[rd])
        elif (instr >> 11) == 0x1D:
            self.registers[15] = self.registers[rm] & 0xFFFFFFFE
            self.mode = 1 if self.registers[rm] & 0x1 else 0

    def update_flags(self, result):
        self.flags['Z'] = 1 if result == 0 else 0
        self.flags['N'] = 1 if result < 0 else 0

    def run(self, instructions):
        self.registers[15] = 0
        pc = self.registers[15]

        while pc < len(instructions) * 4:
            idx = pc // 4
            instr = instructions[idx]

            if self.cache_enabled:
                self.cache.access_instruction(pc)

            decoded = self.decode_thumb(instr) if self.mode == 1 else self.decode_arm(instr)
            print(f"PC: {pc:08x}, Decoded: {decoded}")

            if self.mode == 1:
                self.execute_thumb(instr)
                if decoded.startswith("BX"):
                    pc = self.registers[15]
                    continue
                pc += 2
            else:
                self.execute_arm(instr)
                pc += 4

            self.registers[15] = pc

            print(f"Registers: {self.registers}")
            print(f"Flags: {self.flags}\n")

if __name__ == "__main__":
    sim = ARMSimulator(blocksize=8, unified_size=32)
    sim.mode = 0
    sim.registers[1] = 41
    sim.registers[2] = 4
    instructions = sim.load_binary("test_mixed.txt")
    sim.run(instructions)
    sim.cache.output()