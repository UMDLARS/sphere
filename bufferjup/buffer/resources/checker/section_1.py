#!/usr/bin/python3
import subprocess
import sys
import os
import re
import textwrap
from itertools import combinations

def main():
    # Checks the usage. This shouldn't be giving an error, since it's called from the notebook.
    if (len(sys.argv) != 3):
        print("Usage: ./section_1.py <step_num> <answer (if step 6)>")
        sys.exit(2)

    step = sys.argv[1]

    # We need the student's username throughout this entire lab.
    username = "USERNAME_GOES_HERE"
    pathname = f"/home/{username}/topic_1"

    # Checks Step 1.
    if (step == "1"):
        # Checking for directory/file existence.
        if (not os.path.exists(pathname + "/step_1.c")):
            sys.exit(2)

        # Source file exists. Compiling the program to see if it works.
        compile_result = subprocess.run('gcc -o ' + pathname + '/step_1 ' + pathname + '/step_1.c 2>/dev/null', shell=True)

        # Did not compile correctly.
        if (compile_result.returncode == 1):
            sys.exit(3)

        # If it gets to this point, then it did compile correctly.
        result = subprocess.run(pathname + '/step_1', shell=True, text=True, capture_output=True)

        # Delete the compiled file, since the student will be doing this in the next step.
        os.remove(pathname + "/step_1")

        # Checks if the username was printed.
        if (result.stdout == username + "\n" or result.stdout == username):
            sys.exit(0)

        # Checks to see if there was an error.
        elif (result.stderr != ""):
            sys.exit(3)

        # This is if there's no error, but did not print the username.
        else:
            sys.exit(1)

    # Check Step 2.
    elif (step == "2"):
        # Checking for file existence.
        if (not os.path.exists(pathname + "/step_2")):
            sys.exit(1)

        else:
            # Checking to make sure that it's not an empty file that the student may have created to "trick"
            # the notebook.
            result = subprocess.run('file ' + pathname + '/step_2', shell=True, text=True, capture_output=True)
            if ("step_2: ELF 64-bit LSB pie executable" in result.stdout):
                sys.exit(0)

            else:
                sys.exit(2)

    # Check Step 3.
    elif (step == "3"):
        # Checking for directory/file existence.
        if (not os.path.exists(pathname + "/step_2")):
            sys.exit(2)

        # Should be a fairly straight-forward process. This check is very similar to Step 1.
        result = subprocess.run(pathname + '/step_2', shell=True, text=True, capture_output=True)

        # Checks if the username was printed.
        if (result.stdout == username + "\n" or result.stdout == username):
            sys.exit(0)

        # Checks to see if there was an error.
        elif (result.stderr != ""):
            sys.exit(3)

        # This is if there's no error, but did not print the username.
        else:
            sys.exit(1)

    # Check Step 4.
    elif step == "4":
        # Checking for directory/file existence.
        if not os.path.exists(pathname + "/step_4.c") or not os.path.exists(pathname + "/step_4"):
            sys.exit(2)

        # Read the student's code.
        with open(pathname + "/step_4.c", "r") as f:
            text = f.read()

        # Adjusted declaration pattern to exclude function declarations.
        decl_pattern = r'^\s*int\s+(?!\w+\s*\()[^;]+;'
        decl_matches = re.findall(decl_pattern, text, re.MULTILINE)

        variables = set()
        for match in decl_matches:
            # Remove 'int' and split by commas.
            var_part = match.strip()
            var_part = var_part[len('int'):].strip()  # Remove 'int' from the beginning.
            var_parts = [part.strip() for part in var_part.split(',')]
            for part in var_parts:
                # Remove any trailing semicolons.
                part = part.rstrip(';').strip()
                # Check if the variable is initialized.
                if '=' in part:
                    var_name, _ = part.split('=')
                    variables.add(var_name.strip())
                else:
                    variables.add(part.strip())

        # Find all assignments of variables to numeric values.
        assign_pattern = r'\b(\w+)\s*=\s*(\d+)\s*;'
        assign_matches = re.findall(assign_pattern, text)

        variable_values = {}
        for var_name, value in assign_matches:
            var_name = var_name.strip()
            if var_name in variables:
                value = int(value)
                if 1 <= value <= 1000:
                    variable_values[var_name] = value

        # Check if there are at least two variables with assigned values.
        valid_vars = list(variable_values.keys())

        if len(valid_vars) >= 2:
            # Generate all pairs of variables.
            var_pairs = list(combinations(valid_vars, 2))

            # Search for addition operations involving these variables.
            addition_found = False
            for var1, var2 in var_pairs:
                # Pattern to match any addition of the two variables.
                addition_pattern = re.compile(
                    r'\b{}\s*\+\s*{}\b|\b{}\s*\+\s*{}\b'.format(
                        re.escape(var1), re.escape(var2),
                        re.escape(var2), re.escape(var1)
                    )
                )

                # Search for addition expressions.
                if addition_pattern.search(text):
                    addition_found = True
                    break

                # Pattern to match assignment of addition to a variable.
                assignment_addition_pattern = re.compile(
                    r'\b\w+\s*=\s*({}\s*\+\s*{}|{}\s*\+\s{})\s*;'.format(
                        re.escape(var1), re.escape(var2),
                        re.escape(var2), re.escape(var1)
                    )
                )
                if assignment_addition_pattern.search(text):
                    addition_found = True
                    break

            if addition_found:
                # Updated regex pattern for the printf statement.
                printf_pattern = re.compile(
                    r'printf\s*\(.*%[di].*', re.DOTALL
                )

                # Search for the printf statement.
                if printf_pattern.search(text):
                    # Run the program and check the output.
                    result = subprocess.run(
                        pathname + '/step_4',
                        shell=True,
                        text=True,
                        capture_output=True
                    )

                    # Handle execution errors.
                    if result.returncode != 0:
                        sys.exit(3)

                    # Validate the output.
                    try:
                        output = result.stdout.strip()
                        # Extract integers from the output.
                        output_numbers = re.findall(r'-?\d+', output)
                        output_numbers = [int(num) for num in output_numbers]

                        # Sum the values of the variables.
                        expected_sum = sum(variable_values[var] for var in [var1, var2])

                        if expected_sum in output_numbers:
                            # Step is passed.
                            sys.exit(0)
                        else:
                            # Output does not contain the expected sum.
                            sys.exit(1)

                    except ValueError:
                        # Output does not contain valid integers.
                        sys.exit(4)
                else:
                    # printf statement not found.
                    sys.exit(1)
            else:
                # Addition operation not found.
                sys.exit(1)
        else:
            # Less than two valid variables found.
            sys.exit(1)


    # Check Step 5.
    elif step == "5":
        # Checking for directory/file existence.
        if not os.path.exists(pathname + "/step_5.c") or not os.path.exists(pathname + "/step_5"):
            sys.exit(2)

        # Read the student's code.
        with open(pathname + "/step_5.c", "r") as f:
            text = f.read()

        # Adjusted regex pattern.
        pattern = r'^\s*char\s*(\*?)\s*(\w+)\s*(\[\s*\d*\s*\])?\s*=\s*"([^"]*)"\s*;'

        # Find all matches.
        matches = re.findall(pattern, text, re.MULTILINE)

        # Filter valid matches.
        valid_matches = []
        print(matches)
        for ptr, varname, array_brackets, assigned_str in matches:
            # Check for invalid declarations (both pointer and array brackets).
            if ptr and array_brackets:
                continue
            # Ensure the assigned string matches the username.
            if assigned_str == username:
                valid_matches.append((ptr, varname, array_brackets, assigned_str))

        # Proceed if at least one valid match is found.
        if valid_matches:
            # Run the program and capture the output.
            result = subprocess.run(
                pathname + '/step_5',
                shell=True,
                text=True,
                capture_output=True
            )

            # Handle execution errors (e.g., segmentation fault).
            if result.returncode != 0:
                sys.exit(3)

            # Check if the output contains "Hello, username".
            output = result.stdout.lower()
            expected_phrase = f"hello, {username.lower()}"
            if expected_phrase in output:
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            # No valid declarations found.
            sys.exit(5)

    # Check Step 6. This requires user input!
    elif (step == "6"):
        # Check to make sure that the previous steps have been completed.
        # Getting a list of the files that should've been created before starting.
        completed_files = ["step_1.c", "step_2", "step_4.c", "step_4", "step_5.c", "step_5"]

        for file in completed_files:
            file_path = f"/home/USERNAME_GOES_HERE/topic_1/{file}"
            if not os.path.exists(file_path):
                sys.exit(2)

        if (sys.argv[2] == "0"):
            # The answer is correct. Before exiting with code 1, we need to create a new file for the student for the next step.
            # If it already exists, do not overwrite it. This may lose progress if the student is checking all their answers.
            if (not os.path.exists(pathname + "/step_7.c")):
                # This is the source code for Step 7:
                step_7_outline = """
#include <stdio.h>
    
void sum(int* a, int* b, int* c) {
    // Your answer here.
}
    
int main() {
    int a, b, c;
    
    a = 1;
    b = 2;
    c = 0;
    
    // Your answer here.
    
    printf("%d\\n", c);
    return 0;
}
                """
    
                # Remove leading whitespace and extra newline
                step_7_outline = textwrap.dedent(step_7_outline).strip()
    
                f = open(pathname + "/step_7.c", "w+")
                f.write(step_7_outline)
                f.close()
    
            # Now, exit.
            sys.exit(0)

        else:
            sys.exit(1)

    # Checks Step 7.
    elif step == "7":
        # Checking for directory/file existence.
        if not os.path.exists(pathname + "/step_7.c") or not os.path.exists(pathname + "/step_7"):
            sys.exit(2)

        # Read the student's code
        with open(pathname + "/step_7.c", "r") as f:
            text = f.read()

        # Updated regex pattern for the assignment inside sum()
        pattern_assignment = r'\*c\s*=\s*\(?\s*(\*a\s*\+\s*\*b|\*b\s*\+\s*\*a)\s*\)?\s*;'

        # Updated regex pattern for the function call to sum()
        pattern_function_call = r'sum\s*\(\s*&a\s*,\s*&b\s*,\s*&c\s*\)\s*;'

        # Check if the assignment is present
        if re.search(pattern_assignment, text, re.MULTILINE):
            # Check if sum() is called correctly
            if re.search(pattern_function_call, text, re.MULTILINE):
                # Now, attempt to run the program
                result = subprocess.run(
                    pathname + '/step_7',
                    shell=True,
                    text=True,
                    capture_output=True
                )

                # Handle execution errors
                if result.returncode != 0:
                    sys.exit(3)

                # Get the output and strip any whitespace
                output = result.stdout.strip()

                # Check to see if the output is "3"
                if output == "3":
                    # Before exiting successfully, create a new file for the next step
                    if not os.path.exists(pathname + "/step_8.c"):
                        step_8_outline = """
                        #include <stdio.h>
                        #include <stdlib.h>

                        int main() {
                            // Create the variables.
                            int num_elements;
                            const float PI = 3.14159;

                            // Ask for user input.
                            char input[10];
                            printf("Enter the number of elements: ");
                            fgets(input, sizeof(input), stdin);
                            num_elements = atoi(input);

                            // TASK 1: Use malloc to create array_of_floats.
                            // It should be a pointer of type "float"!

                            // Populating the array.
                            for (int i = 0; i < num_elements; ++i) {
                                array_of_floats[i] = i * PI;
                            }

                            // Printing the elements.
                            printf("Array elements: ");
                            for (int i = 0; i < num_elements; ++i) {
                                printf("%.5f ", array_of_floats[i]);
                            }
                            printf("\\n");

                            // TASK 2: Free the array.

                            return 0;
                        }
                        """

                        # Remove leading whitespace and extra newline
                        step_8_outline = textwrap.dedent(step_8_outline).strip()

                        with open(pathname + "/step_8.c", "w+") as f:
                            f.write(step_8_outline)

                    # Now exit.
                    sys.exit(0)
                else:
                    sys.exit(1)
            else:
                # sum() function call is incorrect
                sys.exit(4)
        else:
            # Assignment to *c is incorrect
            sys.exit(4)

    # Check Step 8.
    if step == "8":
        # Checking for directory/file existence.
        if (not os.path.exists(pathname + "/step_8.c") or not os.path.exists(pathname + "/step_8")):
            sys.exit(2)

        # Read the student's code
        with open(pathname + "/step_8.c", "r") as f:
            text = f.read()

        # Updated regex pattern for the malloc statement
        pattern_malloc = r'\s*float\s*\*\s*array_of_floats\s*=\s*\(\s*float\s*\*\s*\)\s*malloc\s*\(\s*(.*?)\s*\)\s*;'
        malloc_match = re.search(pattern_malloc, text, re.MULTILINE)

        if malloc_match:
            # Extract the argument inside malloc()
            malloc_arg = malloc_match.group(1).strip()

            # Remove all whitespace for easier pattern matching
            malloc_arg_no_space = re.sub(r'\s+', '', malloc_arg)

            # Remove outer parentheses if they exist
            if malloc_arg_no_space.startswith('(') and malloc_arg_no_space.endswith(')'):
                malloc_arg_no_space = malloc_arg_no_space[1:-1]

            # Patterns to match both orders of multiplication
            pattern_expr1 = r'num_elements\*sizeof\(float\)'
            pattern_expr2 = r'sizeof\(float\)\*num_elements'

            # Check if malloc_arg matches either pattern
            if re.fullmatch(pattern_expr1, malloc_arg_no_space) or re.fullmatch(pattern_expr2, malloc_arg_no_space):
                # Updated regex pattern for the free statement with optional space
                pattern_free = r'\s*free\s*\(\s*array_of_floats\s*\)\s*;'
                if re.search(pattern_free, text, re.MULTILINE):
                    # Now, attempt to run the program. Silence any errors.
                    # Start the process.
                    process = subprocess.Popen(
                        pathname + '/step_8',
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                    # Send the input and get the output and error
                    output, error = process.communicate(input="5\n".encode())

                    # Decode the output and error
                    output = output.decode()
                    error = error.decode()

                    # In case there was an error.
                    if error != "":
                        sys.exit(3)

                    # Should be the correct output.
                    expected_output = "Enter the number of elements: Array elements: 0.00000 3.14159 6.28318 9.42477 12.56636 \n"

                    if output == expected_output:
                        # Next step needs to be written before exiting.
                        if not os.path.exists("/home/" + username + "/topic_2/step_9.c"):
                            step_9_outline = """
                            #include <stdio.h>
                            #include <string.h>

                            void copy_string() {
                                char *str1 = "Hello!";
                                char str2[10];

                                strcpy(str2, str1);

                                printf("%s\\n", str2);
                            }

                            int main() {
                                copy_string();
                                return 0;
                            }
                            """

                            # BEFORE WRITING, check if topic_2/ is created.
                            if not os.path.exists("/home/" + username + "/topic_2/"):
                                os.mkdir("/home/" + username + "/topic_2/")

                            # Remove leading whitespace and extra newline
                            step_9_outline = textwrap.dedent(step_9_outline).strip()

                            with open("/home/" + username + "/topic_2/step_9.c", "w+") as f:
                                f.write(step_9_outline)

                        # Now exit.
                        sys.exit(0)

                    else:
                        # Output is incorrect.
                        sys.exit(1)
                else:
                    # The free statement is missing or incorrect.
                    sys.exit(4)
            else:
                # The malloc argument does not match the expected patterns.
                sys.exit(4)
        else:
            # The malloc statement is missing or incorrect.
            sys.exit(4)

main()
