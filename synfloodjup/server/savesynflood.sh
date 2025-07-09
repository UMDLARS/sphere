# Define the temporary directory and current user variables.
export TMP="/tmp/save"
export USER=$(whoami)

# Create the temporary directory if it doesn't exist.
mkdir -p $TMP

# Change to the temporary directory.
pushd $TMP

# Attempt to copy the student's stream.sh file over.
scp -o StrictHostKeyChecking=no client:~/stream.sh .
if [ -e "/home/.checker/stream.sh" ]; then
    cp "/home/.checker/stream.sh" $TMP
    rm -f "/home/.checker/stream.sh"
fi

# Attempt to copy over their text files from tcpdump.
scp -o StrictHostKeyChecking=no client:~/tcpdump_cookies* .
if [[ -f tcpdump_cookies_off.txt && -f tcpdump_cookies_on.txt ]]; then
    cp tcpdump_cookies_off.txt tcpdump_cookies_on.txt "$TMP"
    echo "Files copied to $TMP"
fi

# Check if step_2_response.txt exists and copy it if it does.
if [ -e "/home/.checker/responses/step_2_response.txt" ]; then
    cp "/home/.checker/responses/step_2_response.txt" $TMP
fi

# Check if step_3_response.txt exists in the attacker node and copy it if it does.
scp -o StrictHostKeyChecking=no attacker:~/../.checker/responses/step_3_answer.txt .
if [ -e "/home/.checker/step_3_answer.txt" ]; then
    cp "/home/.checker/step_3_answer.txt" $TMP
    rm -f "/home/.checker/step_3_answer.txt"
fi

# Create the tarball, then move it to the home directory temporarily to scp it over.
tar -cvf ${USER}_synflood.tar.gz .
mv ${TMP}/${USER}_synflood.tar.gz ~

# Return to the previous directory.
popd

# Clean up.
rm -r $TMP
