#!/bin/bash

# Define the temporary directory and user.
export TMP="/tmp/save"
export USER=$(whoami)

# Prepare the temp directory.
mkdir -p $TMP
pushd $TMP

# Copy everything from "/home/.checker/responses".
mkdir -p "$TMP/home/.checker/responses"
cp -r /home/.checker/responses/* "$TMP/home/.checker/responses/" 2>/dev/null

# Check if "script2_modified.py" or "script3_modified.py" exist.
# If not, check /tmp/analysis and copy as *_incomplete.py if found.

# Student is still working on script2, and does not have a final version yet.
if [ ! -f "$TMP/home/.checker/responses/script2_modified.py" ] && [ -f "/tmp/analysis/script2_modified.py" ]; then
    cp /tmp/analysis/script2_modified.py "$TMP/home/.checker/responses/script2_incomplete.py"
fi

# Student is still working on script3, and does not have a final version yet.
if [ ! -f "$TMP/home/.checker/responses/script3_modified.py" ] && [ -f "/tmp/analysis/script3_modified.py" ]; then
    cp /tmp/analysis/script3_modified.py "$TMP/home/.checker/responses/script3_incomplete.py"
fi

# Create and move tarball.
tar -cvf "${USER}_dwarf.tar.gz" .
mv "${USER}_dwarf.tar.gz" ~

popd
rm -r $TMP
