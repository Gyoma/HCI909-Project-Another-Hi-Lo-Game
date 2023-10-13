import subprocess
import sys
import os

current_folder = os.path.dirname(os.path.abspath(__file__))

def create_server_subprocess(capture_output_s=True):
    return subprocess.Popen([sys.executable, os.path.join(current_folder, "server.py")], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)

def running(popen):
    return popen.poll() is None
