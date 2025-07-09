#!/usr/bin/python3
import subprocess
import sys
import os
import time

SSH_KEY = "/home/USERNAME_GOES_HERE/.ssh/merge_key"
USER = "USERNAME_GOES_HERE"
REMOTE_SERVER = "server"
SAVE_DIR = "/home/USERNAME_GOES_HERE/saves"

def run_ssh_command(host: str, command: str):
    subprocess.run(
        f"ssh -i {SSH_KEY} {USER}@{host} '{command}'",
        shell=True,
        stdout=subprocess.DEVNULL
    )

def run_scp_command(host: str, remote_path: str, local_path: str):
    subprocess.run(
        f"scp -i {SSH_KEY} {USER}@{host}:{remote_path} {local_path} &> /dev/null",
        shell=True,
        stdout=subprocess.DEVNULL
    )

def main():
    if len(sys.argv) != 2:
        print("Usage: ./save.py <labname>")
        sys.exit(1)

    labname = sys.argv[1]
    final_filename = os.path.join(SAVE_DIR, f"{USER}_{labname}.tar.gz")
    temp_filename = f"{final_filename}.new"
    remote_tarball = os.path.basename(final_filename)

    # Run remote save script.
    # For the lab names that do not have a node named after the lab name itself... 
    if labname == "xss" or labname == "synflood":
        run_ssh_command(REMOTE_SERVER, f"/home/.checker/save{labname}.sh")
    # Special command for the firewalls lab.
    elif labname == "firewalls":
        run_ssh_command(REMOTE_SERVER, "bash -l -c '/home/.checker/savefirewalls.sh'")
    # Everything else.
    else:
        run_ssh_command(labname, f"/home/.checker/save{labname}.sh")
    print("Backup tarball created.")

    # Copy file from remote server.
    scp_host = REMOTE_SERVER if labname in ["xss", "firewalls", "synflood"] else labname
    run_scp_command(scp_host, f"~/{remote_tarball}", temp_filename)
    print("Backup tarball copied onto the XDC as a temporary file.")

    # Wait for file transfer to complete.
    while not os.path.exists(temp_filename):
        time.sleep(1)

    # Atomically move file into place.
    os.rename(temp_filename, final_filename)
    print("New tarball has been moved into place.")

    # Clean up remote tarball.
    run_ssh_command(scp_host, f"rm -f {remote_tarball} &> /dev/null")
    print("Remote tarball removed.")

main()
