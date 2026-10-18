#!/usr/bin/python3
import os
import subprocess
import sys
import re
import mysql.connector
import glob

def find_node_executable():
    node_paths = glob.glob('/home/USERNAME_FOR_NODE/.nvm/versions/node/*/bin/node')
    if node_paths:
        # Return the first matching path, which is the version number. This changes quite a bit.
        return node_paths[0]
    else:
        print("Node executable not found.")
        sys.exit(2)

def main():
    if (len(sys.argv) != 3):
        print("Usage: ./section_2.py <step_num> <keep_work>")
        sys.exit(1)

    # This is used for obtaining the results:
    node_executable = find_node_executable()

    # Check if the step is between 2-4. If so, check if keep_work is 1 or 0. Otherwise,
    # if on Step 5, skip this check. It should be the victim's credit card number instead.
    if (sys.argv[2] != "1" and sys.argv[2] != "0"
         and int(sys.argv[1]) >= 2 and int(sys.argv[1]) <= 4):
        print("<keep_work> must be 1 (True) or 0 (False). If you are on Step 5, provide the victim's credit card number instead.")
        sys.exit(1)

    step = sys.argv[1]
    keep_work = sys.argv[2]

    # Each of these steps (except Step 5) need to call a JavaScript file.
    if (step == "2"):
        # If a student doesn't want to keep their work, then run this entire step through section_2.js.
        if (keep_work == "0"):
            # Run the section_2.js file. Saves the response from the payload.
            result = subprocess.run(f"{node_executable} /home/.checker/section_2.js 2", shell=True, capture_output=True, text=True)

            # Check to see if there was an error. A non-zero exit code from section_2.js
            # (for example, the browser failing to launch) is an error too, not a failed check.
            if (result.returncode != 0 or result.stderr != ""):
                sys.exit(2)

            # Otherwise, get the output and check it.
            elif ("62\n" in result.stdout):
                sys.exit(0)

            else:
                sys.exit(1)

        # If a student wants to run a check on their previous work, then a response should've been saved earlier.
        elif (keep_work == "1"):
            # Check to see if the student has already done the work.
            if (not os.path.exists("/home/.checker/responses/step_2_response.txt")):
                sys.exit(3)

            # Save the response.
            f = open("/home/.checker/responses/step_2_response.txt", "r")
            response = f.read()
            f.close()

            # If they already did it, then we will need to do some string parsing.
            # Check for all <script> tags, then save them into an array.
            pattern = re.compile(r"(?<=<script>)(.*?)(?=<\/script>)", re.DOTALL)
            matches = re.findall(pattern, response)

            # For all of the <script> tag matches, we need to find all console.log()'s.
            # If we get matches, see if they print the result of 2*31, as the instructions state.
            for code in matches:
                # Before checking, strip all whitespaces so that the regex will be cleaner.
                stripped_code = re.sub('\\s+', '', code)
                if (re.search(r"(?<=console\.log\()((2\*31)|(31\*2))(?=\))", stripped_code)):
                    # There's a match! Exit successfully.
                    sys.exit(0)

            # If the code reaches here, then the step did not pass.
            sys.exit(1)

    # Steps 3 and 4 are super similar.
    elif (step == "3" or step == "4"):
        # If a student doesn't want to keep their work, then run this entire step through section_2.js.
        if (keep_work == "0"):
            # Call the section_2.js file for Step 3.
            result = subprocess.run(f"{node_executable} /home/.checker/section_2.js {step}", shell=True, capture_output=True, text=True)
            sys.exit(result.returncode)

        # If a student wants to run a check on their previous work, then a response should've been saved earlier.
        elif (keep_work == "1"):
            # Check to see if the student has already done the work.
            if (not os.path.exists("/home/.checker/responses/step_" + str(step) + "_response.txt")):
                sys.exit(3)

            # Save the response.
            f = open("/home/.checker/responses/step_" + str(step) + "_response.txt", "r")
            response = f.read()
            f.close()

            # Since their work was saved, we will need to divide at the divider that was made in the previous check.
            responses = response.split("\n-DIVIDER-\n")

            # There are supposed to be two responses from this.
            if (len(responses) != 2):
                sys.exit(2)

            # Now, check to see if the elements are the different. Required to pass the step.
            if (responses[0] != responses[1]):
                # If this was Step 3, then exit with 1.
                if (step == "3"):
                    sys.exit(0)

                # If this was Step 4, then we need to do one more check.
                elif (step == "4"):
                    # Check if the second response contains the URL of the victim.
                    if ("http://10.0.1.1/xss_practice.php?auth=TSATtX2ZLqcBfi3qbG7d7knDomApvaEJ" in responses[1]):
                        sys.exit(0)

                    else:
                        sys.exit(1)

            # Otherwise, the test fails.
            else:
                sys.exit(1)

    # Checking Step 5, which is just a SQL call.
    elif (step == "5"):
        try:
            # Creating a connection and a cursor.
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='xss'
            )

            cursor = conn.cursor()

            # Take the provided query, then run it.
            cursor.execute('SELECT note FROM notes WHERE username = "Hacker"')

            result = cursor.fetchall()

            # Close the connection/cursor, then return the query result.
            conn.close()
            cursor.close()

            # Now, check to see if the student provided the correct number.
            # Note that when the victim's notes get reset, their card number will always appear
            # in the first result of the SELECT query. Additionally, for Step 5, the <keep_work>
            # variable is acting as the user input here, so we will check with that. Not the best
            # practice, but will keep the code cleaner. Use result[0][0] because it's a tuple.
            if (keep_work in result[0][0]):
                sys.exit(0)

            else:
                sys.exit(1)

        except mysql.connector.Error as e:
            # print(f"Error executing SQL query: {e}")
            sys.exit(2)

main()
