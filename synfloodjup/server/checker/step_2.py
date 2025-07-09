#!/usr/bin/python3
import subprocess
import sys
import os

def main():
    if (len(sys.argv) != 1):
        print("Usage: ./step_2.py")
        sys.exit(2)

    # Just need to run a basic command and check the output.
    process = subprocess.run(['sudo', 'sysctl', 'net.ipv4.tcp_syncookies'], capture_output=True, text=True)

    response_file = "/home/.checker/responses/step_2_response.txt"

    if (process.stdout == "net.ipv4.tcp_syncookies = 0\n"):
        # Add the process response to the responses/ directory, so that it will pass in the future.
        f = open(response_file, "w+")
        f.write(process.stdout)
        f.close()
        
        sys.exit(0)

    else:
        # If it failed, check to see if it was passed previous. Students will be toggling this on/off
        # for the future steps.
        if (os.path.exists(response_file)):
            sys.exit(0)

        sys.exit(1)

main()

