#!/bin/bash

# Define the temporary directory and user
export TMP="/tmp/save"
export USER=$(whoami)

# Prepare the temp directory
mkdir -p $TMP
pushd $TMP

# 1. Copy everything from /home/.checker/responses
mkdir -p "$TMP/home/.checker/responses"
cp -r /home/.checker/responses/* "$TMP/home/.checker/responses/" 2>/dev/null

# 2. Check if script2_modified.py or script3_modified.py exist
#    If not, check /tmp/analysis and copy as *_incomplete.py if found

# script2
if [ ! -f "$TMP/home/.checker/responses/script2_modified.py" ] && [ -f "/tmp/analysis/script2_modified.py" ]; then
    cp /tmp/analysis/script2_modified.py "$TMP/home/.checker/responses/script2_incomplete.py"
fi

# script3
if [ ! -f "$TMP/home/.checker/responses/script3_modified.py" ] && [ -f "/tmp/analysis/script3_modified.py" ]; then
    cp /tmp/analysis/script3_modified.py "$TMP/home/.checker/responses/script3_incomplete.py"
fi

# 3. Create and move tarball
tar -cvf "${USER}_dwarf.tar.gz" .
mv "${USER}_dwarf.tar.gz" ~

popd
rm -r $TMP

