#!/usr/bin/python3
import subprocess
import sys
import os
import time
import signal
import re

def main():
    if (len(sys.argv) != 2):
        print("Usage: ./section_4.py <step>")
        sys.exit(2)

    # Define the step and the port for each step.
    step = sys.argv[1]
    
    port = ""
    
    if (step == "14"):
        port = "80"

    elif (step == "15"):
        port = "3306"

    elif (step == "16"):
        port = "443"

    elif (step == "17"):
        port = "22"

    elif (step == "18"):
        ports = "10000:10005"
        
        
    # First, check to see if the student has already answered this.
    result = subprocess.run('ssh -o StrictHostKeyChecking=no -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@server "cat /home/.checker/responses/step_' + step + '_answer.txt 2> /dev/null"', capture_output=True, text=True, shell=True)
    answer = result.stdout

    # Student has an answer already.
    if (answer != ""):
        # Remove the divider so that the answer/response can be examined.
        answers = answer.split("\n-DIVIDER-\n")

        # Make sure that the necessary rule is added.
        if (answers[0] == "" or 
            (port not in answers[0] and int(step) >= 14 and int(step) <= 17) or 
            ("10000:10005" not in answers[0] and step == "18")):
            # No rules present or the necessary rule is unavailable. Inform the student.
            sys.exit(3)

        # Checks for Steps 14 and 15.
        if (step == "14" or step == "15"):
            if ("Connected to server" in answers[1]):
                sys.exit(1)
        
            # Otherwise, successful.
            elif (answers[1].endswith("Trying 10.0.1.1...\n")):
                sys.exit(0)
                
            # Not sure if this will happen, but if it does, return unsuccessful.
            else:
                sys.exit(2)

        # Checks for Step 16.
        elif (step == "16"):
            # We will see how many successful connections there were.
            matches = re.findall(r'Connected to (\w+).com', answers[1])

            # Make sure that only one connection was made. Presumably Stack Overflow.
            if (len(matches) != 1):
                sys.exit(1)

            # Make sure that the other three connections failed.
            matches = re.findall(r'telnet: Unable to connect to remote host', answers[1])

            if (len(matches) != 3):
                sys.exit(1)

            # If the previous conditions were not matched, then it was successful.
            sys.exit(0)

        # Checks for Step 17.
        elif (step == "17"):
            if ("ssh: connect to host server port 22:" not in answers[1]):
                sys.exit(1)

            else:
                sys.exit(0)

        # Checks for Step 18.
        elif (step == "18"):
            if ("Hello!" in answers[1]):
                sys.exit(1)

            else:
                sys.exit(0)
        
    # There's no answer for the step. Prepare to do the test.
    else:
        # Test Steps 14 through 17. Step 18 needs a bit of a different test.
        if (int(step) >= 14 and int(step) <= 17):
            # We will need to get the list of firewall rules from the server node. Used for saving later if successful.
            rules = ""
            if (step == "14" or step == "15"):
                result = subprocess.run('ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@server "bash -l -c \'sudo iptables -S\'"', shell=True, capture_output=True, text=True)
                rules = result.stdout

            elif (step == "16" or step == "17"):
                result = subprocess.run('ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@client "bash -l -c \'sudo iptables -S\'"', shell=True, capture_output=True, text=True)
                rules = result.stdout
    
            # Remove all of the predefined rules. Only capture the current rules that the student added.
            rules = rules.replace("-P INPUT ACCEPT\n-P FORWARD ACCEPT\n-P OUTPUT ACCEPT\n", "")
    
            # Check if any rules are present.
            if (rules == "" or port not in rules):
                # No rules present or the necessary rule is unavailable. Inform the student.
                sys.exit(3)
    
            # Now, we can begin the test. Navigate into client to test the connection.
            # Call -tt parameter to fix the pseudoterminal error.
            process = subprocess.Popen(["ssh", "-tt", "-i", "/home/USERNAME_GOES_HERE/.ssh/merge_key", "USERNAME_GOES_HERE@client"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
            # Wait to prevent a race condition.
            time.sleep(2)
    
            # Run the telnet command.
            if (step == "14" or step == "15"):
                process.stdin.write("telnet server " + port + "\n")
                process.stdin.flush()
                # Wait for a bit to allow telnet to respond.
                time.sleep(5)

            elif (step == "16"):
                def start_telnet_session(process, address, port):
                    process.stdin.write(f"telnet {address} {port}\n")
                    process.stdin.flush()
                    time.sleep(3)  # Wait for telnet to respond
                    process.stdin.write("\n\n")
                    process.stdin.flush()
                
                def graceful_exit(process):
                    process.stdin.write(chr(29))  # chr(29) corresponds to ^]
                    process.stdin.flush()
                    time.sleep(1)
                    process.stdin.write("quit\n")
                    process.stdin.flush()
                    time.sleep(1)  # Allow some time for telnet to quit
                
                def forceful_exit(process):
                    process.stdin.write(chr(3))  # chr(3) corresponds to Ctrl + C
                    process.stdin.flush()
                    time.sleep(1)
                
                # Start telnet session for Stack Overflow and exit gracefully
                start_telnet_session(process, "stackoverflow.com", 443)
                graceful_exit(process)
                
                # Start telnet sessions for the other websites and exit forcefully
                start_telnet_session(process, "wikipedia.com", 443)
                forceful_exit(process)
                
                start_telnet_session(process, "d.umn.edu", 443)
                forceful_exit(process)
                
                start_telnet_session(process, "github.com", 443)
                forceful_exit(process)

            elif (step == "17"):
                process.stdin.write("ssh server\n")
                process.stdin.flush()
                # Wait for a bit to allow telnet to respond.
                time.sleep(5)
    
            # Call Ctrl + C.
            process.send_signal(signal.SIGINT)
    
            try:
                # Wait for a bit to allow telnet to respond.
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()
                stdout, stderr = process.communicate()

            # Terminate the process, in case it hasn't done so yet.
            process.terminate()
            # For debugging:
            print(stdout)
            print(stderr)
            
    
            # Some checks for Steps 14 and 15.
            if (step == "14" or step == "15"):
                if ("Connected to server" in stdout):
                    sys.exit(1)
        
                # Otherwise, successful. We can write the output as a response.
                elif (stdout.endswith("Trying 10.0.1.1...\n")):
                    # Write the file before returning successfully.
                    content = rules + "\n-DIVIDER-\n" + stdout
                    # The content[:-1] will remove the newline that gets made.
                    result = subprocess.run('ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@server "echo \'' + content[:-1] + '\' > /home/.checker/responses/step_' + step + '_answer.txt"', capture_output=True, text=True, shell=True)
                    sys.exit(0)

                # Shouldn't happen.
                else:
                    sys.exit(2)

            # Now, if it is step 16, we have a couple other checks.
            elif (step == "16"):
                # We will see how many successful connections there were.
                matches = re.findall(r'Connected to (\w+).com', stdout)

                # Make sure that only one connection was made. Presumably Stack Overflow.
                if (len(matches) != 1):
                    sys.exit(1)

                # Make sure that the other three connections failed.
                matches = re.findall(r'telnet: Unable to connect to remote host', stdout)

                print("Matches: " + str(len(matches)))

                if (len(matches) != 3):
                    sys.exit(1)

                # If the previous conditions were not matched, then it was successful.
                # Write the student's response as a file so that it can be used later for quicker checks.
                content = rules + "\n-DIVIDER-\n" + stdout
                # The content[:-1] will remove the newline that gets made.
                result = subprocess.run('ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@server "echo \'' + content[:-1] + '\' > /home/.checker/responses/step_' + step + '_answer.txt"', capture_output=True, text=True, shell=True)
                sys.exit(0)

            # Simply check to see if the client node was able to connect to the server node.
            elif (step == "17"):
                if ("ssh: connect to host server port 22:" not in stdout):
                    sys.exit(1)

                else:
                    # Write the student's response as a file so that it can be used later for quicker checks.
                    content = rules + "\n-DIVIDER-\n" + stdout
                    # The content[:-1] will remove the newline that gets made.
                    result = subprocess.run('ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@server "echo \'' + content[:-1] + '\' > /home/.checker/responses/step_' + step + '_answer.txt"', capture_output=True, text=True, shell=True)
                    sys.exit(0)
                
            # Not sure if this will happen, but if it does, return unsuccessful.
            else:
                sys.exit(2)

        # Special check for Step 18.
        elif (step == "18"):
            # Rules should be applied to the server node.
            result = subprocess.run('ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@server "bash -l -c \'sudo iptables -S\'"', shell=True, capture_output=True, text=True)
            rules = result.stdout

            # Check to see if the rule is using 10000:10005.
            if (rules == "" or "10000:10005" not in rules):
                # No rules present or the necessary rule is unavailable. Inform the student.
                sys.exit(3)

            # To make testing easier, we're just going to do this twice. One on port 10005, then port 10006.
            for i in range(10005, 10007):
                # Now, we can begin the tests. Navigate into both nodes.
                # Call -tt parameter to fix the pseudoterminal error.
                process1 = subprocess.Popen(["ssh", "-tt", "-i", "/home/USERNAME_GOES_HERE/.ssh/merge_key", "USERNAME_GOES_HERE@server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                process2 = subprocess.Popen(["ssh", "-tt", "-i", "/home/USERNAME_GOES_HERE/.ssh/merge_key", "USERNAME_GOES_HERE@client"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
                time.sleep(2)
    
                # Start the nc connection on the server node.
                process1.stdin.write("nc -u -l -p " + str(i) + "\n")
                process1.stdin.flush()
    
                # Start the nc connection on the client node.
                process2.stdin.write("nc -u server " + str(i) + "\n")
                process2.stdin.flush()
    
                time.sleep(1)
    
                # Send a response to the server.
                process2.stdin.write("Hello!\n")
                process2.stdin.flush()
    
                time.sleep(1)
    
                # Terminate both processes. 
                try:
                    process1.terminate()
                    process2.terminate()
                    
                    # Only need the server process.
                    stdout, stderr = process1.communicate(timeout=5)
    
                # A timeout shouldn't be happening with this step.
                except subprocess.TimeoutExpired:
                    sys.exit(2)

                # If the message didn't appear on port 10005, exit unsuccessfully.
                if ("Hello!" not in stdout and i == 10005):
                    print(stdout)
                    sys.exit(1)

                # 10005 passed, now checking 10006. If "Hello!" did not appear, we pass.
                if ("Hello!" not in stdout and i == 10006):
                    # We can exit successfully now. Save the response from the student.
                    content = rules + "\n-DIVIDER-\n" + stdout
                    # The content[:-1] will remove the newline that gets made.
                    # This is going to be a little illegible, but still won't have "Hello!" in it...
                    result = subprocess.run('ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@server "echo \'' + content[:-1] + '\' > /home/.checker/responses/step_' + step + '_answer.txt"', capture_output=True, text=True, shell=True)
                    sys.exit(0)

            # Should've exited successfully from here.
            sys.exit(1)
                    

main()
