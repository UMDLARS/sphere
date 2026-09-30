import os
import subprocess
import re
import threading
import queue
import time
from IPython.display import display, HTML
from enum import Enum
import shlex
import html

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
    SY = "synflood"
    M = "mitm"
    W = "worm"
    D = "dwarf"

# ---------------------------------------------------------------------------
# Install verification
# ---------------------------------------------------------------------------
CHECKER_DIR = "/home/.checker"
SSH_KEY = "/home/USERNAME_GOES_HERE/.ssh/merge_key"


def _run_runlab(labname):
    try:
        return subprocess.run(
            ['bash', '/home/runlab', f'{labname}jup'],
            capture_output=True, text=True, timeout=600
        )
    except subprocess.TimeoutExpired as e:
        return subprocess.CompletedProcess(e.cmd, -1, stdout="", stderr="runlab timed out")


def _checker_status(labname):
    cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "LogLevel=ERROR",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=10",
        "-i", SSH_KEY,
        f"USERNAME_GOES_HERE@{labname}",
        f"test -d {CHECKER_DIR} && test -n \"$(ls -A {CHECKER_DIR})\"",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return "unreachable", "ssh timed out"

    print(result)

    detail = (result.stderr or "").strip()
    if result.returncode == 0:
        return "present", detail
    if result.returncode == 255:
        return "unreachable", detail or "ssh exited with 255"
    return "missing", detail


# This is going to be called whenever the lab has finished installing.
# Fixes a possible race condition with SPHERE's runlab command. The install can
# finish AFTER runlab returns, so we poll for the checker files instead of 
# testing once, and only re-run runlab if they still haven't shown up.
def verify_install(labname, attempts=3, wait_timeout=45, poll_interval=5):
    last_status, last_detail = "unknown", ""

    for attempt in range(1, attempts + 1):
        # Give the (possibly still-running) install time to land before judging it.
        deadline = time.time() + wait_timeout
        while True:
            last_status, last_detail = _checker_status(labname)
            if last_status == "present":
                return True, ""
            if time.time() >= deadline:
                break
            time.sleep(poll_interval)

        if attempt == attempts:
            break

        print(f"Checker files not found ({last_status}). Restarting install "
              f"(attempt {attempt + 1} of {attempts})...")
        _run_runlab(labname)
        # Installing sometimes happens after the script has ended. Enforcing a short wait time.
        time.sleep(5)

    return False, f"status={last_status}; {last_detail}"


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

def warn_student(labname):
    warning_path = f"/home/USERNAME_GOES_HERE/saves/.{labname}_warning"
    if os.path.exists(warning_path):
        os.remove(warning_path)
        return True
    return False

def load_notebook(labname):
    with load_lock:
        result = subprocess.run([
            '/home/USERNAME_GOES_HERE/resources/load.py', labname
        ], capture_output=True, text=True)
        result_queue.put(result)

    # Removes the warning after loading the lab.
    warning_path = f"/home/USERNAME_GOES_HERE/saves/.{labname}_warning"
    if os.path.exists(warning_path):
        os.remove(warning_path)

def trigger_load(labname):
    load_thread = threading.Thread(target=load_notebook, args=(labname,))
    load_thread.start()
    load_thread.join()
    return result_queue.get()

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
            stopexp = subprocess.run(f'bash /home/stopexp {labname}jup', capture_output=True, text=True, shell=True)
            output.clear_output()
            if ("Error deleting the experiment" in stopexp.stdout):
                output.clear_output()
                display(HTML(f"<span style='color: red;'>There was an error stopping your {labname} lab. You may have a different lab that's active, or the {labname} lab is currently inactive.</span>"))

            else:
                display(HTML("<span>Done. Result:</span>"))
                print(stopexp.stdout)
                display(HTML("<newline><span style='color: green;'><strong>Your lab has been ended.</strong></span>"))

def load_lab(labname, output0_2):
    with output0_2:
        output0_2.clear_output()
        display(HTML("<span>Searching for an existing lab in your notebook...</span>"))

    if (os.path.exists(f"/home/USERNAME_GOES_HERE/saves/USERNAME_GOES_HERE_{labname}.tar.gz")):
        with output0_2:
            output0_2.clear_output()
            display(HTML("<span>Loading your lab...</span> \
                <span><img width='12px' height='12px' style='margin-left: 3px;' src='resources/loading.gif'></span>"))
            result = trigger_load(labname)
            if (result.returncode == 1):
                output0_2.clear_output()
                display(HTML("<span style='color: green;'>Your lab has been successfully loaded. Please click on the <img width='20px' height='20px' style='margin-left: 1px;' src='resources/fast_forward.png'> icon at the top of your notebook to reflect your changes.</span>"))
            elif (result.returncode == 2):
                output0_2.clear_output()
                display(HTML(f"<span style='color: red;'>The {labname} lab is inaccessible. Please start your lab. If you have already started it, wait a minute and try again.</span>"))
            else:
                output0_2.clear_output()
                display(HTML("<span style='color: red;'>An error occurred while loading your lab.</span>"))

    else:
        with output0_2:
            output0_2.clear_output()
            display(HTML("<span style='color: red;'>You do not have a saved tarball for this lab.</span>"))

def prepare_lab(labname, output0):
    with output0:
        os.chdir("/home/USERNAME_GOES_HERE")
        output0.clear_output()

        # Check if the student has the pass.txt file.
        if (not os.path.exists("/home/USERNAME_GOES_HERE/pass.txt")):
            with output0:
                output0.clear_output()
                display(HTML("<span style='color: red;'>Please create ~/pass.txt before clicking Start Lab. This file must contain your SPHERE password.</span>"))
                return

        # Sign in first.
        if not sign_in_student(output0):
            return

        material_pattern = f"real.{labname}jup.USERNAME_GOES_HERE"
        result = subprocess.run(
            ['mrg', 'list', 'materializations'],
            capture_output=True, text=True
        )

        if re.search(material_pattern, result.stdout):
            display(HTML(
                "<span style='color: orange;'>An existing activation for this lab already exists.</span> "
                "<span>You might have run another lab without stopping it. Attaching the existing activation...</span>"
            ))

            detach_result = subprocess.run(
                'mrg xdc detach xdc.USERNAME_GOES_HERE',
                shell=True, capture_output=True, text=True
            )
            
            if detach_result.returncode != 0:
                print(f"Note: XDC detach reported a non-zero exit ({detach_result.returncode}); continuing anyway.")
                print(detach_result.stdout + detach_result.stderr)

            attach_result = subprocess.run(
                f'mrg xdc attach xdc.USERNAME_GOES_HERE {material_pattern}',
                shell=True, capture_output=True, text=True
            )
            
            attach_output = attach_result.stdout + attach_result.stderr
            if attach_result.returncode != 0 and "XDC not ready yet" not in attach_output:
                print(f"Note: XDC attach reported a non-zero exit ({attach_result.returncode}); continuing anyway.")
                print(attach_output)

            display(HTML(
                "<span>Re-running the installation... </span>"
                "<span><img width='12px' height='12px' style='margin-left: 3px;' src='resources/loading.gif'></span>"
            ))


            check_autosave(labname)

            subprocess.run(
                ['bash', '/home/runlab', f'{labname}jup'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )

            # Installing sometimes happens after the script has ended. Enforcing a short wait time.
            time.sleep(5)

            output0.clear_output()
            display(HTML(
                "<br><span style='color: green;'><strong>Your lab has been re-installed. </strong></span>"
                "<span>When you're finished, close your lab at the bottom of the notebook.</span>"
            ))

        else:
            display(HTML("<span>No existing activations are found.</span>"))
            display(HTML(
                f"<span>Starting the {labname} lab. This will take a few minutes to process. Please wait.</span> "
                "<span><img width='12px' height='12px' style='margin-left: 3px;' src='resources/loading.gif'></span>"
            ))

        try:
            startexp = subprocess.run(
                ['bash', '/home/startexp', f'{labname}jup'],
                capture_output=True, text=True, check=True
            )
        
        except subprocess.CalledProcessError as e:
            output0.clear_output()
            combined = (e.stdout or "") + (e.stderr or "")
        
            if "The provided credentials are invalid" in combined:
                msg = "Unable to authenticate into SPHERE. Please ensure that your password in <code>~/pass.txt</code> is correct."
            else:
                msg = "There was an error starting your experiment."
        
            display(HTML(f"<span style='color: red;'>{msg}</span>"))
            return
            
        output0.clear_output()
        output_html = startexp.stdout.strip()

        display(HTML(
            f"<span>Done. Result:</span>"
            f"<div style='max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9;'>"
            f"<pre style='white-space: pre-wrap;'>{output_html}</pre></div>"
        ))

        if "XDC already attached" in startexp.stdout:
            match = re.search(r"real\.(.*?)\.USERNAME_GOES_HERE", startexp.stdout)
            existing_lab = match.group(1) if match else None

            if existing_lab == labname:
                display(HTML("<span style='color: red;'>Your lab was already started. Please continue to the next step.</span>"))
            elif existing_lab:
                display(HTML(
                    f"<span style='color: orange;'>Warning: You did not stop your previous experiment. </span>"
                    f"<span>Please stop your experiments before starting a new one. Detaching the <code>{existing_lab}</code> experiment.</span>"
                ))
                subprocess.run('mrg xdc detach xdc.USERNAME_GOES_HERE', shell=True, check=True)
                display(HTML("<span>Attaching the current lab.</span>"))
                subprocess.run(
                    f'mrg xdc attach xdc.USERNAME_GOES_HERE {material_pattern}',
                    shell=True, check=True
                )

        display(HTML("<span>Allocating lab resources onto the node. <u>Please wait a little longer...</u></span><span><img width='12px' height='12px' style='margin-left: 3px;' src='resources/loading.gif'></span>"))

        check = _run_runlab(labname)
        if check.returncode != 0:
            output0.clear_output()
            display(HTML(
                "<span style='color: red;'>The lab installation script failed. "
                "Please click Start Lab again. If this keeps happening, contact your instructor.</span>"
                f"<details><summary>Details</summary><pre style='white-space: pre-wrap;'>"
                f"{html.escape((check.stderr or check.stdout or '').strip())}</pre></details>"
            ))
            return

        # Installing sometimes happens after the script has ended. Enforcing a short wait time.
        time.sleep(5)

        # Making sure that the lab was installed fine.
        output0.clear_output()
        display(HTML("<span>Lab is installed. Verifying that the lab was configured properly...</span> <span><img width='12px' height='12px' style='margin-left: 3px;' src='resources/loading.gif'></span>"))
        installed, detail = verify_install(labname)

        output0.clear_output()
        if not installed:
            display(HTML(
                "<span style='color: red;'><strong>Your lab started, but its files did not finish installing.</strong></span> "
                "<span>Please click Start Lab again to retry. If this keeps happening, contact your instructor.</span>"
                f"<details><summary>Details</summary><pre style='white-space: pre-wrap;'>{html.escape(detail)}</pre></details>"
            ))
            return

        check_autosave(labname)

        display(HTML(
            "<br><span style='color: green;'><strong>Setup complete. You may begin the lab! </strong></span>"
            "<span>When you're finished, close your lab at the bottom of the notebook. Your lab will be active for one week.</span>"
        ))

        # Extend the XDC's expiration by two weeks, following this lab being started.
        try:
            startexp = subprocess.run(
                ['mrg', 'xdc', 'update', 'expiration', 'xdc.USERNAME_GOES_HERE', '2w'],
                capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            display(HTML("<span style='color: orange;'>Warning: XDC expiration failed to extend by two weeks.</span>"))



#################
# Debugging Tips:
#################

"""
Use something like this if you are trying to debug something within this script.
result = subprocess.run(f'bash /home/runlab {labname}jup', capture_output=True, text=True, shell=True)
with output0:
    output0.append_stdout(f"Return code: {result.returncode}\n")
    output0.append_stdout(f"STDOUT:\n{result.stdout}\n")
    output0.append_stdout(f"STDERR:\n{result.stderr}\n")

RESTART THE KERNEL WHEN SAVING THIS FILE! This will make your updates appear in the notebooks!
"""