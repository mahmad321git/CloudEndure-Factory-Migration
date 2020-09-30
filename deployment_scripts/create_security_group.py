import boto3
import json
import sys
import botocore

def _parse_template(client,template):
    with open(template) as template_fileobj:
        template_data = template_fileobj.read()
    client.validate_template(TemplateBody=template_data)
    return template_data

def create_stack(parameters,profile):

    session = boto3.Session(profile_name=profile)
    cf_client = session.client(service_name='cloudformation')
    sg_template_data = _parse_template(cf_client,'cloudformation/network/security-group.yaml')
    sg_params=[
        {
            'ParameterKey': 'Project',
            'ParameterValue': parameters['Project']
        },
        {
            'ParameterKey': 'Environment',
            'ParameterValue': parameters['Environment']
        },
        {
            'ParameterKey': 'SGName',
            'ParameterValue': parameters['name']
        },
        {
            'ParameterKey': 'SGNameSSM',
            'ParameterValue': parameters['name'].replace('-', '_')
        },
        {
            'ParameterKey': 'SGDescription',
            'ParameterValue': parameters['description']
        },
        {
            'ParameterKey': 'VpcName',
            'ParameterValue': parameters['vpc_name'].replace('-', '_')
        }
    ]
    try:
        sg_stack_name = parameters['Project'] + '-' + parameters['name'] + '-sg-' + parameters['Environment']
        print('Creating {}'.format(sg_stack_name))
        response = cf_client.create_stack(
            StackName=sg_stack_name,
            TemplateBody=sg_template_data,
            Parameters=sg_params,
        )
        waiter = cf_client.get_waiter('stack_create_complete')
        print("...waiting for stack to be ready...")
        waiter.wait(
            StackName=sg_stack_name,
            WaiterConfig={
                'Delay': 5
            }
        )
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        print(error_message)