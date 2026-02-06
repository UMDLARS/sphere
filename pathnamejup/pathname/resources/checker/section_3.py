#!/usr/bin/python3
import subprocess
import sys
import os
import time
import re
import builtins

# The following helper functions are going to be used for Step 12.
def copy_of_view_memo():
    function_copy = """@app.route('/memo/<path:memo_id>')
def view_memo(memo_id):
    # Get the URL of the memo.
    memo_filename = os.path.join(MEMO_DIR, str(memo_id))
    memo_content = ""

    ### Step 12 Solution START ###



    ### Step 12 Solution END ###

    # Attempt to access the file.
    try:
        # Read in the file as memo_content.
        with open(memo_filename) as file:
            memo_content = file.read()
    except FileNotFoundError:
        abort(404)

    # Check if memo_id is numeric. If it's not, an error. Set memo_id = -1.
    if not memo_id.isnumeric():
        memo_id = -1

    # Print view_memo.html page.
    return render_template('view_memo.html', memo_id=memo_id, memo=memo_content)
"""

    return function_copy


# Takes out the solution blocks for checks.
def extract_solution_block(content):
    pattern = re.compile(r'(\s*### Step 12 Solution START ###.*?### Step 12 Solution END ###\s*)', re.DOTALL)
    match = pattern.search(content)
    if match:
        return match.group(1)
    return ""

# The main function.
def main():
    # Check usage.
    if (len(sys.argv) != 3):
        print("Usage: ./section_3.py <step> <input - Step 11 only, use NA for Step 12.>")
        sys.exit(2)

    step = sys.argv[1]
    payload = sys.argv[2]

    if ("etc" not in payload and "passwd" not in payload and step == "11"):
        sys.exit(3)

    # Before running this step, in case the process wasn't closed previously, do this to kill any
    # existing processes on port 5010, which is what the checker is using.
    result = subprocess.run(['lsof', '-t', f'-i:5010'], capture_output=True, text=True)
    pids = result.stdout.strip()
    if pids:
        subprocess.run(['kill', *pids.split()])

    # This file should've already been made.
    if (not os.path.exists("/lab/memo.py")):
        sys.exit(2)

    # Navigate into the /lab directory.
    os.chdir("/lab")

    # Before attempting to run Step 11, the student may have already patched it.
    # If they've done this, we will make a temporary copy of the memo.py file with the
    # payload removed.
    step_11_reverted = ""
    if (step == "11"):
        with open("/lab/memo.py", 'r') as file1:
            # Remove the possible fix.
            content = file1.read()
            solution_block = extract_solution_block(content)
            content_clean = re.sub(re.escape(solution_block), '\n    ', content, flags=re.DOTALL)

            # Write the temp file.
            f = open("/lab/memo_copy.py", "w")
            f.write(content_clean)
            f.close()

            # Assign this string so that the process will call the temp file.
            step_11_reverted = "_copy"


    # Start the server on port 5010.
    process = subprocess.Popen(["python3", "-m", "flask", "--app", "memo" + step_11_reverted, "run", "-p", "5010"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # To prevent a race condition.
    time.sleep(2)

    # Check Step 11.
    if (step == "11"):
        # Making sure that Step 5 was complete before checking.
        if (os.path.exists("/lab/memo.py")):
            f = open("/lab/memo.py")
            contents = f.read()
            if "### Step 12 Solution START ###" not in contents:
                f.close()
                sys.exit(4)

        # Attempt to navigate to the URL that the student provided.
        result = subprocess.run("curl 127.0.0.1:5010/memo/" + payload, shell=True, capture_output=True, text=True)

        # Replace "result" with "result.stdout".
        result = result.stdout

        # Check if the result has buttons include in it. If they exist, remove them.
        pattern = re.compile(r'(?<=</p>)(.*?)(?=</body>)', re.DOTALL)
        result = re.sub(pattern, "", result)

        # PRINT the payload, since it will be used to show the student.
        print(result)

        # Now, close the subprocess, then return if there are no errors.
        process.terminate()
        process.wait()

        # Remove the temp file.
        os.remove("/lab/memo_copy.py")

        # For debugging:
        # process_output, process_errors = process.communicate()

        if ("daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin" in result):
            sys.exit(0)

        else:
            sys.exit(1)

    elif (step == "12"):
        with open("/lab/memo.py", 'r') as file1:
            content1 = file1.read()
            content2 = copy_of_view_memo()

            # Check that there are only six functions.
            matches = re.findall(r'def (\w+)', content1)
            if (len(matches) != 6):
                sys.exit(3)

            accepted_functions = ['index', 'add_memo', 'delete_memo', 'view_memo', 'load_memos', 'get_next_memo_id']

            for match in matches:
                if match not in accepted_functions:
                    sys.exit(3)

            # File doesn't appear to have extra functions. Now, extract the view_memo() body from content1.
            pattern = re.compile(r"(@app\.route\(.+\)\s+def\s+view_memo\(.+?\):[\s\S]+?return\s+render_template\(.+?\))")
            match1 = pattern.search(content1)
            match2 = pattern.search(content2)

            content1 = match1.group(1).strip()
            content2 = match2.group(1).strip()

            # Extract the student's solution.
            solution_block1 = extract_solution_block(content1)
            solution_block2 = extract_solution_block(content2)

            # Remove solution blocks for comparison using regular expressions for exact match.
            content1_clean = re.sub(re.escape(solution_block1), '\n    ', content1, flags=re.DOTALL)
            content2_clean = re.sub(re.escape(solution_block2), '\n    ', content2, flags=re.DOTALL)

            # Check if view_memo's content outside the solution blocks is the same.
            if content1_clean != content2_clean:
                sys.exit(4)

            # Check if os.path.realpath is called in the solution block without comments.
            pattern = re.compile(r'^\s*[^#]*\bos\.path\.realpath\(', re.MULTILINE)

            # Search for the pattern in the solution block.
            if not pattern.search(solution_block1):
                sys.exit(5)

            # If the script hasn't ended yet, then the attempt is valid.
            # Attempt the payload that the student used.
            if (not os.path.exists("/home/.checker/responses/step_11_answer.txt")):
                sys.exit(6)

            # Read in the student's payload from their previous response.
            f = open("/home/.checker/responses/step_11_answer.txt", "r")
            payload = f.read()
            f.close()

            # Before attempting the payload, create a basic memo to make sure the student doesn't redirect
            # all memos to the index page.
            f = open("/lab/memos/9999", "w")
            f.write("test")
            f.close()

            # Testing the fix.
            result = subprocess.run("curl -L -w \"%{url_effective}\n\" -o /dev/null -s 127.0.0.1:5010/memo/9999", shell=True, capture_output=True, text=True)

            # If this was redirected, the step fails. This redirect should be done if attempting to read a file outside of the memos directory.
            if (result.stdout == "http://127.0.0.1:5010/"):
                os.remove("/lab/memos/9999")
                sys.exit(7)

            # Remove the test memo.
            os.remove("/lab/memos/9999")

            # Attempt to navigate to the URL that the student provided.
            # The "L" flag is used to follow the redirect.
            result = subprocess.run("curl -L -w \"%{url_effective}\n\" -o /dev/null -s 127.0.0.1:5010/memo/" + payload, shell=True, capture_output=True, text=True)

            print(repr(result.stdout))

            # Check if the user was redirected properly
            if (result.stdout == "http://127.0.0.1:5010/\n"):
                sys.exit(0)

            else:
                sys.exit(1)


main()
