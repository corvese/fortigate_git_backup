import requests, os
from getpass import getpass
from git import Repo, InvalidGitRepositoryError

class fortigate_backup:
    def __init__(self, fortigate_ip, username, password, https_port='443'):
        self.username = username
        self.password = password
        self.fortigate_ip = fortigate_ip
        self.https_port = https_port

        self.parent_backup_location = os.path.join(os.getcwd(), 'backups')
        self.config_file_backup_location = None
        self.config_file_backup_filename = f'{self.fortigate_ip}-config_backup.conf'
        self.backup_folder_exists = None
        self.api_session = None
        self.fortigate_config = None
        self.git_repo = None
        self.config_changed = None

    @property
    def _initialize_api_session(self):
        """Connects to the Fortigate Firewall via API, authenticates and sets an object attribute of
        an HTTPS session for additional API calls"""

        api_session = requests.session()
        login_url = (f'https://{self.fortigate_ip}:{self.https_port}/logincheck')
        login_payload = {'username': self.username, 'secretkey': self.password}
        api_login = api_session.post(login_url, data=login_payload, verify=False)
        for cookie in api_login.cookies:
            if cookie.name == 'ccsrftoken':
                csrftoken = cookie.value
                api_session.headers.update({'X-CSRFTOKEN': csrftoken})
                self.api_session = api_session

    @property
    def _api_download_config(self):
        """Uses the API HTTPS session from the method '_initialize_api_session' to do an HTTPS GET API request 
        to the IP address of the Fortigate to download its configuration"""

        self.fortigate_config = self.api_session.get(f'https://{self.fortigate_ip}:{self.https_port}' \
        '/api/v2/monitor/system/config/backup?scope=global', verify=False).text

    @property
    def _validate_backup_folder_exists(self):
        """Checks to see if the parent/root backup directory exists, creates it if it is missing,
        then checks to see if there is a device specific directory (device's ip address) within that"""

        if os.path.exists(self.parent_backup_location) is False:
            os.mkdir(self.parent_backup_location)
        
        if self.fortigate_ip in os.listdir(self.parent_backup_location):
            self.backup_folder_exists = True
            self.config_file_backup_location = os.path.join(self.parent_backup_location, self.fortigate_ip)
        else:
            self.backup_folder_exists = False

    @property
    def _create_device_backup_folder(self):
        """Creates a device specific backup folder in the parent/root backup folder"""

        os.mkdir(os.path.join(self.parent_backup_location, self.fortigate_ip))
        self.config_file_backup_location = os.path.join(self.parent_backup_location, self.fortigate_ip)

    @property
    def _validate_git_repo_exists(self):
        """Verifies if a git repository is present in the device specific directory"""

        try:
            self.git_repo = Repo(path=self.config_file_backup_location)
            self.git_repo_exists = True
        except InvalidGitRepositoryError:
            self.git_repo_exists = False

    @property
    def _create_git_repo(self):
        """Creates a git repository"""

        if self.git_repo_exists is False:
            self.git_repo = Repo.init(path=self.config_file_backup_location)
        else:
            pass

    @property
    def _git_diff_compare(self):
        """Takes the commit where HEAD is currently pointed and compares it to the working directory
        If there changes it will return a bool == TRUE, otherwise it will return FALSE"""

        hcommit = self.git_repo.head.commit
        git_diff_bool = hcommit.diff(None)
        self.config_changed = bool(git_diff_bool)

    @property
    def _git_stage_and_commit(self):
        """Stages the config backup file in the device specific directory, then commits it"""
        
        self.git_repo.index.add([self.config_file_backup_filename])
        self.git_repo.index.commit('Automated Commit')

    @property
    def _write_configuration_file(self):
        """After the config file is downloaded from the Fortigate, overwrites (or creates one if it is not present)
        the configuration file in the device specific directory"""

        config_file = open(os.path.join(self.config_file_backup_location, self.config_file_backup_filename), 'w')
        config_file.write(self.fortigate_config)
        config_file.close()

    @property
    def backup(self):
        """Final method that ties all aforementioned methods together"""
        self._initialize_api_session
        self._api_download_config
        self._validate_backup_folder_exists
        if self.backup_folder_exists is False:
            self._create_device_backup_folder
        self._write_configuration_file
        self._validate_git_repo_exists
        if self.git_repo_exists is False:
            self._create_git_repo
            self._git_stage_and_commit
        elif self.git_repo_exists is True:
            self._git_diff_compare
            if self.config_changed is True:
                self._git_stage_and_commit
            else:
                pass

if __name__ == "__main__":
    fortigate_ip = input('IP address: ')
    username = input('Username: ')
    password = getpass('Password: ')
    backup = fortigate_backup(fortigate_ip, username, password)
    backup.backup