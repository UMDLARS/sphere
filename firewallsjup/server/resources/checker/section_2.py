#!/usr/bin/python3
import subprocess
import sys
import time
import re
import os
import signal

def main():
    # Checks usage.
    if (len(sys.argv) != 3):
        print("Usage: ./section_2.py <step> <answer - Steps 6 and 7>")
        print(f"Arguments: {sys.argv}")
        sys.exit(2)

    step = sys.argv[1]
    answer = sys.argv[2]

    # Check Step 5.
    if (step == "5"):
        result = subprocess.run("sudo iptables -S", shell=True, text=True, capture_output=True)
        if ("-A OUTPUT -p tcp -m tcp --dport 80 -j DROP" in result.stdout):
            # Save the result.
            f = open("/home/.checker/responses/step_5_response.txt", "w")
            f.write(result.stdout)
            f.close()

            # Now exit.
            sys.exit(0)

        else:
            # Before exiting unsuccessfully, check to see if the student answered it before.
            if (os.path.exists("/home/.checker/responses/step_5_response.txt")):
                f = open("/home/.checker/responses/step_5_response.txt", "r")
                content = f.read()
                f.close()

                if ("-A OUTPUT -p tcp -m tcp --dport 80 -j DROP" in content):
                    sys.exit(0)

            sys.exit(1)

    # Check Step 6.
    if (step == "6"):
        answers = answer.split("\n")

        # Shouldn't happen, but check just in case.
        if (len(answers) != 2):
            sys.exit(2)

        if (answers[0].lower() == "output" and answers[1].lower() == "drop"):
            sys.exit(0)

        else:
            sys.exit(1)

    # Check Step 7.
    if (step == "7"):
        # Split the answer up.
        answers = answer.split(" ")

        # Check to see if a valid command is used.
        pattern = r'^(telnet|curl|nc)'
        matches = re.findall(pattern, answers[0])

        # Before running the command, we need to check to see if this step is being re-ran after
        # Topic 4 was started. If it is, then this step will not work. Make a backup of the rules.
        steps = [14, 15, 16, 17, 18]
        file_exists = any(os.path.exists(f"/home/.checker/responses/step_{step}_answer.txt") for step in steps)
        backup = ""

        rules = subprocess.run("sudo iptables -S", shell=True, capture_output=True, text=True)

        # If any of the questions from Topic 4 was already answered, make a backup of their current rules.
        if file_exists:
            backup = (rules.stdout).replace("-P INPUT ACCEPT\n-P FORWARD ACCEPT\n-P OUTPUT ACCEPT\n", "")

            # Now, replace the rules with the ones that are required for this step.
            subprocess.run("sudo iptables -F", shell=True)
            subprocess.run("sudo iptables -A OUTPUT -p tcp --dport 80 -j DROP", shell=True)

        # In case students proceed with deleting the step, but don't make it to Topic 4 yet.
        elif ("-A OUTPUT -p tcp -m tcp --dport 80 -j DROP" not in rules.stdout):
            subprocess.run("sudo iptables -A OUTPUT -p tcp --dport 80 -j DROP", shell=True)

        # Checking if there was one occurrence/statement being executed.
        if (len(matches) == 1):
            # If so, attempt to execute it. Will need to handle separate cases.
            if (matches[0] == "telnet" or matches[0] == "nc" or matches[0] == "curl"):
                # This will require the second user input.
                # Begin the command.
                process = subprocess.Popen(answers, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                try:
                    # Feed through the second input.
                    time.sleep(1)
                    process.stdin.write(answer[1])
                    process.stdin.flush()
                    time.sleep(1)

                except Exception as e:
                    print(e)
                    # Shouldn't happen. However, if a backup was made, revert to it before exiting.
                    if (backup != ""):
                        # Flush the current iptables rules.
                        subprocess.run("sudo iptables -F", shell=True)

                        # Restore the backed-up rules.
                        for line in backup.splitlines():
                            if line.strip():
                                subprocess.run(f"sudo iptables {line}", shell=True)

                    sys.exit(2)

                # Wait for a timeout.
                try:
                    stdout, stderr = process.communicate(timeout=5)
                    # For debugging:
                    print(stdout)
                except subprocess.TimeoutExpired:
                    process.terminate()

                    # If the process times out, check to see if the firewall rule was active.
                    result = subprocess.run("sudo iptables -S", shell=True, capture_output=True, text=True)
                    if ("-A OUTPUT -p tcp -m tcp --dport 80 -j DROP" in result.stdout):
                       # Before returning success, write the step that the student used and save it.
                       # Include the current firewall rules, too.
                       f = open("/home/.checker/responses/step_7_response.txt", "w+")
                       f.write(result.stdout)
                       f.write("\n-DIVIDER-\n")
                       f.write(answer)
                       f.close()

                       # If the student had previously done Step 8, remove the rule again.
                       if (os.path.exists("/home/.checker/responses/step_8_response.txt")):
                           subprocess.run("sudo iptables -F", shell=True)

                       # If a backup was made, revert to it before exiting.
                       if (backup != ""):
                           # Flush the current iptables rules.
                           subprocess.run("sudo iptables -F", shell=True)

                           # Restore the backed-up rules.
                           for line in backup.splitlines():
                               if line.strip():
                                   subprocess.run(f"sudo iptables {line}", shell=True)

                       # Now terminate.
                       sys.exit(0)

                    # Student may have used a timeout in their command.
                    else:
                        # If this is reached, don't restore a backup. One wasn't made.
                        sys.exit(3)

                # If the student reaches here, there was no timeout. The firewall rule may not have been applied.
                # This can still happen if the rule was applied, however. Restoring the backup (if any).
                if (backup != ""):
                    # Flush the current iptables rules.
                    subprocess.run("sudo iptables -F", shell=True)

                    # Restore the backed-up rules.
                    for line in backup.splitlines():
                        if line.strip():
                            subprocess.run(f"sudo iptables {line}", shell=True)

                sys.exit(1)

    # Check Step 8.
    if (step == "8"):
        # Check to see if the step was previously completed.
        if (os.path.exists("/home/.checker/responses/step_8_response.txt")):
            f = open("/home/.checker/responses/step_8_response.txt", "r")
            content = f.read()
            f.close()

            if (content == "-P INPUT ACCEPT\n-P FORWARD ACCEPT\n-P OUTPUT ACCEPT\n"):
                sys.exit(0)

            else:
                sys.exit(1)

        else:
            # Just check to make sure that the rule was flushed.
            result = subprocess.run("sudo iptables -S", shell=True, text=True, capture_output=True)
            if (result.stdout == "-P INPUT ACCEPT\n-P FORWARD ACCEPT\n-P OUTPUT ACCEPT\n"):
                # Before returning successfully, make sure that the student had already done this step already.
                if (os.path.exists("/home/.checker/responses/step_5_response.txt")):
                    f = open("/home/.checker/responses/step_5_response.txt", "r")
                    content = f.read()
                    f.close()

                    # Making sure the rule was in there.
                    if ("-A OUTPUT -p tcp -m tcp --dport 80 -j DROP" in content):
                        # Write the current result of the rules.
                        f = open("/home/.checker/responses/step_8_response.txt", "w+")
                        f.write(result.stdout)
                        f.close()
                        sys.exit(0)

            else:
                sys.exit(1)

main()
