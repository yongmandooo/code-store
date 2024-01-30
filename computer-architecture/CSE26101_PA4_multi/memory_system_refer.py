import math

class Block:
    def __init__(self, cacheline_size):
        self.valid=0
        self.tag = 0
        self.data=[0x00]*cacheline_size


class Set:
    def __init__(self, cacheline_size, associativity):
        self.blocks = [Block(cacheline_size) for i in range(associativity)]
        self.history = list(range(associativity)) # Access history for LRU replacement


class MemLike:
    def __init__(self, data_size, upper = None, lower = None):
        self.upper = upper
        self.data_size = data_size
        self.lower = lower
            
    def set_relations(self, upper=None, lower=None):
        self.upper = upper
        self.lower = lower


    def read(self, address) -> list:
        print("read: not implemented")
        pass


    def write(self, address, value):
        print("write: not implemented")
        pass
    

    def fetch(self, address):
        print("fetch: not implemented")
        pass


    def write_back(self, address, value):
        print("write_back: not implemented")
        pass
    

    def dump(self):
        pass
    
     
class RAM(MemLike):
    class mem_region_t:
        def __init__(self, start, size, type=0):
            self.start = start
            self.size = size
            self.mem = []
            self.off_bound = -(size)*type #For useful memory dump
            self.type = type
            self.dirty = False


        def set_off_bound(self, off):
            self.dirty = True
                
            if self.type == 0:
                self.off_bound = max(off, self.off_bound)
            else:
                self.off_bound = min(off, self.off_bound)


        def init_bound(self):
            self.dirty = False


    def __init__(self, data_size):
        #  All simulated memory will be managed by this class
        #  use the mem_write and mem_read functions to
        #  access/modify the simulated memory
        self.mem_grow_up=0
        self.mem_grow_down=-1
        # Basic Information
        self.mem_text_size = 0x00100000

        self.mem_text_start = 0x00400000
        #data section
        self.mem_data_start = 0x10000000
        self.mem_data_size = 0x00100000

        #stack section
        self.mem_stack_start = 0x80000000
        self.mem_stack_size = 0x00100000

        self.bytes_per_word = 4           
        
        self.data_size = data_size

        self.block_addr_mask = ~(self.data_size-1)

        # Main memory
        # memory will be dynamically allocated at initialization
        self.mem_text = self.mem_region_t(self.mem_text_start, self.mem_text_size)
        self.mem_data = self.mem_region_t(self.mem_data_start, self.mem_data_size)
        self.mem_stack = self.mem_region_t(self.mem_stack_start-self.mem_stack_size, self.mem_stack_size, self.mem_grow_down)
        self.mem_regions = [self.mem_text, self.mem_data, self.mem_stack]
        self.mem_nregions = 3

        for i in range(self.mem_nregions):
            self.mem_regions[i].mem = [0] * self.mem_regions[i].size

    # Procedure: read
    # Purpose: Read cacheline-size data from Memory
    def read(self, address):
        # mask address offset
        address = address & self.block_addr_mask
        
        for segment in self.mem_regions:
            if address >= segment.start and address < (segment.start + segment.size):
                offset = address - segment.start
                return segment.mem[offset:offset + self.data_size]
    
    
    # Procedure: write
    # Purpose: Write cacheline-size data to Memory
    def write(self, address, data):
        # mask address offset
        address = address & self.block_addr_mask
        
        for segment in self.mem_regions:
            if address >= segment.start and address < (segment.start + segment.size):
                offset = address - segment.start
                segment.set_off_bound(offset + self.data_size)
                segment.mem[offset:offset + self.data_size] = data


    def mdump(self, start, stop):
        print("-------------------------------------")
        for b in range(start, stop+1, self.data_size):
            line = f"{b:08x}...{(b + self.data_size - self.bytes_per_word):08x}| " 
            block = self.read(b)
                
            for i in range(0, self.data_size, self.bytes_per_word):
                word = (block[i+3] << 24) | (block[i+2] << 16) | (block[i+1] << 8) | (block[i] << 0)
                line+= f"{word:08x}."
                    
            line +="|"
            print(line)
        print("")


    def dump(self):
        if self.mem_data.dirty:
            dstart, dstop = self.mem_data.start, self.mem_data.start+self.mem_data.off_bound
            print("data section [0x%8x..0x%8x] :" % (dstart, dstop))
            self.mdump(dstart,dstop-4)
            print("")
    
        if self.mem_stack.dirty:
            dstart, dstop = self.mem_stack.start+self.mem_stack.off_bound, self.mem_stack.start+self.mem_stack_size
            print("stack section [0x%8x..0x%8x] :" % (dstart, dstop))
            self.mdump(dstart,dstop-4)
            print("")
        



class Cache(MemLike):
    def __init__(self, cacheline_size, data_size, upper = None, lower = None):
        super().__init__(data_size, upper, lower)
        self.associativity = 4
        self.n_sets = 8
        self.cacheline_size = cacheline_size
        self.idx_mask = 0b111 << int(math.log(self.cacheline_size, 2))
        self.offset_mask = self.cacheline_size - 1
        self.tag_mask = 0xffffffff - self.idx_mask - self.offset_mask
        self.sets = [Set(self.cacheline_size, self.associativity) for _ in range(self.n_sets)]


    def get_tag(self, address):
        return (address & self.tag_mask) >> int(math.log(self.idx_mask + self.offset_mask + 1, 2))


    def get_idx(self, address):
        return (address & self.idx_mask) >> int(math.log(self.cacheline_size, 2))


    def get_offset(self, address):
        return (address & self.offset_mask)

    
    def read(self, address):
        tag = self.get_tag(address)
        idx = self.get_idx(address)
        offset = self.get_offset(address)
        tag_list = [block.tag for block in self.sets[idx].blocks]
        if self.is_hit(address):
            self.handle_set_history(self.sets[idx], tag_list.index(tag))
            return self.sets[idx].blocks[tag_list.index(tag)].data[offset:offset + self.data_size]
        else:
            self.evict(address) 
            return self.read(address) # data 바꿨으니 read 다시 시도

    def write(self, address, value):
        tag = self.get_tag(address)
        idx = self.get_idx(address)
        offset = self.get_offset(address)
        tag_list = [block.tag for block in self.sets[idx].blocks]
        # print(tag_list)
        if self.is_hit(address):
            # print("hit")
            self.handle_set_history(self.sets[idx], tag_list.index(tag))
            for index, data in enumerate(value):
                self.sets[idx].blocks[tag_list.index(tag)].data[offset + index] = data
        else:
            # print("miss", address)
            # print("taglist in write 1")
            # for block in self.sets[idx].blocks:
            #     print(block.tag)
            self.evict(address) 
            self.write(address, value) # data 바꿨으니 write 다시 시도


    def fetch(self, address) -> list:
        return self.lower.read(address)
    

    def write_back(self, address, value):
        self.lower.write(address, value)

    def is_hit(self, address):
        tag = self.get_tag(address)
        idx = self.get_idx(address)
        tag_list = [block.tag for block in self.sets[idx].blocks]
        if tag in tag_list:
            block = self.sets[idx].blocks[tag_list.index(tag)]
            if block.valid == 1:
                return True
            else:
                return False
        else:
            return False
        
    def handle_set_history(self, set, way):
        if way in set.history:
            set.history.remove(way)
        set.history.append(way)

    def evict(self, address):
        idx = self.get_idx(address)
        tag = self.get_tag(address)
        lru_index = self.sets[idx].history[0]
        target_block = self.sets[idx].blocks[lru_index]

        if target_block.valid == 1:
            self.write_back(address, target_block.data)

        lower_data = self.fetch(address)
        zero_data = []
        for _ in range(self.cacheline_size):
            zero_data.append(0)
        self.sets[idx].blocks[lru_index].valid = 1
        self.sets[idx].blocks[lru_index].tag = tag
        self.sets[idx].blocks[lru_index].data = lower_data if lower_data != None and len(lower_data) == self.cacheline_size else zero_data

    def dump(self):
        print("Cache content:")

        empty = " " * self.cacheline_size
        print(f"|index| v |  tag   | {empty}way0{empty} | v |  tag   | {empty}way1{empty} | v |  tag   | {empty}way2{empty} | v |  tag   | {empty}way3{empty} |")
        
        idx = 0
        for set in self.sets:
            pline = f"| {idx:03b} |"
            for b in set.blocks:
                data = 0
                data_str = ""
                cnt = 0
                for byte in b.data:
                    data |= byte << cnt*8
                    cnt +=1
                    if cnt == 4:
                        data_str += f"{data:08x}."
                        data = 0
                        cnt = 0                
                pline += f" {b.valid} | {b.tag:06x} | {data_str} |"        
            print(pline)
            idx += 1
        
        print("")


class Memory:

    instance = None

    def __init__(self):
        self.L1 = Cache(32, 4)
        self.L2 = Cache(64, 32)
        self.RAM = RAM(64)
        
        self.L1.set_relations(lower=self.L2)
        self.L2.set_relations(self.L1, self.RAM)
        self.RAM.set_relations(upper=self.L2)

        
    def read(self, address):
        self.L1.read(address)
    
    def write(self, address, value):
        list_value = list()
        for i in range(4):
            list_value.append((value >> (i * 8)) & 0xFF)
        self.L1.write(address, list_value)

    def dump(self):
        self.L1.dump()
        self.L2.dump()
        self.RAM.dump()
        
    @staticmethod
    def get_instance():
        if Memory.instance == None:
            Memory.instance = Memory()
            
        return Memory.instance
    


        
                


    