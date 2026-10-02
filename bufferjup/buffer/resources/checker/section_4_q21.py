#!/usr/bin/python3
import subprocess
import sys
import re
import os

# This function removes C comments from source code, so that a commented-out strncpy() isn't counted.
# String and character literals are left alone, so something like "//" inside a string isn't mangled.
def strip_c_comments(code):
    pattern = r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''

    def replacer(match):
        text = match.group(0)
        # Comments start with a slash. Replace them with a space. Otherwise, keep the literal.
        if (text.startswith("/")):
            return " "
        return text

    return re.sub(pattern, replacer, code, flags=re.DOTALL)

# This function finds every strncpy() call in the code, then returns a list of the third arguments
# (the length). It walks through the parentheses by hand, so nested calls such as
# strncpy(a, b, sizeof(a) - 1) are split on the correct commas.
def get_strncpy_lengths(code):
    lengths = []

    for match in re.finditer(r'\bstrncpy\s*\(', code):
        i = match.end()
        depth = 1
        args = []
        current = ""
        quote = None

        while (i < len(code) and depth > 0):
            char = code[i]

            if (quote):
                # Inside of a string/char literal. Only stop at the matching, unescaped quote.
                current += char
                if (char == "\\" and i + 1 < len(code)):
                    current += code[i + 1]
                    i += 1
                elif (char == quote):
                    quote = None

            elif (char == '"' or char == "'"):
                quote = char
                current += char

            elif (char in "([{"):
                depth += 1
                current += char

            elif (char in ")]}"):
                depth -= 1
                if (depth > 0):
                    current += char

            elif (char == "," and depth == 1):
                args.append(current.strip())
                current = ""

            else:
                current += char

            i += 1

        args.append(current.strip())

        # strncpy(dest, src, n). If there are fewer than three arguments, it's not a normal call.
        # Treat the missing length as an empty string, which will not contain max_len.
        if (len(args) >= 3):
            lengths.append(args[2])
        else:
            lengths.append("")

    return lengths

def main():
    # This file is going to be ran in a loop within the notebook. It will take one step at a time.
    if (len(sys.argv) != 2):
        print("Usage: ./section_4_q21.py <step_to_test>")
        sys.exit(2)

    step = sys.argv[1]
    username = "USERNAME_GOES_HERE"

    # Before running this step, check to make sure that the topic has been started.
    if (not os.path.exists(f"/home/{username}/topic_4")):
        sys.exit(6)

    # Define the directory where CMakeLists.txt is located.
    compile_script = f"/home/{username}/topic_4/wormwood_fix/run.sh"

    try:
        result = subprocess.run(
            [compile_script, "--compile-only"],
            cwd=f"/home/{username}/topic_4/wormwood_fix",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        sys.exit(5)

    # Much like section_4.py, Step 18 is different from Steps 17, 19, and 20.
    # Step 17 is the strncpy() step, so it is the only step that checks the length.
    if (step == "17"):
        # Make sure that every strncpy() the student used is bounded by max_len, and not by a fixed value.
        wormwood_path = "/home/" + username + "/topic_4/wormwood_fix/wormwood.c"

        if (not os.path.exists(wormwood_path)):
            sys.exit(2)

        f = open(wormwood_path, "r")
        wormwood_source = f.read()
        f.close()

        for length in get_strncpy_lengths(strip_c_comments(wormwood_source)):
            # The length must reference the max_len variable (max_len, max_len - 1, etc.).
            if (not re.search(r'\bmax_len\b', length)):
                sys.exit(7)

        # Every strncpy() is bounded correctly.
        sys.exit(0)

    elif (step == "17" or step == "19" or step == "20"):
        # Get the student's previous payload for this step.
        if (not os.path.exists("/home/.checker/responses/step_" + step + "_answer.txt")):
            sys.exit(2)

        # Get the payload.
        f = open("/home/.checker/responses/step_" + step + "_answer.txt", "r")
        payload = f.read()
        f.close()

        # Remove the newline that it generates.
        payload = payload[:-1]

        # Run the student's payload within "wormwood_test", then see if it crashes.
        command = "/home/.checker/section_4.py " + step + " \'" + payload + "\' 0"
        result = subprocess.run(command, shell=True, text=True, capture_output=True)

        # Get the return code, which should be 1. Otherwise, if it fails, then this step does not pass.
        if (result.returncode != 0):
            sys.exit(1)

        # Now, run the payload through the fixed command.
        command = "/home/.checker/section_4.py " + step + " \'" + payload + "\' 1"
        result = subprocess.run(command, shell=True, text=True, capture_output=True)

        # Check to see if it fails (returning 2 from a time out error).
        if (result.returncode == 2):
            # A success!
            sys.exit(0)

        # Otherwise, a failure.
        else:
            # Returning 3 to let the student know that their payload broke the original program, but
            # wasn't fixed in their "fixed" program.
            sys.exit(3)


    elif (step == "18"):
        # Make sure the files exist before reading in the files.
        file_1 = "/home/" + username + "/topic_4/wormwood_fix/wormwood.c"

        if (not os.path.exists(file_1)):
            sys.exit(2)

        # The only step that we cannot check is the string vulnerability. Instead, we're just going
        # to check this one through regex. Read in the Wormwood file.
        f = open(file_1, "r")
        wormwood = f.read()
        f.close()

        # Find the segment which should contain the string vulnerability.
        pattern = r'^\s*console_printf\s*\(\s*([\'"])(?:\\.|(?!\1).)*%s(?:\\.|(?!\1).)*\1\s*,\s*user_user\s*\)\s*;$'
        matches = re.findall(pattern, wormwood, re.MULTILINE | re.DOTALL)

        if (matches):
            sys.exit(0)

        else:
            sys.exit(1)

    # Invalid input.
    else:
        sys.exit(4)

main()
