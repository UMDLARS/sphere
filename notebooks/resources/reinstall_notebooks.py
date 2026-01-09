import os
import subprocess
import sys
from IPython.display import display, HTML
from IPython import get_ipython

def installation():
    class StopExecution(Exception):
        def _render_traceback_(self):
            pass

    try:
        import ipywidgets as widgets
    except ModuleNotFoundError as e:
        print(f"Jupyter Widgets isn't installed. This is possibly due to an update rolled out by SPHERE. "
              "The notebook will revert your installations. Please wait.\n")

        # If the extension is uninstalled, it's very possible that install_notebooks.sh is also missing.
        # Pulling install_notebooks. Need to invoke sudo for this.
        command = (
            'sudo curl -LJO https://raw.githubusercontent.com/UMDLARS/sphere/refs/heads/main/install_notebooks.sh '
            '&& sudo mv install_notebooks.sh /home/install_notebooks.sh '
            '&& sudo chmod a+x /home/install_notebooks.sh'
        )

        # Run the command using subprocess with shell=True
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while downloading the install_notebooks.sh script. Error: {e}\n")
            raise StopExecution("Exiting early. This message will not be printed.\n")

        # Now, running the script to re-install the files.
        command = '/home/install_notebooks.sh'

        print("Running the installation. If you see a pop-up window appear, click OVERWRITE. "
              "Please wait until the notebook fixes your installation...\n")

        # Running the re-installation.
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running the install_notebooks.sh script. Error: {e}\n")
            raise StopExecution("Exiting early. This message will not be printed.\n")

        print(f"Please click the fast-forward icon (>>) at the top of the notebooks, and try re-compiling again.\n")
        raise StopExecution("Exiting early. This message will not be printed.\n")
