import boto3
import json
import sys
import botocore

def _parse_template(client,template):
    with open(template) as template_fileobj:
        template_data = template_fileobj.read()
    client.validate_template(TemplateBody=template_data)
    return template_data

def create_sg_ingress(cf_client,template,params,parameters,port=None):
    try:
        sg_ingress_stack_name = parameters['Project'] + '-' + parameters['name'] + '-sg-ingress-' + str(port) + '-' + parameters['Environment']
        print('Creating {}'.format(sg_ingress_stack_name))
        response = cf_client.create_stack(
            StackName=sg_ingress_stack_name,
            TemplateBody=template,
            Parameters=params,
        )
        waiter = cf_client.get_waiter('stack_create_complete')
        print("...waiting for stack to be ready...")
        waiter.wait(
            StackName=sg_ingress_stack_name,
            WaiterConfig={
                'Delay': 5
            }
        )
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        print(error_message)

def create_stack(parameters,profile):

    session = boto3.Session(profile_name=profile)
    cf_client = session.client(service_name='cloudformation')
    sg_ingress_template_data = _parse_template(cf_client,'cloudformation/network/security-group-ingress.yaml')

    if isinstance(parameters['ports'], list):
        for port in parameters['ports']:
            sg_ingress_params=[
                {
                    'ParameterKey': 'Project',
                    'ParameterValue': parameters['Project']
                },
                {
                    'ParameterKey': 'Environment',
                    'ParameterValue': parameters['Environment']
                },
                {
                    'ParameterKey': 'CidrIp',
                    'ParameterValue': parameters['cidr']
                },
                {
                    'ParameterKey': 'SourceGroupId',
                    'ParameterValue': parameters['source_sg_name']
                },
                {
                    'ParameterKey': 'FromPort',
                    'ParameterValue': str(port)
                },
                {
                    'ParameterKey': 'ToPort',
                    'ParameterValue': str(port)
                },
                {
                    'ParameterKey': 'SGName',
                    'ParameterValue': parameters['name'].replace('-', '_')
                }
            ]
            create_sg_ingress(cf_client,sg_ingress_template_data,sg_ingress_params,parameters,port)
    else:
        sg_ingress_params=[
            {
                'ParameterKey': 'Project',
                'ParameterValue': parameters['Project']
            },
            {
                'ParameterKey': 'Environment',
                'ParameterValue': parameters['Environment']
            },
            {
                'ParameterKey': 'CidrIp',
                'ParameterValue': parameters['cidr']
            },
            {
                'ParameterKey': 'SourceGroupId',
                'ParameterValue': parameters['source_sg_name']
            },
            {
                'ParameterKey': 'FromPort',
                'ParameterValue': parameters['ports']
            },
            {
                'ParameterKey': 'ToPort',
                'ParameterValue': parameters['ports']
            },
            {
                'ParameterKey': 'SGName',
                'ParameterValue': parameters['name']
            }
        ]
        create_sg_ingress(cf_client,sg_ingress_template_data,sg_ingress_params,parameters,parameters['ports'])