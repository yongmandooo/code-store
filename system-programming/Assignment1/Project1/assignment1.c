#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include "assignment1.h"

int main() {
	FILE* input;
	input = fopen("input.txt", "r");

	FILE* output;
	output = fopen("output.txt", "w");
	
	int len = get_len(input);

	char* buffer = malloc(sizeof(char) * (len));
	set_buffer(buffer, len, input);

	signed_character(buffer, len, output);
	character(buffer, len, output);
	unsigned_character(buffer, len, output);
	signed_integer(buffer, len, output);
	unsigned_integer(buffer, len, output);
	float_number(buffer, len, output);
	double_number(buffer, len, output);

	free(buffer);

	if (input != NULL) {	
		fclose(input);
	}

	if (output != NULL) {
		fclose(output);
	}

	//float_num f1 = { '0', "00000000", "00000000000000000000000" };
	//float a = float_num_calculator(f1);
	//float_num f2 = { '0', "10000010", "00110110000000000000000" };
	//float b = float_num_calculator(f2);
	//printf("%lf %lf", a, b);

	//double_num d1 = { '0', "00000000000", "0000000000000000000000000000000000000000000000000000" };
	//printf("d1 source is %c %s %s", d1.sign_bit, d1.exponent_bit, d1.mantissa_bit);
	//double c = double_num_calculator(d1);
	//double_num d2 = { '0', "00000000000", "0000000000000000000000000000000000000000000000000001" };
	//double d = double_num_calculator(d2);
	//printf("%e %e", c, d);

	return 0;
}