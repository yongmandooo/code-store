'''
MIPS-32 Instruction Level Simulatr

CSE261 UNIST
run.py
'''

import util
import initialize
import ctypes


def OPCODE(INST):
    return INST.opcode


def SET_OPCODE(INST, VAL):
    INST.opcode = ctypes.c_short(VAL).value


def FUNC(INST):
    return INST.func_code


def SET_FUNC(INST, VAL):
    INST.func_code = ctypes.c_short(VAL).value


def RS(INST):
    return INST.rs


def SET_RS(INST, VAL):
    INST.rs = ctypes.c_ubyte(VAL).value


def RT(INST):
    return INST.rt


def SET_RT(INST, VAL):
    INST.rt = ctypes.c_ubyte(VAL).value


def RD(INST):
    return INST.rd


def SET_RD(INST, VAL):
    INST.rd = ctypes.c_ubyte(VAL).value


def FS(INST):
    return RD(INST)


def SET_FS(INST, VAL):
    SET_RD(INST, VAL)


def FT(INST):
    return RT(INST)


def SET_FT(INST, VAL):
    SET_RT(INST, VAL)


def FD(INST):
    return SHAMT(INST)


def SET_FD(INST, VAL):
    SET_SHAMT(INST, VAL)


def SHAMT(INST):
    return INST.shamt


def SET_SHAMT(INST, VAL):
    INST.shamt = ctypes.c_ubyte(VAL).value


def IMM(INST):
    return INST.imm


def SET_IMM(INST, VAL):
    INST.imm = ctypes.c_short(VAL).value


def BASE(INST):
    return RS(INST)


def SET_BASE(INST, VAL):
    SET_RS(INST, VAL)


def IOFFSET(INST):
    return IMM(INST)


def SET_IOFFSET(INST, VAL):
    SET_IMM(INST, VAL)


def IDISP(INST):
    X = INST.imm << 2
    return SIGN_EX(X)


def COND(INST):
    return RS(INST)


def SET_COND(INST, VAL):
    SET_RS(INST, VAL)


def CC(INST):
    return (RT(INST) >> 2)


def ND(INST):
    return ((RT(INST) & 0x2) >> 1)


def TF(INST):
    return (RT(INST) & 0x1)


def TARGET(INST):
    return INST.target


def SET_TARGET(INST, VAL):
    INST.target = VAL


def ENCODING(INST):
    return INST.encoding


def SET_ENCODIGN(INST, VAL):
    INST.encoding = VAL


def EXPR(INST):
    return INST.expr


def SET_EXPR(INST, VAL):
    INST.expr = VAL


def SOURCE(INST):
    return INST.source_line


def SET_SOURCE(INST, VAL):
    INST.source_line = VAL


# Sign Extension
def SIGN_EX(X):
    if (X) & 0x8000:
        return X | 0xffff0000
    else:
        return X
    
def ZERO_EX(X):
    return X & 0x0000ffff

COND_UN = 0x1
COND_EQ = 0x2
COND_LT = 0x4
COND_IN = 0x8

# Minimum and maximum values that fit in instruction's imm field
IMM_MIN = 0xffff8000
IMM_MAX = 0x00007fff

UIMM_MIN = 0
UIMM_MAX = (1 << 16)-1


def BRANCH_INST(TEST, TARGET):
    if TEST:
        target = TARGET
        JUMP_INST(target)


def JUMP_INST(TARGET):
    import util
    util.CURRENT_STATE.PC = TARGET


def LOAD_INST(LD, MASK):
    return (LD & (MASK))


# Procedure: get_inst_info
# Purpose: Read instruction information
def get_inst_info(pc):
    return initialize.INST_INFO[(pc - util.MEM_TEXT_START) >> 2]

def change_to_signed(reg_data):
    if reg_data > 0x7fffffff:
        val = (val & 0xffffffff) - 0xffffffff - 1
    
    return reg_data

# Procedure: process_instruction
# Purpose: Process one instruction
def process_instruction():
    # Implement this function
    # erase "pass" to start implementing
    #현재 CPU(메인 메모리 - 레지스터 및 PC) 상태: util.CURRENT_STATE 
    instr = get_inst_info(util.CURRENT_STATE.PC)

    util.inst_file.write(f"opcode: {hex(instr.opcode)}, func_code: {hex(instr.func_code)}\n")
    rs = instr.rs
    rt = instr.rt
    rd = instr.rd
    shamt = instr.shamt
    imm = instr.imm
    rg_list = util.CURRENT_STATE.REGS
    new_pc = -1

    # TYPE I
    # 0xa: (0b001010)SLTI
    # 0x8: (0b001000)ADDI
    # 0x9: (0b001001)ADDIU
    # 0xc: (0b001100)ANDI
    # 0xf: (0b001111)LUI
    # 0xd: (0b001101)ORI
    # 0xb: (0b001011)SLTIU
    # 0x23: (0b100011)LW
    # 0x2b: (0b101011)SW
    # 0x4: (0b000100)BEQ
    # 0x5: (0b000101)BNE
    if instr.opcode == 0xa:
        # SLTI
        if change_to_signed(rg_list[rs]) < change_to_signed(SIGN_EX(imm)):
            rg_list[rt] = 1
        else:
            rg_list[rt] = 0
    elif instr.opcode == 0x8:
        #ADDI
        rg_list[rt] = change_to_signed(rg_list[rs]) + SIGN_EX(imm)
    elif instr.opcode == 0x9:
        #ADDIU
        rg_list[rt] = rg_list[rs] + SIGN_EX(imm)
    elif instr.opcode == 0xc:
        #ANDI
        rg_list[rt] = rg_list[rs] & (imm & 0x0000ffff)
    elif instr.opcode == 0xf:
        #LUI
        rg_list[rt] = imm << 16
    elif instr.opcode == 0xd:
        #ORI
        rg_list[rt] = rg_list[rs] | (imm & 0x0000ffff)
    elif instr.opcode == 0xb:
        #SLTIU
        temp_rs = rg_list[rs]
        if rg_list[rs] < 0:
            temp_rs += 2*0x80000000

        temp_imm = imm
        if imm < 0:
            temp_imm += 2*0x8000
            
        if temp_rs < temp_imm:
            rg_list[rt] = 1
        else:
            rg_list[rt] = 0
    elif instr.opcode == 0x23:
        #LW
        rg_list[rt] = util.mem_read((rg_list[rs] + SIGN_EX(imm)) & 0xffffffff)
    elif instr.opcode == 0x2b:
        #SW
        util.mem_write((rg_list[rs] + SIGN_EX(imm)) & 0xffffffff, rg_list[rt])
    elif instr.opcode == 0x4:
        #BEQ
        if rg_list[rs] == rg_list[rt]:
            new_pc = util.CURRENT_STATE.PC + change_to_signed(SIGN_EX(imm))*4 + 4
    elif instr.opcode == 0x5:
        #BNE
        if rg_list[rs] != rg_list[rt]:
            new_pc = util.CURRENT_STATE.PC + change_to_signed(SIGN_EX(imm))*4 + 4

    # TYPE R
    # 0x0: (0b000000)ADD, SLT, ADDU, AND, NOR, OR, SLTU, SLL, SRL, SUBU  if JR
    elif instr.opcode == 0x0:
        if instr.func_code == 0x20:
            #ADD
            rg_list[rd] = change_to_signed(rg_list[rs]) + change_to_signed(rg_list[rt])
        elif instr.func_code == 0x2a:
            #SLT
            if change_to_signed(rg_list[rs]) < change_to_signed(rg_list[rt]):
                rg_list[rd] = 1
            else:
                rg_list[rd] = 0
        elif instr.func_code == 0x21:
            #ADDU
            rg_list[rd] = rg_list[rs] + rg_list[rt]
        elif instr.func_code == 0x24:
            #AND
            rg_list[rd] = rg_list[rs] & rg_list[rt]
        elif instr.func_code == 0x27:
            #NOR
            rg_list[rd] = ~( rg_list[rs] | rg_list[rt] )
        elif instr.func_code == 0x25:
            #OR
            rg_list[rd] = rg_list[rs] | rg_list[rt]
        elif instr.func_code == 0x2b:
            #SLTU
            if rg_list[rs] < rg_list[rt]:
                rg_list[rd] = 1
            else:
                rg_list[rd] = 0
        elif instr.func_code == 0x00:
            #SLL
            rg_list[rd] = rg_list[rt] << shamt
        elif instr.func_code == 0x02:
            #SRL
            rg_list[rd] = rg_list[rt] >> shamt
        elif instr.func_code == 0x23 or instr.func_code == 0x22:
            #SUBU #SUB
            rg_list[rd] = rg_list[rs] - rg_list[rt]
        elif instr.func_code == 0x08:
            #JR
            new_pc = rg_list[rs]
        else:
            pass

    # TYPE J
    # 0x2: (0b000010)J
    # 0x3: (0b000011)JAL
    elif instr.opcode == 0x2:
        new_pc = instr.target << 2
    elif instr.opcode == 0x3:
        rg_list[31] = util.CURRENT_STATE.PC + 8
        new_pc = instr.target << 2
        util.CURRENT_STATE.REGS = rg_list
    else:
        pass
        
    util.CURRENT_STATE.REGS = rg_list
    if new_pc == -1:
        util.CURRENT_STATE.PC += 4
    else:
        util.CURRENT_STATE.PC = new_pc

    if(util.CURRENT_STATE.PC >= util.MEM_TEXT_START+initialize.NUM_INST*4) or util.CURRENT_STATE.PC == 0:
        util.RUN_BIT=False



