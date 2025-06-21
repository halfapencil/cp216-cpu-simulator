class ControlUnit:
    def __init__(self, memory, registers, decoder, executor, alu):
        self.memory = memory
        self.registers = registers
        self.decoder = decoder
        self.executor = executor
        self.alu = alu
        self.is_arm_mode = True  # Default to ARM mode

    def fetch(self):
        # Fetch instruction from memory based on PC
        pc_value = self.registers.get_register_value("pc")
        if pc_value:
            pc_addr = int(pc_value, 16)
            binary_code = self.memory.load_mem_cell(hex(pc_addr))
            if binary_code:
                return binary_code
        return None

    def decode(self, binary_code):
        # Decode the fetched instruction
        is_arm = self.decoder.identify_mode(binary_code)
        if is_arm is not None:
            self.is_arm_mode = is_arm
            return self.decoder.decode_instruction(binary_code, is_arm)
        return None

    def execute(self, instruction):
        # Execute the decoded instruction
        if instruction:
            self.registers.set_ir(instruction[0], instruction[1])  # Set IR
            increment = 4 if self.is_arm_mode else 2  # Increment PC by 4 (ARM) or 2 (Thumb)
            success = self.executor.execute_instruction(instruction, self.is_arm_mode)
            if success and instruction[0] not in ["B", "BEQ", "BNE", "BGT"]:  # Skip PC update for branches
                self.executor.update_pc(increment)
            return success
        return False

    def run_cycle(self):
        # Run one cycle of the fetch-decode-execute pipeline
        instruction = self.fetch()
        if instruction:
            decoded = self.decode(instruction)
            if decoded:
                return self.execute(decoded)
        return False

    def switch_mode(self, new_mode):
        # Switch between ARM and Thumb modes
        if new_mode in [True, False]:
            self.is_arm_mode = new_mode
            return True
        return False