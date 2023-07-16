#include "assignment3.h"

int main (int argc, char *argv[]) {

    int fd;

    if(argc != 2){
        printf("Usage: assignment3 <text file>\n");
        return 0;
    }

    fd = open(argv[1], O_RDONLY|O_SYNC);
    FILE *fp = fdopen(fd, "r");
    int fp_size = sizeof(fp);

    const int max = 256;
    char line[max];
    char* exit_quote = "I'm exiting...\n";

    int init_pipefd[2];
    pipe(init_pipefd);
    int final_pipefd[2];
    pipe(final_pipefd);
    int first_line = 1;
    void* ptr = &first_line;
    write(final_pipefd[WRITE], ptr, max);

    pid_t pid;
    pid = fork();

    if(pid>0){
        handle_pipe(final_pipefd, init_pipefd, fp, line, max, 0);

        wait(NULL);
        printf("%d %s", getpid(), exit_quote);
        exit(0);
    }else if(pid == 0){
        int second_pipefd[2];
        pipe(second_pipefd);

        pid_t pid2 = fork();
        if(pid2 > 0){
            handle_pipe(init_pipefd, second_pipefd, fp, line, max, 0);
            
            wait(NULL);
            printf("%d %s", getpid(), exit_quote);
            exit(0);
        }else if(pid2 == 0){
            int third_pipefd[2];
            pipe(third_pipefd);

            pid_t pid3 = fork();
            if(pid3 > 0){
                handle_pipe(second_pipefd, third_pipefd, fp, line, max, 0);

                wait(NULL);
                printf("%d %s", getpid(), exit_quote);
                exit(0);
            }else if(pid3 == 0){
                int fourth_pipefd[2];
                pipe(fourth_pipefd);

                pid_t pid4 = fork();
                if(pid4 > 0){
                    handle_pipe(third_pipefd, fourth_pipefd, fp, line, max, 0);

                    wait(NULL);
                    printf("%d %s", getpid(), exit_quote);
                    exit(0);
                }else if(pid4 == 0){
                    handle_pipe(fourth_pipefd, final_pipefd, fp, line, max, 1);

                    printf("%d %s", getpid(), exit_quote);
                    exit(0);
                }
            }
        }
    }

    return 0;
}