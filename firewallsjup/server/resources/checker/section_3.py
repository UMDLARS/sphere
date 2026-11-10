#!/usr/bin/python3
import sys
import os
import re
import subprocess
import socket

def main():
    # Checks usage.
    if (len(sys.argv) != 3):
        print("Usage: ./section_3.py <step> <answer>")
        sys.exit(2)

    step = sys.argv[1]
    answer = ' '.join(sys.argv[2].split())

    # Check Step 9
    if (step == "9"):
        if (answer == "-t filter"):
            # Correct answer. Save the response so that other steps can refer to it.
            f = open("/home/.checker/responses/step_9_answer.txt", "w+")
            f.write(answer)
            f.close()
            sys.exit(0)

        else:
            sys.exit(1)

    # Check Step 10.
    if (step == "10"):
        # Need a regular expression for checking this step.
        # This is checking if the answer is of the form '-A OUTPUT -o {eth1, ens3f0}' or
        # '-o {eth1, ens3f0} -A OUTPUT'
        # (I'm pretty sure this is longer than just including the whole list of possiblities lol)
        if (answer in [fmt for inf in ['eth1', 'ens3f0'] for fmt in [f"-o {inf} -A OUTPUT", f"-A OUTPUT -o {inf}"]]):
            # Correct answer. Save the response so that other steps can refer to it.
            f = open("/home/.checker/responses/step_10_answer.txt", "w+")
            f.write(answer)
            f.close()
            sys.exit(0)

        else:
            sys.exit(1)

    # Check Step 11.
    if (step == "11"):
        # Need a regular expression for checking this step.
        if (answer == "-m state --state NEW -p tcp" or answer == "-p tcp -m state --state NEW"):
            # Correct answer. Save the response so that other steps can refer to it.
            f = open("/home/.checker/responses/step_11_answer.txt", "w+")
            f.write(answer)
            f.close()
            sys.exit(0)

        else:
            sys.exit(1)

    # Check Step 12.
    if (step == "12"):
        # NOTE: Google's IP address changes depending on which server that gets pinged.
        # To allow this step to work over the world, get some "wildcard" IP addresses.
        ips = set()

        # Use dig to get all A records for google.com
        try:
            dig_result = subprocess.run(
                ["dig", "google.com", "+short", "A"],
                capture_output=True,
                text=True,
                check=True
            )
            dig_ips = dig_result.stdout.strip().splitlines()
            ips.update(dig_ips)
        except subprocess.CalledProcessError as e:
            print(f"Error executing dig: {e}")

        # Additionally, use socket to get all IP addresses
        try:
            addr_info = socket.getaddrinfo("google.com", None)
            socket_ips = {item[4][0] for item in addr_info if item[0] in (socket.AF_INET, socket.AF_INET6)}
            ips.update(socket_ips)
        except socket.gaierror as e:
            print(f"Error resolving hostname: {e}")

        # Optionally, remove any IPv6 addresses if you only need IPv4
        ips = {ip for ip in ips if '.' in ip}  # Keeps only IPv4 addresses

        # Convert the set to a sorted list for consistency
        ips = sorted(ips)

        # Use a regular expression to check if the student's answer is formatted correctly.
        pattern = (
            r"(?=.*-s\s+10\.0\.1\.1)"
            r"(?=.*-d\s+" + re.escape(ip) + r")"
            r"(?=.*--dport\s+1234)"
        )
        if not re.search(pattern, answer):
            sys.exit(1)

        # Check if the IP is in the list of google IPs.
        if ip not in ips:
            sys.exit(3)

        # Everything matches. Save and end successfully.
        with open("/home/.checker/responses/step_12_answer.txt", "w") as fp:
            f.write(answer)

        sys.exit(0)


    # Check Step 13.
    if (step == "13"):
        # This should be pretty self-explanatory.
        if (answer == "-j DROP"):
            f = open("/home/.checker/responses/step_13_answer.txt", "w")
            f.write(answer)
            f.close()
            sys.exit(0)

        else:
            sys.exit(1)


main()
