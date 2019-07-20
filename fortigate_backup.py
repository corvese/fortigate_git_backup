import requests, os, json
from getpass import getpass
from git import Repo, InvalidGitRepositoryError

def initilize_api_session(username, password, fortigate_ip):
    """Connects to the Fortigate Firewall via API, authenticates and returns a HTTPS session for additional API calls

    Params:
    username(str): Username to authenticate with the Fortigate firewall
    password(str): Password to authenticate with the Fortigate firewall
    fortigate_ip(str): IP address of the Fortigate firewall

    Returns:
    api_session(class): HTTPS API session"""

    api_session = requests.session()
    login_url = ('https://{0}/logincheck'.format(fortigate_ip))
    login_payload = {'username': username, 'secretkey': password}
    api_login = api_session.post(login_url, data=login_payload, verify=False)
    for cookie in api_login.cookies:
        if cookie.name == 'ccsrftoken':
            csrftoken = cookie.value
            api_session.headers.update({'X-CSRFTOKEN': csrftoken})
    return api_session

def api_call_get(api_session, fortigate_ip, api_url):
    """Uses the API HTTPS session from the function initialize_api_session to do a HTTP GET request at an API
    URL on the Fortigate 

    Params:
    api_session(class): Object of the API session from initialize_api_session
    fortigate_ip(str): IP address of the Fortigate firewall
    api_url(str): Fortigate API V2 URL to obtain the Fortigate firewall's configuration

    Returns:
    api_call.text(str): A string output of a dictionary from the API call
    """

    api_call = api_session.get('https://{0}/api/v2/'.format(fortigate_ip) + api_url, verify=False)
    return api_call.text
    
def create_repo_folder_and_or_modify_config_file(fortigate_config):
    """Will create a new folder with the Fortigate Firewall's IP address if one is not already present

    Params:
    fortigate_config(str): String of the Fortigate's configuration from the api_call_get function 

    Returns:
    file_name_with_new_dir(str): Returns a string of the Fortigate Firewall's configuration file and ABSOLUTE directory path
    """
    
    current_dir = os.getcwd()
    new_directory_name = fortigate_ip
    file_name_with_new_dir = os.path.join(current_dir, new_directory_name, "{0}-config_backup.conf".format(fortigate_ip))
    if new_directory_name in os.listdir(current_dir):
        fortigate_backup_file = open(file_name_with_new_dir, 'w')
        fortigate_backup_file.write(fortigate_config)
        return file_name_with_new_dir
    else:
        os.mkdir(new_directory_name)
        fortigate_backup_file = open(file_name_with_new_dir, 'w')
        fortigate_backup_file.write(fortigate_config)
        return file_name_with_new_dir

def git_initialize_repo(fortigate_dir):
    """Takes a directory and will initialize a git repository

    Params:
    fortigate_dir(str): String of a directory


    Returns(class): Git repo object
    """

    repo = Repo.init(fortigate_dir)
    return repo

def git_stage_and_commit(repo, conf_filename):
    """Takes a repo object and a filename and will stage and commit that file

    Params:
    repo(class): Git repo object
    conf_filename(str): String of a file/filepath and file to stage and commmit

    Returns:
    None
    """
    repo.index.add([str(conf_filename)])
    repo.index.commit('Automated Commit')

def confirm_existing_repo_or_initialize(fortigate_dir, conf_filename):
    """Takes a directory and confirms if it is a git repo, if it isn't, it will create a repo with
    git_initilize_repo and will then make an initial commit to 1 file specific in conf_filename

    Params:
    fortigate_dir(str): String of a directory
    conf_filename(str): Filename to commit

    Returns:
    repo(class): Git repo object
    """

    try:
        repo = Repo(fortigate_dir)
        return repo
    except InvalidGitRepositoryError:
        repo = git_initialize_repo(fortigate_dir)
        git_stage_and_commit(repo, conf_filename)
        return repo
        
def git_diff_compare(repo):
    """Takes the commit where HEAD is currently pointed and compares it to the working directory
    If there changes it will return a bool == TRUE, otherwise it will return FALSE

    Params:
    repo(class): Git repo object

    Returns:
    bool(bool): Returns a bool of git's diff 
    """

    hcommit = repo.head.commit
    git_diff_bool = hcommit.diff(None)
    return bool(git_diff_bool)

def git_compare(fortigate_ip, conf_filename):
    """Master function that contains all aforementioned git functions
    
    Params:
    fortigate_ip(str): IP address of the Fortigate firewall
    conf_filename(str): A string of the Fortigate Firewall configuration file and ABSOLUTE directory

    Returns:
    None
    """

    fortigate_dir = os.path.join(os.getcwd(), fortigate_ip)
    repo = confirm_existing_repo_or_initialize(fortigate_dir, conf_filename)
    if git_diff_compare(repo) is True:
        git_stage_and_commit(repo, conf_filename)
   
if __name__ == "__main__":
    fortigate_ip = input('IP address: ')
    username = input('Username: ')
    password = getpass('Password: ')
    api_session = initilize_api_session(username, password, fortigate_ip)
    api_url = 'monitor/system/config/backup?scope=global'
    config_download = api_call_get(api_session, fortigate_ip, api_url)
    conf_filename = create_repo_folder_and_or_modify_config_file(config_download)
    git_compare(fortigate_ip, conf_filename)








