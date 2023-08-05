[![PyPI version](https://badge.fury.io/py/pywinos.svg)](https://badge.fury.io/py/pywinos)
[![Build Status](https://travis-ci.org/c-pher/PyWinOS.svg?branch=master)](https://travis-ci.org/c-pher/PyWinOS)
[![Coverage Status](https://coveralls.io/repos/github/c-pher/PyWinOS/badge.svg?branch=master)](https://coveralls.io/github/c-pher/PyWinOS?branch=master)

# PyWinOS

The cross-platform tool to work with remote and local Windows OS.

PyWinOS uses the Windows Remote Manager (WinRM) service. It can establish connection to a remote server based on Windows
OS and execute commands:

- PowerShell
- Command line
- WMI.

It can execute commands locally using subprocess and command-line too.

For more information on WinRM, please
visit [Microsoft’s WinRM site](https://docs.microsoft.com/en-us/windows/win32/winrm/portal?redirectedfrom=MSDN)
It based on [pywinrm](https://pypi.org/project/pywinrm/).

PyWinOS (main methods) returns `WinResponse` object with properties:

- `exited`: Exit code (int)
- `stdout`: standard output stream (`converted to dict if got appropriate content`)
- `stderr`: standard err stream
- `ok`: Is exit code == 0 (bool)

## Installation

For most users, the recommended method to install is via pip:

```cmd
pip install pywinos
```

or from source:

```cmd
python setup.py install
```

## Import
```python
from pywinos import WinOSClient
```
---
## Usage (remote server)
#### Run PowerShell:

```python
from pywinos import WinOSClient

tool = WinOSClient(host='172.16.0.126', username='administrator', password='qqq123aaa', logger_enabled=True)
response = tool.run_ps(command='$PSVersionTable.PSVersion')

# 2022-07-17 23:04:22 | INFO      | WinOSClient         232 | 172.16.0.48    PS | $PSVersionTable.PSVersion
# 2022-07-17 23:04:23 | INFO      | WinOSClient         264 | 172.16.0.48    PS | 0:
# 	Major  Minor  Build  Revision
# -----  -----  -----  --------
# 5      1      17763  316
```

```python
from pywinos import WinOSClient

tool = WinOSClient(host='172.16.0.126', username='administrator', password='qqq123aaa', logger_enabled=True)
response = tool.run_ps('Get-Service -Name "ALG" | ConvertTo-Json')

# 2022-07-18 21:02:02 | INFO      | WinOSClient         220 | 172.16.0.48    | PS  | Get-Service -Name "ALG" | ConvertTo-Json -Depth 1
# 2022-07-18 21:02:03 | INFO      | WinOSClient         252 | 172.16.0.48    | PS  | 0:
# 	{'CanPauseAndContinue': False, 'CanShutdown': False, 'CanStop': False, 'DisplayName': 'App...

print(response.stdout)
# {'CanPauseAndContinue': False, 'CanShutdown': False, 'CanStop': False, 'DisplayName': 'Application Layer Gatew...}

print(response.stderr)
# None

print(response.ok)
# True
```

#### Run command line:

```python
from pywinos import WinOSClient

tool = WinOSClient('172.16.0.126', 'administrator', 'P@ssw0rd', logger_enabled=False)
response = tool.run_cmd(command='whoami')

# 2022-07-17 23:06:46 | INFO      | WinOSClient         232 | 172.16.0.48    CMD | whoami
# 2022-07-17 23:06:46 | INFO      | WinOSClient         264 | 172.16.0.48    CMD | 0:
# 	autovm1\administrator

```

### Instance of a WinResponse can be pretty printed

```python
import WinOSClient

client = WinOSClient('172.16.0.48', 'administrator', 'zzz123ZZZ', logger_enabled=True, log_level='DEBUG')
result = client.is_service_running('alg')
print(result)
```

```json
{
  "exit_code": 0,
  "ok": true,
  "stdout": "autovm1\\administrator",
  "stderr": "",
  "cmd": "whoami",
  "raw": "<Responsecode0, out b'autovm1\\administrato', err b''>"
}
```

- `exit_code`: Exit code (int)
- `ok`: Is exit code == 0 (bool)
- `stdout`: standard output stream
- `stderr`: standard err stream
- `cmd`: Command sent
- `raw`: Response class from WinRM

### Main low-level methods to work with local/remote Windows OS:

* run_cmd
* run_cmd_local
* run_ps
* run_ps_local

### High-level methods:

* Use `list_all_methods()` to get list of all methods.

## Changelog

### UNRELEASED

##### 2.0.0 (04.08.2022)

NEW version without back compatibility.

- Response is dict by default.
- Logger updated

##### 1.2.8a (18.07.2022)

Changes reverted and refactored

- Response is a WinResponse class with properties (see this readme from a very beginning)
- stdout will be converted to dict if possible
- ResponseParser renamed to the WinResponse

##### 1.2.8 (17.07.2022)

Breaking changes

From now on dict with exit_code, ok, stdout, stderr, cmd, raw keys returns

ResponseParser:

- .stdout: try to return json if possible
- .stderr: "CLIXML..." suppressed and returns None if no errors
- obj print returns pretty dict

WinOSClient:

- log_level instance attr added. INFO by default
- log format changed
- debug log added
- run_cmd and run_ps returns dict now
- if stderr is not empty -> log entry + RemoteCommandExecutionError raise
- many methods renamed according commandlet used name
- many high-level methods removed in favor to use "general" method. i.e. get_service_status removed. Use get_service
  and 'Status' key from dict result
- cmdlet used added into docstring

Renamed:

- remove -> remove_item + "ignore_errors=False" param added
- get_network_adapter_state -> get_net_adapter
- disable_network_adapter -> disable_net_adapter
- enable_network_adapter -> enable_net_adapter
- get_disks -> get_disk and removed dimensions
- get_volumes -> get_volume and removed dimensions

Obsolete:

- all "*_local" high-level methods
- attach_share()
- is_disk_offline
- get_volumes_count : use get_volume

RemoteCommandExecutionError added

##### 1.2.7 (3.06.2022)

- log format changed according to other modules
- get_volumes() fixed to process all volumes (including service volumes without label)
- get_disks() changed. Keys are int now.
- "EntitiesQuantity" key added to bot methods
- FAQ updated

##### 1.2.6 (3.06.2022)

- Logger name changed to 'WinOSClient'
- get_disks() returns dict with disk number as key and dict with disk info as value
- get_volumes() returns dict with volume name as key and dict with volume info as value
  Both of them have optional param to get info only for specific disk/volume

##### 1.2.5 (29.04.2022)

New methods:

- .get_xml()
- .get_xml_local()

##### 1.2.4 (29.04.2022)

New method added:

- .get_disks() returns list of dict with disks info

Method updated:

- .get_volumes(): added dimension=None param. Sizes can be converted to "MB" and "GB".
  To get bytes do not set this param
- .get_volumes() extended with the "SizeUsed" field

##### 1.2.3 (28.04.2022)

New methods added:

- .get_volumes() returns list of dicts with volumes info
- .get_volumes_count() returns dict including CD-ROMs and system reserved volumes

##### 1.2.2 (22.04.2022)

- .get_process(), .get_process_local(), .get_service_file_version(), .get_service_file_version_local() raise
  ProcessLookupError if process not found
- .get_service(), .get_service_local() raise ServiceLookupError if service not found
- All method related to xmk handling marked as deprecated
- ServiceLookupError exception added
- Typos fixed

##### 1.2.1 (17.04.2022)

- updated to manage logger state

##### 1.2.0 (6.04.2022)

- External logger used
- Logger moved into class in order to have access to it after inheritance
