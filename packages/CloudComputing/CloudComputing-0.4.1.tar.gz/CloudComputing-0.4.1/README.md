# CloudComputing for Python

The `CloudComputing` package can be used to easily exploit advanced functions such as remote executing over SSH and cloud storage (OneDrive/GDrive) with Python.\
The remote execution (`remote_exec.py`) is handled over SSH: source files can be developed and maintained locally and then executed remotely over SSH.\
Cloud storage is based on the Python package [cloudsync](https://pypi.org/project/cloudsync/), that supports both Google Drive and OneDrive. It allows to store large datasets on the cloud and access them both locally and remotely, combined with the `remote_exec` functionality. 

### Requirements

All the required Python packages are installed automatically with this package. `CloudComputing` works on Python 3: it was developed and tested on Python 3.9.6 on Linux. The `remote_exec` module is currently working only on Unix systems (by choice...)\
You need to set up a secure shell (SSH) connection with the remote host for the `remote_exec` module before using this functionality. You may find instructions on how to do this on the web, such as [this one](https://medium.com/@SergioPietri/how-to-setup-and-use-ssh-for-remote-connections-e86556d804dd).
### Install

The install process should be straight-forward: `pip install CloudComputing`. I recommend using [pyenv](https://github.com/pyenv/pyenv).

### Configuration
#### Cloud Storage
The `cloud_storage` module is based on the PyPi package `cloudsync`. By default, the latter handles authentication with a OAuth token and does not store user credentials, requiring re-authentication at every session. The `config` module provides functions to save and manage the OAuth token. This is saved in json format locally, either in `$HOME` (default) or in a user-provided path. Both OneDrive Personal and OneDrive for Business accounts should work out-of-the-box, with support for shared folders. To authenticate, run `config.make_auth()`:
``` bash
python -c 'import CloudComputing as cc; cc.make_auth()'
```

#### Remote Execution

The `remote_exec` module can be configured either with a `config.ini` file, either globally (user space) or locally (project workspace). Please mind that the local configuration has higher priority over the global one, if any. This is intended to have both a user-defined default server and project-specific servers.
##### Global Configuration
The global configuration can be set either manually or calling the `config.make_config()` function:
``` bash
python -c 'import CloudComputing as cc; cc.make_config()'
```
This will set the default `user@host` and the default `port` for SSH communication. The global configuration file is stored in `$HOME/.$USER-config.ini`.
##### Local Configuration
Any project may have its local configuration. Local configurations have higher priority. They are specified by means of a local `config.ini` in the project's path, with the following structure. 
``` ini
; config.ini
[SSH]
host = "user@127.0.0.1"
port = 22
```
Local configurations may be created also with `config.make_config(local=True)`

##### Remote Python Interpreter
I recommend using [pyenv](https://github.com/pyenv/pyenv) in the remote machine to handle different projects with different Python versions and/or virtual environments. As of now, `remote_exec()` provides the `rdir` option, used to set the remote directory after SSH login. This requires prior configuration with `pyenv` or `pyvenv`. 
<!-- 
Check out the documentation to configure `pyenv` on the remote machine and specify the remote Python interpreter. 
-->

### Disclaimer

This software is released with the GNU General Public License v3.0.

### Example

##### Cloud Storage
``` python
#!/usr/bin/env python
import CloudComputing as cc
import pandas as pd
print("CloudComputing version: {}".format(cc.__version__))

# Download file from OneDrive...
path_in_onedrive = "/test.csv"
f = cc.download_file(path_in_onedrive)
# ... and import it to Pandas
df = pd.read_csv(f)
print(df.info())
```
##### Remote execution
``` python
#!/usr/bin/env python
import CloudComputing as cc
print("CloudComputing version {}".format(cc.__version__))
# Remote execution of this script
cc.remote_exec()

# The rest of this file runs on a remote server via SSH...
import os
print("This is running on: {}".format(os.environ['HOME']))
```

#### Cloud Storage + Remote Execution
Combining Cloud Storage and Remote Execution requires installing and configuring `CloudComputing` also in the remote machine.