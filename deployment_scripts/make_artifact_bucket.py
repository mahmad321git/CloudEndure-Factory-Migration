import boto3
import json
import sys
import botocore

with open('src\\framework\\config\\config.json', 'rb') as f:
    configs = json.load(f)
session = boto3.Session(profile_name=configs['AWS_MIGRATION_PROFILE'])
s3_client = session.client(service_name='s3')

def create_bucket(project,environment):

    try:
        print('Creating artifact S3 Bucket')
        response = s3_client.create_bucket(
            Bucket=project + '-cf-artifact-bucket-' + environment
        )
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        print(error_message)