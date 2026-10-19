#!/usr/bin/python3
import subprocess
import sys
import os
import getpass
import time
import shutil
import re

# This is an environment variable that's used to run ./section_1 while requiring section_1.py to be ran with it.
SECRET_VALUE = "897dba53d0bd4e72adf9215db3948"

def main():
    if len(sys.argv) != 2:
        print("Usage: ./section_1.py <step>")
        sys.exit(2)

    step = sys.argv[1]
    user = getpass.getuser()

    # Kill any leftover process on port 5010.
    result = subprocess.run(['lsof', '-t', '-i:5010'], capture_output=True, text=True)
    pids = result.stdout.strip()
    if pids:
        subprocess.run(['kill', *pids.split()])

    # Creating the environment variable.
    env = os.environ.copy()
    env["CHECKER_SECRET"] = SECRET_VALUE

    # Checking Step 2.
    if step == "2":
        # Checks to see if the student has previously passed this step.
        resp_path = "/home/.checker/responses/step_2_response.txt"
        if os.path.exists(resp_path):
            with open(resp_path, "r") as f:
                old_data = f.read()

            # Checking to make sure that the "Hello, World!" string was printed previously.
            if "<p>Hello, World!</p>" in old_data:
                # Pass with success. Was completed correctly beforehand.
                sys.exit(0)
            else:
                # This shouldn't have happened, as the student cannot previously "pass" with the wrong output.
                # Remove the bad file, then continue with the rest of the check.
                os.remove(resp_path)

        # Continuing with the proper check.
        path_2 = f"/home/{user}/step_2.py"
        # File doesn't exist.
        if not os.path.exists(path_2):
            sys.exit(2)

        # Heading into the student's directory so that we can open a process to run the Flask application.
        os.chdir(f"/home/{user}")

        # Start the student's server on port 5010 so that there's no conflicts.
        process = subprocess.Popen(
            ["python3", "-m", "flask", "--app", "step_2", "run", "-p", "5010"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        # To prevent any race conditions.
        time.sleep(2)

        # Calling a curl request and getting the output.
        curl_result = subprocess.run(
            ["curl", "127.0.0.1:5010"],
            capture_output=True, text=True
        )

        # Finish the task so that we can read the output.
        process.terminate()
        process.wait()

        # Checks if "Hello, World!" is printed properly. It should, since the answer is given to them in the notebook.
        if "<p>Hello, World!</p>" in curl_result.stdout:
            # Save a response file so we know we've passed.
            with open(resp_path, "w") as f:
                f.write(curl_result.stdout)

            # Before exiting successfully, create the next file for ~/step_3.py.
            c_result = subprocess.run(["/home/.checker/section_1", "2"], env=env, capture_output=True)

            # Should be successful.
            if c_result.returncode == 0:
                # If they pass, copy step_2.py to step_3.py for the next step.
                path_3 = f"/home/{user}/step_3.py"
                if not os.path.exists(path_3):
                    shutil.copyfile(path_2, path_3)
                sys.exit(0)

            # Something odd happened. They passed, but something is wrong with the checker script. Return a code of 3.
            else:
                os.remove(resp_path)
                sys.exit(3)
        else:
            # They have the wrong output (shouldn't happen, as the answer is given to them in the step).
            sys.exit(1)

    # Checking Step 3.
    elif step == "3":
        # Getting the response path, so that we can check if it was previously passed.
        resp_path = "/home/.checker/responses/step_3_response.txt"
    
        # If this file already exists, check if we previously passed Step 3.
        if os.path.exists(resp_path):
            with open(resp_path, "r") as f:
                old_data = f.read()
            # Checking the response and seeing if the template was printed.
            if "<h1>Welcome to Step 3!</h1>" in old_data:
                # Previously passed. Skip the step.
                sys.exit(0)
            else:
                # This was an invalid response that somehow got passed. Remove and continue with the rest of the check.
                os.remove(resp_path)
    
        # Defining a fresh path that we will be testing this on.
        path_3 = f"/home/{user}/step_3.py"

        # In case they haven't made step_3.py yet. This should've been done automatically.
        if not os.path.exists(path_3):
            sys.exit(2)
    
        # Start the student's server, just like Step 2. (This will be repeated throughout each step of the file).
        os.chdir(f"/home/{user}")
        process = subprocess.Popen(
            ["python3", "-m", "flask", "--app", "step_3", "run", "-p", "5010"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        time.sleep(2)
    
        curl_result = subprocess.run(
            ["curl", "127.0.0.1:5010"],
            capture_output=True, text=True
        )
    
        process.terminate()
        process.wait()
    
        # Now check if the returned HTML contains <h1>Welcome to Step 3!</h1>.
        if "<h1>Welcome to Step 3!</h1>" in curl_result.stdout:
            # Save a response file so we know we've passed.
            with open(resp_path, "w") as f:
                # Storing the output here.
                f.write(curl_result.stdout)
    
            # Now call the C code to finalize Step 3. sudo is required here since we need to make a directory in /.
            c_result = subprocess.run(
                ["sudo", "env", f"CHECKER_SECRET={SECRET_VALUE}", "/home/.checker/section_1", "3"],
                capture_output=True
            )

            # Should work.
            if c_result.returncode == 0:
                # Giving ownership to the student so that they can freely work within it.
                if os.path.exists("/lab"):
                    st_info = os.stat("/lab")
                    if st_info.st_uid == 0:
                        subprocess.run(["sudo", "chown", "-R", user, "/lab"])
                sys.exit(0)

            # Something went wrong with the checker script.
            else:
                # If the C code fails, remove the response so we can try again later.
                os.remove(resp_path)
                sys.exit(3)
        else:
            # The student is still returning "<p>Hello, World!</p>" or otherwise incorrect.
            sys.exit(1)

    # Checking Step 4.
    elif step == "4":
        # Defining the path, like always.
        resp_path = "/home/.checker/responses/step_4_response.txt"

        # If step_4_response.txt already exists, check if it was successful originally.
        if os.path.exists(resp_path):
            with open(resp_path, "r") as f:
                old_data = f.read()

            # There should've been a divider here, which we will split.
            if "\n-DIVIDER-\n" in old_data:
                parts = old_data.split("\n-DIVIDER-\n", 1)
                old_code = parts[0]
                old_curl = parts[1]

                # Defined the correct response, with some leniency in the answer.
                pattern = r'return\s+redirect\s*\(\s*url_for\s*\(\s*[\'"]index[\'"]\s*\)\s*\)'
                matches = re.findall(pattern, old_code)

                # If the redirect worked, this should be included in the curl request.
                has_redirect_html = ("<p>You should be redirected automatically to the target URL: <a href=\"/\">/</a>. If not, click the link." in old_curl)

                # There should be two matches for the redirects.
                if len(matches) >= 2 and has_redirect_html:
                    sys.exit(0)

                # Their response is actually invalid, but something allowed them to pass. Remove their response.
                else:
                    os.remove(resp_path)

            # If there was no divider, then this file was incorrectly made.
            else:
                os.remove(resp_path)

        # This file should exist.
        if not os.path.exists("/lab/memo.py"):
            sys.exit(2)

        # Read in their file.
        with open("/lab/memo.py", "r") as f:
            user_code = f.read()

        # Creating a regular expression with their response, adding some whitespace and quotation leniency.
        pattern = r'return\s+redirect\s*\(\s*url_for\s*\(\s*[\'"]index[\'"]\s*\)\s*\)'
        matches = re.findall(pattern, user_code)

        # This is in case they forgot to add two of the redirects.
        if len(matches) < 2:
            sys.exit(1)

        # Navigating into their /lab directory so that we can run their Flask application, like the previous steps.
        os.chdir("/lab")
        process = subprocess.Popen(
            ["python3", "-m", "flask", "--app", "memo", "run", "-p", "5010"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        time.sleep(2)

        # Attempting to add a memo using a cURL request.
        curl_result = subprocess.run(
            "curl -X POST -d \"memo=test\" -v http://127.0.0.1:5010/add_memo",
            shell=True, capture_output=True, text=True
        )

        process.terminate()
        process.wait()

        # The redirect should be working.
        redirect_snippet = "<p>You should be redirected automatically to the target URL: <a href=\"/\">/</a>. If not, click the link."
        if redirect_snippet in curl_result.stdout:
            # They were successful, and we will need to create a response text file so that we can refer back to it later.
            with open(resp_path, "w") as f:
                f.write(user_code)
                # Need a divider so that we can split the code and the cURL request in the check.
                f.write("\n-DIVIDER-\n")
                f.write(curl_result.stdout)

            # Generating the next step.
            c_result = subprocess.run(["/home/.checker/section_1", "4"], env=env, capture_output=True)

            # This should be working.
            if c_result.returncode == 0:
                sys.exit(0)

            # Otherwise, something went wrong with the checker file.
            else:
                os.remove(resp_path)
                sys.exit(3)
        else:
            sys.exit(1)

    # Checking Step 5.
    elif step == "5":
        resp_path = "/home/.checker/responses/step_5_response.txt"

        # Checking if they previously passed this.
        if os.path.exists(resp_path):
            with open(resp_path, "r") as f:
                old_data = f.read()

            # There should be a divider in their response.
            if "\n-DIVIDER-\n" in old_data:
                parts = old_data.split("\n-DIVIDER-\n", 1)
                old_code = parts[0]
                old_curl = parts[1]

                # This cURL response should be in their correct file.
                if "< HTTP/1.1 302 FOUND" in old_curl:
                    sys.exit(0)

                # Otherwise, they somehow passed, but their notebook generated the wrong file.
                else:
                    os.remove(resp_path)
            
            # Otherwise, remove their response, since this is an invalid file.
            else:
                os.remove(resp_path)

        # Checks to make sure that their memo.py file still exists.
        if not os.path.exists("/lab/memo.py"):
            sys.exit(2)

        # Starting up their Flask application with a process.
        os.chdir("/lab")
        with open("memo.py", "r") as f:
            user_code = f.read()

        process = subprocess.Popen(
            ["python3", "-m", "flask", "--app", "memo", "run", "-p", "5010"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        time.sleep(2)

        # Create a test memo with 9999 as the ID.
        test_memo_path = "/lab/memos/9999"
        with open(test_memo_path, "w") as f:
            f.write("test")

        # Attempt to delete it with their function.
        curl_result = subprocess.run(
            "curl -X POST -v http://127.0.0.1:5010/delete_memo/9999",
            shell=True, capture_output=True, text=True
        )

        # There was no valid delete function.
        if "< HTTP/1.1 302 FOUND" not in curl_result.stderr:
            process.terminate()
            process.wait()
            if os.path.exists(test_memo_path):
                os.remove(test_memo_path)
            sys.exit(1)

        # This shouldn't happen, since this was automatically generated for them.
        if os.path.exists(test_memo_path):
            process.terminate()
            process.wait()
            sys.exit(1)

        # At this point, they should've passed the step. Create their "success" file.
        with open(resp_path, "w") as f:
            f.write(user_code)
            f.write("\n-DIVIDER-\n")
            f.write(curl_result.stderr.strip())

        # Generate the file for their next step (which is Step 11).
        c_result = subprocess.run(["/home/.checker/section_1", "5"], env=env, capture_output=True)

        # Suspending the process.
        process.terminate()
        process.wait()

        # If the next step was correctly generated, exit successfully.
        if c_result.returncode == 0:
            sys.exit(0)

        # This will only happen if an error happened with the checker script.
        else:
            os.remove(resp_path)
            sys.exit(3)

    # Invalid parameter(s).
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
