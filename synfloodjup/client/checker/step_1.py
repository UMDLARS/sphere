#!/usr/bin/python3
import subprocess
import sys
import os
import time
import signal
import re

def clean_output(output):
    # Remove non-printable characters.
    output = re.sub(r'[^\x20-\x7E\n]', '', output)
    return output

def main():
    if (len(sys.argv) != 1):
        print("Usage: ./step_2.py")
        sys.exit(1)

    pathname = "/home/USERNAME_GOES_HERE/stream.sh"

    # Check to see if the file exists yet.
    if (not os.path.exists(pathname)):
        # Doesn't exist.
        sys.exit(2)

    # Reading in the file contents.
    f = open(pathname, "r")
    file_contents = f.read()
    f.close()

    # Check #1: Check to see if the student is calling "curl".
    if ("curl" not in file_contents):
        sys.exit(3)

    # Check #2: Validating their URL.
    if ("index.html" not in file_contents):
        sys.exit(4)

    # Check #3: Check to see if the student is letting the script sleep.
    if ("sleep" not in file_contents):
        sys.exit(5)

    # Check #4: Check to see if the student is using a "while true" loop.
    if ("while true" not in file_contents):
        sys.exit(6)

    # If the script gets up to this point, it should be a valid script.
    # Test if the script doesn't produce errors.
    if (not os.access(pathname, os.X_OK)):
        sys.exit(7)

    # Now, run the file for three seconds.
    try:
        # Start the process.
        process = subprocess.Popen(['bash', pathname],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid
        )

        time.sleep(3)

        # Terminate the whole process group.
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)

        # Wait for termination.
        process.wait(timeout=5)

        # Getting the output and cleaning it. stderr usually has hidden characters.
        stdout_output, stderr_output = process.communicate()
        stderr_output = clean_output(stderr_output)

        if "Could not resolve host:" in stderr_output:
            sys.exit(9)

    # In case anything goes wrong with the process running. Shouldn't be the students' fault.
    except Exception as e:
        sys.exit(8)

    # If we get to here, then it should pass.
    sys.exit(0)

main()
