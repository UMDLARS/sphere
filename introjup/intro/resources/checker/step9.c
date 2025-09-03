#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pwd.h>
#include <fcntl.h>   // for mkstemp

int main() {
    // Get the home directory.
    const char *homedir = getenv("HOME");

    if (homedir == NULL) {
        homedir = getpwuid(getuid())->pw_dir;
    }

    // Creating two variables: Path to sowpods.txt and path to output.txt.
    char key[128];
    char studentAns[128];

    // NOTE: We keep your original 'key' variable and comment above,
    // but below we will securely create TWO temp files (key1 and key2)
    // so that either diff ordering is accepted.
    snprintf(key, sizeof(key), "/tmp/.step9Ans");
    snprintf(studentAns, sizeof(studentAns), "%s/Important Data/lists/listdiff.txt", homedir);

    if (access(studentAns, F_OK) == 0) {
        // The answer exists, so we will generate a key.

        // Command buffer used for the following two checks. First, to create the key.
        char command[2048];

        // --- NEW: create two secure temp files to hold both possible diff outputs ---
        char key1[] = "/tmp/.step9Ans1.XXXXXX";
        char key2[] = "/tmp/.step9Ans2.XXXXXX";
        int fd1 = mkstemp(key1);
        int fd2 = mkstemp(key2);
        if (fd1 == -1 || fd2 == -1) {
            if (fd1 != -1) close(fd1);
            if (fd2 != -1) close(fd2);
            return 1;
        }
        close(fd1);
        close(fd2);

        // First, to create the key.
        // (We now generate BOTH orderings.)
        // Order: list1 then list2
        snprintf(command, sizeof(command),
                 "diff \"%s/Important Data/lists/list1.txt\" \"%s/Important Data/lists/list2.txt\" > \"%s\"",
                 homedir, homedir, key1);
        system(command);

        // Order: list2 then list1
        snprintf(command, sizeof(command),
                 "diff \"%s/Important Data/lists/list2.txt\" \"%s/Important Data/lists/list1.txt\" > \"%s\"",
                 homedir, homedir, key2);
        system(command);

        // Second, using diff to save the agony of writing C for file comparisons.
        // Accept if student's file matches EITHER ordering.
        int check;
        snprintf(command, sizeof(command), "diff -q \"%s\" \"%s\" > /dev/null", studentAns, key1);
        if (system(command) == 0) {
            check = 0;  // matches first ordering
        } else {
            snprintf(command, sizeof(command), "diff -q \"%s\" \"%s\" > /dev/null", studentAns, key2);
            check = (system(command) == 0) ? 0 : 1; // 0 if matches reversed ordering
        }

        // Remove the file.
        // (Now removing both temp files.)
        unlink(key1);
        unlink(key2);

        // Check to see if the files were the same.
        if (check == 0) {
            // output.txt is correct.
            return 0;
        }
        else {
            // output.txt is different from the answer.
            return 2;
        }
    }
    else {
        // Answer doesn't exist.
        return 3;
    }

    // Error with checking.
    return 1;
}

