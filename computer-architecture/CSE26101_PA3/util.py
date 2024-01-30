'''
MIPS-32 Instruction Level Simulatr

CSE261 UNIST
util.py

DO NOT MODIFY THIS FILE!
You should only modify the parse.py and run.py files!
'''

import initialize
import ctypes

# Basic Information
MEM_TEXT_START = 0x00400000
MEM_TEXT_SIZE = 0x00100000
MEM_DATA_START = 0x10000000
MEM_DATA_SIZE = 0x00100000
MIPS_REGS = 32
BYTES_PER_WORD = 4

# Pipeline Execution
PIPE_STAGE = 5

IF_STAGE  = 0
ID_STAGE  = 1
EX_STAGE  = 2
MEM_STAGE = 3
WB_STAGE  = 4


inst_file = None

class CPU_State:
    def __init__(self):
        self.PC = 0  # program counter
        self.REGS = [0] * MIPS_REGS    # register file
        # Pipeline Execution
        self.REGS_LOCK = [0] * MIPS_REGS # register lock to support stalls Lock registers when data is not ready
        self.PIPE = [0] * PIPE_STAGE # PC being executed at each stage
        self.PIPE_STALL = [0] * PIPE_STAGE

        #IF_ID_latch
        self.IF_ID_INST = 0
        self.IF_ID_NPC = 0

        #ID_EX_latch
        self.ID_EX_NPC = 0
        self.ID_EX_REG1 = 0
        self.ID_EX_REG2 = 0
        self.ID_EX_IMM = ""
        self.ID_EX_DEST = ""

        #EX_MEM_latch
        self.EX_MEM_NPC = 0
        self.EX_MEM_ALU_OUT = 0
        self.EX_MEM_W_VALUE = 0
        self.EX_MEM_BR_TARGET = 0
        self.EX_MEM_BR_TAKE = 0
        self.EX_MEM_DEST = ""

        #MEM_WB_latch
        self.MEM_WB_NPC = 0
        self.MEM_WB_ALU_OUT = 0
        self.MEM_WB_MEM_OUT = 0
        self.MEM_WB_BR_TAKE = 0
        self.MEM_WB_DEST = ""

        #Forwarding
        self.EX_MEM_FORWARD_REG = ""
        self.MEM_WB_FORWARD_REG = ""
        self.EX_MEM_FORWARD_VALUE = 0
        self.MEM_WB_FORWARD_VALUE = 0

        #To choose right PC
        self.IF_PC = 0
        self.JUMP_PC = 0
        self.BRANCH_PC = 0


# You should decode your instructions from the
# ASCII-binary format to this structured format
class instruction:
    def __init__(self):
        # short
        self.opcode = 0
        # short
        self.func_code = 0
        # uint32_t
        self.value = 0
        # uint32_t
        self.target = 0
        # unsinged char
        self.rs = 0
        # unsinged char
        self.rt = 0
        # short
        self.imm = 0
        # unsinged char
        self.rd = 0
        # unsinged char
        self.shamt = 0


#  All simulated memory will be managed by this class
#  use the mem_write and mem_read functions to
#  access/modify the simulated memory
class mem_region_t:
    def __init__(self, start, size):
        self.start = start
        self.size = size
        self.mem = []


# Main memory
# memory will be dynamically allocated at initialization
MEM_TEXT = mem_region_t(MEM_TEXT_START, MEM_TEXT_SIZE)
MEM_DATA = mem_region_t(MEM_DATA_START, MEM_DATA_SIZE)
MEM_REGIONS = [MEM_TEXT, MEM_DATA]
MEM_NREGIONS = 2

# CPU State info
CURRENT_STATE = CPU_State()
RUN_BIT = 0
INSTRUCTION_COUNT = 0
# Pipeline Execution State
FETCH_BIT = 0
CYCLE_COUNT = 0
BR_BIT = True
FORWARDING_BIT = True
MAX_INSTRUCTION_NUM = 0
NUM_INST = 0



# Procedure: fromBinary
# Purpose: From binary to integer
def fromBinary(bits):
    eq = 0
    m = 1
    for bit in bits[::-1]:
        b = int(bit)
        eq += b * m
        m *= 2
    return eq


# Procedure: mem_read
# Purpose: read a 32-bit word from memory
def mem_read(address):
    address = ctypes.c_uint32(address).value
    for i in range(MEM_NREGIONS):
        if address >= MEM_REGIONS[i].start and address < (MEM_REGIONS[i].start + MEM_REGIONS[i].size):
            offset = ctypes.c_uint32(address - MEM_REGIONS[i].start).value
            return (MEM_REGIONS[i].mem[offset + 3] << 24) | (MEM_REGIONS[i].mem[offset + 2] << 16) | (MEM_REGIONS[i].mem[offset + 1] << 8) | (MEM_REGIONS[i].mem[offset + 0] << 0)
    print("Memory Read Error: Exceed memory boundary 0x%x\n"%address)
    exit(1)
# Procedure: mem_write
# Purpose: Write a 32-bit word to memory
def mem_write(address, value):
    address = address& 0xffffffff
    value = value& 0xffffffff
    for i in range(MEM_NREGIONS):
        if address >= MEM_REGIONS[i].start and address < (MEM_REGIONS[i].start + MEM_REGIONS[i].size):
            offset = address - MEM_REGIONS[i].start

            MEM_REGIONS[i].mem[offset + 3] = (value >> 24) & 0xFF
            MEM_REGIONS[i].mem[offset + 2] = (value >> 16) & 0xFF
            MEM_REGIONS[i].mem[offset + 1] = (value >> 8) & 0xFF
            MEM_REGIONS[i].mem[offset + 0] = (value >> 0) & 0xFF
            return
    print("Memory Write Error: Exceed memory boundary 0x%08x"%address)
    exit(1)

# Procedure: cycle
# Purpose: Execute a cycle
def cycle():
    import run
    run.process_instruction()
    
    if INSTRUCTION_COUNT >= MAX_INSTRUCTION_NUM:
        global RUN_BIT
        RUN_BIT = False
    
    global CYCLE_COUNT
    CYCLE_COUNT += 1

    # for debug
    # print(INSTRUCTION_COUNT, " - Current PC: %x" % CURRENT_STATE.PC)


# Procedure: run n
# Purpose: Simulate MIPS for n cycles
def run():
    if RUN_BIT == False:
        print("Can't simulate, Simulator is halted\n")
        return False
    
    print("Simulating for %lu instructions...\n" % MAX_INSTRUCTION_NUM)

    while RUN_BIT:
        cycle()

    print("Simulator halted after %lu cycles\n" % CYCLE_COUNT)


# Procedure: go
# Purpose: Simulate MIPS until HALTed
def go():
    if RUN_BIT == False:
        print("Can't simulate, Simulator is halted\n")
        return
    print("Simulating...\n")
    while RUN_BIT:
        cycle()
    print("Simulator halted\n")


# Procedure: mdump
# Purpose: Dump a word-aligned region of memory to the output file.
def mdump(start, stop):
    print("Memory content [0x%8x..0x%8x] :" % (start, stop))
    print("-------------------------------------")
    for i in range(start, stop+1, 4):
        print("0x%08x: 0x%08x" % (i, mem_read(i)))
    print("")


# Procedure: rdump
# Purpose:  Dump current register and bus values to the output file.
def rdump():
    print("Current register values : ")
    print("-------------------------------------")
    print("PC: 0x%08x" % CURRENT_STATE.PC)
    print("Registers:")
    for k in range(MIPS_REGS):
        print("R%d: 0x%08x" % (k, ctypes.c_uint(CURRENT_STATE.REGS[k]).value))
    print("")

# Procedure : pdump
# Purpose   : Dump current pipeline PC state
def pdump():
    print("Current pipeline PC state :")
    print("-------------------------------------")
    print("CYCLE %lu:" % CYCLE_COUNT, end="")

    for k in range(PIPE_STAGE):
        if CURRENT_STATE.PIPE[k]:
            print("0x%08x" % CURRENT_STATE.PIPE[k], end="")
        else:
            print("          ", end="")

        if k != PIPE_STAGE - 1:
            print("|", end="")
    print("\n")

# Procedure : init_memory
# Purpose : Allocate and zero memory
def init_memory():
    for i in range(MEM_NREGIONS):
        MEM_REGIONS[i].mem = [0] * MEM_REGIONS[i].size


# Procedure : init_inst_info
# Purpose : Initialize instruction info
def init_inst_info(NUM_INST):
    for i in range(NUM_INST):
        initialize.INST_INFO[i].value = 0
        initialize.INST_INFO[i].opcode = 0
        initialize. INST_INFO[i].func_code = 0
        initialize.INST_INFO[i].rs = 0
        initialize.INST_INFO[i].rt = 0
        initialize.INST_INFO[i].rd = 0
        initialize.INST_INFO[i].imm = 0
        initialize.INST_INFO[i].shamt = 0
        initialize.INST_INFO[i].target = 0
