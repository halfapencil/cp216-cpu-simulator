class CacheSim:
    def __init__(self, blocksize, unified_size):
        self.blocksize = blocksize
        self.unified_size = unified_size

        # L1 Instruction and Data cache blocks
        self.i_block = 1024 // self.blocksize
        self.d_block = 1024 // self.blocksize

        # L2 unified cache blocks
        self.l2_block = (16 * 1024) // self.unified_size

        # Cache arrays
        self.i_cache = [None] * self.i_block
        self.d_cache = [None] * self.d_block
        self.l2_cache = [None] * self.l2_block

        # Performance counters
        self.i_miss = 0
        self.d_miss = 0
        self.l2_miss = 0
        self.writeback = 0

    def access_instruction(self, pc):
        block_id = (pc // self.blocksize) % self.i_block
        tag = (pc // self.blocksize) // self.i_block
        line = self.i_cache[block_id]

        if line is None or line['tag'] != tag:
            self.i_miss += 1
            self.i_cache[block_id] = {'tag': tag}
            self._check_l2(pc)

    def access_data(self, pc, is_store):
        block_id = (pc // self.blocksize) % self.d_block
        tag = (pc // self.blocksize) // self.d_block
        line = self.d_cache[block_id]

        if line is None or line['tag'] != tag:
            self.d_miss += 1

            if line is not None and line.get('dirty', False):
                self.writeback += 1

            self.d_cache[block_id] = {'tag': tag, 'dirty': is_store}
            self._check_l2(pc)
        elif is_store:
            self.d_cache[block_id]['dirty'] = True

    def _check_l2(self, pc):
        l2_block_id = (pc // self.unified_size) % self.l2_block
        l2_tag = (pc // self.unified_size) // self.l2_block
        line = self.l2_cache[l2_block_id]

        if line is None or line['tag'] != l2_tag:
            self.l2_miss += 1
            self.l2_cache[l2_block_id] = {'tag': l2_tag}

    def get_cost(self):
        return 0.5 * self.i_miss + self.d_miss + self.l2_miss + self.writeback

    def output(self):
        print(f"L1 Instruction Misses: {self.i_miss}")
        print(f"L1 Data Misses:        {self.d_miss}")
        print(f"L2 Unified Misses:     {self.l2_miss}")
        print(f"Writebacks:            {self.writeback}")
        print(f"Total Cost:            {self.get_cost()}")