#!/bin/bash

# Define the temporary directory and current user variables.
export TMP="/tmp/load"
export USER=$(whoami)

# Create the temporary directory if it doesn't exist.
mkdir -p $TMP

# Change to the temporary directory.
pushd $TMP

# Move the tarball into the temporary directory.
mv /tmp/${USER}_posix.tar.gz $TMP

# Extract the tarball while preserving permissions and ownerships.
sudo tar -xvpzf ${USER}_posix.tar.gz

# Check if the home directory contents exist in the temporary directory and move them to the appropriate places.
# Need to use the find command for this, since cp and mv are not working with directories and keeping permissions.
# The find command will limit the search to the immediate contents of the directory, then executes the move command of find's match
# to move the contents into the home directory.
if [ -d "${TMP}/home/${USER}/posix_practice/" ]; then
    sudo find "${TMP}/home/${USER}/posix_practice/" -mindepth 1 -maxdepth 1 -exec mv -t "/home/${USER}/posix_practice/" {} +
fi

if [ -d "${TMP}/home/${USER}/special_permissions/" ]; then
    sudo find "${TMP}/home/${USER}/special_permissions/" -mindepth 1 -maxdepth 1 -exec mv -t "/home/${USER}/special_permissions/" {} +
fi

# Check if /collections/ exists, move it if it does.
if [ -d "${TMP}/collections/" ]; then
    sudo rm -rf "/collections"
    sudo mv "${TMP}/collections" "/"
fi

# Checking if other users have been made and move them if they exist.
for user in ash brock misty james; do
    if [ -d "${TMP}/home/$user" ]; then
        sudo rm -rf "/home/$user"
        sudo mv "${TMP}/home/$user" "/home/"
    fi
done

# Check if the student has responses, and move them if they do.
if [ -d "${TMP}/home/.checker/responses" ]; then
    sudo mv "${TMP}/home/.checker/responses/"* "/home/.checker/responses/"
fi

# Copy the users/groups back. These "merge" the users back into /etc/*.
# If we overwrite instead of merging, then students will not be able to sign back in after loading.

# --- /etc/passwd ---
if [ -f "${TMP}/etc/passwd" ]; then
  while IFS=: read -r user pass uid gid gecos home shell; do
    [ -z "$user" ] && continue
    # If the user doesn't exist in real /etc/passwd, append
    if ! getent passwd "$user" >/dev/null; then
      echo "$user:$pass:$uid:$gid:$gecos:$home:$shell" | \
        sudo tee -a /etc/passwd >/dev/null
    fi
  done < <(sudo cat "${TMP}/etc/passwd")
fi

# --- /etc/group ---
if [ -f "${TMP}/etc/group" ]; then
  while IFS=: read -r groupname pass gid members; do
    [ -z "$groupname" ] && continue
    # If the group doesn't exist, append
    if ! getent group "$groupname" >/dev/null; then
      echo "$groupname:$pass:$gid:$members" | \
        sudo tee -a /etc/group >/dev/null
    fi
  done < <(sudo cat "${TMP}/etc/group")
fi

# --- /etc/shadow ---
if [ -f "${TMP}/etc/shadow" ]; then
  while IFS=: read -r user pass rest; do
    [ -z "$user" ] && continue
    # If the user isn't in real /etc/shadow, append
    if ! sudo grep -q "^${user}:" /etc/shadow; then
      echo "$user:$pass:$rest" | sudo tee -a /etc/shadow >/dev/null
    fi
  done < <(sudo cat "${TMP}/etc/shadow")
fi


# Return to the previous directory.
popd

# Clean up.
# rm -f $TMP/${USER}_posix.tar.gz
# sudo rm -rf $TMP
