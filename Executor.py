class Executor:
    def __init__(self, registers, memory):
        self.registers = registers
        self.memory = memory

    def execute_instruction(self, instruction, is_arm):
        opcode, operands = instruction
        if not opcode or not operands:
            return False

        if opcode == "MOV":
            if len(operands) == 2:  # MOV Rd, Rs or MOV Rd, #imm
                self.registers.set_register_value(operands[0], self.registers.get_register_value(operands[1]))
            return True
        elif opcode == "ADD":
            if len(operands) == 3:  # ADD Rd, Rn, Rm
                rn_val = int(self.registers.get_register_value(operands[1]), 2)
                rm_val = int(self.registers.get_register_value(operands[2]), 2)
                result = bin(rn_val + rm_val)[2:].zfill(32)
                self.registers.set_register_value(operands[0], result)
            return True
        elif opcode == "SUB":
            if len(operands) == 3:  # SUB Rd, Rn, Rm
                rn_val = int(self.registers.get_register_value(operands[1]), 2)
                rm_val = int(self.registers.get_register_value(operands[2]), 2)
                result = bin(rn_val - rm_val)[2:].zfill(32)
                self.registers.set_register_value(operands[0], result)
            return True
        elif opcode == "MUL":
            if len(operands) == 3:  # MUL Rd, Rn, Rm
                rn_val = int(self.registers.get_register_value(operands[1]), 2)
                rm_val = int(self.registers.get_register_value(operands[2]), 2)
                result = bin(rn_val * rm_val)[2:].zfill(32)
                self.registers.set_register_value(operands[0], result)
            return True
        elif opcode == "LDR":
            if len(operands) == 2:  # LDR Rd, [Rn]
                addr = int(self.registers.get_register_value(operands[1]), 2)
                value = self.memory.load_mem_cell(hex(addr))
                if value:
                    self.registers.set_register_value(operands[0], value)
            return True
        elif opcode == "STR":
            if len(operands) == 2:  # STR Rd, [Rn]
                addr = int(self.registers.get_register_value(operands[1]), 2)
                value = self.registers.get_register_value(operands[0])
                self.memory.edit_mem_cell(hex(addr), value)
            return True
        elif opcode == "CMP":
            if len(operands) == 2:  # CMP Rn, Rm
                rn_val = int(self.registers.get_register_value(operands[0]), 2)
                rm_val = int(self.registers.get_register_value(operands[1]), 2)
                self.registers.set_flag("Z", 1 if rn_val == rm_val else 0)
                self.registers.set_flag("N", 1 if rn_val < rm_val else 0)
            return True
        elif opcode == "B":
            if len(operands) == 1:  # B offset
                offset = int(operands[0], 16) if operands[0].startswith("0x") else int(operands[0])
                current_pc = int(self.registers.get_register_value("pc"), 16)
                new_pc = hex(current_pc + offset)
                self.registers.set_register_value("pc", new_pc)
            return True
        elif opcode == "BEQ":
            if len(operands) == 1 and self.registers.get_flag("Z") == 1:  # Branch if equal
                offset = int(operands[0], 16) if operands[0].startswith("0x") else int(operands[0])
                current_pc = int(self.registers.get_register_value("pc"), 16)
                new_pc = hex(current_pc + offset)
                self.registers.set_register_value("pc", new_pc)
            return True
        elif opcode == "BNE":
            if len(operands) == 1 and self.registers.get_flag("Z") == 0:  # Branch if not equal
                offset = int(operands[0], 16) if operands[0].startswith("0x") else int(operands[0])
                current_pc = int(self.registers.get_register_value("pc"), 16)
                new_pc = hex(current_pc + offset)
                self.registers.set_register_value("pc", new_pc)
            return True
        elif opcode == "BGT":
            if len(operands) == 1 and self.registers.get_flag("N") == 0:  # Branch if greater than
                offset = int(operands[0], 16) if operands[0].startswith("0x") else int(operands[0])
                current_pc = int(self.registers.get_register_value("pc"), 16)
                new_pc = hex(current_pc + offset)
                self.registers.set_register_value("pc", new_pc)
            return True
        elif opcode == "AND":
            if len(operands) == 3:  # AND Rd, Rn, Rm
                rn_val = int(self.registers.get_register_value(operands[1]), 2)
                rm_val = int(self.registers.get_register_value(operands[2]), 2)
                result = bin(rn_val & rm_val)[2:].zfill(32)
                self.registers.set_register_value(operands[0], result)
            return True
        elif opcode == "ORR":
            if len(operands) == 3:  # ORR Rd, Rn, Rm
                rn_val = int(self.registers.get_register_value(operands[1]), 2)
                rm_val = int(self.registers.get_register_value(operands[2]), 2)
                result = bin(rn_val | rm_val)[2:].zfill(32)
                self.registers.set_register_value(operands[0], result)
            return True
        elif opcode == "EOR":
            if len(operands) == 3:  # EOR Rd, Rn, Rm
                rn_val = int(self.registers.get_register_value(operands[1]), 2)
                rm_val = int(self.registers.get_register_value(operands[2]), 2)
                result = bin(rn_val ^ rm_val)[2:].zfill(32)
                self.registers.set_register_value(operands[0], result)
            return True
        elif opcode == "LSL":
            if len(operands) == 3:  # LSL Rd, Rn, #shift
                rn_val = int(self.registers.get_register_value(operands[1]), 2)
                shift = int(operands[2])  # Immediate shift value
                result = bin(rn_val << shift)[2:].zfill(32)
                self.registers.set_register_value(operands[0], result)
            return True
        return False

    def update_pc(self, increment):
        # Update Program Counter based on instruction size (4 for ARM, 2 for Thumb)
        current_pc = int(self.registers.get_register_value("pc"), 16)
        new_pc = hex(current_pc + increment)
        self.registers.set_register_value("pc", new_pc)