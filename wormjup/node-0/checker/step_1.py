#!/usr/bin/python3
import os
import sys
import subprocess

def main():
    if len(sys.argv) != 1:
        print("Usage: ./step_1.py")
        sys.exit(4)

    # Check on node-0.
    if not (os.path.isfile('/tmp/node-0/paws/paws_server') and
            os.path.isfile('/tmp/node-0/paws/paws_client')):
        sys.exit(1)

    # Check on node-1.
    server = subprocess.run(
        ['ssh', 'node-1', '-o', 'StrictHostKeyChecking=no', 'test', '-f', '/tmp/node-1/paws/paws_server'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    client = subprocess.run(
        ['ssh', 'node-1', '-o', 'StrictHostKeyChecking=no', 'test', '-f', '/tmp/node-1/paws/paws_client'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
   
    if (server.returncode != 0 or client.returncode != 0):
        sys.exit(2)

    # Check for paws_RT.dat.gz on node-1.
    extracted_file = subprocess.run(
        ['ssh', 'node-1', '-o', 'StrictHostKeyChecking=no', 'test', '-f', '/tmp/node-1/paws/paws_RT.dat'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if (extracted_file.returncode != 0):
        sys.exit(3)

    # Otherwise, all steps pass.
    sys.exit(0)

if __name__ == '__main__':
    main()
