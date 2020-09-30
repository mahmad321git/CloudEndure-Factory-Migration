import boto3
import json
import sys
import botocore
from random import randint

with open('src\\framework\\config\\config.json', 'rb') as f:
    configs = json.load(f)
session = boto3.Session(profile_name=configs['AWS_MIGRATION_PROFILE'])
cf_client = session.client(service_name='cloudformation')

def _parse_template(template):
    with open(template) as template_fileobj:
        template_data = template_fileobj.read()
    cf_client.validate_template(TemplateBody=template_data)
    return template_data

def _stack_exists(stack_name):
    stacks = cf_client.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            return True
    return False

def create_stack(parameters,template):
    
    template_data = _parse_template(template)
    params=[
        {
            'ParameterKey': 'Project',
            'ParameterValue': parameters['Project']
        },
        {
            'ParameterKey': 'Environment',
            'ParameterValue': parameters['Environment']
        },
        {
            'ParameterKey': 'CognitoUserEmail',
            'ParameterValue': parameters['CognitoUserEmail']
        },
        {
            'ParameterKey': 'CloudEndureUsername',
            'ParameterValue': parameters['CloudEndureUsername']
        },
        {
            'ParameterKey': 'CloudEndureURL',
            'ParameterValue': parameters['CloudEndureURL']
        },
        {
            'ParameterKey': 'VpcName',
            'ParameterValue': parameters['VpcName']
        }
    ]
    try:
        stack_name = parameters['Project'] + '-main-stack-' + parameters['Environment']
        change_set_name = stack_name + '-change-set-' + str(randint(100,999))
        if _stack_exists(stack_name):
            print('Updating {}'.format(stack_name))
            response = cf_client.create_change_set(
                StackName=stack_name,
                TemplateBody=template_data,
                Parameters=params,
                Capabilities=[
                    'CAPABILITY_NAMED_IAM'
                ],
                ChangeSetName=change_set_name
            )
            waiter = cf_client.get_waiter('change_set_create_complete')
            print("...waiting for change set to be applied...")
            waiter.wait(
                ChangeSetName=change_set_name,
                StackName=stack_name,
                WaiterConfig={
                    'Delay': 10
                }
            )
            print('Change Set Applied')
            response = cf_client.execute_change_set(
                ChangeSetName=change_set_name,
                StackName=stack_name
            )
            waiter = cf_client.get_waiter('stack_update_complete')
            print("...waiting for stack updation...")
            waiter.wait(StackName=stack_name)
            print('Stack Updation Complete')
        else:
            print('Creating {}'.format(stack_name))
            response = cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_data,
                Parameters=params,
                Capabilities=[
                    'CAPABILITY_NAMED_IAM'
                ]
            )
            waiter = cf_client.get_waiter('stack_create_complete')
            print("...waiting for stack to be ready...")
            waiter.wait(StackName=stack_name)
            print('Stack Created')
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        print(error_message)