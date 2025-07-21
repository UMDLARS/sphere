#!/bin/bash

# Define the temporary directory and current user variables.
export TMP="/tmp/save"
export USER=$(whoami)

# Create the temporary directory if it doesn't exist.
mkdir -p $TMP

# Change to the temporary directory.
pushd $TMP

# Save the logs from node-1.
scp node-1:~/log* "$TMP"

# Save the logs from node-0 (here).
cp ~/log* "$TMP" 2>/dev/null

# Check to see if the C files were made.
if [ -e "/home/.checker/responses/step_1_check.txt" ]; then
    mkdir -p "$TMP/home/.checker/responses"
    cp "/home/.checker/responses/step_1_check.txt" "$TMP/home/.checker/responses/"
fi

# Creating the save.
tar -cvf "${USER}_worm.tar.gz" .
mv "${USER}_worm.tar.gz" ~

# Return to the previous directory.
popd

# Clean up.
rm -r $TMP
