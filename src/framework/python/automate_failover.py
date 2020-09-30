import sys
import json
import requests
import argparse
from helper import json_helper
from helper import csv_helper
from helper import parameter_parsing_helper

def get_access_token(username, password, login_host):
    
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


def failover(access_token, tools_host,user_api_token, project_name, wave_id, launch_type, relaunch):
    
    url = tools_host + '/prod/cloudendure'
    access_token = access_token.strip('\"')
    headers = {'Authorization': access_token}
    body = {
        "userapitoken": user_api_token,
        "projectname": project_name,
        "waveid": wave_id,
        "launchtype": launch_type,
        "relaunch": relaunch
    }
    r = requests.post(url=url, headers=headers, data = json.dumps(body))
    print(r.text)



def main(arguments):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--WaveId', required=True)
    parser.add_argument('--LaunchType', required=True)
    args = parser.parse_args(arguments)
    # Reading configs.
    config_path = 'config\\config.json'
    config = json_helper.parse(config_path)
    project_env = '/'.join(['', config['PROJECT'], config['ENV']])
    project_name = config['CE_PROJECTNAME']
    login_endpoint = '/'.join([project_env, 'endpoint', 'login'])
    tools_endpoint = '/'.join([project_env, 'endpoint', 'tools'])
    api_token_path = '/'.join([project_env, 'cloudendure', 'api_token'])
    factory_username = '/'.join([project_env, 'factory', 'username'])
    factory_password = '/'.join([project_env, 'factory', 'password'])
    user_api_token = parameter_parsing_helper \
        .fetch_parameter(api_token_path)
    login_host = parameter_parsing_helper \
        .fetch_parameter(login_endpoint)
    tools_host = parameter_parsing_helper \
        .fetch_parameter(tools_endpoint)
    username = parameter_parsing_helper \
        .fetch_parameter(factory_username)
    password = parameter_parsing_helper \
        .fetch_parameter(factory_password)
    
    relaunch = False
    relaunch = config['RELAUNCH']
    if isinstance(relaunch, str):
        if 'true' in relaunch.lower():
            relaunch = True
        else:
            relaunch = False
            
    access_token = get_access_token(username, password, login_host)
    # FAILOVER
    failover(access_token, tools_host, user_api_token, project_name, args.WaveId, args.LaunchType, relaunch)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))