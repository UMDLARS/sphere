#!/bin/bash

# Define the temporary directory and current user variables.
export TMP="/tmp/save"
export USER=$(whoami)

# Create the temporary directory if it doesn't exist.
mkdir -p $TMP

# Change to the temporary directory.
pushd $TMP

# Save logs from node-1 and rename them.
scp node-1:~/log "$TMP/log_node-1" 2>/dev/null
scp node-1:~/log_2 "$TMP/log_2_node-1" 2>/dev/null

# Save logs from node-0 (local) and rename them.
[ -e ~/log ] && cp ~/log "$TMP/log_node-0"
[ -e ~/log_2 ] && cp ~/log_2 "$TMP/log_2_node-0"

# Save step_1_check.txt if it exists.
if [ -e "/home/.checker/responses/step_1_check.txt" ]; then
    mkdir -p "$TMP/home/.checker/responses"
    cp "/home/.checker/responses/step_1_check.txt" "$TMP/home/.checker/responses/"
fi

# Create tarball.
tar -cvf "${USER}_worm.tar.gz" .
mv "${USER}_worm.tar.gz" ~

# Return to the previous directory.
popd

# Clean up.
rm -r $TMP
