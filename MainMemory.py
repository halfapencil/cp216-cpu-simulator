class MainMemory:
    def __init__(self):
        # Initialize a 2D list with 1024 rows and 2 columns (address, value)
        self.memory = [[None, None] for _ in range(1024)] 
        self.next_free_address = 0x00

    # Store a binary value at the next available address
    def store_mem_cell(self, cell_value):
        if self.next_free_address < 1024: # Check if memory full
            # Set the addr and its corresponding cell value, in a vacant memory cell
            self.memory[self.next_free_address] = [hex(self.next_free_address), cell_value] 

            # Retrive addr to return
            address = self.next_free_address 

            # Increment by 1 row (4 bytes for ARM, 2 for Thumb handled by caller)
            self.next_free_address += 1  

            return hex(address) # Return addr of cell value
        return None  # Return None if memory is full

    # Edit the value at the specified address
    def edit_mem_cell(self, cell_addr, cell_value):
        try:
            addr_index = int(cell_addr, 16) # Convert the hex address into the integer index compatible with the 2d list

            # Ensure addr is valid and the cell addr actually exists in the memory space 
            if 0 <= addr_index < 1024 and self.memory[addr_index][0] == cell_addr:
                self.memory[addr_index][1] = cell_value # Replace the cell value
                return True # Return true if cell edit was succesful

            return False # Return false if cell addr never existed or was misaligned
        
        except (ValueError, IndexError):  # Error handling for any any other misc errors
            return False

    # Load and return the value at the specified address
    def load_mem_cell(self, cell_addr):
        try:
            # Convert hex addr into index for 2d list
            addr_index = int(cell_addr, 16)

            # Ensure addr is valid and the cell addr actually exists in the memory space
            if 0 <= addr_index < 1024 and self.memory[addr_index][0] == cell_addr:
                return self.memory[addr_index][1] # return cell addr contents

            return None # If not addr not valid, return None
        except (ValueError, IndexError):
            return None

    def del_mem_cell(self, cell_addr):
        # Delete the value at the specified address
        try:
            addr_index = int(cell_addr, 16)
            if 0 <= addr_index < 1024 and self.memory[addr_index][0] == cell_addr:
                self.memory[addr_index][1] = None # Set addr cell value to none
                self.next_free_address = cell_addr # let program know about recently freed up cell for use. 
                return True # If del succesful return true
            return False
        except (ValueError, IndexError):
            return False