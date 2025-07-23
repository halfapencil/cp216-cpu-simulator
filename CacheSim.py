
class CacheSim:
    def __init__(self,blocksize,unified_size):
        # initializing variables
        self.main_memory = []

        self.blocksize = blocksize
        self.unified_size = unified_size

        self.i_block = 1024//self.blocksize
        self.d_block = 1024//self.blocksize

        #l1 caches
        self.i_cache = [None] * self.i_block
        self.d_cache = [None] * self.d_block

        # count number of misses
        self.i_miss=0
        self.d_miss=0
        self.l2_miss=0
        self.writeback=0

        # size of l2 cache
        self.l2_block = 16*1024 // self.unified_size
        self.l2_cache = [None] *self.l2_block
        
    def simulate(self,bin):
        f = open(bin,"r")
        for line in f:
            self.main_memory.append(line)       # add instructions to main memory
        program_size = len(self.main_memory)*4
        print(self.main_memory)
        for pc in range(0,program_size,4):

            # determine blockid and tag
            block_id = (pc // self.blocksize) %self.i_block
            tag = (pc % self.blocksize) // self.i_block

            cache_line = self.i_cache[block_id]

            # if the instruction is not in the cache or the tag doesnt match
            if cache_line is None or cache_line['tag'] != tag:
                self.i_miss += 1
                # try to find it in the l2 cache
                l2_block_id = (pc // self.unified_size) % self.l2_block
                l2_tag = (pc % self.unified_size) // self.l2_block
                l2_line = self.l2_cache[l2_block_id]

                # if its not in the l2 cache
                if l2_line is None or l2_line['tag'] != l2_tag:
                    self.l2_miss += 1
                    self.l2_cache[l2_block_id] = {'tag' : l2_tag}

                self.i_cache[block_id] = {'tag':tag, 'dirty':False}
        # Determine if d_cache needed for ldr/str instructions
        #TODO edit if ldr/str instruction 
        if True:

            #TODO determine if its store or not(load)
            store = True

            #determine the block and tag
            d_blockid = (pc//self.blocksize)%self.d_block
            d_tag = (pc//self.blocksize)//self.d_block

            d_line = self.d_cache[d_blockid]
            if d_line is None or d_line['tag'] != d_tag:
                self.d_miss += 1
                
                if d_line is not None and d_line.get('dirty',False):
                    self.writeback += 1
        
                self.d_cache[d_blockid] = {'tag':d_tag, 'dirty':store}
            elif store:
                self.d_cache[blocksize]['dirty'] = True

            #return cost
            return (self.i_miss + self.d_miss)/2 +self.l2_miss+self.writeback


    #debugging
    def output(self):
        print(str(self.i_miss) + " " + str(self.d_miss) + " "+ str(self.l2_miss)+" " + str(self.writeback))



if __name__ == "__main__":
    blocksize = 16          #Block size available for 4,8,16,32 bytes
    unifiedsize = 64        #unified size available for 16,32,64 bytes
    sim = CacheSim(blocksize,unifiedsize)
    sim.simulate("test")
    sim.output()