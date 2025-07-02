#!/usr/bin/python3
import sys
import os
from time import gmtime, strftime
import getpass

def main():
    # Check the number of parameters.
    if (len(sys.argv) != 4 and len(sys.argv) != 5):
        sys.exit(2)

    # Get the current username of the student.
    username = getpass.getuser()

    # Get the timestamp.
    timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    # Get the rest of the parameters for the log.
    new_entry = ""
    if (len(sys.argv) == 4):
        new_entry = f"{username}     {timestamp}     {sys.argv[1]}     {sys.argv[2]}     {sys.argv[3]}\n"

    elif (len(sys.argv) == 5):
        new_entry = f"{username}     {timestamp}     {sys.argv[1]}     {sys.argv[2]}     {sys.argv[3]}     {sys.argv[4]}\n"

    # Now, append to the logs, if they exist.
    f = open(f"/home/{username}/.education/{username}_logs.txt", "a+")
    f.write(new_entry)
    f.close()

main()
