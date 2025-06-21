import tkinter as tk
from tkinter import ttk, filedialog

class SimulatorGUI:
    def __init__(self, stage):
        self.stage = stage
        self.root = tk.Tk()
        self.root.title("ARMv7/Thumb Simulator")
        self.setup_ui()

    def setup_ui(self):
        # Register Display
        reg_frame = ttk.LabelFrame(self.root, text="Register Contents")
        reg_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.reg_vars = [tk.StringVar() for _ in range(16)]
        for i in range(16):
            row = ttk.Frame(reg_frame)
            row.grid(row=i, column=0, sticky="ew")
            ttk.Label(row, text=f"r{i}").grid(row=0, column=0)
            reg_entry = ttk.Entry(row, textvariable=self.reg_vars[i], width=34, state="readonly")
            reg_entry.grid(row=0, column=1)
            if i == 15:  # PC
                reg_entry.config(bg="lightgreen")

        # Memory Display
        mem_frame = ttk.LabelFrame(self.root, text="Memory Contents")
        mem_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ttk.Label(mem_frame, text="Mem Addr").grid(row=0, column=0)
        ttk.Label(mem_frame, text="Value").grid(row=0, column=1)
        self.mem_vars = [[tk.StringVar() for _ in range(2)] for _ in range(10)]
        for i in range(10):
            for j in range(2):
                ttk.Entry(mem_frame, textvariable=self.mem_vars[i][j], width=17, state="readonly").grid(row=i+1, column=j)
        search_frame = ttk.LabelFrame(self.root, text="Search Memory Address")
        search_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=17).grid(row=0, column=0)
        ttk.Button(search_frame, text="Search", command=self.search_memory).grid(row=0, column=1)

        # Instruction Display
        inst_frame = ttk.LabelFrame(self.root, text="Current Instruction")
        inst_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.binary_var = tk.StringVar()
        self.decoded_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="ARM")
        ttk.Label(inst_frame, text="Binary Code:").grid(row=0, column=0)
        ttk.Entry(inst_frame, textvariable=self.binary_var, width=34, state="readonly").grid(row=0, column=1)
        ttk.Label(inst_frame, text="Decoded Instruction:").grid(row=1, column=0)
        ttk.Entry(inst_frame, textvariable=self.decoded_var, width=34, state="readonly").grid(row=1, column=1)
        ttk.Checkbutton(inst_frame, text="ARM", variable=self.mode_var, onvalue="ARM", offvalue="THUMB", state="disabled").grid(row=2, column=0)
        ttk.Checkbutton(inst_frame, text="THUMB", variable=self.mode_var, onvalue="THUMB", offvalue="ARM", state="disabled").grid(row=2, column=1)

        # File Input
        file_frame = ttk.LabelFrame(self.root, text="Upload Source File")
        file_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        ttk.Button(file_frame, text="Choose file", command=self.load_file).grid(row=0, column=0)

        # Control Buttons
        btn_frame = ttk.LabelFrame(self.root, text="Simulation Controls")
        btn_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        ttk.Button(btn_frame, text="Next Instruction", command=self.step).grid(row=0, column=0)
        ttk.Button(btn_frame, text="Continue to End of Program", command=self.run_to_end).grid(row=0, column=1)
        ttk.Button(btn_frame, text="Start Simulation", command=self.start).grid(row=0, column=2)

        self.update_display()

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Binary files", "*.bin")])
        if file_path:
            with open(file_path, "rb") as f:
                data = f.read()
                addr = 0x00
                for byte in data:
                    self.stage.control_unit.memory.store_mem_cell(bin(byte)[2:].zfill(8))
                    addr += 1

    def update_display(self):
        # Update registers
        for i in range(16):
            value = self.stage.control_unit.registers.get_register_value(f"r{i}")
            self.reg_vars[i].set(value if value else "0" * 32)
            if i == 15:  # Flash PC (simplified: update on each call)
                self.reg_vars[i].set(value if value else "0x00")
        # Update memory (show first 10 cells)
        for i in range(10):
            addr = hex(i * 4)
            value = self.stage.control_unit.memory.load_mem_cell(addr)
            self.mem_vars[i][0].set(addr)
            self.mem_vars[i][1].set(value if value else "0" * 32)
        # Update instruction (simplified: use current PC)
        pc = self.stage.control_unit.registers.get_register_value("pc")
        if pc:
            binary = self.stage.control_unit.memory.load_mem_cell(pc)
            if binary:
                decoded = self.stage.control_unit.decode(binary)
                if decoded:
                    self.binary_var.set(binary)
                    self.decoded_var.set(f"{decoded[0]} {', '.join(decoded[1])}")
                    self.mode_var.set("ARM" if self.stage.control_unit.is_arm_mode else "THUMB")
        self.root.after(100, self.update_display)  # Refresh every 100ms

    def search_memory(self):
        addr = self.search_var.get()
        if addr.startswith("0x"):
            value = self.stage.control_unit.memory.load_mem_cell(addr)
            for i in range(10):
                if self.mem_vars[i][0].get() == addr:
                    self.mem_vars[i][1].set(value if value else "0" * 32)
                    break

    def step(self):
        self.stage.step_instruction()
        self.update_display()

    def run_to_end(self):
        self.stage.run_to_completion()
        self.update_display()

    def start(self):
        self.stage.execute_cycle()
        self.update_display()

    def run(self):
        self.root.mainloop()