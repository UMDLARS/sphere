#!/usr/bin/python3
import subprocess
import sys
import os
import time

def main():
    labname = sys.argv[1]

    # (No longer remove the existing file.)

    # Generate the backup via SSH as before.
    if labname == "xss":
        subprocess.run("ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@server '/home/.checker/save" + labname + ".sh'",
                       shell=True, stdout=subprocess.DEVNULL)
    elif labname == "firewalls":
        subprocess.run('ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@server "bash -l -c \'/home/.checker/savefirewalls.sh\'"',
                       shell=True, stdout=subprocess.DEVNULL)
    else:
        subprocess.run("ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@" + labname + " '/home/.checker/save" + labname + ".sh'",
                       shell=True, stdout=subprocess.DEVNULL)
    print("Backup tarball created.")

    # Define temporary and final filenames.
    dest_dir = "/home/USERNAME_GOES_HERE/saves"
    final_filename = os.path.join(dest_dir, "USERNAME_GOES_HERE_" + labname + ".tar.gz")
    temp_filename  = final_filename + ".new"

    # Copy the backup from the remote server using scp to a temporary file.
    if labname in ["xss", "firewalls"]:
        scp_cmd = "scp -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@server:~/" + os.path.basename(final_filename) + " " + temp_filename + " &> /dev/null"
    else:
        scp_cmd = "scp -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@" + labname + ":~/" + os.path.basename(final_filename) + " " + temp_filename + " &> /dev/null"
    subprocess.run(scp_cmd, shell=True, stdout=subprocess.DEVNULL)
    print("Backup tarball copied onto the XDC as a temporary file.")

    # Wait until the file has been transferred.
    while not os.path.exists(temp_filename):
        time.sleep(1)

    # Atomically replace (or create) the final file by renaming the temp file.
    os.rename(temp_filename, final_filename)
    print("New tarball has been moved into place.")

    # Delete the lab's tarball on the remote system.
    if labname in ["xss", "firewalls"]:
        subprocess.run("ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@server 'rm -f " + os.path.basename(final_filename) + " &> /dev/null'",
                       shell=True, stdout=subprocess.DEVNULL)
    else:
        subprocess.run("ssh -i /home/USERNAME_GOES_HERE/.ssh/merge_key USERNAME_GOES_HERE@" + labname + " 'rm -f " + os.path.basename(final_filename) + " &> /dev/null'",
                       shell=True, stdout=subprocess.DEVNULL)
    print("Remote tarball removed.")

main()