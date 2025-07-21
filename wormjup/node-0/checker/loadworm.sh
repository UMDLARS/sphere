#!/bin/bash

# Define the temporary directory and current user variables.
export TMP="/tmp/load"
export USER=$(whoami)

# Create the temporary directory if it doesn't exist.
mkdir -p $TMP

# Change to the temporary directory.
pushd $TMP

# Move the worm lab tarball to the temp directory and extract it.
mv ~/ ${USER}_worm.tar.gz $TMP
tar -xvf "${USER}_worm.tar.gz"

# Restore ~/log* files.
cp "$TMP/log"* ~ 2>/dev/null

# Restore /home/.checker/responses/step_1_check.txt if present.
if [ -e "$TMP/home/.checker/responses/step_1_check.txt" ]; then
    mkdir -p "/home/.checker/responses"
    cp "$TMP/home/.checker/responses/step_1_check.txt" "/home/.checker/responses/"

    # Run `sudo make` on both node-0 and node-1 if step_1_check.txt exists.
    # Local (node-0) make.
    if [ -d "/tmp/node-0/paws" ]; then
        sudo make -C /tmp/node-0/paws
    fi

    # Remote (node-1) make via SSH.
    ssh node-1 'sudo make -C /tmp/node-1/paws'
fi

# Return to previous directory.
popd

# Clean up.
rm -f "/tmp/${USER}_worm.tar.gz"
rm -r $TMP
