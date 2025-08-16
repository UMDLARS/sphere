#!/usr/bin/python3
import sys
import os

def get_perms(path):
    mode = os.stat(path).st_mode
    return oct(mode)[-3:]

def main():
    # Making sure that the function is called correctly:
    if (len(sys.argv) != 3):
        print("Usage: ./section_2.py <step_num> <input>")

    else:
        # First, save the student's response.
        f = open("/home/.checker/responses/step_" + sys.argv[1] + "_answer.txt", "w+")
        f.write(sys.argv[2])
        f.close()

        # Getting the directory of where the POSIX files reside.
        # Subtracting 3 from sys.argv[1] so that we go back three steps to check the respective files.
        path = os.path.expanduser("~/posix_practice/q" + str(int(sys.argv[1]) - 4) + ".txt")

        # Before comparing, check to make sure that the file exists.
        if (not os.path.exists(path)):
            sys.exit(2)

        else:
            # Getting the mode of the file.
            mode = get_perms(path)

            # Finally, compare and return.
            if (int(mode) == int(sys.argv[2])):
                sys.exit(0)
            else:
                sys.exit(1)

        sys.exit(2)

main()
