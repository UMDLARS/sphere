#!/usr/bin/python3
import sys
import os

def get_special_perms(path):
    mode = os.stat(path).st_mode

    # Only returns the special permission bit.
    return oct(mode)[-4]

def main():
    # Making sure that the function is called correctly:
    # (Step 10 doesn't require input, so "foo" will be used for input. It will not be used.)
    if (len(sys.argv) != 3):
        print("Usage: ./section_3.py <step_num> <input>")
        sys.exit(2)

    # Format is correct.
    else:
        # Checking step 8.
        if (sys.argv[1] == "8"):
            # This is a fill in the blank question. Saving the student's response first:
            f = open("/home/.checker/responses/step_8_answer.txt", "w+")
            f.write(sys.argv[2])
            f.close()

            # Check to see if the student answered the correct directory.
            if (sys.argv[2] == "/tmp" or sys.argv[2] == "tmp"):
                sys.exit(0)
            else:
                sys.exit(1)

        # Checking step 10.
        elif (sys.argv[1] == "10"):
            # Need to check three files.
            suid = os.path.expanduser("~/special_permissions/suid.sh")
            sgid = os.path.expanduser("~/special_permissions/sgid.sh")
            sticky = os.path.expanduser("~/special_permissions/sticky/")

            # Check if the file exists first.
            if (not os.path.exists(suid) or not os.path.exists(sgid) or not os.path.exists(sticky)):
                # File(s) do not exist.
                sys.exit(2)
            else:
                # All files exists. Check permissions.
                if (get_special_perms(suid) == "4" and get_special_perms(sgid) == "2" and get_special_perms(sticky) == "1"):
                    sys.exit(0)
                else:
                    sys.exit(1)

        # Checking step 11.
        elif (sys.argv[1] == "11"):
            # Just need to check the full set of permissions for the given input.
            # First, saving the student's answer:
            f = open("/home/.checker/responses/step_11_answer.txt", "w+")
            f.write(sys.argv[2])
            f.close()

            # Answer cannot be pulled from the students' work, so answer will need to be in plain text.
            if (sys.argv[2] == "4437"):
                sys.exit(0)
            else:
                sys.exit(1)

        # Checking step 12.
        elif (sys.argv[1] == "12"):
            # First, saving the student's answer:
            f = open("/home/.checker/responses/step_12_answer.txt", "w+")
            f.write(sys.argv[2])
            f.close()
            
            # Simply just checking true or false.
            if (sys.argv[2] == "False"):
                sys.exit(0)
            else:
                sys.exit(1)

        # In case an invalid step number was given.
        else:
            sys.exit(2)

main()
