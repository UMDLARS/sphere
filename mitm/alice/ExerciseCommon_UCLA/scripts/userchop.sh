#!/bin/bash

# remove all users that have been added to this node.  
# ---------------------------------------------------
# It can be useful to remove student access from a given node in order to keep
# secrets from them.  Users that are group_root in the project will still have
# root access to the node using their passwordless ssh key.
#
# As per Keith Sklower, accounts added to the node are listed in:
#
# /var/emulab/boot/tmcc/accounts 
#
# ... and per Ted Faber, accounts added to containerized nodes are listed in:
#
# /var/containers/config/accounts.yaml
#
# We will remove all these users.

# REMOVE THE EXTRANEOUS USERS
#
# back up original files
cp /etc/passwd /etc/passwd.mitm

# determine whether we are running on DC (Deter Classic) or in 
# a c7rized (containerize) environment, and get the appropriate user list.

# WHATAMI=$( $INSTALL_UCLA/whatami )

# if grep pnode <<< $WHATAMI
# then

	# this is a bare-metal Deter node running the standard software

	# Write just a list of the usernames to a file for later use:
	grep ADDUSER /var/emulab/boot/tmcc/accounts | awk '{ print $2 }' | sed 's/LOGIN=//' > /tmp/lusernames.txt

# else
# 
# 	# we are running inside a container and must do something different
# 	if ! find /usr | grep yaml | grep python &> /tmp/yaml_test.txt
# 	then
# 		if grep -i ubuntu <<< $WHATAMI
# 		then
# 			sudo apt-get install -y python-yaml
# 		elif grep -i centos <<< $WHATAMI
# 		then
# 			sudo yum install -y PyYAML
# 		fi
# 	fi
# 
# 	# use yaml_getusers.py to write the list of added users to a file
# 	/share/education/containerized/ExerciseCommon/bin/yaml_getusers.sh > /tmp/lusernames.txt
# 
# fi

# strip those users from /etc/passwd
grep -v -f /tmp/lusernames.txt /etc/passwd > /tmp/passwd.strip

# replace /etc/passwd
mv /tmp/passwd.strip /etc/passwd
chown root:root /etc/passwd
chmod 644 /etc/passwd

# CHANGE ROOT'S PASSWORD
#
# Students can use 'console' access to log on as root (since the root
# password is known). Accordingly, we need to change root's password.

sudo usermod -p '$6$vH0ZIvdR$m9evPtI8c5fn8STiPKaE9BVrsuo52ACR.GUCfDJLNQFdR9o8HLK6D8Apw0EBsxP5Xj/gxM4cSscwnVeHrVz/s.' root
