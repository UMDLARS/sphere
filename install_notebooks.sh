#!/bin/bash

export USER="$(whoami)"
export LABS="/home/$USER"
export RESOURCES="$LABS/resources"
export SAVES="$LABS/saves"
export EDUCATION="/home/niete018/.education"

# Check if the student is running as root.
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script as sudo."
    exit 1
fi

# Define the directory where the repository should be checked out.
REPO_URL="https://github.com/UMDLARS/sphere"

# Installing some dependencies.
echo "Installing dependencies."
sudo apt-get -qq update
sudo apt-get -qq install git rsync >/dev/null

# sudo is required for these, since the notebooks are ran as root. Hiding the warning about installing packages as root.
echo "Installing required Jupyter extensions."

# NOTE: New changes to SPHERE moved stuff into a venv. We will need to apply some changes before we can install this.

# Making a change in a config file to fix a known issue, enabling the venv, then installing the packages.
# This "sed" command is a workaround, but apparently doesn't fix the issue when installing ipywidgets.
sudo sed -i "s|include-system-site-packages = false|include-system-site-packages = true|g" /usr/local/jupyter/venv/pyvenv.cfg
source /usr/local/jupyter/venv/bin/activate
sudo pip install -q ipywidgets jupyterlab_widgets 2>/dev/null
deactivate

echo "Beginning installation of notebooks."

# Use a temporary directory for cloning.
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR" || exit

# Clone the repository.
git clone "$REPO_URL"
if [ $? -ne 0 ]; then
    echo -e "\033[0;31mFailed to clone the repository. Exiting.\033[0m"
    exit 1
fi

cd sphere || exit

# Checking to see if the notebooks have already been made.
if [ $(find "$LABS" -maxdepth 1 -type f -name "*.ipynb" | wc -l) -eq 8 ]; then
    echo -e "\033[0;31mYour notebooks already exist. Updating your notebooks...\033[0m"
else
    echo -e "\033[0;31mSome (or all) of your notebooks appear to be missing. Adding them...\033[0m"
fi

# Saving the student's logs.
[ -f "$EDUCATION/${USER}_logs.txt" ] && mv "$EDUCATION/${USER}_logs.txt" /tmp

# Excluding the following files:
## saves/ so that students don't lose progress.
## pass.txt so that students don't lose their configuration.
## .local/ so that the kernel doesn't break when running the command.
sudo rsync -a --delete --exclude='saves/' --exclude='pass.txt' --exclude='.local/' notebooks/ ~ >/dev/null

# Ensure 'saves/' exists.
mkdir -p $LABS/saves

# Move the lab resources.
if [ -d "/home/niete018/.education" ]; then
    echo -e "\033[0;31mLab resources for your notebooks already exist. Applying updates...\033[0m"

    # Delete the education directory so that it can be updated. mv will not work if there are already files.
    sudo rm -rf /home/niete018/.education/*
else
    echo -e "\033[0;31mLab resources do not exist on your XDC. Creating them...\033[0m"
    sudo mkdir -p "/home/niete018/.education"
    sudo chown -R "$USER:$USER" "/home/niete018/.education"
fi

# Find and copy all directories ending with 'jup' to the $EDUCATION directory.
for dir in $(find . -maxdepth 1 -type d -name "*jup"); do
    dir_name=$(basename "$dir")
    mv $dir_name $EDUCATION
done

# Move the grades back for the student.
[ -f /tmp/"${USER}_logs.txt" ] && mv /tmp/"${USER}_logs.txt" $EDUCATION

# Finally, copy all of the notebook function files (should be four of them) into the student's XDC.
sudo mv runlab startexp stopexp runr /home
sudo mv grader.py /home/niete018/.education
sudo chmod a+x /home/runlab /home/startexp /home/stopexp /home/runr /home/niete018/.education/grader.py

# Cleanup temporary directory.
rm -rf "$TEMP_DIR"

# Configure all labs to work with the current username.
pushd "$LABS" > /dev/null 2>&1
for notebook in *.ipynb; do
    sed -i "s/USERNAME_GOES_HERE/$USER/g" "$notebook"
done

# Change the USERNAME_GOES_HERE occurrence in the port forwarding script.
sed -i "s/USERNAME_GOES_HERE/$USER/g" "$LABS/resources/port-forward/port-forward-setup"

# Doing the same for the save/load scripts.
sed -i "s/USERNAME_GOES_HERE/$USER/g" "$LABS/resources/save.py"
sed -i "s/USERNAME_GOES_HERE/$USER/g" "$LABS/resources/load.py"
popd > /dev/null 2>&1

# For section_4.py in the resources/firewall/ directory.
sed -i "s/USERNAME_GOES_HERE/$USER/g" "$LABS/resources/firewall/section_4.py"

# And finally, for the install scripts.
find /home/niete018/.education -type f -name install -exec sed -i "s/USERNAME_GOES_HERE/$(whoami)/g" {} +

echo -e "\033[0;32mDone. You can find your notebooks in $LABS. Please refresh your browser's tab before starting a lab.\033[0m"
