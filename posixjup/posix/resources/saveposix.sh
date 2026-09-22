#!/bin/bash

# Define the temporary directory and current user variables.
export TMP="/tmp/save"
export USER=$(whoami)

# Create the temporary directory if it doesn't exist.
mkdir -p $TMP

# Change to the temporary directory.
pushd $TMP

# Create the tarball while preserving permissions and ownerships.
sudo tar -cvpzf ${USER}_posix.tar.gz \
    --exclude="${USER}_posix.tar.gz" \
    /home/${USER}/posix_practice/ \
    /home/${USER}/special_permissions/ \
    /collections/ \
    /home/ash/ \
    /home/brock/ \
    /home/misty/ \
    /home/arthur/ \
    /home/.checker/responses \
    /etc/passwd \
    /etc/group \
    /etc/shadow

# Move the tarball to the home directory.
sudo chown ${USER}:${USER} ${USER}_posix.tar.gz
mv ${USER}_posix.tar.gz ~/

# Return to the previous directory.
popd

# Clean up.
sudo rm -rf $TMP