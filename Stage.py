class Stage:
    def __init__(self, control_unit):
        self.control_unit = control_unit

    def execute_cycle(self):
        # Execute one complete cycle of the fetch-decode-execute pipeline
        return self.control_unit.run_cycle()

    def run_to_completion(self):
        # Run the pipeline until all instructions are executed or an error occurs
        while True:
            success = self.execute_cycle()
            if not success or int(self.control_unit.registers.get_register_value("pc"), 16) >= 1024 * 4:  # Arbitrary memory limit
                break
        return success

    def step_instruction(self):
        # Step through one instruction manually
        return self.execute_cycle()