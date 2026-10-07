#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

#define MAX_ALTS 4
#define MAX_LEN 1024

// Normalize the student's query into a canonical form:
//  - Lowercase the query.
//  - Double quotes become single quotes.
//  - Runs of whitespace collapse to a single space, with none at the start/end.
//  - No spaces on either side of '='.
void normalize(const char* in, char* out, size_t outsz) {
    size_t n = 0;
    int pending_space = 0;

    for (size_t i = 0; in[i] && n + 2 < outsz; i++) {
        char c = in[i];

        if (isspace((unsigned char)c)) {
            pending_space = 1;
            continue;
        }

        if (c == '"') {
            c = '\'';
        }
        c = (char)tolower((unsigned char)c);

        // Only emit a space if it sits between two non-'=' characters.
        if (pending_space && n > 0 && out[n - 1] != '=' && c != '=') {
            out[n++] = ' ';
        }
        pending_space = 0;

        out[n++] = c;
    }
    out[n] = '\0';
}

// Check the student's (already normalized) query against every accepted answer for the step.
int check_query(const char* str, int step) {
    // All answers are written in normalized form: lowercase, single quotes, no spaces around '='.
    // Each step can accept several different queries. Each list ends with NULL.
    static const char* valid_queries[][MAX_ALTS] = {
        { "select * from students;", NULL },
        { "select * from students where student_grade='a';", NULL },
        { "select * from students where student_grade is not null;", NULL },
        { "update students set student_grade='b' where student_name='aaron';",
          "update students set student_grade='b' where student_id=100;", NULL },
        { "delete from students where student_grade is null;", NULL },
        { "select * from students limit 1 offset 1;", NULL }
    };

    // Adjust the index to match the step number.
    if (step >= 4 && step <= 9) {
        for (int i = 0; i < MAX_ALTS && valid_queries[step - 4][i] != NULL; i++) {
            if (strcmp(str, valid_queries[step - 4][i]) == 0) {
                return 0;
            }
        }
    }
    return 1;
}

int main(int argc, char* argv[]) {
    // Check if the correct number of arguments is provided.
    if (argc != 3) {
        printf("Usage: %s <step> <query>\n", argv[0]);
        return 2;  // Error code for incorrect usage.
    }

    // Extract the step number and the user's input.
    int step = atoi(argv[1]);

    // Validate the step number.
    if (step < 4 || step > 9) {
        printf("Error: Step number must be between 4 and 9.\n");
        return 2;  // Error code for incorrect step number.
    }

    // Normalize the input.
    char input[MAX_LEN];
    normalize(argv[2], input, sizeof(input));

    // Check if the normalized input matches any accepted query for this step.
    return check_query(input, step);
}
