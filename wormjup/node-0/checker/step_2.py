#!/usr/bin/python3
import sys
import subprocess
import os

def main():
    if len(sys.argv) != 1:
        print("Usage: ./step_2.py")
        sys.exit(3)

    # Check ~/log on node-0 (this one).
    if not os.path.exists(os.path.expanduser("~/log")):
        sys.exit(1)
    
    # Check ~/log on node-1.
    node_1 = subprocess.run(
        ['ssh', 'node-1', '-o', 'StrictHostKeyChecking=no', 'test', '-f', '~/log'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    if (node_1.returncode != 0):
        sys.exit(2)

    # All checks passed.
    sys.exit(0)

if __name__ == '__main__':
    main()
