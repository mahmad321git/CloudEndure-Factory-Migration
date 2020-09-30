"""
TODO add docstring
"""

import sys
import argparse
import requests
import json
import csv

sys.path.insert(1, '.\\python')
sys.path.insert(1, '..')

from helper import json_helper              # noqa
from helper import parameter_parsing_helper  # noqa

serverendpoint = '/prod/user/servers'
appendpoint = '/prod/user/apps'
waveendpoint = '/prod/user/waves'


def get_reader(file):
    ordered_dict_list = []
    input_file = csv.DictReader(open(file))
    for row in input_file:
        ordered_dict_list.append(row)
    # return input_file
    return ordered_dict_list


def convert_string_to_list(row_str):
    row_list = []
    row_list = row_str.split(';')
    return row_list


def data_validation(data, app_list_csv):
    # Validate app attribute
    for app in app_list_csv:
        match = True
        attr = ""
        app_list_validation = []
        for row in data:
            if app['app_name'].strip() == row['app_name'].strip():
                app_list_validation.append(row)
        for app_validation in app_list_validation:
            wave_name = "Wave " + app_validation['wave_id'].strip()
            if wave_name != app['wave_name'].strip():
                match = False
                attr = 'wave_id'
            elif (app_validation['cloudendure_projectname'].strip()
                  != app['cloudendure_projectname'].strip()):
                match = False
                attr = 'cloudendure_projectname'
            elif app_validation['aws_accountid'] != app['aws_accountid']:
                match = False
                attr = 'aws_accountid'
        if (not match):
            print("Error: App attributes " + attr +
                  " doesn't match, please validate app: " + app['app_name'])
            sys.exit(1)


def uploading_data(data, token, UserHOST, profile, project_env):
    auth = {"Authorization": token}
    waves = json.loads(requests.get(
        UserHOST + waveendpoint, headers=auth).text)
    apps = json.loads(requests.get(UserHOST + appendpoint, headers=auth).text)
    wave_list_csv = []
    app_list_csv = []
    wave_ids = []
    app_list = []
    server_list = []

    for row in data:
        if row['wave_id'].strip() not in wave_list_csv:
            wave_list_csv.append(str(row['wave_id']).strip())
        match = False
        for app in app_list_csv:
            if row['app_name'].lower().strip() == app['app_name'].lower() \
                    .strip():
                match = True
        if (not match):
            app_item = {}
            app_item['app_name'] = row['app_name'].strip()
            app_item['wave_name'] = "Wave " + row['wave_id'].strip()
            app_item['cloudendure_projectname'] = \
                row['cloudendure_projectname'].strip()
            app_item['aws_accountid'] = row['aws_accountid'].strip()
            app_list_csv.append(app_item)

    data_validation(data, app_list_csv)

    # Get Unique new Wave Id, add to the list if Wave Id doesn't exist in the
    #  factory.
    for wave_id in wave_list_csv:
        match = False
        for wave in waves:
            wave_name = "Wave " + wave_id
            if str(wave_name) == str(wave['wave_name']):
                match = True
        if (not match):
            wave_ids.append(wave_id)
    if len(wave_ids) != 0:
        print("New Waves: ")
        print("")
        for wave in wave_ids:
            print("Wave " + wave)
        print("")
        # Creating new Waves in the migration factory
        for wave in wave_ids:
            wave_name = {}
            wave_name['wave_name'] = "Wave " + wave
            r = requests.post(UserHOST + waveendpoint,
                              headers=auth, data=json.dumps(wave_name))
            if r.status_code == 200:
                print("Wave " + wave + " created in the migration factory")
            else:
                print("Wave " + wave + " failed : " + r.text + ".......")
        print("")
        print("----------------------------------------")
        print("")

    # Get Unique new App Name, add to the resource list if App Name doesn't
    #  exist in the factory
    for app_csv in app_list_csv:
        new_waves = json.loads(requests.get(
            UserHOST + waveendpoint, headers=auth).text)
        for wave in new_waves:
            if app_csv['wave_name'] == str(wave['wave_name']):
                app_csv['wave_id'] = wave['wave_id']
                del app_csv['wave_name']
                break
        match = False
        for app in apps:
            if app_csv['app_name'].lower().strip() == app['app_name'].lower() \
                    .strip():
                match = True
                if app_csv['wave_id'] != app['wave_id']:
                    print("Error: Wave_id for app " +
                          app_csv['app_name'] + " doesn't match the Wave_id "
                          "for the same app in the factory")
                    sys.exit(2)
                if (app_csv['cloudendure_projectname']
                        != app['cloudendure_projectname']):
                    print("Error: cloudendure_projectname for app " +
                          app_csv['app_name'] + " doesn't match the "
                          "cloudendure_projectname for the same app "
                          "in the factory")
                    sys.exit(3)
                if app_csv['aws_accountid'] != app['aws_accountid']:
                    print("Error: aws_accountid for app " +
                          app_csv['app_name'] + " doesn't match the "
                          "aws_accountid for the same app in the factory")
                    sys.exit(4)
        if (not match):
            app_list.append(app_csv)
    if len(app_list) != 0:
        print("New Apps: ")
        print("")
        for app in app_list:
            print(app["app_name"])
        print("")
        # Creating new Apps in the migration factory
        for app in app_list:
            r = requests.post(UserHOST + appendpoint,
                              headers=auth, data=json.dumps(app))
            if r.status_code == 200:
                print("App " + app['app_name'] +
                      " created in the migration factory")
            else:
                print("App " + app['app_name'] +
                      " failed : " + r.text + ".......")
        print("")
        print("----------------------------------------")
        print("")
    # Get Unique server names, add to the resource list if Server Name doesn't
    #  exist in the factory
    newapps = json.loads(requests.get(
        UserHOST + appendpoint, headers=auth).text)

    subnets = {}
    securitygroups = {}

    for row in data:
        for app in newapps:
            if row['app_name'].lower().strip() == app['app_name'].lower() \
                    .strip():
                row['app_id'] = app['app_id']
        tags = []
        tag = {}
        server_item = {}
        server_item['server_name'] = row['server_name'].strip()
        tag['key'] = 'Name'
        tag['value'] = row['server_name'].strip()
        tags.append(tag)
        server_item['tags'] = tags
        server_item['app_id'] = row['app_id'].strip()
        server_item['server_os'] = row['server_os'].strip()
        server_item['server_os_version'] = row['server_os_version'].strip()
        server_item['server_fqdn'] = row['server_fqdn'].strip()
        server_item['server_tier'] = row['server_tier'].strip()
        server_item['server_environment'] = row['server_environment'].strip()
        server_item['instanceType'] = row['instanceType'].strip()
        server_item['tenancy'] = row['tenancy'].strip()

        # Subnets
        _subnets = convert_string_to_list(row['subnet_IDs'].strip())
        _subnets_test = convert_string_to_list(row['subnet_IDs_test'].strip())

        subnets_list = []
        for _subnet in _subnets:
            if _subnet not in subnets:
                param = '/'.join([project_env, 'network', _subnet])
                subnets[_subnet] = parameter_parsing_helper \
                    .fetch_parameter(param, profile=profile)

            subnets_list.append(subnets[_subnet])

        subnets_test_list = []
        for _subnet_test in _subnets_test:
            if _subnet_test not in subnets:
                param = '/'.join([project_env, 'network', _subnet_test])
                subnets[_subnet_test] = parameter_parsing_helper \
                    .fetch_parameter(param, profile=profile)

            subnets_test_list.append(subnets[_subnet])

        server_item['subnet_IDs'] = subnets_list
        server_item['subnet_IDs_test'] = subnets_test_list

        # Security Groups
        _securitygroups = convert_string_to_list(
            row['securitygroup_IDs'].strip())
        _securitygroups_test = convert_string_to_list(
            row['securitygroup_IDs_test'].strip())

        securitygroups_list = []
        for _securitygroup in _securitygroups:
            if _securitygroup not in securitygroups:
                param = '/'.join([project_env, 'network', _securitygroup])
                securitygroups[_securitygroup] = parameter_parsing_helper \
                    .fetch_parameter(param, profile=profile)

            securitygroups_list.append(securitygroups[_securitygroup])

        securitygroups_test_list = []
        for _securitygroup_test in _securitygroups_test:
            if _securitygroup_test not in securitygroups:
                param = '/'.join([project_env, 'network',
                                  _securitygroup_test])
                securitygroups[_securitygroup_test] = parameter_parsing_helper \
                    .fetch_parameter(param, profile=profile)

            securitygroups_test_list \
                .append(securitygroups[_securitygroup_test])

        server_item['securitygroup_IDs'] = securitygroups_list
        server_item['securitygroup_IDs_test'] = securitygroups_test_list

        server_list.append(server_item)
    if len(server_list) != 0:
        print("New Servers: ")
        print("")
        for server in server_list:
            print(server['server_name'])
        print("")
        # Creating new Apps in the migration factory
        for server in server_list:
            r = requests.post(UserHOST + serverendpoint,
                              headers=auth, data=json.dumps(server))
            if r.status_code == 200:
                print("Server " + server['server_name'] +
                      " created in the migration factory")
            else:
                print("ERROR: " + server['server_name'] +
                      " failed : " + r.text + ".......")


def Factorylogin(username, password, LoginHOST):
    login_data = {'username': username, 'password': password}
    r = requests.post(LoginHOST + '/prod/login',
                      data=json.dumps(login_data))
    if r.status_code == 200:
        print("Migration Factory : You have successfully logged in")
        print("")
        token = str(json.loads(r.text))
        return token
    else:
        print("ERROR: Incorrect username or password....")
        print("")
        sys.exit(5)


def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--Intakeform', default='0-Migration-intake-form.csv')
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
    print("*Reading intake form List*")
    print("****************************")
    data = get_reader(args.Intakeform)
    print("Intake form data loaded for processing....")
    print("")

    print("*********************************************")
    print("*Creating resources in the migration factory*")
    print("*********************************************")
    aws_profile = config['AWS_DR_PROFILE']
    _ = uploading_data(data, token, UserHOST, aws_profile, project_env)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
