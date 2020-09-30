"""
TODO add docstring
"""

import sys
import argparse
import requests
import json
import subprocess
# import getpass
import time

sys.path.insert(1, '.\\python')
sys.path.insert(1, '..')

from helper import json_helper               # noqa
from helper import ip_address_helper         # noqa
from helper import parameter_parsing_helper  # noqa
linuxpkg = __import__("1-Install-Linux")


HOST = 'https://console.cloudendure.com'
headers = {'Content-Type': 'application/json'}
session = {}
endpoint = '/api/latest/{}'


serverendpoint = '/prod/user/servers'
appendpoint = '/prod/user/apps'


def Factorylogin(username, password, LoginHOST):
    login_data = {'username': username, 'password': password}
    r = requests.post(LoginHOST + '/prod/login',
                      data=json.dumps(login_data))
    if r.status_code == 200:
        print("Migration Factory : You have successfully logged in")
        print("")
        token = str(json.loads(r.text))
        return token
    if r.status_code == 502:
        print("ERROR: Incorrect username or password....")
        sys.exit(1)
    else:
        print(r.text)
        sys.exit(2)


def CElogin(userapitoken, endpoint):
    login_data = {'userApiToken': userapitoken}
    r = requests.post(HOST + endpoint.format('login'),
                      data=json.dumps(login_data), headers=headers)
    if r.status_code == 200:
        print("CloudEndure : You have successfully logged in")
        print("")
    if r.status_code != 200 and r.status_code != 307:
        if r.status_code == 401 or r.status_code == 403:
            print('ERROR: The CloudEndure login credentials provided cannot be'
                  ' authenticated....')
        elif r.status_code == 402:
            print('ERROR: There is no active license configured for this '
                  'CloudEndure account....')
        elif r.status_code == 429:
            print('ERROR: CloudEndure Authentication failure limit has been '
                  'reached. The service will become available for additional'
                  ' requests after a timeout....')

    # check if need to use a different API entry point
    if r.history:
        endpoint = '/' + '/'.join(r.url.split('/')[3:-1]) + '/{}'
        r = requests.post(HOST + endpoint.format('login'),
                          data=json.dumps(login_data), headers=headers)

    session['session'] = r.cookies['session']

    try:
        headers['X-XSRF-TOKEN'] = r.cookies['XSRF-TOKEN']
    # TODO improve the following.
    except Exception:
        pass


def GetCEProject(projectname):
    r = requests.get(HOST + endpoint.format('projects'),
                     headers=headers, cookies=session)
    if r.status_code != 200:
        print("ERROR: Failed to fetch the project....")
        sys.exit(2)
    try:
        # Get Project ID
        project_id = ""
        projects = json.loads(r.text)["items"]
        project_exist = False
        for project in projects:
            if project["name"] == projectname:
                project_id = project["id"]
                project_exist = True
        if not project_exist:
            print("ERROR: Project Name: " + projectname +
                  " does not exist in CloudEndure....")
            sys.exit(3)
        return project_id
    except Exception:
        print("ERROR: Failed to fetch the project....")
        sys.exit(4)


def GetInstallToken(project_id):
    # Get Machine List from CloudEndure
    project = requests.get(
        HOST + endpoint.format('projects/{}').format(project_id),
        headers=headers, cookies=session)
    InstallToken = json.loads(project.text)['agentInstallationToken']
    return InstallToken


def ProjectList(waveid, token, UserHOST, serverendpoint, appendpoint):
    # Get all Apps and servers from migration factory
    auth = {"Authorization": token}
    servers = json.loads(requests.get(
        UserHOST + serverendpoint, headers=auth).text)
    # print(servers)
    apps = json.loads(requests.get(UserHOST + appendpoint, headers=auth).text)
    # print(apps)
    newapps = []

    CEProjects = []
    # Check project names in CloudEndure
    for app in apps:
        Project = {}
        if 'wave_id' in app:
            if str(app['wave_id']) == str(waveid):
                newapps.append(app)
                if 'cloudendure_projectname' in app:
                    Project['ProjectName'] = app['cloudendure_projectname']
                    project_id = GetCEProject(Project['ProjectName'])
                    Project['ProjectId'] = project_id
                    install_token = GetInstallToken(project_id)
                    Project['InstallToken'] = install_token
                    if Project not in CEProjects:
                        CEProjects.append(Project)
                else:
                    print("ERROR: App " + app['app_name'] + " is not linked to"
                          " any CloudEndure project....")
                    sys.exit(5)
    Projects = ServerList(newapps, servers, CEProjects, waveid)
    return Projects


def ServerList(apps, servers, CEProjects, waveid):
    servercount = 0
    Projects = CEProjects
    for Project in Projects:
        Windows = []
        Linux = []
        for app in apps:
            if str(app['cloudendure_projectname']) == Project['ProjectName']:
                for server in servers:
                    if app['app_id'] == server['app_id']:
                        if 'server_os' in server:
                            if 'server_fqdn' in server:
                                if server['server_os'].lower() == "windows":
                                    Windows.append(server)
                                elif server['server_os'].lower() == "linux":
                                    Linux.append(server)
                            else:
                                print("ERROR: server_fqdn for server: " +
                                      server['server_name'] + " doesn't exist")
                                sys.exit(4)
                        else:
                            print('server_os attribute does not exist for '
                                  'server: ' + server['server_name'] +
                                  ', please update this attribute')
                            sys.exit(2)
        Project['Windows'] = Windows
        Project['Linux'] = Linux
        # print(Project)
        servercount = servercount + len(Windows) + len(Linux)
    if servercount == 0:
        print("ERROR: Serverlist for wave: " + waveid + " is empty....")
        sys.exit(3)
    else:
        return Projects


def AgentCheck(projects, token, UserHOST):
    auth = {"Authorization": token}
    success_servers = []
    failed_servers = []
    for project in projects:
        project_id = GetCEProject(project['ProjectName'])
        m = requests.get(HOST + endpoint.format('projects/{}/machines').format(
            project_id), headers=headers, cookies=session)
        if len(project['Windows']) > 0:
            for w in project['Windows']:
                machine_exist = False
                serverattr = {}
                for machine in json.loads(m.text)["items"]:
                    if w["server_name"].lower() == machine[
                            'sourceProperties']['name'].lower() or w[
                                "server_fqdn"].lower() == machine[
                                    'sourceProperties']['name'].lower():
                        machine_exist = True
                if machine_exist:
                    success_servers.append(w['server_fqdn'])
                    serverattr = {
                        "migration_status": "CE Agent Install - Success"}
                else:
                    failed_servers.append(w['server_fqdn'])
                    serverattr = {
                        "migration_status": "CE Agent Install - Failed"}
                _ = requests.put(
                    UserHOST + serverendpoint + '/' + w['server_id'],
                    headers=auth, data=json.dumps(serverattr))
        if len(project['Linux']) > 0:
            for li in project['Linux']:
                serverattr = {}
                machine_exist = False
                serverattr = {}
                for machine in json.loads(m.text)["items"]:
                    if li["server_name"].lower() == machine[
                        'sourceProperties']['name'].lower() or li[
                            "server_fqdn"].lower() == machine[
                                'sourceProperties']['name'].lower():
                        machine_exist = True
                if machine_exist:
                    success_servers.append(li['server_fqdn'])
                    serverattr = {
                        "migration_status": "CE Agent Install - Success"}
                else:
                    failed_servers.append(li['server_fqdn'])
                    serverattr = {
                        "migration_status": "CE Agent Install - Failed"}
                _ = requests.put(UserHOST + serverendpoint + '/' +
                                 li['server_id'], headers=auth,
                                 data=json.dumps(serverattr))
    if len(success_servers) > 0:
        print("***** CE Agent installed successfully on the following "
              "servers *****")
        for s in success_servers:
            print("  " + s)
        print("")
    if len(failed_servers) > 0:
        print("##### CE Agent install failed on the following servers #####")
        for s in failed_servers:
            print("  " + s)


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--Waveid', required=True)
    parser.add_argument('--config', required=True)
    args = parser.parse_args(arguments)

    config = json_helper.parse(args.config)

    project_env = '/'.join(['', config['PROJECT'], config['ENV']])

    # Fetching API Endpoints from AWS Parameter Store.
    login_endpoint = '/'.join([project_env, 'endpoint', 'login'])
    user_endpoint = '/'.join([project_env, 'endpoint', 'user'])
    LoginHOST = parameter_parsing_helper \
        .fetch_parameter(login_endpoint)
    UserHOST = parameter_parsing_helper \
        .fetch_parameter(user_endpoint)

    print("")
    print("****************************")
    print("*Login to Migration factory*")
    print("****************************")

    # Fetching factory login credentials from AWS Parameter Store.
    factory_username = '/'.join([project_env, 'factory', 'username'])
    factory_password = '/'.join([project_env, 'factory', 'password'])

    factory_username = parameter_parsing_helper \
        .fetch_parameter(factory_username)
    factory_password = parameter_parsing_helper \
        .fetch_parameter(factory_password)

    token = Factorylogin(factory_username, factory_password, LoginHOST)

    print("")
    print("****************************")
    print("* Logging into CloudEndure *")
    print("****************************")

    ce_api_token = '/'.join([project_env, 'cloudendure', 'api_token'])

    ce_api_token = parameter_parsing_helper \
        .fetch_parameter(ce_api_token)

    r = CElogin(ce_api_token, endpoint)
    if r is not None and "ERROR" in r:
        print(r)

    print("****************************")
    print("*** Getting Server List ***")
    print("****************************")
    Projects = ProjectList(args.Waveid, token, UserHOST,
                           serverendpoint, appendpoint)
    linux_machines = False
    for project in Projects:
        if (len(project['Windows']) + len(project['Linux']) == 0):
            print("* CE Project " +
                  project['ProjectName'] + " server list is empty *")
        else:
            print("* CE Project " + project['ProjectName'] + " *")
            if len(project['Windows']) > 0:
                print("   # Windows Server List #: ")
                for s in project['Windows']:
                    print("       " + s['server_fqdn'])
            if len(project['Linux']) > 0:
                linux_machines = True
                try:
                    print("   # Linux Server List #: ")
                    for s in project['Linux']:
                        print("       " + s['server_fqdn'])
                except Exception as error:
                    print('ERROR', error)
                    sys.exit(4)
        print("")

    print("*************************************************")
    print("* Logging into Linux Sudo username and password *")
    print("*************************************************")

    if linux_machines:
        user_name = ""
        pass_key = ""
        has_key = False

        linux_username = '/'.join([project_env, 'linux', 'username'])
        linux_password = '/'.join([project_env, 'linux', 'password'])

        user_name = parameter_parsing_helper \
            .fetch_parameter(linux_username)
        has_key = config['HAS_PASSKEY']

        if isinstance(has_key, str):
            if 'true' in has_key.lower():
                has_key = True
            else:
                has_key = False

        if has_key:
            pass_key = config['PASSKEY_LOCATION']
        else:
            pass_key = parameter_parsing_helper \
                .fetch_parameter(linux_password)

    # Pass parameters to PowerShell
    # First Parameter - $reinstall - "Yes" or "No"
    # Second Parameter - $API_token - CloudEndure Install token
    # Third Parameter - $Servername - Server name that matchs Wave Id and
    #  CloudEndure project name
    print("")
    print("*********************************")
    print("* Installing CloudEndure Agents *")
    print("*********************************")
    print("")
    server_status = {}
    for project in Projects:
        server_string = ""
        server_ip_string = ""
        if len(project['Windows']) > 0:
            for server in project['Windows']:
                if ip_address_helper \
                        .is_valid_ip_address(server['server_fqdn']):
                    server_ip_string = server_ip_string \
                        + server['server_fqdn'] + ','
                else:
                    server_string = server_string + server['server_fqdn'] + ','
            server_string = server_string[:-1]
            server_ip_string = server_ip_string[:-1]
            if server_string:
                p = subprocess.Popen(["powershell.exe",
                                      "..\\migration_factory\\"
                                      "automation_scripts\\"
                                      "1-Install-Windows.ps1",
                                      "No", project['InstallToken'],
                                      server_string],
                                     stdout=sys.stdout)
                p.communicate()

            if server_ip_string:
                windows_username = '/'.join([project_env,
                                             'windows', 'username'])
                windows_password = '/'.join([project_env,
                                             'windows', 'password'])

                windows_user_name = parameter_parsing_helper \
                    .fetch_parameter(windows_username)
                windows_pass_key = parameter_parsing_helper \
                    .fetch_parameter(windows_password)
                p = subprocess.Popen(["powershell.exe",
                                      "..\\migration_factory\\"
                                      "automation_scripts\\"
                                      "1-Install-Windows-IPAddr.ps1",
                                      "No", project['InstallToken'],
                                      server_ip_string,
                                      windows_user_name,
                                      windows_pass_key],
                                     stdout=sys.stdout)
                p.communicate()
        if len(project['Linux']) > 0:
            for server in project['Linux']:
                status = linuxpkg.install_cloud_endure(server['server_fqdn'],
                                                       user_name,
                                                       pass_key,
                                                       has_key,
                                                       project['InstallToken'])
                server_status.update({server['server_fqdn']: status})
        print("")

    print("")
    print("********************************")
    print("*Checking Agent install results*")
    print("********************************")
    print("")

    time.sleep(5)
    AgentCheck(Projects, token, UserHOST)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
