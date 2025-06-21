class ArithmeticLogicUnit:
    def __init__(self):
        pass  # No persistent state needed for ALU

    def add(self, operand1, operand2):
        # Perform addition of two 32-bit binary strings
        val1 = int(operand1, 2)
        val2 = int(operand2, 2)
        result = val1 + val2
        return bin(result & 0xFFFFFFFF)[2:].zfill(32)  # Mask to 32 bits

    def sub(self, operand1, operand2):
        # Perform subtraction of two 32-bit binary strings
        val1 = int(operand1, 2)
        val2 = int(operand2, 2)
        result = val1 - val2
        return bin(result & 0xFFFFFFFF)[2:].zfill(32)  # Mask to 32 bits

    def mul(self, operand1, operand2):
        # Perform multiplication of two 32-bit binary strings
        val1 = int(operand1, 2)
        val2 = int(operand2, 2)
        result = val1 * val2
        return bin(result & 0xFFFFFFFF)[2:].zfill(32)  # Mask to 32 bits

    def and_op(self, operand1, operand2):
        # Perform bitwise AND
        val1 = int(operand1, 2)
        val2 = int(operand2, 2)
        result = val1 & val2
        return bin(result)[2:].zfill(32)

    def orr(self, operand1, operand2):
        # Perform bitwise OR
        val1 = int(operand1, 2)
        val2 = int(operand2, 2)
        result = val1 | val2
        return bin(result)[2:].zfill(32)

    def eor(self, operand1, operand2):
        # Perform bitwise XOR
        val1 = int(operand1, 2)
        val2 = int(operand2, 2)
        result = val1 ^ val2
        return bin(result)[2:].zfill(32)

    def lsl(self, operand1, shift_amount):
        # Perform logical shift left
        val1 = int(operand1, 2)
        result = val1 << shift_amount
        return bin(result & 0xFFFFFFFF)[2:].zfill(32)  # Mask to 32 bits

    def compare(self, operand1, operand2):
        # Compare two values and set flags (returns flags dict)
        val1 = int(operand1, 2)
        val2 = int(operand2, 2)
        flags = {
            "Z": 1 if val1 == val2 else 0,  # Zero flag
            "N": 1 if val1 < val2 else 0    # Negative flag
        }
        return flags