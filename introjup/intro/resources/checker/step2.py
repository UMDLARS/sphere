#!/usr/bin/python3
import subprocess
import sys
import os

def check_perms(path):
    mode = os.stat(path).st_mode
    permissions = oct(mode)[-3:]

    # Permissions were not changed from default.
    if (permissions == '644'):
        sys.exit(2)
    else:
        f = open("/home/.checker/step2_perms.txt", "w+")
        f.write(permissions)
        f.close()
        sys.exit(0)

def main():
    path = os.path.expanduser("~/jupyterintro/jupytertest.txt")

    # Check to make sure that the path was made.
    ret = os.path.exists(path)

    # Check logs to see if the student made it. Mainly used for save/restore.
    check_job = subprocess.run("screen -ls | grep 'inotify_session' &> /dev/null", shell=True, stdout=subprocess.DEVNULL)

    # If not tracking mkdir, run it. Student may fail the test, but will work if they try again.
    if (check_job.returncode == 1):
        # Missed. Run the job again because it may have been cancelled somehow.
        command = "./.run_inotify.sh"
        process = subprocess.run(command, shell=True)

    # touch was tracked. Search for it in the logs.
    else:
        if (os.path.exists('/home/.checker/inotify_log.txt')):
            with open('/home/.checker/inotify_log.txt', 'r') as file:
                log_contents = file.read()
                if ("jupyterintro/ CREATE jupytertest.txt" in log_contents):
                    # File was created. Check if perms were made.
                    if os.path.exists("/home/.checker/step2_perms.txt"):
                        sys.exit(0)

                    # Otherwise, if the file doesn't exist yet, we will check the logs.
                    elif (not os.path.exists(path) and \
                          "/home/USERNAME_FOR_NODE/jupyterintro/ ATTRIB jupytertest.txt" in log_contents):
                        sys.exit(0)

                    # File exists, so we will check it directly.
                    else:
                        check_perms(path)

                # Perms were never changed.
                else:
                    sys.exit(1)

    # If not using a restore, just simply check if it exists.
    # Very likely that this will never occur.
    if ret:
        check_perms(path)
    else:
        sys.exit(1)

main()
