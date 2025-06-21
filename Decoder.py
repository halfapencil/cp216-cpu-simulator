class Decoder:
    def __init__(self):
        # Lookup tables for ARM and Thumb opcodes (simplified for initial implementation)
        self.arm_opcodes = {
            "1110" + "00" + "010000" + "0" * 18: "MOV",  # Example ARM MOV pattern
            "1110" + "00" + "100000" + "0" * 18: "ADD",
            "1110" + "00" + "001000" + "0" * 18: "SUB",
            "1110" + "00" + "000000" + "0" * 18: "AND"
        }
        self.thumb_opcodes = {
            "010000" + "0" * 10: "MOV",  # Example Thumb MOV pattern
            "0001100" + "0" * 8: "ADD",
            "0001101" + "0" * 8: "SUB"
        }

    """
    Decodes a 16/32 bit binary string into a Arm/Thumb instruction
    Param:
    - binary_code: 16/32 bit string from source file
    - is_arm
    """
    def decode_instruction(self, binary_code, is_arm):
        # Decode 32-bit ARM or 16-bit Thumb instruction
        if is_arm:
            # Confirm valid binary string length
            if len(binary_code) != 32:
                return None
            
            # NOTE: string below is 26, but len of a string in self.arm_opcodes is 30?
            opcode_key = binary_code[:26]  # Simplified key for ARM (adjust based on actual bit fields)

            # Check if opcode from string matches stored opcodes
            if opcode_key in self.arm_opcodes:
                opcode = self.arm_opcodes[opcode_key]
                # Extract operands (simplified: assuming Rd, Rn, Rm or immediate)
                rd = int(binary_code[26:28], 2)  # Example: bits 26-27 for Rd
                rn = int(binary_code[28:30], 2)  # Example: bits 28-29 for Rn
                return (opcode, [f"r{rd}", f"r{rn}"])
        else:  # Thumb
            if len(binary_code) != 16:
                return None
            opcode_key = binary_code[:7]  # Simplified key for Thumb (adjust based on actual bit fields)
            if opcode_key in self.thumb_opcodes:
                opcode = self.thumb_opcodes[opcode_key]
                # Extract operands (simplified: assuming Rd, Rs)
                rd = int(binary_code[7:9], 2)  # Example: bits 7-8 for Rd
                rs = int(binary_code[9:11], 2)  # Example: bits 9-10 for Rs
                return (opcode, [f"r{rd}", f"r{rs}"])
        return None

    def identify_mode(self, binary_code):
        # Simple mode detection (to be refined with actual ARM/Thumb switch logic)
        if len(binary_code) == 32:
            return True  # ARM mode
        elif len(binary_code) == 16:
            return False  # Thumb mode
        return None