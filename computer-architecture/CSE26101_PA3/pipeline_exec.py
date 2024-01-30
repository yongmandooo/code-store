import util
import parse
import run
from os import path


def load_program(file_name):
    if not path.exists(file_name):
        print(f"Error: Can't open program file {file_name}\n")
        return -1
    
    with open(file_name, 'r') as fd:
        ii = 0
        buffer = ""
        flag = 0
        global text_size

        while True:
            buffer = fd.read(32)
            if buffer == "":
                break
            
            if flag == 0:
                text_size = util.fromBinary(buffer)
                
                