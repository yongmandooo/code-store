import sys


class inst_t:
    def __init__(self, name, op, type, funct):
        self.name = name
        self.op = op
        self.type = type
        self.funct = funct
    
    
    def compare(self, op):
        
        if self.type == "R":
            if self.op == op[0:6] and self.funct == op[26:]:
                return True
            else:
                return False
        else:
            if self.op == op[0:6]:
                return True
            else:
                return False
        
    
    def error_print(self):
        print(f"{self.name} was not correctly converted")


ADD = inst_t("add", "000000", 'R', "100000")
ADDI = inst_t("addi", "001000", 'I', "")
ADDIU = inst_t("addiu", "001001", "I", "")  # 0
ADDU = inst_t("addu",    "000000", 'R', "100001")  # 1
AND = inst_t("and",     "000000", 'R', "100100")
ANDI = inst_t("andi",    "001100", 'I', "")
BEQ = inst_t("beq",     "000100", 'I', "")
BNE = inst_t("bne",     "000101", 'I', "")
J = inst_t("j",       "000010", 'J', "")
JAL = inst_t("jal",     "000011", 'J', "")
JR = inst_t("jr",      "000000", 'R', "001000")
LUI = inst_t("lui",     "001111", 'I', "")
LW = inst_t("lw",      "100011", 'I', "")
NOR = inst_t("nor",     "000000", 'R', "100111")
OR = inst_t("or",      "000000", 'R', "100101")
ORI = inst_t("ori",     "001101", 'I', "")
SLT = inst_t("slt", "000000", 'R', "101010")
SLTI = inst_t("slti", "001010", 'I', "")
SLTIU = inst_t("sltiu",    "001011", 'I', "")
SLTU = inst_t("sltu",    "000000", 'R', "101011")
SLL = inst_t("sll",     "000000", 'R', "000000")
SRL = inst_t("srl",     "000000", 'R', "000010")
SW = inst_t("sw",      "101011", 'I', "")
SUB = inst_t("sub", "000000", 'R', "100010")
SUBU = inst_t("subu",    "000000", 'R', "100011")

inst_list = [ADD,  ADDI, ADDIU, ADDU, AND,
             ANDI, BEQ,  BNE,   J,    JAL, 
             JR,   LUI,   LW,   NOR,
             OR,   ORI,  SLT,   SLTI, SLTIU,  
             SLTU, SLL,  SRL,   SW, 
             SUB,  SUBU, ]

block_indicator_str = "Current register values"

current_inst = ""
inst_ind = 0

if __name__ == "__main__":
       
    argc = len(sys.argv)

    if argc != 2:
        print("The nuber of argv is not 2")
        exit(1)
    
    file_name = sys.argv[1] 
    f_in = "./sample_input/" + file_name + ".result"
    f_out = "./sample_output/" + file_name + ".out"
    f_inst_out = "./sample_output/" + file_name + ".inst"
    failure = False


    with open(f_in, 'r') as fd_in:
        with open(f_out, 'r') as fd_out:
            with open(f_inst_out, 'r') as fd_inst:

                student = fd_in.readlines()
                ans = fd_out.readlines()
                inst_lines = fd_inst.readlines()

                           
                if len(student) == 0:
                    print("your file is empty")
                    failure = True
                elif len(student) != len(ans):
                    print("your line of code is less(or more) than answer.")
                    failure = True        
                else:
                    for i in range(len(ans)):
                        if ans[i][:len(block_indicator_str)] == block_indicator_str:
                            current_inst = inst_lines[inst_ind]
                            inst_ind += 1

                        if student[i] != ans[i]:
                            if inst_ind == 0:
                                print("logs before the cycles is not correct")
                            else:
                                print("state after executing instruction with " + current_inst[:-1] + " is not correct")

                            failure = True
                            break
                            
                if failure:
                    print("NON-PASS")
                else:
                    print("PASS")
