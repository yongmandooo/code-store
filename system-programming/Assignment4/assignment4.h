#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef struct {
    char name[256];
    int size;
}mem_table_entry;

typedef struct {
    char type[8];
    char data[1024];
}struct_table_entry;

void manage_heap_area(char* heap_area, int filled, mem_table_entry* mem_table, int current_table_index){
    while(1){
        int task_type;
        printf("Do you want to allocate data (1) or deallocate data (2) ?\n");
        fflush(stdin);
        scanf("%d", &task_type);
        int passed = 0;

        if(task_type == 1){

            int max_type = 8;
            int max_name = 256;
            char type[max_type];
            char name[max_name];
            printf("Input the type of data you want to allocate and the name of the data\n");
            scanf("%s %s", type, name);

            int size = 0;
            if(strncmp(type, "short", 5) == 0){
                size = 2;
                if(filled + size <= 64){
                    mem_table_entry new_entry;
                    strcpy(new_entry.name, name);
                    new_entry.size = size;
                    mem_table[current_table_index] = new_entry;
                    current_table_index++;
                    printf("Please input a value for the data type\n");
                    short data;
                    scanf("%hi", &data);
                    void* ptr = &data;
                    char* ptr2 = ptr;
                    for(int i = 0; i < sizeof(short); i++){
                        heap_area[filled + i] = ptr2[i];
                    }
                    filled += size;
                } else {
                    passed = 1;
                    int remain = 64 - filled;
                    printf("There is not enough memory for the data which you require, you can only use %d byte(s)\n", remain);
                }
            } else if(strncmp(type, "char", 4) == 0){
                size = 1;
                if(filled + size <= 64){
                    mem_table_entry new_entry;
                    strcpy(new_entry.name, name);
                    new_entry.size = size;
                    mem_table[current_table_index] = new_entry;
                    current_table_index++;
                    printf("Please input a value for the data type\n");
                    char data;
                    scanf(" %c", &data);
                    heap_area[filled] = data;
                    filled += size;
                } else {
                    passed = 1;
                    int remain = 64 - filled;
                    printf("There is not enough memory for the data which you require, you can only use %d byte(s)\n", remain);
                }
            } else if(strncmp(type, "float", 5) == 0){
                size = 4;
                if(filled + size <= 64){
                    mem_table_entry new_entry;
                    strcpy(new_entry.name, name);
                    new_entry.size = size;
                    mem_table[current_table_index] = new_entry;
                    current_table_index++;
                    printf("Please input a value for the data type\n");
                    float data;
                    scanf("%f", &data);
                    void* ptr = &data;
                    char* ptr2 = ptr;
                    for(int i = 0; i < sizeof(float); i++){
                        heap_area[filled + i] = ptr2[i];
                    }
                    filled += size;
                } else {
                    passed = 1;
                    int remain = 64 - filled;
                    printf("There is not enough memory for the data which you require, you can only use %d byte(s)\n", remain);
                }
            } else if(strncmp(type, "long", 4) == 0){
                size = 8;
                if(filled + size <= 64){
                    mem_table_entry new_entry;
                    strcpy(new_entry.name, name);
                    new_entry.size = size;
                    mem_table[current_table_index] = new_entry;
                    current_table_index++;
                    printf("Please input a value for the data type\n");
                    long data;
                    scanf("%li", &data);
                    void* ptr = &data;
                    char* ptr2 = ptr;
                    for(int i = 0; i < sizeof(long); i++){
                        heap_area[filled + i] = ptr2[i];
                    }
                    filled += size;
                } else {
                    passed = 1;
                    int remain = 64 - filled;
                    printf("There is not enough memory for the data which you require, you can only use %d byte(s)\n", remain);
                }
            } else if(strncmp(type, "struct", 6) == 0){
                unsigned int number_of_data;
                printf("How many data should be in the struct\n");
                scanf("%u", &number_of_data);
                struct_table_entry struct_table[number_of_data];
                printf("Please input each type and its value\n");
                int type_error = 0;
                for(unsigned int i = 0; i < number_of_data; i++){
                    scanf("%s %s", struct_table[i].type, struct_table[i].data);
                    if(strncmp(struct_table[i].type, "short", 5) == 0){
                        size += 2;
                    }else if(strncmp(struct_table[i].type, "char", 4) == 0){
                        size += 1;
                    }else if(strncmp(struct_table[i].type, "float", 5) == 0){
                        size += 4;
                    }else if(strncmp(struct_table[i].type, "long", 4) == 0){
                        size += 8;
                    } else {
                        type_error++;
                    }
                }
                if(filled + size <= 64 && type_error == 0){
                    mem_table_entry new_entry;
                    strcpy(new_entry.name, name);
                    new_entry.size = size;
                    mem_table[current_table_index] = new_entry;
                    current_table_index++;
                    for(unsigned int i = 0; i < number_of_data; i++){
                        if(strncmp(struct_table[i].type, "short", 5) == 0){
                            short data = (short) atoi(struct_table[i].data);
                            void* ptr = &data;
                            char* ptr2 = ptr;
                            for(int i = 0; i < sizeof(short); i++){
                                heap_area[filled + i] = ptr2[i];
                            }
                            filled += 2;
                        }else if(strncmp(struct_table[i].type, "char", 4) == 0){
                            char data = *struct_table[i].data;
                            heap_area[filled] = data;
                            filled += 1;
                        }else if(strncmp(struct_table[i].type, "float", 5) == 0){
                            float data = atof(struct_table[i].data);
                            void* ptr = &data;
                            char* ptr2 = ptr;
                            for(int i = 0; i < sizeof(float); i++){
                                heap_area[filled + i] = ptr2[i];
                            }
                            filled += 4;
                        }else if(strncmp(struct_table[i].type, "long", 4) == 0){
                            long data = atol(struct_table[i].data);
                            void* ptr = &data;
                            char* ptr2 = ptr;
                            for(int i = 0; i < sizeof(long); i++){
                                heap_area[filled + i] = ptr2[i];
                            }
                            filled += 8;
                        }
                    }
                } else if(filled + size > 64 && type_error == 0) {
                    passed = 1;
                    int remain = 64 - filled;
                    printf("There is not enough memory for the data which you require, you can only use %d byte(s)\n", remain);
                }
            } 

        } else if(task_type == 2){
            printf("Input the name of data you want to deallocate\n");
            char target_variable[256];
            scanf("%s", target_variable);
            int target_variable_size = 0;
            int target_variable_offset = 0;
            int target_variable_index = 0;
            int founded = 0;
            for(int i = 0; i < current_table_index; i++){
                if(founded == 0){
                    if(strncmp(mem_table[i].name, target_variable, 256) == 0){
                        target_variable_size = mem_table[i].size;
                        target_variable_index = i;
                        founded = 1;
                    } else {
                        target_variable_offset += mem_table[i].size;
                    }
                }
            }

            if(founded == 1){
                for(int j = 0; j < filled - (target_variable_offset + target_variable_size); j++){
                    heap_area[target_variable_offset + j] = heap_area[target_variable_offset + target_variable_size + j];
                }
                for(int k = 1; k <= target_variable_size; k++){
                    heap_area[filled - k] = 0;
                }
                filled -= target_variable_size;

                for(int l = 0; l < current_table_index - (target_variable_index + 1); l++){
                    mem_table[target_variable_index + l] = mem_table[target_variable_index + 1 + l]; 
                }
                current_table_index--;
            }
        }

        if(passed == 0){
            printf("There is memory dump!\n");
            const char *buffer = heap_area;
            size_t len = 64;
            for(size_t i = 0; i < len; i++){
                if(i > 0 && i%16 == 0) {
                    printf("\n");
                }
                printf("%02x ", buffer[i] & 0xff);
            }
            puts("");
            printf("\n");

            printf("------Data you have now------\n");
            for(int j = 0; j < current_table_index; j++){
                printf("%s\n", mem_table[j].name);
            }
        }
        printf("\n");
    }
}