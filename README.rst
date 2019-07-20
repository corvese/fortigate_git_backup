Fortigate Config Download & Git Comparison
==========================================
Automating backups and using version control to manage configuration changes is a great way to manage network infrastructure. This project was my attempt at doing just that

This project was tested with the following device:

- Fortigate Firewall model 60E
- FortiOS v6.0.4 (build-0231)
- FortiOS API version 2

How it works
------------

- The ``fortigate_backup.py`` program will create a HTTPS session based on some user input
- The session is then used to make an API call to a Fortigate Firewall appliance
- An HTTPS GET request is made via the FortiOS API to download a copy of the device's current configuration
- If a new directory does not exist with that Fortigate firewall's IP address, one is created
- A git repo is then initialized or a git diff is executed (against the downloaded configuration file)
    - If there was no git repo, one is made and an initial commit is made with the first instance of the device's configuration is documented
    - If there was a git repo pre-existing, a git diff is done and if there is a difference, commit the new configuration

Usage
-----

- Run ``fortigate_backup.py`` from the terminal
- You will be prompted for the following:
    - ``IP address``: IP address of the Fortigate device
    - ``username``: Fortigate appliance's administrative password
    - ``password``: Fortigate appliance administrative password
- The script will run and return no output in the terminal (see how it works above for what is done)

Moving Further
--------------

- This script could be expanded/improved further to:
    - Write the config backups to a specific folder
    - Add multithreading to run this program with multiple other firewalls
    - Refactoring to make the code 'cleaner'
    - Add in more error handling