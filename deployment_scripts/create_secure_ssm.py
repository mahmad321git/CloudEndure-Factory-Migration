import boto3
import json
import sys
import botocore

with open('src\\framework\\config\\config.json', 'rb') as f:
    configs = json.load(f)
session = boto3.Session(profile_name=configs['AWS_MIGRATION_PROFILE'])
ssm_client = session.client(service_name='ssm')

def get_ssm_parameters(name):
    try:
        response = ssm_client.get_parameter(
            Name=name,
            WithDecryption=False
        )
        if response['Parameter']['Value'] is not None:
            return True
    except Exception as ex:
        return False

def create_ssm(project,environment,service,param_name,param_value):

    try:
        name = '/' + project + '/' + environment + '/' + service + '/' + param_name
        if not get_ssm_parameters(name):
            response = ssm_client.put_parameter(
                Name=name,
                Value=param_value,
                Type='SecureString',
                Tier='Standard'
            )
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        print(error_message)