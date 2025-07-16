#!/usr/bin/python3
import sys
import subprocess
import os

def main():
    if len(sys.argv) != 1:
        print("Usage: ./step_2.py")
        sys.exit(3)

    # Check ~/log_2 on node-0 (this one).
    if not os.path.exists(os.path.expanduser("~/log_2")):
        sys.exit(1)
    
    # Check ~/log_2 on node-1.
    node_1 = subprocess.run(
        ['ssh', 'node-1', '-o', 'StrictHostKeyChecking=no', 'test', '-f', '~/log_2'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    if (node_1.returncode != 0):
        sys.exit(2)

    # All checks passed.
    sys.exit(0)

if __name__ == '__main__':
    main()
