#!/usr/bin/python3
import sys

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
        if ((answer1 == "telnet localhost 80" or answer1 == "telnet 10.0.1.1 80") and (answer2 == "GET /index.html" or answer2 == "GET /index.html HTTP/1.0")):
            sys.exit(0)

        elif "HTTP" in answer2:
            sys.exit(3)

        else:
            sys.exit(1)

    # Check Step 4.
    if (step == "4"):
        # Split the answers.
        answers = answer.split("\\n")

        required_params = ["-l", "-p 10000"]

        other_components_present = all(component in answers[0] for component in required_params)

        # Check the two solutions.
        if (answers[0].startswith("nc") and other_components_present and (answers[1] == "nc server 10000" or answers[1] == "nc 10.0.1.1 10000")):
            sys.exit(0)

        else:
            sys.exit(1)


main()
