#!/bin/bash

# Define the temporary directory and user.
export TMP="/tmp/load"
export USER=$(whoami)

# Prepare the temp directory.
mkdir -p $TMP
pushd $TMP

# Move tarball to temp and extract.
mv ~/${USER}_dwarf.tar.gz $TMP
tar -xvf "${USER}_dwarf.tar.gz"

# Restore everything back to /home/.checker/responses.
mkdir -p /home/.checker/responses
cp -r "$TMP/home/.checker/responses/"* /home/.checker/responses/ 2>/dev/null

# Handle script2/script3 cases.
#  If modified versions exist, copy them to /home/.checker/responses (already done above).
#  If incomplete versions exist, move them to /tmp/analysis as modified versions.

# Moving script2 back.
if [ -f "$TMP/home/.checker/responses/script2_incomplete.py" ]; then
    cp "$TMP/home/.checker/responses/script2_incomplete.py" /tmp/analysis/script2_modified.py
fi

# Moving script3 back.
if [ -f "$TMP/home/.checker/responses/script3_incomplete.py" ]; then
    cp "$TMP/home/.checker/responses/script3_incomplete.py" /tmp/analysis/script3_modified.py
fi

popd
rm -f "/tmp/${USER}_dwarf.tar.gz"
rm -r $TMP
