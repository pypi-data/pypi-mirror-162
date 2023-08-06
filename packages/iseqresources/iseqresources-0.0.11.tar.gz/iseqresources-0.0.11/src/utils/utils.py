import json
from getpass import getpass
import gitlab
import os
import requests
from jira import JIRA


def load_json(json_path: str, gitlab_token: str) -> dict:
    if json_path.startswith("https://"):
        gl = gitlab_auth(gitlab_token)
        file = get_tools_and_databases_json(gl)
        return json.loads(file.decode().decode('utf-8'))
    with open(json_path, "r") as json_file:
        return json.load(json_file)


def save_json(json_path: str, resources_dict: dict):
    with open(json_path, "w") as json_file:
        json.dump(resources_dict, json_file, indent=2)


def save_json_to_gitlab(data: dict, gitlab_token: str):
    gl = gitlab_auth(gitlab_token)
    file = get_tools_and_databases_json(gl)
    file.content = json.dumps(data)
    file.save(branch='main', commit_message='Update file')


def get_gitlab_token():
    print('''Please enter Gitlab token (https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)''')
    return check_gitlab_token(getpass())


def check_gitlab_token(token: str):
    try:
        _ = gitlab_auth(token)
    except gitlab.GitlabAuthenticationError:
        print("Gitlab token is invalid")
        return get_gitlab_token()
    return token


def gitlab_auth(gitlab_token: str):
    gl = gitlab.Gitlab(private_token=gitlab_token)
    gl.auth()
    return gl


def get_tools_and_databases_json(gl_auth: gitlab.Gitlab):
    project_id = 38164378 # iseqresources Gitlab ID
    project = gl_auth.projects.get(project_id)
    file = project.files.get(file_path='json/tools_and_databases.json', ref='main')
    return file


def get_github_token():
    print('''Please enter Github token (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)''')
    return check_github_token(getpass())


def check_github_token(token: str):
    headers = {'Authorization': 'token ' + token}
    login = requests.get('https://api.github.com/user', headers=headers)
    if not login.ok:
        print("Github token is invalid")
        return get_github_token()
    return token


def get_jira_auth(server: str, epic_id: str):
    email = input('Please enter JIRA email: ')
    print('''Please enter JIRA token (https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)''')
    token = getpass()
    return check_jira_auth(email, token, server, epic_id)


def check_jira_auth(email: str, token: str, server: str, epic_id: str):
    jira_options = {'server': server}
    try:
        jira = JIRA(options=jira_options, basic_auth=(email, token))
        jira.issue(epic_id)
        return email, token
    except:
        print("JIRA token is invalid")
        return get_jira_auth(server, epic_id)


def clear_screen():
    return os.system('cls' if os.name=='nt' else 'clear')