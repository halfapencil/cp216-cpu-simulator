
class CacheSim:
    def __init__(self,blocksize,unified_size):
        self.main_memory = []

        self.blocksize = blocksize
        self.unified_size = unified_size

        self.i_block = 1024//self.blocksize
        self.d_block = 1024//self.blocksize

        self.i_cache = [None] * self.i_block
        self.d_cache = [None] * self.d_block

        self.i_miss=0
        self.d_miss=0
        self.l2_miss=0
        self.writeback=0

        self.l2_block = 16*1024 // self.unified_size
        self.l2_cache = [None] *self.l2_block
        

    def simulate(self,bin):
        f = open(bin,"r")
        for line in f:
            self.main_memory.append(line)
        program_size = len(self.main_memory)*4
        for pc in range(0,program_size,4):
            block_id = (pc // self.blocksize) %self.i_block
            tag = (pc % self.blocksize) // self.i_block

            cache_line = self.i_cache[block_id]
            if cache_line is None or cache_line['tag'] != tag:
                self.i_miss += 1

                l2_block_id = (pc // self.unified_size) % self.l2_block
                l2_tag = (pc % self.unified_size) // self.l2_block
                l2_line = self.l2_cache[l2_block_id]

                if l2_line is None or l2_line['tag'] != l2_tag:
                    self.l2_miss += 1
                    self.l2_cache[l2_block_id] = {'tag' : l2_tag}

                self.i_cache[block_id] = {'tag':tag}
            pass

    def output(self):
        print(str(self.i_miss) + " " + str(self.d_miss) + " "+ str(self.l2_miss)+" " + str(self.writeback))

if __name__ == "__main__":
    blocksize = 16          #Block size available for 4,8,16,32 bytes
    unifiedsize = 64        #unified size available for 16,32,64 bytes
    sim = CacheSim(blocksize,unifiedsize)
    sim.simulate("test")
    sim.output()