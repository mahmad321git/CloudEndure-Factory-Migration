"""
TODO add docstring
"""

# from __future__ import print_function
import sys
import argparse
import requests
import json
import subprocess
# import getpass

sys.path.insert(1, '.\\python')
sys.path.insert(1, '..')

from helper import json_helper              # noqa
from helper import parameter_parsing_helper  # noqa

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


def ServerList(waveid, token, UserHOST):
    # Get all Apps and servers from migration factory
    auth = {"Authorization": token}
    servers = json.loads(requests.get(
        UserHOST + serverendpoint, headers=auth).text)
    # print(servers)
    apps = json.loads(requests.get(UserHOST + appendpoint, headers=auth).text)
    # print(apps)

    # Get App list
    applist = []
    for app in apps:
        if 'wave_id' in app:
            if str(app['wave_id']) == str(waveid):
                applist.append(app['app_id'])

    # Get Server List
    serverlist = []
    for app in applist:
        for server in servers:
            if app == server['app_id']:
                if 'server_os' in server:
                    if 'server_fqdn' in server:
                        if server['server_os'].lower() == "windows":
                            serverlist.append(server['server_fqdn'])
                    else:
                        print("ERROR: server_fqdn for server: " +
                              server['server_name'] + " doesn't exist")
                        sys.exit(4)
                else:
                    print('server_os attribute does not exist for server: ' +
                          server['server_name'] +
                          ", please update this attribute")
                    sys.exit(2)

    if len(serverlist) == 0:
        print("ERROR: Serverlist for wave: " + waveid + " contains no Windows"
              "servers....")
        print("")
        sys.exit(5)
    else:
        print("successfully retrived server list")
        for s in serverlist:
            print(s)
        return serverlist


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--Waveid', required=True)
    parser.add_argument('--Source', required=True)
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

    print("****************************")
    print("*Getting Server List*")
    print("****************************")
    Servers = ServerList(args.Waveid, token, UserHOST)

    print("")
    print("*************************************")
    print("*Copying files to post_launch folder*")
    print("*************************************")

    for server in Servers:
        destpath = "'\\" + "\\" + server + \
            "\\c$\\Program Files (x86)\\CloudEndure\\post_launch\\'"
        sourcepath = "'" + args.Source + "\\*'"
        command1 = "if (!(Test-path " + destpath + \
            ")) {New-Item -Path " + destpath + " -ItemType directory}"
        command2 = "Copy-Item -Path " + sourcepath + " -Destination " + destpath
        print("Copying files to server: " + server)
        p1 = subprocess.Popen(["powershell.exe", command1], stdout=sys.stdout)
        p1.communicate()
        p2 = subprocess.Popen(["powershell.exe", command2], stdout=sys.stdout)
        p2.communicate()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
