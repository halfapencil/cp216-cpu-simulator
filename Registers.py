class Registers:
    def __init__(self):
        # Initialize 16 registers as a 2D list (16 x 2)
        self.register_bank = [[f"r{i}", "0" * 32] for i in range(16)]
        # Special register attributes
        self.sp = "0" * 32  # Stack Pointer (r13)
        self.lr = "0" * 32  # Link Register (r14)
        self.pc = "0x00"    # Program Counter (r15), initialized to 0x00
        self.ir = ["", ""]  # Instruction Register: [opcode, operands]
        self.flags = {"Z": 0, "N": 0}  # Condition flags: Zero, Negative

    def get_register_value(self, reg_name):
        # Retrieve value of a register by name (e.g., "r0", "sp", "pc")
        if reg_name in [f"r{i}" for i in range(13)]:
            index = int(reg_name[1:])
            return self.register_bank[index][1]
        elif reg_name == "sp":
            return self.sp
        elif reg_name == "lr":
            return self.lr
        elif reg_name == "pc":
            return self.pc
        return None

    def set_register_value(self, reg_name, value):
        # Set value of a register (32-bit binary string or hex for pc)
        if len(value) != 32 and reg_name != "pc":
            return False
        if reg_name in [f"r{i}" for i in range(13)]:
            index = int(reg_name[1:])
            self.register_bank[index][1] = value[:32]  # Ensure 32-bit
            return True
        elif reg_name == "sp":
            self.sp = value[:32]
            return True
        elif reg_name == "lr":
            self.lr = value[:32]
            return True
        elif reg_name == "pc":
            self.pc = value if value.startswith("0x") else f"0x{value}"
            return True
        return False

    def set_ir(self, opcode, operands):
        # Set Instruction Register with opcode and operands
        self.ir = [opcode, operands]

    def get_ir(self):
        # Retrieve Instruction Register contents
        return self.ir

    def set_flag(self, flag_name, value):
        # Set condition flag (Z or N)
        if flag_name in self.flags:
            self.flags[flag_name] = value
            return True
        return False

    def get_flag(self, flag_name):
        # Retrieve condition flag value
        return self.flags.get(flag_name, None)