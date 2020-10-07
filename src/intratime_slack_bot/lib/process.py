import subprocess
import os
import signal

# ----------------------------------------------------------------------------------------------------------------------


def is_running(process):
    check = subprocess.check_output(('ps', '-aux')).decode().find(process)
    return check != -1

# ----------------------------------------------------------------------------------------------------------------------


def run(command):
    process = subprocess.Popen(command)
    return process.pid

# ----------------------------------------------------------------------------------------------------------------------


def stop(pid):
    os.kill(pid, signal.SIGSTOP)

# ----------------------------------------------------------------------------------------------------------------------


def kill(pid):
    os.kill(pid, signal.SIGKILL)
