#include "assignment4.h"

int main (){

    char* heap_area = (char *)malloc(sizeof(char) * 64);
    int filled = 0; // index of filled heap area
    mem_table_entry mem_table[64];
    int current_table_index = 0; // number of variables
    
    manage_heap_area(heap_area, filled, mem_table, current_table_index);

    return 0;
}