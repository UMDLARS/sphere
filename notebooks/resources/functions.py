import os
import subprocess
import re
import threading
import queue
import time
from IPython.display import display, HTML
from enum import Enum
import shlex

save_lock = threading.Lock()
load_lock = threading.Lock()
result_queue = queue.Queue()

class LabInitial(Enum):
    I = "intro"
    PO = "posix"
    B = "buffer"
    PA = "pathname"
    S = "sqli"
    X = "xss"
    F = "firewalls"

def save_notebook(labname):
    with save_lock:
        subprocess.run([
            '/home/USERNAME_GOES_HERE/resources/save.py', labname
        ], capture_output=True, text=True)

def trigger_save(labname, question=None, response=None, answer=""):
    save_thread = threading.Thread(target=save_notebook, args=(labname,))
    save_thread.start()

    if answer:
        answer = re.sub(r"[\"'`]", "", str(answer))
    
    cmd_args = ["/home/USERNAME_GOES_HERE/.education/grader.py", LabInitial(labname).name]
    
    if question is not None:
        cmd_args.append(str(question))
    if response is not None:
        cmd_args.append(str(response))
    if answer:
        cmd_args.append(answer)

    result = subprocess.run(cmd_args, capture_output=True, text=True)

def load_notebook(labname):
    with load_lock:
        result = subprocess.run([
            '/home/USERNAME_GOES_HERE/resources/load.py', labname
        ], capture_output=True, text=True)
        result_queue.put(result)

def trigger_load(labname):
    load_thread = threading.Thread(target=load_notebook, args=(labname,))
    load_thread.start()
    load_thread.join()
    return result_queue.get()

def warn_student(labname):
    warning_path = f"/home/USERNAME_GOES_HERE/saves/.{labname}_warning"
    if os.path.exists(warning_path):
        os.remove(warning_path)
        return True
    return False

def sign_in_student(output0):
    with output0:
        output0.clear_output()
        display(HTML("<span>Signing you into SPHERE...</span> <span><img width='12px' height='12px' style='margin-left: 3px;' src='resources/loading.gif'></span>"))
        subprocess.run(
            ["mrg", "config", "set", "server", "grpc.sphere-testbed.net"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        subprocess.run(
            ["mrg", "login", "USERNAME_GOES_HERE", "-p", open("/home/USERNAME_GOES_HERE/pass.txt").read().strip()],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        output0.clear_output()
    return True

def check_autosave(labname):
    if os.path.exists(f"/home/USERNAME_GOES_HERE/saves/USERNAME_GOES_HERE_{labname}.tar.gz"):
        subprocess.run(f"touch /home/USERNAME_GOES_HERE/saves/.{labname}_warning", shell=True)

def stop_lab(labname, confirm, output):
    # Check to make sure that the student wants to confirm ending the lab.
    if (confirm.value == False):
        with output:
            output.clear_output()
            display(HTML("<newline><span style='color: red;'>Please confirm that you wish to end the lab.</span>"))

    else:
        # Writing the information to an empty field below the button.
        with output:
            output.clear_output()
            
            display(HTML(f"<span>Stopping the {labname} lab. This will take a minute to process. Please wait.</span> \
                <span><img width='12px' height='12px' style='margin-left: 3px;' src='resources/loading.gif'></span>"))
            stopexp = subprocess.run(f'bash /share/stopexp {labname}jup', capture_output=True, text=True, shell=True)
            output.clear_output()
            if ("Error deleting the experiment" in stopexp.stdout):
                output.clear_output()
                display(HTML(f"<span style='color: red;'>There was an error stopping your {labname} lab. You may have a different lab that's active, or the {labname} lab is currently inactive.</span>"))

            else:
                display(HTML("<span>Done. Result:</span>"))
                print(stopexp.stdout)
                display(HTML("<newline><span style='color: green;'><strong>Your lab has been ended.</strong></span>"))

def prepare_lab(labname, output0):
    with output0:
        os.chdir("/home/USERNAME_GOES_HERE")
        output0.clear_output()

        # Sign in first.
        signedIn = sign_in_student(output0)
        if not signedIn:
            return

        materialPattern = f"real.{labname}jup.USERNAME_GOES_HERE"
        result = subprocess.run(['mrg', 'list', 'materializations'], capture_output=True, text=True)
        checkMaterial = result.stdout
        regex = re.compile(materialPattern)
        match = regex.search(checkMaterial)

        if match:
            display(HTML(
                "<span style='color: orange;'>An existing activation for this lab already exists. </span>"
                "<span>You might have run another lab without stopping this one. Attaching the existing activation...</span>"
            ))
            subprocess.run('mrg xdc detach xdc.USERNAME_GOES_HERE', shell=True)
            subprocess.run(f'mrg xdc attach xdc.USERNAME_GOES_HERE real.{labname}jup.USERNAME_GOES_HERE', shell=True)
            display(HTML(
                "<span>Re-running the installation... </span> \
                <span><img width='12px' height='12px' style='margin-left: 3px;' src='resources/loading.gif'></span>"
            ))

            check_autosave(labname)

            subprocess.run(f'bash /share/runlab {labname}jup', capture_output=False, text=True, shell=True)
            output0.clear_output()
            
            display(HTML(
                "<newline><span style='color: green;'><strong>Your lab has been re-installed. </strong></span>"
                "<span>When you're finished, close your lab at the bottom of the notebook.</span>"
            ))
        else:
            display(HTML("<span>No existing activations are found.</span>"))
            display(HTML(
                f"<span>Starting the {labname} lab. This will take a few minutes to process. Please wait.</span> \
                <span><img width='12px' height='12px' style='margin-left: 3px;' src='resources/loading.gif'></span>"
            ))

            try:
                startexp = subprocess.run(f'bash /share/startexp {labname}jup', capture_output=True, text=True, shell=True)
            except Exception:
                output0.clear_output()
                display(HTML("<span style='color: red;'>There was an error starting your experiment.</span>"))
                return

            output0.clear_output()
            if startexp.returncode == 1:
                display(HTML(f"""
                <span style='color: red;'>There was an error starting your experiment. The log has been shown below. Please view it and fix any mistakes (like an invalid password in ~/pass.txt, or SPHERE may be down).
                If you are stuck and need help, please consult your professor/TA.</span>
                <div style="max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9;">
                <pre style="white-space: pre-wrap;">{startexp.stdout}</pre>
                </div>
                """))
                return

            display(HTML(f"""
            <span>Done. Result:</span>
            <div style="max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9;">
            <pre style="white-space: pre-wrap;">{startexp.stdout}</pre>
            </div>
            """))

            if "XDC already attached" in startexp.stdout:
                existingLab = re.search(r"real.(.*).USERNAME_GOES_HERE", startexp.stdout).group(1)
                if labname == existingLab:
                    display(HTML("<span style='color: red;'>Your lab was already started. Please continue to the next step.</span>"))
                else:
                    display(HTML(f"<span style='color: orange;'>Warning: You did not stop your previous experiment. </span><span>Please stop your experiments before starting a new one. Detaching the {existingLab} experiment.</span>"))
                    subprocess.run('mrg xdc detach xdc.USERNAME_GOES_HERE', shell=True, check=True)
                    display(HTML("<span>Attaching the current lab.</span>"))
                    subprocess.run(f'mrg xdc attach xdc {materialPattern}', shell=True, check=True)

            display(HTML("<span>Allocating lab resources onto the node. <u>Please wait a little longer...</u></span>"))
            time.sleep(2)
            subprocess.run(f'bash /share/runlab {labname}jup', shell=True)
            check_autosave(labname)

            display(HTML(
                "<newline><span style='color: green;'><strong>Setup complete. You may begin the lab! </strong></span>"
                "<span>When you're finished, close your lab at the bottom of the notebook. Your lab will be active for one week.</span>"
            ))

#################
# Debugging Tips:
#################

"""
Use something like this if you are trying to debug something within this script.
result = subprocess.run(f'bash /share/runlab {labname}jup', capture_output=True, text=True, shell=True)
with output0:
    output0.append_stdout(f"Return code: {result.returncode}\n")
    output0.append_stdout(f"STDOUT:\n{result.stdout}\n")
    output0.append_stdout(f"STDERR:\n{result.stderr}\n")

RESTART THE KERNEL WHEN SAVING THIS FILE! This will make your updates appear in the notebooks!
"""
