import MainMemory
import Registers
import Decoder
import Executor
import ArithmeticLogicUnit
import ControlUnit
import Stage
import SimulatorGUI

class SimulatorConfig:
    def __init__(self):
        self.memory = MainMemory()
        self.registers = Registers()
        self.decoder = Decoder()
        self.alu = ArithmeticLogicUnit()
        self.executor = Executor(self.registers, self.memory)
        self.control_unit = ControlUnit(self.memory, self.registers, self.decoder, self.executor, self.alu)
        self.stage = Stage(self.control_unit)
        self.gui = SimulatorGUI(self.stage)

    def parse_binary_file(self, file_path):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                addr = 0x00
                i = 0
                while i < len(data):
                    # Determine chunk size based on current mode (default to ARM initially)
                    chunk_size = 4 if self.control_unit.is_arm_mode else 2
                    if i + chunk_size <= len(data):
                        chunk = data[i:i + chunk_size]
                        # Convert chunk to binary string
                        binary = ''.join(format(byte, '08b') for byte in chunk)
                        # Truncate or pad to ensure correct length
                        binary = binary[:32] if self.control_unit.is_arm_mode else binary[:16]
                        if self.control_unit.is_arm_mode and len(binary) < 32:
                            binary = binary.zfill(32)
                        elif not self.control_unit.is_arm_mode and len(binary) < 16:
                            binary = binary.zfill(16)
                        # Store the instruction
                        self.memory.store_mem_cell(binary)
                        addr += 1
                        i += chunk_size
                    else:
                        break
            return True
        except Exception as e:
            print(f"Error parsing file: {e}")
            return False

    def load_binary_file(self, file_path):
        # Use parse_binary_file to load and separate instructions
        if self.parse_binary_file(file_path):
            # Reset PC to start of memory
            self.registers.set_register_value("pc", "0x00")
            return True
        return False

    def run(self):
        self.gui.run()

if __name__ == "__main__":
    sim = SimulatorConfig()
    sim.load_binary_file("sample.bin")  # Example file path
    sim.run()