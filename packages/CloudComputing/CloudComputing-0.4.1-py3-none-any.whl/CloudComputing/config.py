import cloudsync as cs
import json
import os
from os.path import exists
import subprocess

from CloudComputing.cc_debug import cc_print
from . import vars
import configparser

'''      ------------------      Cloud Storage     ------------------      '''
def get_auth_token():
    oauth_config = cs.command.utils.generic_oauth_config('onedrive')
    provider = cs.create_provider('onedrive', oauth_config=oauth_config)
    creds = provider.authenticate()
    vars.provider = provider
    return creds

def save_auth_token(fname="$HOME/.cc_auth.json", creds=None):
    f = open(fname, 'w')
    json.dump(creds, f)

def check_auth(silent=False):
    defaultPath = os.environ['HOME'] + "/.cc_auth.json"
    if exists(defaultPath):
        if not silent:
            cc_print("Configuration found in: {}".format(defaultPath), 1)
        return defaultPath
    else:
        if not silent:
            cc_print("No configuration found in default path.", 1)
        return False

def make_auth(Force=False):
    # cloud_storage
    if check_auth() == False:
        print("Starting OneDrive auth...")
    else:
        if Force == False:
            cc_print("Use make_auth(Force=True) to overwrite the existing OAuth token.", 2)
            return
    token = get_auth_token()
    defaultPath = os.environ['HOME'] + "/"
    print("Specify path to save OneDrive auth token ({}): ".format(defaultPath), end='')
    f = input() or defaultPath
    f = f + ".cc_auth.json"
    save_auth_token(f, creds=token)
    cc_print("Token saved to file: {}".format(f), 2)

def get_token():
    f = open(vars.creds_path, 'r')
    return f.read()


'''      ------------------      Remote   Exec     ------------------      '''
def check_config(silent=False):
    defaultPath = os.environ['HOME'] + "/." + os.environ['USER'] + "-config.ini"
    if exists(defaultPath):
        if not silent:
            cc_print("[INFO] Global SSH configuration found in {}".format(defaultPath), 1)
        vars.global_config = defaultPath
    else:
        if not silent:
            cc_print("Global SSH configuration not found. Call config.make_config() to create one.", 2)

def make_config(local=False):
    if local:
        defaultPath = "./config.ini"
    else:
        defaultPath = os.environ['HOME'] + "/." + os.environ['USER'] + "-config.ini"
        if exists(defaultPath):
            cc_print("Global configuration already set. This will overwrite the existing configuration.", 1)
    host = input("SSH user@host: ")
    if not "@" in host:
        print("Please provide user and host (e.g., admin@127.0.0.1")
        return
    port = input("SSH port (22): ") or "22" # Default: 22
    f = open(defaultPath, 'w')
    if f.closed:
        cc_print("Unable to open file {}".format(defaultPath), 3)
        return
    f.write("[SSH]\n")
    f.write("host = {}\n".format(host))
    f.write("port = {}\n".format(port))
    f.close()
    cc_print("{} configuration saved successfully.".format("Local" if local else "Global"), 1)
    if local:
        vars.local_config = defaultPath
    else:
        vars.global_config = defaultPath

def load_config():
    p = os.environ['HOME'] + "/." + os.environ['USER'] + "-config.ini"
    if exists(p):
        vars.global_config = p
    p = "./config.ini"
    if exists(p):
        vars.local_config = p
    if vars.global_config == "" and vars.local_config == "":
        cc_print("You need to set either a local or global configuration file.", 2)
        return None
    c = configparser.ConfigParser()
    if vars.local_config == "":
        c.read(vars.global_config)
    else:
        c.read(vars.local_config)
    return c

def check_ssh_connection():
    if vars.global_config == "" and vars.local_config == "":
        cc_print("[ERROR] No valid configuration file found. Exiting...", 3)
        return
    cmd = "ssh -p {} {} uname -n".format(vars.ssh_port, vars.ssh_host)
    print("Testing connection: " + cmd)
    cmd = "ssh -p {} {} uname -n".format(vars.ssh_port, vars.ssh_host)
    try:
        out = subprocess.check_output(cmd, shell=True).decode().strip()
    except subprocess.CalledProcessError:
        cc_print("[WARNING] SSH connection issue.", 2)
        return
    cc_print("Connected to host: {}".format(out), 1)