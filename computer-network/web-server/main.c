#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <pthread.h>
#include <fcntl.h>
#include <sys/stat.h>

#define MAX_CLIENTS 100

char web_dir[255];

void *serverside_request_handler(void* client);

int main(int argc, char **argv) {
    char* server = argv[1];
    int port_num = atoi(argv[2]);
    char* object_directory_path = argv[3];
    strncpy(web_dir, object_directory_path, strlen(object_directory_path));

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket() failed");
        abort();
    }

    struct sockaddr_in sin;
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = INADDR_ANY;
    sin.sin_port = htons(port_num);

    if (bind(sock, (struct sockaddr *)&sin, sizeof(sin)) < 0) {
        perror("bind failed");
        abort();
    }

    // port reusing
    int optval = 1;
    if(setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval)) < 0){
        perror("reuse failed");
        abort();
    }

    int back_log = 4;
    if(listen(sock, back_log) < 0) {
        perror("listen failed");
        abort();
    }

    printf("server is turned on\n");

    struct sockaddr_in client_sin;
    socklen_t addr_len = sizeof(client_sin);

    fd_set read_fds;
    int max_fd;
    int client_socks[MAX_CLIENTS];
    memset(client_socks, 0, sizeof(client_socks));
    // I/O multiplexing with select function
    while (1) {
        FD_ZERO(&read_fds);
        FD_SET(sock, &read_fds);
        max_fd = sock;

        for (int i = 0; i < MAX_CLIENTS; ++i) {
            int client_sock = client_socks[i];
            if (client_sock > 0) {
                FD_SET(client_sock, &read_fds);
                if (client_sock > max_fd) {
                    max_fd = client_sock;
                }
            }
        }

        if (select(max_fd + 1, &read_fds, NULL, NULL, NULL) < 0) {
            perror("select 실패");
            abort();
        }

        if (FD_ISSET(sock, &read_fds)) {
            int client_sock = accept(sock, (struct sockaddr *)&client_sin, &addr_len);
            if (client_sock < 0) {
                perror("accept 실패");
                abort();
            }

            for (int i = 0; i < MAX_CLIENTS; ++i) {
                if (client_socks[i] == 0) {
                    client_socks[i] = client_sock;
                    break;
                }
            }
        }

        for (int i = 0; i < MAX_CLIENTS; ++i) {
            int client_sock = client_socks[i];
            if (client_sock > 0 && FD_ISSET(client_sock, &read_fds)) {
                serverside_request_handler(&client_sock);
                close(client_sock);
                client_socks[i] = 0;
            }
        }
    }

    // I/O multiplexing with multi-threading
    // pthread_t thread_id[MAX_CLIENTS];

    // while (1) {
    //     FD_ZERO(&read_fds);
    //     FD_SET(sock, &read_fds);
    //     max_fd = sock;

    //     for (int i = 0; i < MAX_CLIENTS; ++i) {
    //         int client_sock = client_socks[i];
    //         if (client_sock > 0) {
    //             FD_SET(client_sock, &read_fds);
    //             if (client_sock > max_fd) {
    //                 max_fd = client_sock;
    //             }
    //         }
    //     }

    //     if (select(max_fd + 1, &read_fds, NULL, NULL, NULL) < 0) {
    //         perror("select 실패");
    //         abort();
    //     }

    //     if (FD_ISSET(sock, &read_fds)) {
    //         int client_sock = accept(sock, (struct sockaddr *)&client_sin, &addr_len);
    //         if (client_sock < 0) {
    //             perror("accept 실패");
    //             abort();
    //         }

    //         for (int i = 0; i < MAX_CLIENTS; ++i) {
    //             if (client_socks[i] == 0) {
    //                 client_socks[i] = client_sock;
    //                 break;
    //             }
    //         }
    //     }

    //     for (int i = 0; i < MAX_CLIENTS; ++i) {
    //         int client_sock = client_socks[i];
    //         if (client_sock > 0 && FD_ISSET(client_sock, &read_fds)) {
    //             int *client_sock_ptr = malloc(sizeof(int));
    //             *client_sock_ptr = client_sock;

    //             pthread_create(&thread_id[i], NULL, serverside_request_handler, client_sock_ptr);
    //             client_socks[i] = 0;
    //         }
    //     }
    // }

    // close(sock);

    return 0;
}

void *serverside_request_handler(void* client) {
    int client_sock_descriptor = *(int *)client;
    int datalen;
    char buffer[1024];
    datalen = recv(client_sock_descriptor, buffer, 1024, 0);
    if (datalen < 0) {
        perror("read failed");
        close(client_sock_descriptor);
        return NULL;
    }

    printf("request received:\n%s\n", buffer);

    // extract method
    char req_m[10];
    char req_file_path[255];
    sscanf(buffer, "%s %s", req_m, req_file_path);

    //extract file path
    char file_location[255];
    sprintf(file_location, "%s%s", web_dir, req_file_path);

    int file = open(file_location, O_RDONLY);

    char* res;
    if(strstr(buffer, "HTTP/1.1") == NULL || file == -1) {
        res = "HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n<html><body><h1>400 error</h1></body></html>";
        send(client_sock_descriptor, res, strlen(res), 0);
    }else if(strcmp(req_m, "GET") != 0) {
        res = "HTTP/1.1 501 Not Implemented\r\nContent-Type: text/html\r\n\r\n<html><body><h1>501 error</h1></body></html>";
        send(client_sock_descriptor, res, strlen(res), 0);
    }else{
        struct stat f_stat;
        if (fstat(file, &f_stat) == -1) {
            perror("fail to get file stat");
            close(client_sock_descriptor);
            close(file);
        }

        char header[256];
        snprintf(header, sizeof(header), "HTTP/1.1 200 OK\r\nContent-Length: %lld\r\n\r\n", f_stat.st_size);
        int header_len = strlen(header);

        send(client_sock_descriptor, header, header_len, 0);

        char file_buffer[4096];
        ssize_t read_bytes;
        while ((read_bytes = read(file, file_buffer, sizeof(buffer))) > 0) {
            send(client_sock_descriptor, file_buffer, read_bytes, 0);
        }

        close(file);
    }

    close(client_sock_descriptor);

    return NULL;
}
