import sys
import os
from enum import Enum
from tempfile import TemporaryFile
import re
import ctypes

################################################
# For debug option. If you want to debug, set 1
# If not, set 0.
################################################

DEBUG = 0

MAX_SYMBOL_TABLE_SIZE = 1024
MEM_TEXT_START = 0x00400000
MEM_DATA_START = 0x10000000
BYTES_PER_WORD = 4

################################################
# Additional Components
################################################

class bcolors:
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'


start = '[' + bcolors.BLUE + 'START' + bcolors.ENDC + ']  '
done = '[' + bcolors.YELLOW + 'DONE' + bcolors.ENDC + ']   '
success = '[' + bcolors.GREEN + 'SUCCESS' + bcolors.ENDC + ']'
error = '[' + bcolors.RED + 'ERROR' + bcolors.ENDC + ']  '

pType = [start, done, success, error]


def log(printType, content):
    print(pType[printType] + content)


################################################
# Structure Declaration
################################################

class inst_t:
    def __init__(self, name, op, type, funct):
        self.name = name
        self.op = op
        self.type = type
        self.funct = funct


class symbol_t:
    def __init__(self):
        self.name = 0
        self.address = 0


class la_struct:
    def __init__(self, op, rt, imm):
        self.op = op
        self.rt = rt
        self.imm = imm

class section(Enum):
    DATA = 0
    TEXT = 1
    MAX_SIZE = 2


################################################
# Global Variable Declaration
################################################

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

symbol_struct = symbol_t()
SYMBOL_TABLE = [symbol_struct] * MAX_SYMBOL_TABLE_SIZE

symbol_table_cur_index = 0

data_section_size = 0
text_section_size = 0


################################################
# Function Declaration
################################################

def change_file_ext(fin_name):
    fname_list = fin_name.split('.')
    fname_list[-1] = 'o'
    fout_name = ('.').join(fname_list)
    return fout_name


def symbol_table_add_entry(symbol):
    global SYMBOL_TABLE
    global symbol_table_cur_index

    SYMBOL_TABLE[symbol_table_cur_index] = symbol
    symbol_table_cur_index += 1
    if DEBUG:
        log(1, f"{symbol.name}: 0x" + hex(symbol.address)[2:].zfill(8))


def convert_label(label):
    address = 0
    for i in range(symbol_table_cur_index):
        if label == SYMBOL_TABLE[i].name:
            address = SYMBOL_TABLE[i].address
            break
    return address


def num_to_bits(num, len):
    bit = bin(num & (2**len-1))[2:].zfill(len)
    return bit

#################################################
# # # # # # # # # # # # # # # # # # # # # # # # #
#                                               #
# Please Do not change the above if possible    #
# The TA's are not resposinble for failures     #
# due to changes in the above                   #
#                                               #
# # # # # # # # # # # # # # # # # # # # # # # # #
#################################################

def extract_register_num(reg_str):
    if reg_str.startswith('$'):
        reg_num_ten = int(reg_str[1:])
        reg_num_bin = num_to_bits(reg_num_ten, 5)
        return reg_num_bin
    else:
        print(reg_str)
        return num_to_bits(convert_int_or_hex(reg_str), 5)

def convert_int_or_hex(num_str):
    if num_str[:2] == "0x":
        return int(num_str, 16)
    else :
        return int(num_str)

def make_symbol_table(input):
    size_bit = 0
    address = 0

    cur_section = section.MAX_SIZE.value

    # Read .data section
    lines = input.readlines()
    while len(lines) > 0:
        line = lines.pop(0)
        line = line.strip()
        _line = line
        token_line = _line.strip('\n\t').split()
        temp = token_line[0]

        if temp == ".data":
            '''
            blank
            '''
            cur_section = section.DATA.value
            global data_seg
            data_seg = TemporaryFile('w+')
            continue

        if temp == '.text':
            '''
            blank
            '''
            cur_section = section.TEXT.value
            global text_seg
            text_seg = TemporaryFile('w+')
            continue

        if cur_section == section.DATA.value:
            global data_section_size 
            '''
            blank
            '''
            if temp[-1] == ':':
                symbol = symbol_t()
                symbol.name = temp[:-1]
                symbol.address = ctypes.c_uint(0x10000000 + data_section_size).value
                symbol_table_add_entry(symbol)

            word = line.find(".word")

            if word != -1:
                data_seg.write("%s\n" % line[word:])

            data_section_size += 4

        elif cur_section == section.TEXT.value:
            global text_section_size 
            '''
            blank
            '''
            if temp[-1] == ":":
                symbol = symbol_t()
                symbol.name = temp[:-1]
                symbol.address = ctypes.c_uint(0x00400000 + text_section_size).value
                symbol_table_add_entry(symbol)
                continue

            label = line.find(":")
            if label < 0:
                parsed_line = line.strip().replace(',', '').split()
                line_op = parsed_line[0]
                if line_op == "la":
                    addr = ""
                    for symbol in SYMBOL_TABLE:
                        if symbol.name == parsed_line[2]:
                            addr = format(symbol.address, "08x")
                    
                    line = "lui" + " " + parsed_line[1] + ", " + "0x" + addr[:4]
                    text_section_size += 4
                    text_seg.write("%s\n" % line)
                    if addr[4:] != "0000":
                        line = "ori" + " " + parsed_line[1] + ", " + parsed_line[1] + ", " + "0x" + addr[4:]
                        text_section_size += 4
                        text_seg.write("%s\n" % line)
                elif line_op == "move":
                    line = "addi" + " " + parsed_line[1] + ", " + parsed_line[2] + ", " + "0"
                    text_section_size += 4
                    text_seg.write("%s\n" % line)
                elif line_op == "blt":
                    line = "slt" + " " + "$1" + ", " + parsed_line[1] + ", " + parsed_line[2]
                    text_section_size += 4
                    text_seg.write("%s\n" % line)
                    line = "bne" + " " + "$1" + ", " + "0" + ", " + parsed_line[3]
                    text_section_size += 4
                    text_seg.write("%s\n" % line)
                elif line_op == "push":
                    line = "addi" + " " + "$29" + ", " + "$29" + ", " + "-4"
                    text_section_size += 4
                    text_seg.write("%s\n" % line)
                    line = "sw" + " " + parsed_line[1] + " " + "0($29)"
                    text_section_size += 4
                    text_seg.write("%s\n" % line)
                elif line_op == "pop":
                    line = "lw" + " " + parsed_line[1] + " " + "0($29)"
                    text_section_size += 4
                    text_seg.write("%s\n" % line)
                    line = "addi" + " " + "$29" + ", " + "$29" + ", " + "4"
                    text_section_size += 4
                    text_seg.write("%s\n" % line)
                else:
                    text_section_size += 4
                    text_seg.write("%s\n" % line)
            
        address += BYTES_PER_WORD

def record_text_section(fout):
    # print text section
    cur_addr = MEM_TEXT_START
    text_seg.seek(0)

    lines = text_seg.readlines()
    for line in lines:
        line = line.strip()
        inst_type, rs, rt, rd, imm, shamt = '0', num_to_bits(0, 5), num_to_bits(0, 5), num_to_bits(0, 5), num_to_bits(0, 16), num_to_bits(0, 5)

        result_bin = ""
        line = line.replace(',', '').split()
        inst_obj = eval(line[0].upper())
        inst_type = inst_obj.type
        name = inst_obj.name
        '''
        blank: Find the instruction type that matches the line
        '''
        if inst_type == 'R':
            if name == "jr":
                rs = extract_register_num(line[1])
            elif name == "sll" or name =="srl":
                rd = extract_register_num(line[1])
                rt = extract_register_num(line[2])
                shamt = num_to_bits(convert_int_or_hex(line[3]), 5)
            else:
                rd = extract_register_num(line[1])
                rs = extract_register_num(line[2])
                rt = extract_register_num(line[3])

            result_bin = inst_obj.op + str(rs) + str(rt) + str(rd) + str(shamt) + inst_obj.funct
            '''
            blank
            '''
            if DEBUG:
                log(1, f"0x" + hex(cur_addr)[2:].zfill(
                    8) + f": op: {inst_obj.op} rs:${rs} rt:${rt} rd:${rd} shamt:{shamt} funct:{inst_obj.funct}")

        if inst_type == 'I':        
            if name == "beq" or name == "bne" :
                rt = extract_register_num(line[2])
                rs = extract_register_num(line[1])
                for symbol in SYMBOL_TABLE:
                    if symbol.name == line[3]:
                        imm = num_to_bits((symbol.address-(cur_addr + 4))//4, 16)
            elif name == "lw" or name == "sw":
                #base register
                rt = extract_register_num(line[1])
                target = line[2]
                paren_start_idx = target.find('(')
                paren_end_idx = target.find(")")
                rs = extract_register_num(target[paren_start_idx + 1: paren_end_idx])
                imm = num_to_bits(convert_int_or_hex(target[:paren_start_idx]), 16)
            elif name == "lui":
                rt = extract_register_num(line[1])
                imm = num_to_bits(convert_int_or_hex(line[2]), 16)
            else:
                rt = extract_register_num(line[1])
                rs = extract_register_num(line[2])
                imm = num_to_bits(convert_int_or_hex(line[3]), 16)

            result_bin = inst_obj.op + str(rs) + str(rt) + str(imm)
            '''
            blank
            '''
            if DEBUG:
                log(1, f"0x" + hex(cur_addr)
                    [2:].zfill(8) + f": op:{inst_obj.op} rs:${rs} rt:${rt} imm:0x{imm}")

        if inst_type == 'J':
            addr = 0
            for symbol in SYMBOL_TABLE:
                if symbol.name == line[1]:
                    addr = format(symbol.address, "032b")
            addr = addr[4:30]

            result_bin = inst_obj.op + addr
            '''
            blank
            '''
            if DEBUG:
                log(1, f"0x" + hex(cur_addr)
                    [2:].zfill(8) + f" op:{inst_obj.op} addr:{addr}")

        fout.write(f"{result_bin}")
        cur_addr += BYTES_PER_WORD


def record_data_section(fout):
    cur_addr = MEM_DATA_START
    data_seg.seek(0)

    lines = data_seg.readlines()
    
    for line in lines:
        '''
        blank
        '''
        line = line.strip()
        token_line = line.strip('\n\t').split()
        data = token_line[-1]
        data = int(data, 0)
        fout.write("%s" % num_to_bits(data, 32))

        if DEBUG:
            log(1, f"0x" + hex(cur_addr)[2:].zfill(8) + f": {line}")

        cur_addr += BYTES_PER_WORD


def make_binary_file(fout):
    if DEBUG:
        # print assembly code of text section
        text_seg.seek(0)
        lines = text_seg.readlines()
        for line in lines:
            line = line.strip()

    if DEBUG:
        log(1,
            f"text size: {text_section_size}, data size: {data_section_size}")

    print(f"data section size: {data_section_size}")
    print(f"text section size: {text_section_size}")
    '''
    blank: Print text section size and data section size
    '''
    fout.write("%s" % num_to_bits(int(text_section_size),32))
    fout.write("%s" % num_to_bits(int(data_section_size),32))

    record_text_section(fout)
    record_data_section(fout)

#################################################
# # # # # # # # # # # # # # # # # # # # # # # # #
#                                               #
# Please Do not change the below if possible    #
# The TA's are not resposinble for failures     #
# due to changes in the below code.             #
#                                               #
# # # # # # # # # # # # # # # # # # # # # # # # #
#################################################

################################################
# Function: main
#
# Parameters:
#   argc: the number of argument
#   argv[]: the array of a string argument
#
# Return:
#   return success exit value
#
# Info:
#   The typical main function in Python language.
#   It reads system arguments from terminal (or commands)
#   and parse an assembly file(*.s)
#   Then, it converts a certain instruction into
#   object code which is basically binary code
################################################


if __name__ == '__main__':
    argc = len(sys.argv)
    log(1, f"Arguments count: {argc}")

    if argc != 2:
        log(3, f"Usage   : {sys.argv[0]} <*.s>")
        log(3, f"Example : {sys.argv[0]} sample_input/example.s")
        exit(1)

    input_filename = sys.argv[1]
    input_filePath = os.path.join(os.curdir, input_filename)

    if os.path.exists(input_filePath) == False:
        log(3,
            f"No input file {input_filename} exists. Please check the file name and path.")
        exit(1)

    f_in = open(input_filePath, 'r')

    if f_in == None:
        log(3,
            f"Input file {input_filename} is not opened. Please check the file")
        exit(1)

    output_filename = change_file_ext(sys.argv[1])
    output_filePath = os.path.join(os.curdir, output_filename)

    if os.path.exists(output_filePath) == True:
        log(0, f"Output file {output_filename} exists. Remake the file")
        os.remove(output_filePath)
    else:
        log(0, f"Output file {output_filename} does not exist. Make the file")

    f_out = open(output_filePath, 'w')
    if f_out == None:
        log(3,
            f"Output file {output_filename} is not opened. Please check the file")
        exit(1)

    ################################################
    # Let's compelte the below functions!
    #
    #   make_symbol_table(input)
    #   make_binary_file(output)
    ################################################

    make_symbol_table(f_in)

    # print("\nsymbol table")
    # for symbol in SYMBOL_TABLE:
    #     if symbol.name != 0:
    #         print("name: %s," % symbol.name, "address:", "%s" % format(symbol.address, "08x").strip())
    # print("\n")

    # data_seg.seek(0)
    # print("\ndata segment")
    # data_seg_lines = data_seg.readlines()
    # for data_seg_line in data_seg_lines:
    #     print(data_seg_line[:-1])
    # print("\n")

    # text_seg.seek(0)
    # print("\ntext segment")
    # text_seg_lines = text_seg.readlines()
    # for text_seg_line in text_seg_lines:
    #     print(text_seg_line[:-1])
    # print("\n")

    make_binary_file(f_out)

    f_in.close()
    f_out.close()
