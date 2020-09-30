import boto3
import json
from botocore.exceptions import ClientError

#Creating a boto3 ssm object for ssm
with open('src\\framework\\config\\config.json', 'rb') as f:
    configs = json.load(f)
session = boto3.Session(profile_name=configs['AWS_MIGRATION_PROFILE'])
ssm = session.client(service_name='ssm')


def get_ssm_parameters(name):
    try:
        response = ssm.get_parameter(
            Name=name,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except ClientError as error:
        if error.response['Error']['Code'] == 'ParameterNotFound':
            return 'NULL'
        else:
            raise error