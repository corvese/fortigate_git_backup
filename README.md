# Fortigate Config Download & Git Comparison
---
Automating backups and using version control to manage configuration changes is a great way to manage network infrastructure. This project was my attempt at doing just that

This project was tested with the following device:

- Fortigate Firewall model 60E
- FortiOS v6.0.9 (build-0335)
- FortiOS API version 2

## How it works
---

- The `fortigate_backup.py` program will create a HTTPS session based on some user input
- The HTTPS session is then used to make an API call to a Fortigate Firewall appliance
- An HTTPS GET request is made via the FortiOS API to download a copy of the device's current configuration
- A folder called `backups` is then created (if it does not exist) and then a nested folder within it is created with the device's IP address
- A git repo is then initialized or a git diff is executed (against the downloaded configuration file)
    - If there was no git repo, one is made and an initial commit is made with the first instance of the device's configuration is documented
    - If there was a git repo pre-existing, a git diff is done and if there is a difference, commit the new configuration

## Usage
---

##### Method one:
- Run `fortigate_backup.py` from the terminal
- You will be prompted for the following:
    - `IP address`: IP address of the Fortigate device
    - `username`: Fortigate appliance's administrative password
    - `password`: Fortigate appliance administrative password
- The script will run and return no output in the terminal (see how it works above for what is done)
- The configuration file will be saved to `\backups\<DEVICE_IP>`

##### Method Two:
- Added a `creds.py` file to the same directory you have `fortigate_backup.py`
- In the file `creds.py` create two variables (strings) `username` and `password`
- Run the API locally with `uvicorn config_change_listener:app --host 0.0.0.0`. Make sure your firewall allows connections to be initiated externally
  - Alternatively (and more practically), you can run this on a server as well as a service...
  - Uvicorn uses a default port of 8000. Your request should be to `http://<IP HERE>:8000/configuration_backup`
 - When the fortigate receives the request it takes the device's source IP, then will run `fortigate_backup.py` against that IP to download the configuration

###### So how is this API useful?
- You can configure a Fortigate to use a webhook ([Fortinet documentation here](https://docs.fortinet.com/document/fortigate/6.2.2/cookbook/989735/webhook-action)) and map a trigger of a configuration change to launch the webhook and call the API
- Essentially whenever a configuration change is made on the Fortigate it will trigger the webhook, contact that API lisener, which will then have the script download the config and track version control using GIT



## Moving Further
---

- This script could be expanded/improved further to:
    - Add option to save to a specific folder
    - Add multithreading to run this program with multiple other firewalls
    - Add in error handling