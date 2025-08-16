#!/usr/bin/python3
import sys
import os

def get_perms(path):
    mode = os.stat(path).st_mode
    return oct(mode)[-3:]

def main():
    if (len(sys.argv) != 2):
        print("Usage: ./section_1.py step_num")
        return 0

    else:
        # Testing Step 1.
        if (sys.argv[1] == "1"):
            path = os.path.expanduser("~/posix_practice/q1.txt")

            # Checking to make sure that the path still exists.
            if (not os.path.exists(path)):
                sys.exit(2)
            else:
                # File exists. To check if executable bit exists for each user, each number from the mode must be odd.
                for permission in get_perms(path):
                    if (int(permission) % 2 == 0):
                        sys.exit(1)

                # If the loop never failed, then the step passes.
                sys.exit(0)

        # Testing Step 2.
        elif (sys.argv[1] == "2"):
            path = os.path.expanduser("~/posix_practice/q2.txt")

            # Checking to make sure that the path still exists.
            if (not os.path.exists(path)):
                sys.exit(2)
            else:
                # File exists. To check if write permission exists for each just the owner, it must be 2, 3, 6, or 7.
                # However, to match the format of the other checks, we need to check when the check FAILS.
                # If checkOwner is true, we're checking just the owner. Otherwise, we are checking the group/other perms.
                # Group/Other cannot have the write permissions, so we will need to check for this, too.
                checkOwner = True
                for permission in get_perms(path):
                    if ((permission != "2" and permission != "3" and permission != "6" and permission != "7") and checkOwner) or \
                       ((permission == "2" or permission == "3" or permission == "6" or permission == "7") and not checkOwner):
                        sys.exit(1)

                    checkOwner = False

                # If the loop never failed, then the step passes.
                sys.exit(0)

         # Testing Step 3.
        elif (sys.argv[1] == "3"):
            path = os.path.expanduser("~/posix_practice/q3.txt")

            # Checking to make sure that the path still exists.
            if (not os.path.exists(path)):
                sys.exit(2)
            else:
                # Just need to check the specific permissions.
                if (get_perms(path) != "615"):
                    sys.exit(1)
                else:
                    sys.exit(0)

main()
