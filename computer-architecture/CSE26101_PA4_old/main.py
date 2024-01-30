'''
MIPS-32 Instruction Level Simulatr

CSE261 UNIST
main.py

Do NOT MODIFY THIS FILE
You should only modify the parse.py and run.py files!
'''

import sys
import memory_system

argc = len(sys.argv)

f = open(sys.argv[argc-1], 'r')

mem = memory_system.Memory.get_instance()

for line in f:
    temp = line.split()
    try:
        if temp[0] == "print":
            mem.dump()
        elif len(temp) == 2:
            mem.write(int(temp[0]), int(temp[1]))
        else:
            mem.read(int(temp[0]))
    except:
        continue

print("Simulator halted\n")
mem.dump()

f.close()
