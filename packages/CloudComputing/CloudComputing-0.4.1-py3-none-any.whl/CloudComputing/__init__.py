from .cloud_storage import connect, change_namespace, download_file, read_remote_csv_pandas
from .config import get_auth_token, save_auth_token, check_auth, make_auth, check_config, make_config, load_config, check_ssh_connection, get_token
from .remote_exec import remote_exec
from . import vars
from .cc_debug import cc_print
from tempfile import gettempdir
from os import mkdir, path
import sys, __main__

# CloudComputing version
__version__ = "0.4.1"
# Author (GitHub username)
__author__ = "mp1994"

# This is set only when CC is imported in the remote server
__token__ = None
vars.token = __token__

## Global variables
# cloud_storage
vars.creds_path = check_auth(silent=True)
creds = vars.creds_path
# remote_exec
check_config(silent=True)
c = load_config()
if not c is None:
    vars.ssh_host = c['SSH']['host']
    vars.ssh_port = c['SSH']['port']
# Temp dir for download caching
vars.tempdir = gettempdir() + "/cc_cache/"
try:
    mkdir(vars.tempdir)
except FileExistsError:
    pass
# Get path of calling script (if any)
if hasattr(__main__, "get_ipython"):
    vars.__file__ = None
else:
    vars.__file__ = path.abspath(sys.argv[0])