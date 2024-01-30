'''
MIPS-32 Instruction Level Simulatr

CSE261 UNIST
run.py
'''

import util
import initialize
import ctypes


def OPCODE(INST):
    return ctypes.c_short(INST.opcode).value


def SET_OPCODE(INST, VAL):
    INST.opcode = ctypes.c_short(VAL).value


def FUNC(INST):
    return ctypes.c_short(INST.func_code).value


def SET_FUNC(INST, VAL):
    INST.func_code = ctypes.c_short(VAL).value


def RS(INST):
    return ctypes.c_ubyte(INST.rs).value


def SET_RS(INST, VAL):
    INST.rs = ctypes.c_ubyte(VAL).value


def RT(INST):
    return ctypes.c_ubyte(INST.rt).value


def SET_RT(INST, VAL):
    INST.rt = ctypes.c_ubyte(VAL).value


def RD(INST):
    return ctypes.c_ubyte(INST.rd).value


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
    return ((RT(INST)&0xffffffff) >> 2)


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
def UNSIGNED(X):
    if (X) & 0x8000:
        return X & 0xffffffff
    else:
        return X 
        

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
    return initialize.INST_INFO[(pc - util.MEM_TEXT_START)>> 2]

def change_to_signed(reg_data):
    if reg_data > 0x7fffffff:
        val = (val & 0xffffffff) - 0xffffffff - 1
    
    return reg_data

# Procedure: process_instruction
# Purpose: Process one instruction
def process_instruction():
    # * Your implementation here *
    #load use hazard detection
    load_use_hazard = False
    if (util.CURRENT_STATE.PIPE[util.ID_STAGE] and
        OPCODE(get_inst_info(util.CURRENT_STATE.PIPE[util.ID_STAGE])) == 0x23 and
        (util.CURRENT_STATE.ID_EX_DEST == RS(util.CURRENT_STATE.IF_ID_INST)or
         util.CURRENT_STATE.ID_EX_DEST == RT(util.CURRENT_STATE.IF_ID_INST))):
        load_use_hazard = True
    
    #state propagation
    util.CURRENT_STATE.PIPE[util.WB_STAGE] = util.CURRENT_STATE.PIPE[util.MEM_STAGE]
    util.CURRENT_STATE.PIPE[util.MEM_STAGE] = util.CURRENT_STATE.PIPE[util.EX_STAGE]
    if util.CURRENT_STATE.JUMP_PC != 0:
        util.CURRENT_STATE.PIPE[util.EX_STAGE] = util.CURRENT_STATE.PIPE[util.ID_STAGE]
        Flush_By_Jump()
        util.CURRENT_STATE.PIPE[util.IF_STAGE] = util.CURRENT_STATE.PC
        util.CURRENT_STATE.JUMP_PC = 0
    elif util.CURRENT_STATE.EX_MEM_BR_TAKE == 1:
        print("branch taken")
        util.CURRENT_STATE.EX_MEM_BR_TAKE = 0
        Flush_By_Branch()
        util.CURRENT_STATE.PIPE[util.IF_STAGE] = util.CURRENT_STATE.PC
        util.CURRENT_STATE.EX_MEM_BR_TARGET = 0
    else:
        if util.CURRENT_STATE.PIPE[util.IF_STAGE] != util.CURRENT_STATE.PC:
            util.CURRENT_STATE.PIPE[util.EX_STAGE] = util.CURRENT_STATE.PIPE[util.ID_STAGE]
            util.CURRENT_STATE.PIPE[util.ID_STAGE] = util.CURRENT_STATE.PIPE[util.IF_STAGE]
            util.CURRENT_STATE.PIPE[util.IF_STAGE] = Choose_PC()
        else:
            util.CURRENT_STATE.PIPE[util.EX_STAGE] = None

    if not load_use_hazard and (util.CURRENT_STATE.PC < util.MEM_TEXT_START+initialize.NUM_INST*4 and util.CURRENT_STATE.PC != 0):
        util.CURRENT_STATE.PC += 4

    if (util.CURRENT_STATE.PIPE[util.IF_STAGE] == None and
        util.CURRENT_STATE.PIPE[util.ID_STAGE] == None and
        util.CURRENT_STATE.PIPE[util.EX_STAGE] == None and
        util.CURRENT_STATE.PIPE[util.MEM_STAGE] == None):
        util.RUN_BIT = False

    #argument setting
    id_ex_npc = util.CURRENT_STATE.ID_EX_NPC
    id_ex_reg1 = util.CURRENT_STATE.ID_EX_REG1
    if id_ex_reg1 == util.CURRENT_STATE.EX_MEM_FORWARD_REG:
        reg1_val = util.CURRENT_STATE.EX_MEM_FORWARD_VALUE
        util.CURRENT_STATE.EX_MEM_FORWARD_REG = ""
        util.CURRENT_STATE.EX_MEM_FORWARD_VALUE = 0
    elif id_ex_reg1 == util.CURRENT_STATE.MEM_WB_FORWARD_REG:
        reg1_val = util.CURRENT_STATE.MEM_WB_FORWARD_VALUE
        util.CURRENT_STATE.MEM_WB_FORWARD_REG = ""
        util.CURRENT_STATE.MEM_WB_FORWARD_VALUE = 0
    else:
        reg1_val = util.CURRENT_STATE.REGS[id_ex_reg1]
    id_ex_reg2 = util.CURRENT_STATE.ID_EX_REG2
    if id_ex_reg2 == util.CURRENT_STATE.EX_MEM_FORWARD_REG:
        reg2_val = util.CURRENT_STATE.EX_MEM_FORWARD_VALUE
        util.CURRENT_STATE.EX_MEM_FORWARD_REG = ""
        util.CURRENT_STATE.EX_MEM_FORWARD_VALUE = 0
    elif id_ex_reg2 == util.CURRENT_STATE.MEM_WB_FORWARD_REG:
        reg2_val = util.CURRENT_STATE.MEM_WB_FORWARD_VALUE
        util.CURRENT_STATE.MEM_WB_FORWARD_REG = ""
        util.CURRENT_STATE.MEM_WB_FORWARD_VALUE = 0
    else:
        reg2_val = util.CURRENT_STATE.REGS[id_ex_reg2]
    id_ex_imm = util.CURRENT_STATE.ID_EX_IMM
    id_ex_dest = util.CURRENT_STATE.ID_EX_DEST

    ex_mem_npc = util.CURRENT_STATE.EX_MEM_NPC
    ex_mem_alu_out = util.CURRENT_STATE.EX_MEM_ALU_OUT
    ex_mem_w_value = util.CURRENT_STATE.EX_MEM_W_VALUE
    ex_mem_br_target = util.CURRENT_STATE.EX_MEM_BR_TARGET
    ex_mem_br_take = util.CURRENT_STATE.EX_MEM_BR_TAKE
    ex_mem_dest = util.CURRENT_STATE.EX_MEM_DEST

    mem_wb_npc = util.CURRENT_STATE.MEM_WB_NPC
    mem_wb_alu_out = util.CURRENT_STATE.MEM_WB_ALU_OUT
    mem_wb_mem_out = util.CURRENT_STATE.MEM_WB_MEM_OUT
    mem_wb_br_take = util.CURRENT_STATE.MEM_WB_BR_TAKE
    mem_wb_dest = util.CURRENT_STATE.MEM_WB_DEST

    #running datapath
    if util.CURRENT_STATE.PIPE[util.IF_STAGE]:
        IFetch_Stage()
    if util.CURRENT_STATE.PIPE[util.ID_STAGE]:
        IDecode_Stage()
    if util.CURRENT_STATE.PIPE[util.EX_STAGE]:
        Execute_Stage(reg1_val, reg2_val, id_ex_imm, id_ex_npc, id_ex_dest)
    if util.CURRENT_STATE.PIPE[util.MEM_STAGE]:
        Memory_Stage(ex_mem_alu_out, ex_mem_dest, ex_mem_npc, ex_mem_br_take)
    if util.CURRENT_STATE.PIPE[util.WB_STAGE]:
        WriteBack_Stage(mem_wb_dest, mem_wb_alu_out, mem_wb_mem_out)

    #data hazard detection
    if (util.CURRENT_STATE.EX_MEM_W_VALUE == 1 and util.CURRENT_STATE.EX_MEM_DEST != 0 and (util.CURRENT_STATE.EX_MEM_DEST == util.CURRENT_STATE.ID_EX_REG1)):
            util.CURRENT_STATE.EX_MEM_FORWARD_REG = util.CURRENT_STATE.ID_EX_REG1
            util.CURRENT_STATE.EX_MEM_FORWARD_VALUE = util.CURRENT_STATE.EX_MEM_ALU_OUT
    if (util.CURRENT_STATE.EX_MEM_W_VALUE == 1 and util.CURRENT_STATE.EX_MEM_DEST != 0 and (util.CURRENT_STATE.EX_MEM_DEST == util.CURRENT_STATE.ID_EX_REG2)):
            util.CURRENT_STATE.EX_MEM_FORWARD_REG = util.CURRENT_STATE.ID_EX_REG2
            util.CURRENT_STATE.EX_MEM_FORWARD_VALUE = util.CURRENT_STATE.EX_MEM_ALU_OUT
    if not (util.CURRENT_STATE.EX_MEM_W_VALUE == 1 and util.CURRENT_STATE.EX_MEM_DEST != 0 and (util.CURRENT_STATE.EX_MEM_DEST == util.CURRENT_STATE.ID_EX_REG1 or util.CURRENT_STATE.EX_MEM_DEST == util.CURRENT_STATE.ID_EX_REG2)):
        if util.CURRENT_STATE.PIPE[util.MEM_STAGE]:
            instr = get_inst_info(util.CURRENT_STATE.PIPE[util.MEM_STAGE])
            opcode = OPCODE(instr)
            if ((opcode == 0x0 or opcode == 0xa or opcode == 0x8 or opcode == 0x9 or opcode == 0xc or opcode == 0xf or opcode == 0xd or opcode == 0xb or opcode == 0x23) and
                util.CURRENT_STATE.MEM_WB_DEST != 0):
                if util.CURRENT_STATE.MEM_WB_DEST == util.CURRENT_STATE.ID_EX_REG1:
                    util.CURRENT_STATE.MEM_WB_FORWARD_REG = util.CURRENT_STATE.ID_EX_REG1
                    if opcode == 0x23:
                        util.CURRENT_STATE.MEM_WB_FORWARD_VALUE = util.CURRENT_STATE.MEM_WB_MEM_OUT
                    else:
                        util.CURRENT_STATE.MEM_WB_FORWARD_VALUE = util.CURRENT_STATE.MEM_WB_ALU_OUT
                if util.CURRENT_STATE.MEM_WB_DEST == util.CURRENT_STATE.ID_EX_REG2:
                    util.CURRENT_STATE.MEM_WB_FORWARD_REG = util.CURRENT_STATE.ID_EX_REG2
                    if opcode == 0x23:
                        util.CURRENT_STATE.MEM_WB_FORWARD_VALUE = util.CURRENT_STATE.MEM_WB_MEM_OUT
                    else:
                        util.CURRENT_STATE.MEM_WB_FORWARD_VALUE = util.CURRENT_STATE.MEM_WB_ALU_OUT

# /***************************************************************/
# /*                                                             */
# /* Procedure: IFetch_Stage                                     */
# /*                                                             */
# /* Purpose: Instruction fetch                                  */
# /*                                                             */
# /***************************************************************/
def IFetch_Stage():
    instr = get_inst_info(util.CURRENT_STATE.PIPE[util.IF_STAGE])
    util.CURRENT_STATE.IF_ID_INST = instr
    util.CURRENT_STATE.IF_ID_NPC = util.CURRENT_STATE.PIPE[util.IF_STAGE]

# /***************************************************************/
# /*                                                             */
# /* Procedure: IDecode_Stage                                    */
# /*                                                             */
# /* Purpose: Instruction decode                                 */
# /*                                                             */
# /***************************************************************/
def IDecode_Stage():
    instr = get_inst_info(util.CURRENT_STATE.PIPE[util.ID_STAGE])
    util.CURRENT_STATE.ID_EX_REG1 = RS(instr)
    util.CURRENT_STATE.ID_EX_REG2 = RT(instr)
    util.CURRENT_STATE.ID_EX_IMM = IMM(instr)
    if OPCODE(instr) == 0x0:
        util.CURRENT_STATE.ID_EX_DEST = RD(instr)
    elif OPCODE(instr) == 0x3:
        util.CURRENT_STATE.ID_EX_DEST = 31
    else:
        util.CURRENT_STATE.ID_EX_DEST = RT(instr)

    if OPCODE(instr) == 0x0 and FUNC(instr) == 0x08:
        util.CURRENT_STATE.JUMP_PC = util.CURRENT_STATE.REGS[RS(instr)]
        util.CURRENT_STATE.PC = util.CURRENT_STATE.REGS[RS(instr)]

    if OPCODE(instr) == 0x2:
        # J
        util.CURRENT_STATE.JUMP_PC = instr.target << 2
        util.CURRENT_STATE.PC = instr.target << 2

    if OPCODE(instr) == 0x3:
        # JAL
        util.CURRENT_STATE.JUMP_PC = instr.target << 2
        util.CURRENT_STATE.PC = instr.target << 2

    util.CURRENT_STATE.ID_EX_NPC = util.CURRENT_STATE.PIPE[util.ID_STAGE]



# /***************************************************************/
# /*                                                             */
# /* Procedure: Execute_Stage                                    */
# /*                                                             */
# /* Purpose: Instruction execution                              */
# /*                                                             */
# /***************************************************************/
def Execute_Stage(reg1_val, reg2_val, imm, npc, dest):
    instr = get_inst_info(util.CURRENT_STATE.PIPE[util.EX_STAGE])
    opcode = OPCODE(instr)
    shamt = SHAMT(instr)
    func = FUNC(instr)
    out = 0
    w_val = 1
    rs = reg1_val
    rt = reg2_val
    if opcode == 0xa:
        # SLTI
        if change_to_signed(rs) < change_to_signed(SIGN_EX(imm)):
            out = 1
        else:
            out = 0
    elif opcode == 0x8:
        #ADDI
        out = change_to_signed(rs) + SIGN_EX(imm)
    elif opcode == 0x9:
        #ADDIU
        out = rs + SIGN_EX(imm)
    elif opcode == 0xc:
        #ANDI
        out = rs & (imm & 0x0000ffff)
    elif opcode == 0xf:
        #LUI
        out = imm << 16
    elif opcode == 0xd:
        #ORI
        out = rs | (imm & 0x0000ffff)
    elif opcode == 0xb:
        #SLTIU
        temp_rs = rs
        if temp_rs < 0:
            temp_rs += 2*0x80000000

        temp_imm = imm
        if temp_imm < 0:
            temp_imm += 2*0x8000
            
        if temp_rs < temp_imm:
            out = 1
        else:
            out = 0
    elif opcode == 0x23:
        #LW
        w_val = 0
        out = (rs + SIGN_EX(imm)) & 0xffffffff
    elif opcode == 0x2b:
        #SW
        w_val = 0
        out = (rs + SIGN_EX(imm)) & 0xffffffff
    elif opcode == 0x4:
        #BEQ
        w_val = 0
        util.CURRENT_STATE.EX_MEM_BR_TARGET = util.CURRENT_STATE.PIPE[util.EX_STAGE] + change_to_signed(SIGN_EX(imm))*4 + 4
        if rs == rt:
            util.CURRENT_STATE.EX_MEM_BR_TAKE = 1
            util.CURRENT_STATE.PC = util.CURRENT_STATE.EX_MEM_BR_TARGET
    elif opcode == 0x5:
        #BNE
        w_val = 0
        util.CURRENT_STATE.EX_MEM_BR_TARGET = util.CURRENT_STATE.PIPE[util.EX_STAGE] + change_to_signed(SIGN_EX(imm))*4 + 4
        if rs != rt:
            util.CURRENT_STATE.EX_MEM_BR_TAKE = 1
            util.CURRENT_STATE.PC = util.CURRENT_STATE.EX_MEM_BR_TARGET

    # TYPE R
    # 0x0: (0b000000)ADD, SLT, ADDU, AND, NOR, OR, SLTU, SLL, SRL, SUBU  if JR
    elif opcode == 0x0:
        if func == 0x20:
            #ADD
            out = change_to_signed(rs) + change_to_signed(rt)
        elif func == 0x2a:
            #SLT
            if change_to_signed(rs) < change_to_signed(rt):
                out = 1
            else:
                out = 0
        elif func == 0x21:
            #ADDU
            out = rs + rt
        elif func == 0x24:
            #AND
            out = rs & rt
        elif func == 0x27:
            #NOR
            out = ~( rs | rt )
        elif func == 0x25:
            #OR
            out = rs | rt
        elif func == 0x2b:
            #SLTU
            if rs < rt:
                out = 1
            else:
                out = 0
        elif func == 0x00:
            #SLL
            out = rt << shamt
        elif func == 0x02:
            #SRL
            out = rt >> shamt
            if rt < 0:
                out = out & 0x7fffffff
        elif func == 0x23 or func == 0x22:
            #SUBU #SUB
            out = rs - rt
        elif func == 0x08:
            #JR
            w_val = 0
        else:
            pass

    # TYPE J
    # 0x2: (0b000010)J
    # 0x3: (0b000011)JAL
    elif opcode == 0x2:
        # J
        w_val = 0
    elif opcode == 0x3:
        # JAL
        out =  util.CURRENT_STATE.PIPE[util.EX_STAGE] + 8
    else:
        pass

    util.CURRENT_STATE.EX_MEM_NPC = npc
    util.CURRENT_STATE.EX_MEM_ALU_OUT = out
    util.CURRENT_STATE.EX_MEM_W_VALUE = w_val
    util.CURRENT_STATE.EX_MEM_DEST = dest


# /***************************************************************/
# /*                                                             */
# /* Procedure: Memory_Stage                                     */
# /*                                                             */
# /* Purpose: Memory related execution                           */
# /*                                                             */
# /***************************************************************/
def Memory_Stage(alu_out, dest, npc, br_take):
    instr = get_inst_info(util.CURRENT_STATE.PIPE[util.MEM_STAGE])
    opcode = OPCODE(instr)
    if opcode == 0x23:
        #LW
        util.CURRENT_STATE.MEM_WB_MEM_OUT = util.mem_read(alu_out)
    elif opcode == 0x2b:
        #SW
        util.mem_write(alu_out, dest)

    util.CURRENT_STATE.MEM_WB_ALU_OUT = alu_out
    util.CURRENT_STATE.MEM_WB_NPC = npc
    util.CURRENT_STATE.MEM_WB_BR_TAKE = br_take
    util.CURRENT_STATE.MEM_WB_DEST = dest

# /***************************************************************/
# /*                                                             */
# /* Procedure: WriteBack_Stage                                  */
# /*                                                             */
# /* Purpose: Write back related execution                       */
# /*                                                             */
# /***************************************************************/
def WriteBack_Stage(dest, alu_out, mem_out):
    instr = get_inst_info(util.CURRENT_STATE.PIPE[util.WB_STAGE])
    opcode = OPCODE(instr)

    if opcode == 0x0 or opcode == 0xa or opcode == 0x8 or opcode == 0x9 or opcode == 0xc or opcode == 0xf or opcode == 0xd or opcode == 0xb or opcode == 0x3:
        util.CURRENT_STATE.REGS[dest] = alu_out
    elif opcode == 0x23:
        util.CURRENT_STATE.REGS[dest] = mem_out


# /***************************************************************/
# /*                                                             */
# /* Procedure: Choose_PC                                        */
# /*                                                             */
# /* Purpose: Choose corret PC among 3 candidates                */
# /*                                                             */
# /***************************************************************/
def Choose_PC():
    return_pc = 0
    if util.CURRENT_STATE.PC >= (util.MEM_TEXT_START+initialize.NUM_INST*4) or util.CURRENT_STATE.PC == 0:
        return_pc = None
    else:
        return_pc = util.CURRENT_STATE.PC
    
    # if util.CURRENT_STATE.EX_MEM_BR_TAKE:
    #     util.CURRENT_STATE.EX_MEM_BR_TARGET = 0
    #     util.CURRENT_STATE.EX_MEM_BR_TAKE = 0
    # elif util.CURRENT_STATE.JUMP_PC != 0:
    #     util.CURRENT_STATE.PC = util.CURRENT_STATE.JUMP_PC + 8
    #     util.CURRENT_STATE.JUMP_PC = 0
    # else:
    #     util.CURRENT_STATE.PC += 4

    return return_pc

# /***************************************************************/
# /*                                                             */
# /* Procedure: Flush_By_Jump                                    */
# /*                                                             */
# /* Purpose: Flush IF, ID stage                                 */
# /*                                                             */
# /***************************************************************/
def Flush_By_Jump():
    util.CURRENT_STATE.PIPE[util.IF_STAGE] = None
    util.CURRENT_STATE.PIPE[util.ID_STAGE] = None

    util.CURRENT_STATE.IF_ID_INST = 0
    util.CURRENT_STATE.IF_ID_NPC = 0
    
# /***************************************************************/
# /*                                                             */
# /* Procedure: Flush_By_Branch_EX                               */
# /*                                                             */
# /* Purpose: Flush IF, ID stage                                 */
# /*          and stall IF, ID stage if prediction bit is unset  */
# /*                                                             */
# /***************************************************************/
def Flush_By_Branch_EX():
    pass


# /***************************************************************/
# /*                                                             */
# /* Procedure: Flush_By_Branch_MEM                              */
# /*                                                             */
# /* Purpose: Flush IF, ID, and EX stage                         */
# /*      and stall IF, ID, EX stage if prediction bit is unset  */
# /*                                                             */
# /***************************************************************/
def Flush_By_Branch_MEM():
    pass


# /***************************************************************/
# /*                                                             */
# /* Procedure: Flush_By_Branch                                  */
# /*                                                             */
# /* Purpose: Flush IF, ID, EX, MEM stage                        */
# /*                                                             */
# /***************************************************************/
def Flush_By_Branch():
    util.CURRENT_STATE.PIPE[util.IF_STAGE] = None
    util.CURRENT_STATE.PIPE[util.ID_STAGE] = None
    util.CURRENT_STATE.PIPE[util.EX_STAGE] = None

    util.CURRENT_STATE.IF_ID_INST = 0
    util.CURRENT_STATE.IF_ID_NPC = 0

    util.CURRENT_STATE.ID_EX_NPC = 0
    util.CURRENT_STATE.ID_EX_REG1 = 0
    util.CURRENT_STATE.ID_EX_REG2 = 0
    util.CURRENT_STATE.ID_EX_IMM = ""
    util.CURRENT_STATE.ID_EX_DEST = ""