#!/usr/bin/python3
import subprocess
import sys
import os
import shutil

def main():
    if (len(sys.argv) != 1):
        print("Usage: ./step_4.py")
        sys.exit(3)

    tmp_dir = "/tmp/analysis/"

    # Make sure that the file exists.
    if (not os.path.exists(f"{tmp_dir}/script3_modified.py")):
        sys.exit(1)

    # Running the file.
    result = subprocess.run(['python3', f'{tmp_dir}/script3_modified.py', f'{tmp_dir}/binary1.out'], capture_output=True, text=True)

    # Check if it ran properly.
    if (result.returncode != 0):
        sys.exit(2)

    # Ran correctly. Save the output of it, and a copy of itself.
    f = open("/home/.checker/responses/step_4_response.txt", "w+")
    f.write(result.stdout)
    f.close()

    # Now, creating the copy.
    shutil.copyfile(f"{tmp_dir}/script3_modified.py", "/home/.checker/responses/script3_modified.py")

    # Exiting successfully.
    sys.exit(0)

if __name__ == "__main__":
    main()
