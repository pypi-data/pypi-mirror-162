# -*- coding: utf-8 -*-

"""mesh_sync provides entry point main()."""

__version__ = "1.0.8"

import argparse
import base64
import re
import sys
import os
import requests


def check_if_dot_git_exists() -> bool:
    # Scan the root directory for .git
    for root, dirs, files in os.walk(os.getcwd()):
        if '.git' in dirs:
            return True
    return False


def find_git_url() -> str or None:
    """
    Scan the .git folder for the repository url and name
    :return:
    """
    for root, dirs, files in os.walk(os.getcwd()):
        if '.git' in dirs or '.git' in files or '.git' in root:
            for file in files:
                if file == 'config':
                    with open(os.path.join(root, file), 'r') as f:
                        contents = f.read()
                        url = re.search(r'url\s*=\s*(.*)', contents).group(1)
                        path_and_project_name = url.replace("https://github.com/", "").replace(".git", "")
                        return path_and_project_name
    return None


def fetch_latest_commit_hash() -> str or None:
    """
    Scan the .git folder for the latest commit hash
    :return:
    """

    url = "https://api.github.com/repos/MeshMonitors-Remote-1/ShopifyMonitor/commits"

    payload = {}
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'Bearer -',
        'Cookie': '_octo=GH1.1.613847517.1655532567; logged_in=no'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


def download_and_replace_file(session, url, file_path: str, auth_token: str):
    """
    Download a file from a url and replace the file at the given path
    :param auth_token:
    :param session:
    :param url:
    :param file_path:
    :return:
    """
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'Bearer {auth_token}',
        'Cookie': '_octo=GH1.1.613847517.1655532567; logged_in=no'
    }
    response = session.request("GET", url, headers=headers)

    if response.status_code != 200:
        print("File_Get Error: %s" % response.text)
        return None

    # Make folder if it doesn't exist
    if '/' in file_path:
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

    with open(file_path, 'wb') as f:
        file_content = base64.b64decode(response.json()['content'])
        f.write(file_content)


def get_update_file(auth_token: str, repo_url, force: bool) -> str or None:
    """
    Scan the .git folder for the latest commit hash
    :param force:
    :param auth_token:
    :param repo_url:
    :return:
    """

    url = f"https://api.github.com/repos/{repo_url}/contents/UPDATE_FILE"
    session = requests.Session()

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'Bearer {auth_token}',
        'Cookie': '_octo=GH1.1.613847517.1655532567; logged_in=no'
    }

    response = session.request("GET", url, headers=headers)

    if response.status_code == 200:
        # Get the file content and since it's a base64 encoded string, decode it
        content = base64.b64decode(response.json()['content'])

        # Convert the content to a string
        content = content.decode('utf-8')
        if force:
            if len(content) > 0:
                change_list = content.split('\n')
                for change in change_list:
                    change_wanted = change.split(':')
                    if len(change_wanted) > 1:
                        change_action = change_wanted[0]
                        change_file = change_wanted[1]
                        if change_action == 'overwrite':
                            print("Overwrite/Download file: %s" % change_file)
                            link = f"https://api.github.com/repos/" \
                                   f"{repo_url}/contents/{change_file}"
                            download_and_replace_file(session, link, change_file, auth_token)
        else:
            ask_for_confirmation = input("Do you want to replace the update/download files with the latest version? ["
                                         "y/n] ")
            if ask_for_confirmation.lower() == 'y':
                if len(content) > 0:
                    change_list = content.split('\n')
                    for change in change_list:
                        change_wanted = change.split(':')
                        if len(change_wanted) > 1:
                            change_action = change_wanted[0]
                            change_file = change_wanted[1]
                            if change_action == 'overwrite':
                                print("Overwrite/Download file: %s" % change_file)
                                link = f"https://api.github.com/repos/" \
                                       f"{repo_url}/contents/{change_file}"
                                download_and_replace_file(session, link, change_file, auth_token)
            else:
                print("Aborting...")
                sys.exit(0)
    else:
        print("Auth Error: %s" % response.text)
        return None


def get_all_files(auth_token: str, tree_url, repo_url, force: bool) -> None:
    session = requests.Session()

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'Bearer {auth_token}',
        'Cookie': '_octo=GH1.1.613847517.1655532567; logged_in=no'
    }

    response = session.request("GET", tree_url, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        for file in response_json['tree']:
            if file['type'] == 'blob':
                print(">> Downloading file: %s" % file['path'])
                url = f"https://api.github.com/repos/{repo_url}/contents/" + file['path']
                download_and_replace_file(session, url, file['path'], auth_token)
    else:
        print("Auth Error: %s" % response.text)
        return None


def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Downloads the latest version of the update files from the github repo')
    parser.add_argument('-p', help='Project ID', required=False)

    # Add argument called update that requires no arguments
    parser.add_argument('-u', help='Update files', action='store_true')

    # Add argument called -f that forces without asking for confirmation
    parser.add_argument('-f', help='Force update', action='store_true')

    # Add argument for the auth token
    parser.add_argument('-t', help='Auth token', required=False)

    args = parser.parse_args()
    project_id = args.p
    print("Project ID: %s" % project_id)
    # Check if user wrote the -u argument
    if args.u:
        print(">> Updating files...")
        # Check if UPDATE_FILE exists in the root of the folder
        if os.path.exists('UPDATE_FILE'):
            print(">> Found UPDATE_FILE")
            # Check if 'project' is in the UPDATE_FILE
            with open('UPDATE_FILE', 'r') as f:
                content = f.read()
                if 'project' in content:
                    # Get the project name using regex
                    project_name = re.search(r'project:(.*)', content).group(1)
                    print(">> Project name: %s" % project_name)
                    if not args.t:
                        token = input("Enter your GitHub token: ")
                    else:
                        token = args.t

                    git_url_input = project_name.rstrip('/')

                    # Remove spaces from all the sides of the string
                    git_url_input = git_url_input.strip()

                    if '/' not in git_url_input:
                        # Single Project ID given, add prefix 'MeshMonitors-Remote-1/'
                        git_url_input = f"MeshMonitors-Remote-1/{git_url_input}"

                    if git_url_input is not None:
                        is_empty = os.listdir(os.getcwd()) == []
                        if is_empty:
                            print(">> No files found in the current directory, downloading latest version...")
                            get_all_files(token,
                                          f"https://api.github.com/repos/{git_url_input}/git/trees/master?recursive=1",
                                          git_url_input, force=args.f)
                        else:
                            print(">> Found files in the current directory, updating latest version...")
                            get_update_file(auth_token=token, repo_url=git_url_input, force=args.f)

                else:
                    print(">> No project found in the UPDATE_FILE")
        else:
            print(">> No UPDATE_FILE found in root of folder")
    else:
        try:
            token = input("Enter your GitHub token: ")

            print(">> Executing mesh_sync version %s." % __version__)
            if check_if_dot_git_exists():
                print(">> Found .git folder, checking for updates...")
                git_url = find_git_url()
                if git_url is not None:
                    print(">> Found git url: %s" % git_url)
                    get_update_file(auth_token=token, repo_url=git_url, force=args.f)
            else:

                print(">> Could not find .git url")
                if project_id is None:
                    git_url_input = input("Please enter the [Project ID] that was given to you: ")
                else:
                    git_url_input = project_id

                git_url_input = git_url_input.rstrip('/')

                # Remove spaces from all the sides of the string
                git_url_input = git_url_input.strip()

                if '/' not in git_url_input:

                    # Single Project ID given, add prefix 'MeshMonitors-Remote-1/'
                    git_url_input = f"MeshMonitors-Remote-1/{git_url_input}"

                if git_url_input is not None:
                    is_empty = os.listdir(os.getcwd()) == []
                    if is_empty:
                        print(">> No files found in the current directory, downloading latest version...")
                        get_all_files(token, f"https://api.github.com/repos/{git_url_input}/git/trees/master?recursive=1",
                                      git_url_input, force=args.f)
                    else:
                        print(">> Found files in the current directory, updating latest version...")
                        get_update_file(auth_token=token, repo_url=git_url_input, force=args.f)
                else:
                    print("Please enter a valid git url. Aborting...")
                    sys.exit(0)
        except Exception as e:
            print("Error: %s" % e)
            sys.exit(0)
        finally:
            print(">> Done.")
