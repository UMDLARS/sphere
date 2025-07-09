#!/bin/bash

# Define the temporary directory and current user variables.
export TMP="/tmp/load"
export USER=$(whoami)

# Create the temporary directory if it doesn't exist.
mkdir -p $TMP

# Change to the temporary directory.
pushd $TMP

# Move the tarball into the temporary directory.
mv /tmp/${USER}_synflood.tar.gz $TMP

# Extract the tarball.
tar -xvf ${TMP}/${USER}_synflood.tar.gz

# If stream.sh exists, send it back to client:~/stream.sh.
if [ -e "${TMP}/stream.sh" ]; then
    scp stream.sh client:~/stream.sh
fi

# If step_2_response.txt exists, place it in /home/.checker/responses/.
if [ -e "${TMP}/step_2_response.txt" ]; then
    mkdir -p /home/.checker/responses
    cp step_2_response.txt /home/.checker/responses/step_2_response.txt
fi

# If step_3_response.txt exists, send it to attacker:~/../.checker/responses/.
if [ -e "${TMP}/step_3_response.txt" ]; then
    scp step_3_response.txt attacker:~/../.checker/responses/step_3_response.txt
fi

# Return to the previous directory.
popd

# Clean up.
rm -f /tmp/${USER}_synflood.tar.gz
rm -r $TMP

