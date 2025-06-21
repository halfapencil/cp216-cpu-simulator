import MainMemory
import Registers
import Decoder
import Executor
import ArithmeticLogicUnit
import ControlUnit
import Stage
import SimulatorGUI

def setup_simulator():
    memory = MainMemory()
    registers = Registers.Registers()
    decoder = Decoder()
    alu = ArithmeticLogicUnit()
    executor = Executor(registers, memory)
    control_unit = ControlUnit(memory, registers, decoder, executor, alu)
    stage = Stage(control_unit)
    gui_app = SimulatorGUI(stage)
    return gui_app

def load_sample_data(memory):
    # Sample binary data (simplified 32-bit ARM instructions)
    sample_data = [
        "11100011101000000000000000000001",  # MOV r0, #1
        "11100010100000010010000000000000",  # ADD r1, r0, r0
        "11100000100100000001000000000000"   # SUB r2, r1, r0
    ]
    for data in sample_data:
        memory.store_mem_cell(data)

def run_tests(gui_app):
    print(f"Starting tests")
    # Test initial state
    assert gui_app.stage.control_unit.registers.get_register_value("r0") == "0" * 32, "Initial r0 value incorrect"
    # Simulate a few steps (manual simulation for testing)
    gui_app.step()
    gui_app.step()
    gui_app.step()
    final_r0 = gui_app.stage.control_unit.registers.get_register_value("r0")
    assert final_r0 == "00000000000000000000000000000001", "MOV instruction failed"
    print("Tests passed successfully!")

if __name__ == "__main__":
    gui_app = setup_simulator()
    load_sample_data(gui_app.stage.control_unit.memory)
    run_tests(gui_app)
    gui_app.run()