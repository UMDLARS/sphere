#!/usr/bin/python3
import subprocess
import sys
import os
import time
from enum import Enum

SSH_KEY = "/home/USERNAME_GOES_HERE/.ssh/merge_key"
USER = "USERNAME_GOES_HERE"
REMOTE_SERVER = "server"
SAVE_DIR = f"/home/{USER}/saves"

from enum import Enum

class LabHost(Enum):
    XSS = "server"
    SYNFLOOD = "server"
    FIREWALLS = "server"
    WORM = "node-0"
    DWARF = "analysis"

    @staticmethod
    def get_host(labname: str) -> str:
        mapping = {
            "xss": LabHost.XSS,
            "synflood": LabHost.SYNFLOOD,
            "firewalls": LabHost.FIREWALLS,
            "worm": LabHost.WORM,
            "dwarf": LabHost.DWARF
        }
        return getattr(mapping.get(labname.lower()), "value", labname)

def run_command(command: str):
    return subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)

def is_node_reachable(host: str) -> bool:
    result = run_command(f"ping -c 3 {host}")
    return result.returncode == 0

def transfer_tarball(labname: str, host: str) -> bool:
    local_tarball = os.path.join(SAVE_DIR, f"{USER}_{labname}.tar.gz")
    remote_path = f"{USER}@{host}:/tmp"
    cmd = f"scp -i {SSH_KEY} -o StrictHostKeyChecking=no {local_tarball} {remote_path}"
    run_command(cmd)

    # Wait until the file appears on the remote side
    remote_file = f"/tmp/{USER}_{labname}.tar.gz"
    while True:
        test_cmd = f"ssh -i {SSH_KEY} {USER}@{host} 'test -f {remote_file}'"
        if run_command(test_cmd).returncode == 0:
            return True
        time.sleep(1)

def run_load_script(labname: str, host: str):
    load_script = f"/home/.checker/load{labname}.sh"
    cmd = f"ssh -i {SSH_KEY} -o StrictHostKeyChecking=no {USER}@{host} '{load_script}'"
    run_command(cmd)

def main():
    if len(sys.argv) != 2:
        print("Usage: ./load.py <labname>")
        sys.exit(1)

    labname = sys.argv[1]
    host = LabHost.get_host(labname)

    if not is_node_reachable(host):
        sys.exit(2)

    print("Node is reachable. Transferring backup...")
    if transfer_tarball(labname, host):
        print("Transfer confirmed. Executing load script...")
        run_load_script(labname, host)
        print("Load script executed.")

    sys.exit(1)


main()
