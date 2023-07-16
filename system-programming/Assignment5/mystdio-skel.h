#ifndef MYSTDIO_H
#define MYSTDIO_H	1

#include <fcntl.h>
#include <sys/file.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>

#define BUFSIZE     1024    /* Default buffer size: 1024 bytes  */
#define EOF         -1      /* to indicate the end of the file. */

#define SEEK_SET    0       /* Seek from beginning of file.     */
#define SEEK_CUR    1       /* Seek from current position.      */
#define SEEK_END    2       /* Seek from end of file.           */

#define STDIN_FD    0
#define STDOUT_FD   1
#define STDERR_FD   2

typedef struct _myFILE{
	int fd;                 /* file descriptor of this file     */
    char rdbuffer[BUFSIZE]; /* read buffer of this file         */
    char wrbuffer[BUFSIZE]; /* write buffer of this file        */
    int mode_flag;          /* flag to describe opened mode     */
    int offset;             /* current position of a file (file position indicator) */
    int last_operation;     /* last operation for this file (read or write) */
} myFILE;

/*
 *  Exclusive Lock: Only 1 process can access this file at once.
 *   - I can have lock (ownership) of this file. (Use only once to get a lock)
 *   - but other processes CANNOT have the lock after I get the lock (until I unlock).
 *   - HINT: get the exclusive lock if you are a writer of this file.
 *   - returns: 1 if I can get the lock (success), otherwise 0
 */
int lockThisFileAsExclusive(myFILE *file){
    return flock(file->fd, LOCK_EX | LOCK_NB) == 0;
}

/*
 *  Shared Lock: Several processes can access this file at once.
 *   - I can have a lock (ownership) of this file. (Use only once to get a lock)
 *   - but other processes can have the lock too.
 *   - HINT: get the shared lock if you are a reader of this file.
 *   - returns: 1 if I can get the lock (success), otherwise 0
 */
int lockThisFileAsShared(myFILE *file){
    return flock(file->fd, LOCK_SH | LOCK_NB) == 0;
}

/*
 *  unlock this file after I finish to use this file.
 *  - returns: 1 if I can unlock the lock (success), otherwise 0
 */
int unlockThisFile(myFILE *file){
    return flock(file->fd, LOCK_UN | LOCK_NB) == 0;
}

myFILE *myfopen(const char *pathname, const char *mode);
int myfclose(myFILE *stream);
int myfseek(myFILE *stream, int offset, int whence);
int myfread(void *ptr, int size, int nmemb, myFILE *stream);
int myfwrite(const void *ptr, int size, int nmemb, myFILE *stream);
int myfflush(myFILE *stream);

/* ************************
 *  Implement after here. *
 * ************************ */

/* fopen mode: "r", "r+", "w", "w+", "a", "a+" */
myFILE *myfopen(const char *pathname, const char *mode){
    int fd_temp;
    int mode_flag_temp;
    int offset_temp = 0;
    if(strcmp(mode, "r") == 0){
        fd_temp = open(pathname, O_RDONLY);
        mode_flag_temp = O_RDONLY;
    } else if(strcmp(mode, "r+") == 0){
        fd_temp = open(pathname, O_RDWR);
        mode_flag_temp = O_RDWR;
    } else if(strcmp(mode, "w") == 0){
        fd_temp = open(pathname, O_WRONLY | O_TRUNC);
        mode_flag_temp = O_WRONLY | O_TRUNC;
    } else if(strcmp(mode, "w+") == 0){
        fd_temp = open(pathname, O_RDWR | O_CREAT | O_TRUNC);
        mode_flag_temp = O_RDWR | O_CREAT | O_TRUNC;
    } else if(strcmp(mode, "a") == 0){
        fd_temp = open(pathname, O_WRONLY | O_APPEND);
        mode_flag_temp = O_WRONLY | O_APPEND;
        offset_temp = lseek(fd_temp, 0, SEEK_END);
    } else if(strcmp(mode, "a+") == 0){
        fd_temp = open(pathname, O_RDWR | O_CREAT | O_APPEND);
        mode_flag_temp = O_RDWR | O_CREAT | O_APPEND;
        offset_temp = lseek(fd_temp, 0, SEEK_END);
    } else{
        return NULL;
    }
    
    if(fd_temp > 0){
        myFILE *newFile;
        newFile->fd = fd_temp;
        newFile->mode_flag = mode_flag_temp;
        newFile->offset = offset_temp;
        return newFile;
    } else {
        return NULL;
    }
}

int myfclose(myFILE *stream){
    int f_result = myfflush(stream);
    int result = close(stream->fd);
    if(f_result < 0 || result < 0){
        return EOF;
    }
    return result;
}

int myfseek(myFILE *stream, int offset, int whence){
    if(whence == SEEK_SET){
        stream->offset = offset;
    } else if(whence == SEEK_CUR){
        stream->offset += offset;
    } else if(whence == SEEK_END){
        int file_end = lseek(stream->fd, 0, SEEK_END);
        stream->offset = file_end + offset;
    } else {
        return -1;
    }
    return 0;
}

int myfread(void *ptr, int size, int nmemb, myFILE *stream){

    int lock_result = 0;
    while(lock_result == 0){
        lock_result = lockThisFileAsShared(stream);
    }

    lseek(stream->fd, stream->offset, SEEK_SET);
    int remain = size * nmemb;
    int transfered_bytes = 0;
    int read_items = 0;
    int read_bytes = 0;
    while(remain > 0){
        if(read_bytes + size >= BUFSIZE){
            memcpy((char*) ptr + transfered_bytes, stream->rdbuffer, read_bytes);
            memset(stream->rdbuffer, 0, BUFSIZE);
            transfered_bytes = transfered_bytes + read_bytes;
            read_items = 0;
            read_bytes = 0;
        }
        int result = read(stream->fd, stream->rdbuffer + (read_items * size), size);
        if(result < 0){
            stream->last_operation = 0;
            return read_items + transfered_bytes / size;
        }
        stream->offset += size;
        read_items++;
        read_bytes += size;
        remain -= size;
    }
    memcpy((char*) ptr + transfered_bytes, stream->rdbuffer, read_bytes);
    stream->last_operation = 0;
    int unlock_result = unlockThisFile(stream);
    return nmemb;
}

int myfwrite(const void *ptr, int size, int nmemb, myFILE *stream){

    int lock_result = 0;
    while(lock_result == 0){
        lock_result = lockThisFileAsExclusive(stream);
    }

    lseek(stream->fd, stream->offset, SEEK_SET);
    int remain = size * nmemb;
    int written_bytes = 0;
    int current_src_point = 0;
    while(remain > 0){
        memset(stream->wrbuffer, 0, BUFSIZE);
        int current_bytes;
        if(remain >= BUFSIZE){
            current_bytes = BUFSIZE;
        } else {
            current_bytes = remain;
        }
        memcpy(stream->wrbuffer, (char*) ptr + current_src_point, current_bytes);
        remain -= current_bytes;
        current_src_point += current_bytes;

        int buffer_remain = current_bytes;
        while(buffer_remain > 0){
            int current_buffer_bytes;
            if(buffer_remain >= size){
                current_buffer_bytes = size;
            } else {
                current_buffer_bytes = buffer_remain;
            }

            int result = write(stream->fd, stream->wrbuffer + written_bytes, current_buffer_bytes);
            if(result < 0){
                stream->last_operation = current_buffer_bytes;
                return written_bytes / size;
            }

            written_bytes += current_buffer_bytes;
            stream->offset += current_buffer_bytes;
            stream->last_operation = current_buffer_bytes;
            buffer_remain -= current_buffer_bytes;
        }
    }

    int unlock_result = unlockThisFile(stream);
    return nmemb;
}

int myfflush(myFILE *stream){
    if(stream->last_operation > 0){
        int result = write(stream->fd, stream->wrbuffer, stream->last_operation);
        if(result < 0){
            return EOF;
        }
    }
    memset(stream->rdbuffer, 0, BUFSIZE);
    memset(stream->wrbuffer, 0, BUFSIZE);
    return 0;
}

#endif // mystdio.h included