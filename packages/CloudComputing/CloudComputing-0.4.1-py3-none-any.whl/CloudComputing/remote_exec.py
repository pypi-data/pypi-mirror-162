import os
import subprocess
import tempfile as tf
from . import vars
from .config import get_token
from .cc_debug import cc_print
from time import sleep


def remote_exec(rdir="./", path=None, verbose=True, logfile="nohup.out",parallel=False,args_User="001"):
    # If localhost, return
    if 'localhost' in vars.ssh_host or '127.0.0.1' in vars.ssh_host:
        cc_print("Running on local machine...", 2)
        return

    # Run locally if iPython, otherwise set path
    if vars.__file__ is None:
        cc_print("Running on local iPython kernel")
        return
    else:
        path = vars.__file__ if path is None else path

    cc_print("Running from file: {}".format(path), 1)

    # Check if this file is already running remotely
    running = True
    try:
        out = subprocess.check_output("ssh -p {} {} 'pgrep -f {}'".format(vars.ssh_port, vars.ssh_host, path.split('/')[-1]), shell=1)
    except subprocess.CalledProcessError:
        running = False
    if running and not parallel:
        cc_print("This script is already running on the remote machine!", 2)
        a = input("           Press X to stop the remote execution, or M to monitor its execution [M]: ")
        if a.upper() == 'X':
            r = subprocess.Popen("/usr/bin/ssh -p {} {} 'kill $(pgrep -f {})'".format(vars.ssh_port, vars.ssh_host, path.split('/')[-1]), shell=1)
            r.wait()
            exit(1)
        # Re-start the tail process and exit
        subprocess.run("/usr/bin/ssh -p {} {} 'tail -f {}'".format(vars.ssh_port, vars.ssh_host, (rdir + "/" + logfile)), shell=True) 
        exit(0)        

    # Open the calling script (from path) and read the file
    fin = open(path, 'r')
    # Split the script and take everything after separator
    s = fin.read().split("rdir=")[-1]
    s = s[s.find("\n")+1:len(s)]   

    # Do we need to import CloudComputing? 
    if "CloudComputing" in s or "cc" in s:
        s = "import CloudComputing as cc\ncc.vars.token = {}\ncc.__token__ = cc.vars.token\ncc.connect()\nprint(__file__)\n".format(get_token()) + s
    
    # Write to file
    tmp = os.path.join(tf.gettempdir(), path.split('/')[-1])
    fout = open(tmp, 'w')
    fout.write(s)
    fout.close()
    
    # Create the logfile in the remote working directory
    xmd = "/usr/bin/ssh -p {} {} 'echo > {}'".format(vars.ssh_port, vars.ssh_host, (rdir + "/" + logfile))
    r = subprocess.Popen(xmd, shell=True)
    r.wait()

    # Copy the temp file (script) to the remote working dir
    xmd = "/usr/bin/scp -o ConnectTimeout=2 -P {} {} {}:{} > /dev/null".format(vars.ssh_port, tmp, vars.ssh_host, tmp) # Copy to /tmp/
    r = subprocess.Popen(xmd, shell=True)
    r.wait()
    # Check if SSH connection timed-out
    if r.returncode == 1:
        cc_print("SSH connection timed out! Check settings and retry.", 2)
        exit(1)

    # Command to run over ssh
    # '&' in remote command will not exit if we close the local shell
    # Log stdout and stderr in remote logfile
    cmd = cmd = "/usr/bin/ssh -p {} {} 'cd {} && ".format(vars.ssh_port, vars.ssh_host, rdir)
    cmd = cmd + "python -u {} -u {}  ' ".format(tmp, args_User) # Run file from /tmp
    print(cmd)
    # Popen is non blocking, code execution locally will continue
    r = subprocess.Popen(cmd, shell=True)   
    cc_print("Logging to file: {}".format(logfile), 1)
    
    # If in verbose mode, tail the remote logfile
    if verbose:
        subprocess.run("/usr/bin/ssh -p {} {} 'tail -f {}'".format(vars.ssh_port, vars.ssh_host, (rdir + "/" + logfile)), shell=True)    

    # Exit to prevent the calling script to run locally after remote exeuction
    exit(0)
