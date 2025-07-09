#!/usr/bin/python3
import sys
import shlex

# Required options and their expected values
REQUIRED_PARAMS = {
    "--dst": "server",
    "--highrate": "100",
    "--proto": "6",
    "--src": "1.1.2.0",
    "--srcmask": "255.255.255.0"
}

def main():
    if len(sys.argv) != 2:
        print("Usage: ./check_flooder.py 'Your Answer Here'")
        sys.exit(1)

    # Parse the command string into arguments (like a shell)
    try:
        args = shlex.split(sys.argv[1])
    except ValueError as e:
        print(f"Error parsing command: {e}")
        sys.exit(1)

    # Check prefix
    if len(args) < 2 or args[0] != "sudo" or args[1] != "flooder":
        sys.exit(2)

    # Build a dictionary of options and values
    arg_dict = {}
    i = 2  # start after "sudo flooder"
    while i < len(args) - 1:
        if args[i].startswith("--"):
            arg_dict[args[i]] = args[i + 1]
            i += 2
        else:
            i += 1

    # Check required parameters
    for key, value in REQUIRED_PARAMS.items():
        if arg_dict.get(key) != value:
            sys.exit(3)

    sys.exit(0)

main()
