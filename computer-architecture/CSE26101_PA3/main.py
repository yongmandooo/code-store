'''
MIPS-32 Instruction Level Simulatr

CSE261 UNIST
main.py

Do NOT MODIFY THIS FILE
You should only modify the parse.py and run.py files!
'''

import initialize
import util
import sys
import parse
count = 1
addr1 = 0
addr2 = 0
num_inst = 0
i = 100  # for loop

mem_dump_set = 0
num_inst_set = 0
pipe_dump_set = 0
register_dump_set = 0

argc = len(sys.argv)

# Error Checking
if argc < 2:
    print("Error: usage: ",
          sys.argv[0], " [-m addr1:addr2] [-d] [-n num_instr] inputBinary")
    exit(1)

mips = initialize.MIPS(sys.argv[argc-1])

# Create a .inst file in write mode
util.inst_file = open(sys.argv[argc-1][:-1] + "inst", "w")

# for checking parse result
# parse.print_parse_result(initialize.INST_INFO)

while count != argc - 1:
    if (sys.argv[count] == '-m'):
        count += 1
        tokens = sys.argv[count].split(':')
        addr1 = int(tokens[0], 16)
        addr2 = int(tokens[1], 16)
        mem_dump_set = 1
    elif (sys.argv[count] == '-n'):
        count += 1
        num_inst = int(sys.argv[count], 10)
        num_inst_set = 1
    elif (sys.argv[count] == '-d'):
        register_dump_set = 1
    elif (sys.argv[count] == '-p'):
        pipe_dump_set = 1
    else:
        print("Error: usage: ",
              sys.argv[0], "[-m addr1:addr2][-d][-n num_instr] inputBinary")
        exit(1)
    count += 1


if num_inst_set:
    util.MAX_INSTRUCTION_NUM = num_inst
else:
    util.MAX_INSTRUCTION_NUM = 100 

if num_inst_set and num_inst <= 0:
    print("Error: The number of instructions should be positive integer\n")
    exit()


# Pipeline
if pipe_dump_set:
    print("Simulating for %lu instructions...\n" % util.MAX_INSTRUCTION_NUM)
    
    while util.RUN_BIT:
        util.cycle()
        util.pdump()

        if register_dump_set:
            util.rdump()
        if mem_dump_set:
            util.mdump(addr1, addr2)

    print("Simulator halted after %lu cycles\n\n" % util.CYCLE_COUNT)

else:
    util.run()
    util.rdump()

    if mem_dump_set:
        util.mdump(addr1, addr2)

exit()


# No Pipeline
# print("Simulating for %d cycles...\n" % i)
# while i > 0:
#     if util.RUN_BIT == False:
#             print("Simulator halted\n")
#             break
#     util.cycle()
#     util.rdump()

#     if mem_dump_set:
#         util.mdump(addr1, addr2)
#     i -= 1
