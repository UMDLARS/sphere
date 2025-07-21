#!/bin/bash

# Define the temporary directory and current user variables.
export TMP="/tmp/load"
export USER=$(whoami)

# Create the temporary directory if it doesn't exist.
mkdir -p $TMP

# Change to the temporary directory.
pushd $TMP

# Move the tarball to the temp directory and extract it.
mv ~/${USER}_worm.tar.gz $TMP
tar -xvf "${USER}_worm.tar.gz"

# Restore local logs from node-0.
[ -e "$TMP/log_node-0" ] && cp "$TMP/log_node-0" ~/log
[ -e "$TMP/log_2_node-0" ] && cp "$TMP/log_2_node-0" ~/log_2

# Restore remote logs to node-1.
[ -e "$TMP/log_node-1" ] && scp "$TMP/log_node-1" node-1:~/log
[ -e "$TMP/log_2_node-1" ] && scp "$TMP/log_2_node-1" node-1:~/log_2

# Restore step_1_check.txt and run make if needed.
if [ -e "$TMP/home/.checker/responses/step_1_check.txt" ]; then
    mkdir -p "/home/.checker/responses"
    cp "$TMP/home/.checker/responses/step_1_check.txt" "/home/.checker/responses/"

    # Run "sudo make" on node-0.
    if [ -d "/tmp/node-0/paws" ]; then
        sudo make -C /tmp/node-0/paws
    fi

    # Run "sudo make" on node-1.
    ssh node-1 'sudo make -C /tmp/node-1/paws'
fi

# Return to the previous directory.
popd

# Clean up.
rm -f "/tmp/${USER}_worm.tar.gz"
rm -r $TMP
