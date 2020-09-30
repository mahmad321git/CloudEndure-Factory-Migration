"""
TODO add docstring
"""

# from __future__ import print_function
import paramiko
import sys
import argparse
import requests
import json
# import getpass
import os

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
    servers = json.loads(
        requests.get(UserHOST + serverendpoint, headers=auth).text)
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
                        if server['server_os'].lower() == "linux":
                            serverlist.append(server['server_fqdn'])
                    else:
                        print("ERROR: server_fqdn for server: " + server[
                            'server_name'] + " doesn't exist")
                        sys.exit(4)
                else:
                    print('server_os attribute does not exist for server: ' +
                          server[
                              'server_name'] + ", please update this attribute")
                    sys.exit(2)

    if len(serverlist) == 0:
        print("INFO: Serverlist for wave: " + waveid + " contains no Linux"
              "servers....")
        print("")
        sys.exit(5)
    else:
        print("successfully retrived server list")
        for s in serverlist:
            print(s)
        print("")
        return serverlist


def open_ssh(host, username, key_pwd, using_key):
    ssh = None
    try:
        if using_key:
            private_key = paramiko.RSAKey.from_private_key_file(key_pwd)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=username, pkey=private_key)
        else:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=username, password=key_pwd)
    except IOError as io_error:
        error = "Unable to connect to host " + host + " with username " + \
                username + " due to " + str(io_error)
        print(error)
    except paramiko.SSHException as ssh_exception:
        error = "Unable to connect to host " + host + " with username " + \
                username + " due to " + str(ssh_exception)
        print(error)
    return ssh


def upload_files(host, username, key_pwd, using_key, local_file_path):
    error = ''
    file_path = local_file_path
    ssh = None
    ftp = None
    try:
        ssh = open_ssh(host, username, key_pwd, using_key)
        _ = ssh.exec_command(
            "[ -d /tmp/copy_ce_files ] && echo 'Directory exists' "
            "|| mkdir /tmp/copy_ce_files")
        _ = ssh.exec_command(
            "[ -d '/boot/post_launch' ] && echo 'Directory exists' "
            "|| sudo mkdir /boot/post_launch")
        ftp = ssh.open_sftp()
        if os.path.isfile(file_path):
            filename = file_path.split("/")
            filename = filename[-1]
            ftp.put(file_path, '/tmp/copy_ce_files/' + filename)
        else:
            for file in os.listdir(local_file_path):
                file_path = os.path.join(local_file_path, file)
                if os.path.isfile(file_path):
                    ftp.put(file_path, '/tmp/copy_ce_files/' + file)
                else:
                    print('ignoring the subdirectories... ' + file_path)
        _ = ssh.exec_command(
            "sudo cp /tmp/copy_ce_files/* /boot/post_launch "
            "&& sudo chown cloudendure /boot/post_launch/* "
            "&& sudo chmod +x /boot/post_launch/*")
    except Exception as e:
        error = "Copying " + file_path + " to " + \
                "/boot/post_launch" + " on host " + host + " failed due to " + \
                str(e)
        print(error)
    finally:
        if ftp is not None:
            ftp.close()
        if ssh is not None:
            ssh.close()
    return error


def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.
                                     RawDescriptionHelpFormatter)
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
    servers = ServerList(args.Waveid, token, UserHOST)

    print("*****************************************")
    print("*Provide Linux credentials to copy files*")
    print("*****************************************")
    linux_username = '/'.join([project_env, 'linux', 'username'])
    linux_password = '/'.join([project_env, 'linux', 'password'])

    user_name = parameter_parsing_helper \
        .fetch_parameter(linux_username)
    has_key = config['HAS_PASSKEY']

    if isinstance(has_key, str):
        if 'true' in has_key.lower():
            has_key = True

    if has_key:
        pass_key = config['linux_password']['key']
    else:
        pass_key = parameter_parsing_helper \
            .fetch_parameter(linux_password)

    print("")
    print("*************************************")
    print("*Copying files to post_launch folder*")
    print("*************************************")
    print("")
    for server in servers:
        err_reason = upload_files(server, user_name, pass_key, has_key,
                                  args.Source)
        if not err_reason:
            print("Successfully copied files to " + server)
        else:
            print("Unable to copy files to " +
                  server + " due to " + err_reason)
        print("")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
