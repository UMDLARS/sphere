#!/usr/bin/python3
import subprocess
import sys
import os
import time
from enum import Enum

SSH_KEY = "/home/umdclassmjwb/.ssh/merge_key"
USER = "umdclassmjwb"
REMOTE_SERVER = "server"
SAVE_DIR = "/home/umdclassmjwb/saves"

class LabHost(Enum):
    XSS = "server"
    SYNFLOOD = "server"
    FIREWALLS = "server"
    WORM = "node-0"

    @staticmethod
    def get_host(labname: str) -> str:
        mapping = {
            "xss": LabHost.XSS,
            "synflood": LabHost.SYNFLOOD,
            "firewalls": LabHost.FIREWALLS,
            "worm": LabHost.WORM
        }
        return mapping.get(labname.lower(), labname).value

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

    host = LabHost.get_host(labname)

    if labname == "firewalls":
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


main()
