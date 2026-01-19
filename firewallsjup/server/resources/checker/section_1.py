#!/usr/bin/python3
import sys
import shlex

def main():
    # Checks usage.
    if (len(sys.argv) != 3):
        print("Usage: ./section_1.py <step> <answer>")
        sys.exit(2)

    step = sys.argv[1]
    answer = ' '.join(sys.argv[2].split())

    # Check Step 1.
    if (step == "1"):
        if (answer == "nmap yahoo.com"):
            sys.exit(0)
        else:
            sys.exit(1)

    # Check Step 2.
    if (step == "2"):
        if (answer == "eth1"):
            sys.exit(0)
        else:
            sys.exit(1)

    # Check Step 3.
    if (step == "3"):
        # Split the answers.
        answers = answer.split("\\n")

        answer1 = answers[0].strip()
        answer2 = answers[1].strip()

        # Check the two solutions.
        if ((answer1 == "telnet localhost 80" or answer1 == "telnet 10.0.1.1 80") and answer2 == "GET /index.html"):
            sys.exit(0)

        else:
            sys.exit(1)

    # Check Step 4.
    if (step == "4"):
        # Split the answers.
        answers = answer.split("\\n")
        cmd = shlex.split(answers[0])

        # Must start with nc.
        if cmd[0] != "nc":
            sys.exit(1)

        # Valid flag patterns.
        valid_forms = [
            ["-l", "-p", "10000"],
            ["-p", "10000", "-l"],
            ["-lp", "10000"]
        ]

        # Remove 'nc'.
        args = cmd[1:]

        if args not in valid_forms:
            sys.exit(1)

        # Check second answer.
        if answers[1] not in ("nc server 10000", "nc 10.0.1.1 10000"):
            sys.exit(1)

        sys.exit(0)

main()
