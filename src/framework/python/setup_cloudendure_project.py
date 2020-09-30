import requests
import json
import sys
import os
import base64
import boto3
sys.path.insert(1, '.\\src\\framework\\python')
from helper import csv_helper
from helper import json_helper
from helper import parameter_parsing_helper
from helper import aws_parameter_store_helper

HOST = 'https://console.cloudendure.com'

def create_project(session, accountId,privateKey,publicKey, project_name,projecttype,creds_id,region_name):
    """ This function Creates a CloudEndure project
        and adds AWS credentials to the project"""

    endpoint = '/api/latest/{}'
    aws_cloud_id = None
    resp = session.get(HOST + endpoint.format('clouds'))
    for clouds_item in json.loads(resp.content)['items']:
        if clouds_item['name'] == 'AWS':
            aws_cloud_id = clouds_item['id']
            break
    proj_data = {
                'name': project_name, 
                'type': projecttype, 
                'targetCloudId': aws_cloud_id
            }
    r = session.post(HOST + endpoint.format('projects'), data = json.dumps(proj_data))
    if r.status_code == 201:
        print("Project created succesfully")
    proj_resp = json.loads(r.content)
    project_id = proj_resp['id']
    payload = {
                "cloudId": aws_cloud_id,
                "accountIdentifier": accountId,
                "privateKey": privateKey,
                "publicKey": publicKey
            }
    resp = session.post(url=HOST+endpoint.format('cloudCredentials'), data=json.dumps(payload))
    cloud_credentials_id = json.loads(resp.content)['id']
    data = {'cloudCredentialsIDs': [cloud_credentials_id]}
    resp = session.patch(url=HOST+endpoint.format('projects/{}'.format(project_id)), data=json.dumps(data))
    if resp.status_code == 200:
        print("Cloud Credentials configured")		

    resp = session.get(url=HOST+endpoint.format('cloudCredentials/{}/regions'.format(cloud_credentials_id)))
    resp_target = json.loads(resp.content)['items']
    for regions in resp_target:
        if regions['name'] == region_name:
            target_region = regions['id']
    resp = session.get(url=HOST+endpoint.format('cloudCredentials/{}/regions'.format(creds_id)))
    
    resp_source = json.loads(resp.content)['items'][0]
    return project_id,target_region,resp_source

def replication_settings(session,project_id,target_region,source,repl_subnet,repl_sg):
    """ This function updates the Replication Configurations
        of the project it receives in the parameter"""

    endpoint = '/api/latest/{}'
    data = {
    "region":target_region,
    "volumeEncryptionKey":"",
    "subnetId":repl_subnet,
    "zone":"",
    "usePrivateIp":False,
    "disablePublicIp":False,
    "useDedicatedServer":False,
    "replicationServerType":"",
    "replicationTags":[],
    "replicatorSecurityGroupIDs":[repl_sg],
    "volumeEncryptionAllowed":False,
    "storageLocationId":"",
    "useLowCostDisks":False,
    "converterType":"",
    "proxyUrl":"",
    "bandwidthThrottling":0
}
    r = session.post(HOST + endpoint.format('projects/{}/replicationConfigurations'.format(project_id)), data = json.dumps(data))
    a =json.loads(r.content)
    replicationConfiguration = a['id']
    payload = {
        "id":project_id,
        "replicationConfiguration":replicationConfiguration,
        "sourceRegion":source['id']
        }
    resp = session.patch(url=HOST+endpoint.format('projects/{}'.format(project_id)), data=json.dumps(payload))
    if resp.status_code == 200:
        print("Replication settings succesfully updated")

def login(user_api_token):
    """ This function Logs In to CloudEndure 
        and returns the login session"""

    session = requests.Session()
    session.headers.update({'Content-type': 'application/json', 'Accept': 'text/plain'})
    endpoint = '/api/latest/{}'
    login_data = {'userApiToken': user_api_token}
    r = session.post(HOST + endpoint.format('login'), data = json.dumps(login_data))
    if r.status_code == 200:
        print("Logged in to CloudEndure")
    elif r.status_code != 200 and r.status_code != 307:
	    print("Bad login credentials")
	    sys.exit(1)
    session.headers['X-XSRF-TOKEN'] = session.cookies.get('XSRF-TOKEN')
    return session

def get_aws_creds(aws_profile):
    """ This method returns AWS credentials """
    session = boto3.Session(profile_name=aws_profile)
    credentials =session.get_credentials()
    aws_creds = credentials.get_frozen_credentials()
    access_key = aws_creds.access_key
    secret_access_key = aws_creds.secret_key
    message_bytes = secret_access_key.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    secret_key = base64_bytes.decode('ascii')
    aws_accountid =session.client(service_name='sts').get_caller_identity().get('Account')
    return access_key,secret_key,aws_accountid

def main():
    path = "src/framework/config/config.json"
    config = json_helper.parse(path)
    aws_profile = config['AWS_DR_PROFILE']
    project = config['PROJECT']
    environment = config['ENV']
    region = config['CE_TARGETREGION']
    access_key,secret_key,aws_accountid = get_aws_creds(aws_profile)
    project_name = config['CE_PROJECTNAME']
    projecttype = config['CE_PROJECTTYPE']
    creds_id = config['CE_CREDSID_OTHERINFRA']
    project_env = '/'.join(['', project, environment])
    api_token_path = '/'.join([project_env, 'cloudendure', 'api_token'])
    user_api_token = parameter_parsing_helper \
        .fetch_parameter(api_token_path,path)

    subnet_key = '/'.join([project_env, 'network', 'public_subnet_1'])
    sg_key = '/'.join([project_env, 'network', 'replication_server_sg'])
    # Fetching subnet value from SSM
    repl_subnet = parameter_parsing_helper.fetch_parameter(subnet_key,path,aws_profile)
    # Fetching Security Group value from SSM
    repl_sg = parameter_parsing_helper.fetch_parameter(sg_key,path,aws_profile)
    # Getting Login session
    session  = login(user_api_token)
    # Creating Project with AWS credentials configured
    project_id,target_region,resp_source = create_project(session,aws_accountid,secret_key,access_key,project_name,projecttype,creds_id,region)
    # Updating Replication settings
    replication_settings(session,project_id,target_region,resp_source,repl_subnet,repl_sg)

if __name__ == "__main__":
    main()
    