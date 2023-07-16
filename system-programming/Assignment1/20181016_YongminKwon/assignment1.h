#include <stdio.h>
#include <math.h>

int get_len(FILE* fs) {
	int len = 0;
	if (fs != NULL) {
		char result;
		int is_end = 0;
		while (is_end == 0) {
			result = fgetc(fs);
			if (result == -1) {
				is_end = 1;
			}
			else {
				len++;
			}
		}
		rewind(fs);
	}
	return len;
}

void set_buffer(char* buffer, int len, FILE* fs) {
	if (fs != NULL && buffer != NULL) {
		fgets(buffer, len, fs);
	}
}

void signed_character(char* buffer, int len, FILE* file) {

	fprintf(file, "Signed Char: ");

	int decimal = 0;
	int counter = 7;

	for (int i = 0; i <= len-2; i++) {

		if (buffer[i] == '1') {
			if (counter == 7) {
				decimal -= 1 << (counter);
			}
			else {
				decimal += 1 << (counter);
			}
		}

		if (counter == 0 || (counter != 0 && i == len - 2)) {
			fprintf(file, "%d ", decimal);
			decimal = 0;
			counter = 7;
		}
		else {
			counter--;
		}
	}

	fprintf(file, "\n");
}

void character(char* buffer, int len, FILE* file) {

	fprintf(file, "ASCII Codes: ");

	int decimal = 0;
	int counter = 7;

	for (int i = 0; i <= len - 2; i++) {

		if (buffer[i] == '1') {
			if (counter == 7) {
				decimal -= 1 << (counter);
			}
			else {
				decimal += 1 << (counter);
			}
		}

		if (counter == 0 || ( counter != 0 && i == len - 2 )) {
			if (decimal >= 32 && decimal <= 126) {
				fprintf(file, "%c ", decimal);
			}
			else {
				fprintf(file, ". ");
			}
			decimal = 0;
			counter = 7;
		}
		else {
			counter--;
		}
	}

	fprintf(file, "\n");
}

void unsigned_character(char* buffer, int len, FILE* file) {

	fprintf(file, "Unsigned Char: ");

	int decimal = 0;
	int counter = 7;

	for (int i = 0; i <= len - 2; i++) {

		if (buffer[i] == '1') {
			decimal += 1 << counter;
		}

		if (counter == 0 || (counter != 0 && i == len - 2)) {
			fprintf(file, "%d ", decimal);
			decimal = 0;
			counter = 7;
		}
		else {
			counter--;
		}
	}

	fprintf(file, "\n");
}

void signed_integer(char* buffer, int len, FILE* file) {

	fprintf(file, "Signed Int: ");

	int decimal = 0;
	int counter = 31;

	for (int i = 0; i <= len - 2; i++) {

		if (buffer[i] == '1') {
			if (counter == 31) {
				decimal -= 1 << (counter);
			}
			else {
				decimal += 1 << (counter);
			}
		}

		if (counter == 0 || (counter != 0 && i == len - 2)) {
			fprintf(file, "%d ", decimal);
			decimal = 0;
			counter = 31;
		}
		else {
			counter--;
		}
	}

	fprintf(file, "\n");
}

void unsigned_integer(char* buffer, int len, FILE* file) {

	fprintf(file, "Unsigned Int: ");

	unsigned int decimal = 0;
	int counter = 31;

	for (int i = 0; i <= len - 2; i++) {

		if (buffer[i] == '1') {
			decimal += 1 << (counter);
		}

		if (counter == 0 || i == len - 2) {
			fprintf(file, "%u ", decimal);
			decimal = 0;
			counter = 31;
		}
		else {
			counter--;
		}
	}

	fprintf(file, "\n");
}

typedef struct{
	char sign_bit;
	char exponent_bit[9];
	char mantissa_bit[24];
}float_num;

float float_num_calculator(float_num fnum) {

	int base_num = 1;

	//calculate exponent
	float exponent = 0;
	int temp_e = 0;
	for (int i = 7; i >= 0; i--) {
		if (fnum.exponent_bit[i] == '1') {
			temp_e += 1 << (7 - i);
		}
	}
	temp_e -= 127;
	if (temp_e == 0) {
		exponent = 1;
	}
	else if (temp_e == -127) {
		exponent = pow(2.0, -126);
		base_num = 0;
	}
	else {
		exponent = pow(2.0, temp_e);
	}

	//calculate mantissa
	float mantissa = 0;
	for (int j = 1; j <= 23; j++) {
		if (fnum.mantissa_bit[j-1] == '1') {
			float temp_m = 1 << j;
			mantissa += (1 / temp_m);
		}
	}

	float result = (base_num + mantissa) * exponent;
	if (fnum.sign_bit == '1' && result != 0) {
		result = result * (-1);
	}

	return result;
}

void float_number(char* buffer, int len, FILE* file) {
	float_num temp_f = { '0', "00000000", "00000000000000000000000" };
	int counter = 32;

	fprintf(file, "Signed Float: ");

	for (int i = 0; i <= len - 2; i++) {
		if (counter == 32) {
			if (buffer[i] == '1') {
				temp_f.sign_bit = '1';
			}
		}
		else if (counter > 23 && counter <= 31) {
			if (buffer[i] == '1') {
				temp_f.exponent_bit[31 - counter] = '1';
			}
		}
		else {
			if (buffer[i] == '1') {
				temp_f.mantissa_bit[23 - counter] = '1';
			}
		}
		
		if (counter == 1 || (counter != 1 && i == len - 2)) {

			float f1 = float_num_calculator(temp_f);
			fprintf(file, "%.4f ", f1);

			float_num temp_f2 = { '0', "00000000", "00000000000000000000000" };
			temp_f = temp_f2;
			counter = 32;
		}
		else {
			counter--;
		}
	}
	fprintf(file, "\n");
}

typedef struct {
	char sign_bit;
	char exponent_bit[12];
	char mantissa_bit[53];
}double_num;

double double_num_calculator(double_num dnum) {

	int base_num = 1;

	//calculate exponent
	double exponent = 0;
	int temp_e = 0;
	for (int i = 10; i >= 0; i--) {
		if (dnum.exponent_bit[i] == '1') {
			temp_e += 1 << (10 - i);
		}
	}
	temp_e -= 1023;
	if (temp_e == 0) {
		exponent = 1;
	}
	else if (temp_e == -1023) {
		exponent = pow(2.0, -1022);
		base_num = 0;
	}
	else {
		exponent = pow(2.0, temp_e);
	}

	//calculate mantissa
	double mantissa = 0;
	for (int j = 1; j <= 52; j++) {
		if (dnum.mantissa_bit[j - 1] == '1') {
			mantissa += pow(2.0, j*(-1));
		}
	}

	double result = (base_num + mantissa) * exponent;
	if (dnum.sign_bit == '1' && result != 0) {
		result = result * (-1);
	}

	return result;
}

void double_number(char* buffer, int len, FILE* file) {
	double_num temp_d = { '0', "00000000000", "0000000000000000000000000000000000000000000000000000" };
	int counter = 64;

	fprintf(file, "Signed Double: ");

	for (int i = 0; i <= len - 2; i++) {
		if (counter == 64) {
			if (buffer[i] == '1') {
				temp_d.sign_bit = '1';
			}
		}
		else if (counter > 52 && counter <= 63) {
			if (buffer[i] == '1') {
				temp_d.exponent_bit[63 - counter] = '1';
			}
		}
		else {
			if (buffer[i] == '1') {
				temp_d.mantissa_bit[52 - counter] = '1';
			}
		}

		if (counter == 1 || (counter != 1 && i == len-2)) {

			double d1 = double_num_calculator(temp_d);
			fprintf(file, "%.4f ", d1);

			double_num temp_d2 = { '0', "00000000000", "0000000000000000000000000000000000000000000000000000" };
			temp_d = temp_d2;
			counter = 64;
		}
		else {
			counter--;
		}
	}
	fprintf(file, "\n");
}
