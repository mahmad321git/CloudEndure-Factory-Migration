"""
TODO add docstring
"""

import sys
import argparse
import json
import requests
# import getpass
import time
import paramiko

sys.path.insert(1, '.\\python')
sys.path.insert(1, '..')

from helper import json_helper               # noqa
from helper import parameter_parsing_helper  # noqa

server_endpoint = '/prod/user/servers'
app_endpoint = '/prod/user/apps'


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


def ServerList(waveid, token, UserHOST, Projectname):
    # Get all Apps and servers from migration factory
    auth = {"Authorization": token}
    servers = json.loads(requests.get(
        UserHOST + server_endpoint, headers=auth).text)
    # print(servers)
    apps = json.loads(requests.get(UserHOST + app_endpoint, headers=auth).text)
    # print(apps)

    # Get App list
    applist = []
    for app in apps:
        if 'wave_id' in app:
            if str(app['wave_id']) == str(waveid):
                if Projectname != "":
                    if str(app['cloudendure_projectname']) == str(Projectname):
                        applist.append(app['app_id'])
                else:
                    applist.append(app['app_id'])
    servers_linux = []
    for app in applist:
        for server in servers:
            if app == server['app_id']:
                if 'server_os' in server:
                    if 'server_fqdn' in server:
                        if server['server_os'].lower() == "linux":
                            servers_linux.append(server)
                    else:
                        print("ERROR: server_fqdn for server: " +
                              server['server_name'] + " doesn't exist")
                        sys.exit(4)
                else:
                    print('server_os attribute does not exist for server: ' +
                          server['server_name'] +
                          ", please update this attribute")
                    sys.exit(2)
    if len(servers_linux) == 0:
        print("ERROR: Serverlist for wave: " + waveid +
              " in CE Project " + Projectname + " is empty....")
        print("")
        sys.exit(5)
    else:
        print("successfully retrieved server list")
        print("")
        if len(servers_linux) > 0:
            print("*** Linux Server List ***")
            print("")
            for server in servers_linux:
                print(server['server_name'])
        print("")
        return servers_linux


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


def find_distribution(ssh):
    distribution = "linux"
    output = ''
    error = ''
    try:
        stdin, stdout, stderr = ssh.exec_command("cat /etc/*release")
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
    except IOError as io_error:
        error = "Unable to find distribution due to " + str(io_error)
        print(error)
    except paramiko.SSHException as ssh_exception:
        error = "Unable to find distribution due to " + str(ssh_exception)
        print(error)
    if "ubuntu" in output:
        distribution = "ubuntu"
    elif "fedora" in output:
        distribution = "fedora"
    elif "suse" in output:
        distribution = "suse"
    return distribution


def get_add_user_cmd(ssh, new_user_name, new_user_password):
    try:
        distribution = find_distribution(ssh)
        if "ubuntu" in distribution:
            new_password_encrypt = '$(perl -e \'print crypt($ARGV[0], ' \
                f'"password")\' \'{new_user_password}\')'
            command = 'sudo useradd -m ' + new_user_name + \
                ' -p ' + new_password_encrypt + ' -G sudo'
        else:
            command = 'sudo adduser -m ' + new_user_name + \
                ' -p ' + new_user_password + ' -g wheel'
    except Exception as ex:
        print("Error while fetching add user command due to " + str(ex))
    else:
        return command


def create_user(host, system_login_username, system_key_pwd, using_key,
                new_user_name, new_password):
    if not (new_user_name and new_password):
        print("User name or password cannot be null or empty for the new user")
        return
    ssh_client = None
    try:
        ssh_client = open_ssh(host, system_login_username,
                              system_key_pwd, using_key)
        try:
            add_user_cmd = get_add_user_cmd(
                ssh_client, new_user_name, new_password)
            no_password_sudoers_cmd = "sudo sh -c \"echo '" + \
                new_user_name + " ALL=NOPASSWD: ALL' >> /etc/sudoers\""
            ssh_client.exec_command(add_user_cmd)
            ssh_client.exec_command("sleep 2")
            time.sleep(2)
            stdin, stdout, stderr = ssh_client.exec_command(
                "cut -d: -f1 /etc/passwd")
            users_output_str = stdout.read().decode("utf-8")
            users_list = users_output_str.split("\n")
            if new_user_name in users_list:
                print("")
                print("User %s got created successfully on host %s" %
                      (new_user_name, host))
                ssh_client.exec_command(no_password_sudoers_cmd)
                print("Modified sudoers to set NOPASSWORD for user " +
                      new_user_name)
            else:
                print("User %s not created on host %s" % (new_user_name, host))
        except paramiko.SSHException as ssh_exception:
            error = "Server fails to execute the AddUser command on host " + \
                    host + " with username " + \
                    new_user_name + " due to " + str(ssh_exception)
            print(error)
    except Exception as ex:
        error = "Error while creating user on host " + host + \
                " with username " + new_user_name + " due to " + str(ex)
        print(error)
    finally:
        if ssh_client:
            ssh_client.close()


def delete_linux_user(host, system_login_username, system_key_pwd, using_key,
                      username_to_delete):
    if not username_to_delete:
        print("User name to delete cannot be null or empty")
        return
    ssh_client = None
    try:
        ssh_client = open_ssh(host, system_login_username,
                              system_key_pwd, using_key)
        try:
            delete_user_cmd = 'sudo userdel -r ' + username_to_delete
            ssh_client.exec_command(delete_user_cmd)
            ssh_client.exec_command("sleep 2")
            time.sleep(2)
            stdin, stdout, stderr = ssh_client.exec_command(
                "cut -d: -f1 /etc/passwd")
            users_output_str = stdout.read().decode("utf-8")
            users_list = users_output_str.split("\n")
            if username_to_delete not in users_list:
                print("User deleted successfully on " + host)
            else:
                print("Deletion of user %s was not successfull on %s" % (
                    username_to_delete, host))
        except paramiko.SSHException as ssh_exception:
            error = "Server fails to execute the AddUser command on host " + \
                    host + " with username " + \
                    username_to_delete + " due to " + str(ssh_exception)
            print(error)
    except Exception as ex:
        error = "Error while deleting user on host " + host + \
                " with username " + username_to_delete + " due to " + str(ex)
        print(error)
    finally:
        if ssh_client:
            ssh_client.close()


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--Waveid', required=True)
    parser.add_argument('--CloudEndureProjectName', default="")
    parser.add_argument('--config', required=True)
    parser.add_argument('--modification', required=True)
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
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
    print("*** Getting Server List ****")
    print("****************************")
    linux_servers = ServerList(args.Waveid, token, UserHOST,
                               args.CloudEndureProjectName)

    if len(linux_servers) > 0:
        print("******************************************")
        print("* Login Linux Sudo username and password *")
        print("******************************************")
        linux_username = '/'.join([project_env, 'linux', 'username'])
        linux_password = '/'.join([project_env, 'linux', 'password'])

        admin_usr_name = parameter_parsing_helper \
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

        new_user_name = args.username

        if args.modification.upper() == 'CREATE':
            print("")
            print("*********************************************")
            print("* Creating local sudo user on Linux servers *")
            print("*********************************************")
            print("")
            new_password = args.password

            for server in linux_servers:
                host = server["server_fqdn"]
                create_user(host, admin_usr_name, pass_key, has_key,
                            new_user_name, new_password)
                print("")
        elif args.modification.upper() == 'DELETE':
            print("")
            print("**********************************************")
            print("*Deleting local sudo users on all the servers*")
            print("**********************************************")
            print("")
            print("")
            for server in linux_servers:
                host = server["server_fqdn"]
                delete_linux_user(host, admin_usr_name, pass_key,
                                  has_key, new_user_name)
                print("")
    else:
        print("ERROR: There is no Linux servers in this Wave")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
