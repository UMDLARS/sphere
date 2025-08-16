#!/usr/bin/python3
import sys
import os
import pwd
import grp

# For Steps 18, 22 and 23:
import subprocess

# Used to get the mode of a file.
def get_perms(path):
    mode = os.stat(path).st_mode
    return oct(mode)[-3:]

# Used to get ONLY the special permission of a file.
def get_special_perms(path):
    mode = os.stat(path).st_mode
    return oct(mode)[-4]

# Checks to see if a user exists.
def check_user_exists(username):
    try:
        # This will get the database entry of the user inside of the Unix environment.
        pwd.getpwnam(username)
        return True
    # If the entry cannot be grabbed, then the user doesn't exist. Return false.
    except KeyError:
        return False

# Check to see if the group exists. Similar to getpwnam, but for groups.
def check_group_exists(groupname):
    try:
        grp.getgrnam(groupname)
        return True
    except KeyError:
        return False

# Given the username and the group that they're in, check to see if they're in it.
def check_user_in_group(username, groupname):
    try:
        # Get the database entry for the group, if it exists.
        group = grp.getgrnam(groupname)
        # Check if the username is in the entry, and return the result.
        return (username in group.gr_mem)
    # Returns false if the group doesn't exist.
    except KeyError:
        return False

# This is to check if the owner is correct, given a file path.
def check_owner(path, owner):
    # Gets the file information.
    stat_info = os.stat(path)
    # Gets the UID of the file/dir. Needed for checking the owner.
    uid = stat_info.st_uid
    # Gets the owner of the file.
    user = pwd.getpwuid(uid).pw_name
    # Returns the boolean for the owner matching the provided arguments in the function.
    return user == owner

# This is to check if the group is correct, given a file path.
def check_group(path, group):
    # Gets the file information.
    stat_info = os.stat(path)
    # Gets the GID of the file/dir. Needed for the owner/group.
    gid = stat_info.st_gid
    # Gets the group of the file.
    grp_name = grp.getgrgid(gid).gr_name
    # Returns the boolean for the group matching the provided arguments in the function.
    return grp_name == group

def main():
    if len(sys.argv) != 2:
        print("Usage: ./section_4.py <step_num>")
        sys.exit(2)

    step = sys.argv[1]

    # Checks step 13: Creating the users.
    if step == "13":
        users = ["ash", "misty", "brock", "james"]
        if all(check_user_exists(user) for user in users):
            sys.exit(0)
        else:
            sys.exit(1)

    # Checks step 14: Creating a group.
    elif step == "14":
        if check_group_exists("trainers"):
            sys.exit(0)
        else:
            sys.exit(1)

    # Checks step 15: Adding users to group.
    elif step == "15":
        users = ["ash", "misty", "brock"]
        if all(check_user_in_group(user, "trainers") for user in users):
            if (check_user_in_group("james", "trainers")):
                sys.exit(3)

            else:
                sys.exit(0)
        else:
            sys.exit(1)

    # Checks step 16: Changing group ownership.
    elif step == "16":
        if (os.path.exists("/collections")):
            if check_group("/collections", "trainers"):
                sys.exit(0)
            else:
                sys.exit(1)
        # /collections cannot be found.
        else:
            sys.exit(3)

    # Checks step 17: Changing user ownership and permissions.
    elif step == "17":
        if (os.path.exists("/collections")):
            perms = get_perms("/collections")
            if perms == "775" and check_owner("/collections", "ash"):
                sys.exit(0)
            else:
                sys.exit(1)
        # /collections cannot be found.
        else:
            sys.exit(3)

    # Checks step 18: Changing users/ownership.
    elif step == "18":
        try:
            stat_info = os.stat("/collections/personal_notebook.txt")
            uid = stat_info.st_uid
            gid = stat_info.st_gid
            user = pwd.getpwuid(uid).pw_name
            if user == "brock" and get_perms("/collections/personal_notebook.txt") == "600":
                # Passed the step, but need to move the run_me file over. Doing this in the checker file
                # instead of the notebook so that we don't do SSH'ing for this step.
                # First, we need to see if the file doesn't exist. If not, then we can make it. Otherwise, it will reverse the students' progress.
                if (not os.path.exists("/collections/run_me")):
                    subprocess.run("sudo cp /home/.checker/run_me /collections/; sudo chmod 000 /collections/run_me; sudo chown ash:trainers /collections/run_me", shell=True)
                sys.exit(0)
        except FileNotFoundError:
            sys.exit(3)
        sys.exit(1)

    # Checks step 19: Applying a special permission.
    elif step == "19":
        if (os.path.exists("/collections/run_me")):
            perms = get_perms("/collections/run_me")
            special_perm = get_special_perms("/collections/run_me")
            if perms == "110" and special_perm == "4":
                sys.exit(0)
            else:
                sys.exit(1)

        # /collections/run_me cannot be found.
        else:
            sys.exit(3)

    # Checks step 20: Creating a directory and checking the owner.
    elif step == "20":
        if (os.path.exists("/collections/project")):
            if check_owner("/collections/project", "misty"):
                sys.exit(0)
            else:
                sys.exit(1)

        # /collections/project cannot be found.
        else:
            sys.exit(3)

    # Checks step 21: Changing the directory's permissions.
    elif step == "21":
        if (os.path.exists("/collections/project")):
            perms = get_perms("/collections/project")
            previously_completed = False

            # Need to envoke sudo to see if progress_report.txt exists. Using subprocess.run for this.
            # Reason why we're doing this is because this script runs as umdclassXXXX, who doesn't have access to this file.
            file_exists = subprocess.run("sudo [ -f /collections/project/progress_report.txt ] && echo 1 || echo 0", shell=True, capture_output=True)

            # Need to decode any stdout as UTF-8 before comparing it to a string.
            if (file_exists.stdout.decode('utf-8').strip() == "1"):
                previously_completed = True

            if perms == "770" or previously_completed:
                stat_info = os.stat("/collections/project")
                gid = stat_info.st_gid
                grp_name = grp.getgrgid(gid).gr_name
                if grp_name == "trainers":
                    sys.exit(0)
            sys.exit(1)

        # /collections/project cannot be found.
        else:
            sys.exit(3)

    # Checks step 22: Adding another special permission.
    elif step == "22":
        if (os.path.exists("/collections/project")):
            special_perm = get_special_perms("/collections/project")
            if special_perm == "1":
                # Successful, but create a text file for the next step.
                # We will hide the output of this command. If students are done with Step 23, they will receive an error. We want to hide that.
                # If write perms aren't yet (in the next step), this will behave normally.
                subprocess.run('sudo su - misty -c "echo Our progress is complete! > /collections/project/progress_report.txt" 2>/dev/null', shell=True)
                # Now, return success.
                sys.exit(0)
            else:
                sys.exit(1)

        # /collections/project cannot be found.
        else:
            sys.exit(3)

    # Checks step 23: Adding write protection.
    elif step == "23":
        # The project directory isn't accessible unless you're ash, misty, or brock. Need to use subprocesses for this part.
        # First, seeing if the text file exists.
        result = subprocess.run('sudo su - misty -c "test -f /collections/project/progress_report.txt"', shell=True)

        if (result.returncode == 0):
            # File exists. Now, getting the permissions.
            result = subprocess.run('sudo su - misty -c "stat -c "%a" /collections/project"', shell=True, capture_output=True)

            if (result.stdout == b'1550\n'):
                sys.exit(0)
            else:
                sys.exit(1)

        # /collections/project cannot be found.
        else:
            sys.exit(3)

    # Error occurred in the checker script.
    else:
        sys.exit(2)

main()
