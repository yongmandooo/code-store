#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <sys/wait.h>
#define READ 0
#define WRITE 1

void handle_pipe(int* read_pipe, int* write_pipe, FILE* current_fp, char* buffer, int bf_size, int is_last_child){
    char* final_quote = "Read all data\n";
    char* exit_quote = "exit\n";
    close(read_pipe[WRITE]);
    close(write_pipe[READ]);

    while(1){
        read(read_pipe[READ], buffer, bf_size);
        int iteration = *(int*)(buffer);
        if(strncmp(buffer, final_quote, strlen(final_quote)) == 0){
            if(is_last_child == 1){
                write(write_pipe[WRITE], exit_quote, bf_size);
            }else{
                write(write_pipe[WRITE], final_quote, bf_size);
            }
        }else if (strncmp(buffer, exit_quote, strlen(exit_quote)) == 0){
            write(write_pipe[WRITE], exit_quote, bf_size);
            break;
        }else{
            memset(buffer, 0, bf_size);
            rewind(current_fp);
            for(int i = 0; i < iteration; i++){
                fgets(buffer, bf_size, current_fp);
            }
            printf("%d %s", getpid(), buffer);
            char* result = fgets(buffer, bf_size, current_fp);
            if(result != NULL){
                int next_iteration = iteration + 1;
                void* ptr = &next_iteration;
                write(write_pipe[WRITE], ptr, bf_size);
            }else{
                printf("%d %s", getpid(), final_quote);
                write(write_pipe[WRITE], final_quote, bf_size);
            }
        }
    }
}