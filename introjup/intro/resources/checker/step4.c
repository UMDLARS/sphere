#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    const char *hidden_file = "/usr/share/doc/zerofree/.findme.txt";
    if (access(hidden_file, F_OK) == 0) {
        return 1;
    }
    else {
        return 0;
    }

    return 1;
}
