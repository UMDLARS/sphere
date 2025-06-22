# UMD Duluth Computer Security Labs (CS 4332/5332) 💻  
*By Eric Nieters and Dr. Peter A. H. Peterson*

Welcome to the **UMD Duluth Computer Security Labs Repository**. This repository contains a set of carefully designed labs for **CS 4332/5332: Computer Security** at the University of Minnesota Duluth.

## About These Labs 📖

These labs are developed to provide hands-on experience in **computer security** concepts. Through structured exercises, students explore real-world security challenges, vulnerabilities, and defensive techniques.

Here are the currently available labs, which are fully designed and ready for classroom use:

- Intro to SPHERE
- POSIX Permissions
- Buffer Overflows
- Pathname Attacks
- SQL Injection
- Cross-Site Scripting (XSS)
- Firewalls

**NOTE:** An active SPHERE account is required in order to use these labs. If you do **not** have a SPHERE account and:
- If you **are NOT** enrolled in a class: You will need to register for an account [here](https://edu.sphere-testbed.net/registration?flow=6c1b4d12-1ae7-4532-8d04-7a677ad2436c), and your account must be activated by administrators at SPHERE.
- If you **ARE** enrolled in a class: Your professor and/or TA(s) will provide you with login credentials and directions on how to use these labs.

## Who Are They Made For? 🧑‍🎓

These labs are designed for:

- **Undergraduate (CS 4332) and Graduate (CS 5332) students** at UMD taking Computer Security.
- **Self-learners** interested in exploring security fundamentals hands-on.
- **Educators and researchers** looking for structured security exercises.
- **Industry professionals** who want to sharpen their security skills.

Each lab includes **readings and guided exercises** to ensure accessibility for all levels of learners. You are expected to have some basic knowledge of programming before starting these labs. Additionally, some knowledge in Unix is recommended. If you are not familiar with Unix environments, consider starting with the **Intro** lab.

## Goal 🚀

The primary goal of these labs is to help students develop **a security mindset** by:

- Understanding how real-world attacks work.
- Learning how to exploit vulnerabilities in controlled environments.
- Developing defenses against security threats.
- Encouraging ethical security research and best practices.

By completing these labs, students will gain **practical cybersecurity skills** applicable in academic research, industry, and ethical hacking.

## Terminology 📝

Below is a list of nouns that are used when discussing the SPHERE architecture. These resources will be automatically generated for you with our scripts and notebooks.

- **Experimental Development Container (XDC):** A JupyterLab environment hosted by SPHERE, giving you access to a private Debian environment for testing.
- **Projects:** A collection of experiments that have been created on your account.
- **Node:** A server hosted from SPHERE.
- **Experiment:** A topology of nodes.
- **Reservation:** A request of resources for your experiment.
- **Activation:** A resource containing your live reservation.

# For Instructors & Future Collaborators 👨‍🏫

## How To Set Up Your Classroom 🏫

To begin using these labs in your class, you must have access to the Merge CLI (command line interface). This is used to automate some scripts which will make registration easier for your students. You may download the CLI [here](https://gitlab.com/mergetb/portal/cli/-/releases). There are plenty of releases available.

### Preliminary Setup ⚙️

First, identify your operating system. If you have one of the following operating systems, search for a release with these in the name:
- **Windows:** `windows`
- **MacOS:** `darwin`
- **Linux:** A release that ends with `.deb` (Debian package).

Additionally, you will need to select a release that aligns with your processor. Find your processor below, and download a release that supports your architecture:
- **Intel:** `amd64`
- **AMD:** `amd64`
- **Apple Silicon:** `arm64`

Before continuing with the steps below, find a valid combination of operating system and architecture that works with your machine. For example, if you have a Linux machine with an Intel processor, you will need to download `mrg_X.X.X_linux_amd64.deb`. To verify that your installation is correct, run the following command:
- **Windows:** Using a terminal, navigate to the `mrg` executable that you unzipped and type `mrg`.
- **MacOS/Linux:** After installing the release, type `mrg`. You do not need to be in a specific folder.

If the command is detected, then you are ready to move on to the steps below.

### Creating Your Students' Accounts 🧑‍💻

1. Create the SPHERE accounts for your students. You may follow the documentation [here](https://mergetb.gitlab.io/testbeds/sphere/sphere-docs/docs/experimentation/classes/) to learn how to set up class accounts.
2. Once you have created the accounts, provide the list of usernames/passwords to your students. However, it is recommended to wait until each step before distributing the login credentials. As of 3/1/2025, a username/password will not be emailed to your students automatically. [SPHERE will implement this in the future](https://mergetb.gitlab.io/testbeds/sphere/sphere-docs/docs/experimentation/classes/#:~:text=We%E2%80%99re%20working%20on%20emailing%20the%20students%E2%80%99%20their%20passwords%2C%20and%20hope%20to%20release%20this%20feature%20by%20September%2015%2C%202024.).
3. Create a directory on your machine. This directory will contain some important scripts, like auto-grading and auto-generation within SPHERE.
4. Download `install_notebooks.sh` from this repository and store it in that directory.
5. Create a script called `users.sh` and store your students' usernames/passwords as follows:

    ```bash
    declare -A USERS
    USERS=(
        ["umdclassXXXA"]="password1"
        ["umdclassXXXB"]="password2"
        # Add more usernames here...
    )
    ```

6. Create a script called `generate_xdc.sh`, which will create the testing environments for your students. Copy and paste the script below, then run it:

    ```bash
    #!/bin/bash

    # Sourcing the usernames/passwords from users.sh.
    source users.sh

    # Iterate over each user
    for USERNAME in "${!USERS[@]}"; do
        PASSWORD="${USERS[$USERNAME]}"

        # Sign into the student's account.
        mrg login "$USERNAME" -p "$PASSWORD"
        if [ $? -ne 0 ]; then
            echo "Unsuccessful login: $USERNAME"
            continue
        fi

        # Create their XDC.
        mrg new xdc xdc."$USERNAME"
        if [ $? -ne 0 ]; then
            echo "Unable to create an XDC for $USERNAME."
        else
            echo "XDC for $USERNAME was created successfully."
        fi

        # Give yourself access to their XDCs. Replace <...> with your username (without < > around it).
        # This command may be repeated for additional instructors/TAs.
        mrg new member project "$USERNAME" <YOUR SPHERE USERNAME HERE>

        # Logout of the account.
        mrg logout
    done

    echo "Complete."
    ```

7. Once all XDCs have been generated, create a script called `send_install_script.sh` **within the same directory** as `users.sh`. Copy and paste the script below, then run it:

    ```bash
    #!/bin/bash

    # Sourcing the usernames/passwords from users.sh.
    source users.sh

    # Iterate over each user
    for USERNAME in "${!USERS[@]}"; do
        PASSWORD="${USERS[$USERNAME]}"

        # Sign into the student's account.
        mrg login "$USERNAME" -p "$PASSWORD"
        if [ $? -ne 0 ]; then
            echo "Unsuccessful login: $USERNAME"
            continue
        fi

        # Using scp to copy the script to their accounts.
        mrg xdc scp upload install_notebooks.sh "xdc.$USERNAME:/project/$USERNAME"

        if [ $? -ne 0 ]; then
            echo "Unable to upload the script to $USERNAME."
            continue
        fi

        # Logout of the account.
        mrg logout
    done

    echo "Complete."
    ```

Once you have completed the final step, all students' accounts and testbeds will have been created, and you will have access to their XDCs from SPHERE.

## Grading Your Students 📊

A grading script is available in our private `sphere_instructors` repository. Please contact us below if you'd like permission to access this repo.

## Features For Students 🌟

- Hands-on learning exercises
- Optional exercises for curious students
- Instant, dynamic feedback
- Auto-saving
- Auto-installation and updates
- HTML responses from executing payloads
- Split-screen for notebook and terminal
- Automatic grading
- Loading spinners for longer tasks
- Automatic file generation during progression
- Fill-in-the-blank and memo exercises
- Notebooks tailor username into commands
- Automatic port forwarding setup
- References to programming documentation
- Diagrams to explain exploits
- Automatic lab suspension to free resources
- Topic breakdowns with different goals
- Examples of successful patches/payloads
- Custom-built websites with unsafe code
- Exploits start small, and grow larger in later topics

## Features For Instructors 👩‍🏫

- Remote lab access to aid students
- One-click autograder for all students
- Direct support with SPHERE DevOps
- Timestamped progress from students
- Template for custom labs
- Source code for notebooks to edit changes
- Read memos written by students

## Interested in Contributing? 💡

If you're an instructor or researcher interested in **collaborating**, feel free to open an issue or contact us to become a collaborator. Contributions that enhance lab quality, introduce new exercises, or improve accessibility are always welcome!

## Contact 📩

If you have questions, suggestions, or want to contribute, please reach out to an author:

- **Eric Nieters:** [niete018@d.umn.edu]
- **Dr. Peter A. H. Peterson:** [pahp@d.umn.edu]
- **UMD CS Department:** [https://scse.d.umn.edu/departments-and-programs/computer-science]

## License 📜

These labs are distributed under the **[Creative Commons Attribution-NonCommercial (CC BY-NC 4.0)]** license. See [`LICENSE`](LICENSE) for details.

## Research 🔬

These labs were designed to evaluate students' comprehension as part of a cybersecurity pedagogy thesis. A link to this thesis write-up will be available once it is published.
