#!/usr/bin/python3
import subprocess
import sys
import os
import time

def main():
    labname = sys.argv[1]

    # Check to see if the node is reachable.
    if (labname == "xss" or labname == "firewalls"):
        process = subprocess.run('ping -c 3 server', shell=True, stdout=subprocess.DEVNULL)
    else:
        process = subprocess.run('ping -c 3 ' + labname, shell=True, stdout=subprocess.DEVNULL)

    # Cannot be reached.
    if (process.returncode == 2):
        sys.exit(2)

    # Successfully pinged. Moving data.
    elif (process.returncode == 0):
        if (labname == "xss" or labname == "firewalls"):
            # Node is available. Proceed to transfer over the backup.
            process = subprocess.run("scp -i /home/USERNAME_GOES_HERE/.ssh/merge_key /home/$USER/saves/USERNAME_GOES_HERE_" + labname + ".tar.gz USERNAME_GOES_HERE@server:/tmp", shell=True, stdout=subprocess.DEVNULL)
        else:
            # Node is available. Proceed to transfer over the backup.
            process = subprocess.run("scp -i /home/USERNAME_GOES_HERE/.ssh/merge_key /home/$USER/saves/USERNAME_GOES_HERE_" + labname + ".tar.gz USERNAME_GOES_HERE@" + labname + ":/tmp", shell=True, stdout=subprocess.DEVNULL)

        # Check to make sure that the tarball was transferred before calling the load script for the lab.
        # This is to prevent a race condition, much like the save.py file.
        transfer_success = False

        # Start to validate that the tarball was transferred.
        while (transfer_success == False):
            if (labname == "xss" or labname == "firewalls"):
                process = subprocess.run("ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key server 'test -f /tmp/USERNAME_GOES_HERE_" + labname + ".tar.gz'", shell=True, stdout=subprocess.DEVNULL)
            else:
                process = subprocess.run("ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key " + labname + " 'test -f /tmp/USERNAME_GOES_HERE_" + labname + ".tar.gz'", shell=True, stdout=subprocess.DEVNULL)
            if (process.returncode == 0):
                transfer_success = True

        # Transfer validated. Begin the load command for the respective lab.
        if (labname == "xss" or labname == "firewalls"):
            process = subprocess.run("ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key server '/home/.checker/load" + labname + ".sh'", shell=True, stdout=subprocess.DEVNULL)

        else:
            process = subprocess.run("ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key " + labname + " '/home/.checker/load" + labname + ".sh'", shell=True, stdout=subprocess.DEVNULL)
            
        sys.exit(1)

    # For other return codes.
    else:
        sys.exit(0)

main()
