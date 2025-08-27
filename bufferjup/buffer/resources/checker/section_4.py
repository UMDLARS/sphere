#!/usr/bin/python3
import subprocess
import sys
import os
import time
import re

def main():
    # Check the usage.
    if len(sys.argv) != 4:
        print("Usage: ./section_4.py <step_num> <payload> <0 - test, 1 - fix>")
        sys.exit(2)

    # Create the step/payload.
    step = sys.argv[1]
    payload = sys.argv[2]
    check_test = sys.argv[3]

    # We need the student's username throughout this entire lab.
    username = "USERNAME_FOR_NODE"

    # Depending if check_test is 0 or 1, we will need to check to see if the student is running the unedited or fixed Wormwood.
    if (check_test == "0"):
        check_test = "test"

    elif (check_test == "1"):
        check_test = "fix"

    else:
        sys.exit(2)

    # Step 17, 19, and 20 are the steps that can be properly tested.
    if (step != "18"):
        # Create the Wormwood directory so that we can navigate into it.
        # There's a strange glitch where ./run.sh won't work unless you're in the directory.
        wormwood_dir = f"/home/" + username + "/topic_4/wormwood_" + check_test

        # The file that needs to be called to use Wormwood.
        wormwood = f"{wormwood_dir}/run.sh"

        # Specific to Step 17.
        if (step == "17"):
            try:
                # Change the working directory to where run.sh is located.
                os.chdir(wormwood_dir)

                # Start the process.
                process = subprocess.Popen([wormwood], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                try:
                    # Send 'a' without newline.
                    process.stdin.write("a")
                    process.stdin.flush()
                    time.sleep(0.5)
                    # print("Sent 'a' to the process")

                    # Send the payload without newline.
                    process.stdin.write(payload)
                    process.stdin.flush()
                    time.sleep(0.5)
                    # print(f"Sent payload: {payload}")

                    # Send three newline characters to press "enter".
                    for _ in range(3):
                        process.stdin.write("\n")
                        process.stdin.flush()
                        time.sleep(0.5)
                        # print("Sent newline")

                    # Get the output and error with a timeout.
                    output, error = process.communicate(timeout=5)  # Timeout in seconds

                    # If the program reaches here, then the program exited. We can see if it crashed.
                    if ("The reactor failed catastrophically" in output):
                        sys.exit(0)

                    # If it doesn't crash, exit it with 0.
                    else:
                        sys.exit(1)

                # If the timer expires, then the program never crashed.
                except subprocess.TimeoutExpired:
                    process.terminate()
                    sys.exit(2)

            except Exception as e:
                print(f"An error occurred: {e}", file=sys.stderr)
                sys.exit(2)

        elif (step == "19" or step == "20"):
            # Splitting the "double new line".
            filtered_payloads = payload.split(" ")

            try:
                # Change the working directory to where run.sh is located.
                os.chdir(wormwood_dir)

                # Start the process.
                process = subprocess.Popen([wormwood], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                try:
                    # Send 'a' without newline.
                    process.stdin.write("a")
                    process.stdin.flush()
                    # print("Sent 'a' to the process")
                    time.sleep(0.5)

                    # Send 'super' without newline.
                    process.stdin.write("super")
                    process.stdin.flush()
                    # print("Sent 'super' to the process")
                    time.sleep(0.5)

                    # Send a newline character.
                    process.stdin.write("\n")
                    process.stdin.flush()
                    # print("Sent 'new line' to the process")
                    time.sleep(0.5)

                    for i in range(0, len(filtered_payloads)):
                        # Send the payload.
                        process.stdin.write(filtered_payloads[i])
                        process.stdin.flush()
                        # print(f"Sent {filtered_payloads[i]} to the process.")
                        time.sleep(0.5)

                        if (i == 0 or i == 2):
                            # Send a newline character.
                            process.stdin.write("\n")
                            process.stdin.flush()
                            # print("Sent 'new line' to the process")
                            if (i == 0):
                                time.sleep(0.5)
                            elif (i == 2):
                                time.sleep(10)

                    # Send another newline character.
                    process.stdin.write("\n")
                    process.stdin.flush()
                    # print("Sent 'new line' to the process")
                    time.sleep(0.5)

                    # Get the output and error with a timeout.
                    output, error = process.communicate(timeout=5)

                    # If the program reaches here, then the program exited. We can see if it crashed.
                    if "The reactor failed catastrophically" in output:
                        # Before exiting, check to see if it's Step 20. This was not a crash due to overflow/underflow.
                        # (We should never reach this, since the notebook checks this before running this script. It still works, however.)
                        if (step == "20" and filtered_payloads[1].lower() == "f"):
                            sys.exit(4)

                        else:
                            sys.exit(0)

                    # If it doesn't crash, exit it with 0.
                    else:
                        print("Process completed successfully.")
                        sys.exit(1)

                # If the timer expires, then the program never crashed.
                except subprocess.TimeoutExpired:
                    process.terminate()
                    sys.exit(2)

            except Exception as e:
                # print(f"An error occurred: {e}", file=sys.stderr)
                sys.exit(3)


    # Checks Step 18.
    elif (step == "18"):
        # Gets the user input. Using regular expressions to check the answer here.
        pattern = r"^(?:[^%]*%(?:s|d|x|p)){7}[^%]*%(s)(?:[^%]*%(?:s|d|x|p))*[^%]*$"

        if (re.search(pattern, payload)):
            sys.exit(0)

        else:
            sys.exit(1)


main()
