#!/usr/bin/python3
import subprocess
import sys
import re
import os

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
    if (step == "17" or step == "19" or step == "20"):
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
