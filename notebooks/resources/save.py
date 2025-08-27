#!/usr/bin/python3
import subprocess
import sys
import os
import time
from enum import Enum

SSH_KEY = "/home/USERNAME_GOES_HERE/.ssh/merge_key"
USER = "USERNAME_GOES_HERE"
REMOTE_SERVER = "server"
SAVE_DIR = "/home/USERNAME_GOES_HERE/saves"

SPECIAL_HOSTS = {
    "xss": "server",
    "synflood": "server",
    "firewalls": "server",
    "worm": "node-0",
    "dwarf": "analysis",
}

def get_host(labname: str) -> str:
    """
    Return the remote host for a given lab.
    Uses SPECIAL_HOSTS if labname has a mapping,
    otherwise assumes host == labname.
    """
    return SPECIAL_HOSTS.get(labname.lower(), labname)

def run_ssh_command(host: str, command: str):
    subprocess.run(
        f"ssh -i {SSH_KEY} -o StrictHostKeyChecking=no {USER}@{host} '{command}'",
        shell=True,
        stdout=subprocess.DEVNULL
    )

def run_scp_command(host: str, remote_path: str, local_path: str):
    subprocess.run(
        f"scp -i {SSH_KEY} -o StrictHostKeyChecking=no {USER}@{host}:{remote_path} {local_path} &> /dev/null",
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

    host = get_host(labname)

    if labname.lower() == "firewalls":
        run_ssh_command(host, "bash -l -c '/home/.checker/savefirewalls.sh'")
    else:
        run_ssh_command(host, f"/home/.checker/save{labname}.sh")
    print("Backup tarball created.")

    run_scp_command(host, f"~/{remote_tarball}", temp_filename)
    print("Backup tarball copied onto the XDC as a temporary file.")

    while not os.path.exists(temp_filename):
        time.sleep(1)

    os.rename(temp_filename, final_filename)
    print("New tarball has been moved into place.")

    run_ssh_command(host, f"rm -f {remote_tarball} &> /dev/null")
    print("Remote tarball removed.")

if __name__ == "__main__":
    main()
