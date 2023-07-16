#include <stdio.h>
#include "mystdio-skel.h"
#include <sys/wait.h>

int main(){
    // myFILE *myfile;
    // myfile = myfopen("mystd.txt", "r+");
    // if(myfile == NULL){
    //     printf("fail to myfopen\n");
    // }

    FILE *file;
    file = fopen("std.txt", "r+");
     
    pid_t pid = fork();

    if(pid == 0){
        char *wonju = "WONJU\n";

        // for(int i = 0; i < 5; i++){
        //     int write_result = myfwrite(wonju, 6, 1, myfile);
        //     printf("myfwrite-p1: %d\n", write_result);
        // }

        for(int i = 0; i < 5; i++){
            int write_result = fwrite(wonju, 6, 1, file);
            printf("myfwrite-p1: %d\n", write_result);
        }

    } else {
        char *ulsan = "ULSAN\n";

        // for(int i = 0; i< 5; i++){
        //     int write_result = myfwrite(ulsan, 6, 1, myfile);
        //     printf("myfwrite-p2: %d\n", write_result);
        // }

        for(int i = 0; i< 5; i++){
            int write_result = fwrite(ulsan, 6, 1, file);
            printf("myfwrite-p2: %d\n", write_result);
        }

        wait(NULL);
        int close_result = fclose(file);
        printf("close_result-p2: %d\n", close_result);
    }

    return 0;
}