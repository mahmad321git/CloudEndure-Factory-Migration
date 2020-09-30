"""
TODO add docstring
"""
import sys
import json
import requests

from helper import json_helper
from helper import csv_helper
from helper import parameter_parsing_helper


def get_access_token(username, password, login_host):
    """ This function is used to get access token from API Gateway
        using Cognito User Credentials from SSM Parameter Store."""

    login_url = login_host + '/prod/login'

    login_params = {
        'username': username,
        'password': password
    }

    r = requests.post(url=login_url, data=json.dumps(login_params))
    if r.status_code == 200:
        print("Migration Factory : You have successfully logged in")
        print("")
        token = str(json.loads(r.text))
        return token
    else:
        print("ERROR: Incorrect username or password....")
        print("")
        sys.exit(5)


def get_attributes(access_token, admin_host):
    """ This function is used to get attributes from
        admin/schema/app Endpoint using user access token."""
    admin_app_url = admin_host + '/prod/admin/schema/app'

    access_token = access_token.strip('\"')
    headers = {'Authorization': access_token}

    r = requests.get(url=admin_app_url, headers=headers)

    json_response = r.json()
    return json_response['attributes']


def compare_projectname(attributes, proj_list_csv):
    """ This function compares the project list from API gateway with
        project list from 0-Migration-intake-form.csv file and returns
        a new list containing distinct values from both lists """

    for x in attributes:
        if x['name'] == 'cloudendure_projectname':
            project_list = x['listvalue'].split(",")
        else:
            pass

    for project_name in proj_list_csv:
        if project_name in project_list:
            pass
        else:
            project_list.append(project_name)
    project_names = ','.join(project_list)
    return project_names


def update_attributes(access_token, project_list, admin_host):
    """ This function will update cloudendure_projectname
        attribute with new project list using PUT request"""
    admin_app_url = admin_host + '/prod/admin/schema/app'
    access_token = access_token.strip('\"')
    headers = {'Authorization': access_token}

    data = {
        "event": "PUT",
        "name": "cloudendure_projectname",
        "update": {
                "name": "cloudendure_projectname",
                "description": "cloudendure project name",
                "listvalue": project_list,
                "name": "cloudendure_projectname",
                "type": "list"
        }
    }
    r = requests.put(url=admin_app_url, headers=headers, json=data)
    return r.status_code


if __name__ == "__main__":
    # Reading configs.
    config = json_helper.parse('config\\config.json')

    # Extracting project names from the intake form.
    cloudendure_projectname_list = sorted({intake['cloudendure_projectname']
                                           for intake in csv_helper
                                           .parse(config['INTAKE_FORM'])})

    # Parameter Store structure
    project_env = '/'.join(['', config['PROJECT'], config['ENV']])

    # Fetching API Endpoints from AWS Parameter Store.
    login_endpoint = '/'.join([project_env, 'endpoint', 'login'])
    admin_endpoint = '/'.join([project_env, 'endpoint', 'admin'])

    login_host = parameter_parsing_helper \
        .fetch_parameter(login_endpoint)
    admin_host = parameter_parsing_helper \
        .fetch_parameter(admin_endpoint)

    # Fetching login credentials from AWS Parameter Store.
    factory_username = '/'.join([project_env, 'factory', 'username'])
    factory_password = '/'.join([project_env, 'factory', 'password'])

    username = parameter_parsing_helper \
        .fetch_parameter(factory_username)
    password = parameter_parsing_helper \
        .fetch_parameter(factory_password)

    # Logging into CE Migration Factory.
    access_token = get_access_token(username, password, login_host)

    # Fetching attributes.
    attributes = get_attributes(access_token, admin_host)

    # Comparing projects from intake form and migration factory project list.
    project_list = compare_projectname(
        attributes, cloudendure_projectname_list)

    # Updating attributes.
    status_code = update_attributes(access_token, project_list, admin_host)

    if status_code == 200:
        print("Project List succesfully updated")
    else:
        print(status_code)
