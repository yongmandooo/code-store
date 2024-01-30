# example1
echo for example1:
python3 main.py -m 0x10000000:0x10000010 -n 50 sample_input/example01.o > sample_input/example01.result
python3 grade.py example01

# example2
echo for example2:
python3 main.py -n 50 sample_input/example02.o > sample_input/example02.result
python3 grade.py example02


