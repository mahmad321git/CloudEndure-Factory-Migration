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

    vpc_template_data = _parse_template(cf_client,'cloudformation/network/vpc.yaml')
    vpc_params=[
        {
            'ParameterKey': 'Project',
            'ParameterValue': parameters['Project']
        },
        {
            'ParameterKey': 'Environment',
            'ParameterValue': parameters['Environment']
        },
        {
            'ParameterKey': 'VpcName',
            'ParameterValue': parameters['VpcName']
        },
        {
            'ParameterKey': 'VpcSSMName',
            'ParameterValue': parameters['VpcName'].replace('-', '_')
        },
        {
            'ParameterKey': 'VpcCidrBlock',
            'ParameterValue': parameters['VpcCidrBlock']
        }
    ]
    try:
        stack_name = parameters['Project'] + '-' + getattr(profile, 'lower')().replace('_', '-')  + '-vpc-' + parameters['Environment']
        print('Creating {}'.format(stack_name))
        response = cf_client.create_stack(
            StackName=stack_name,
            TemplateBody=vpc_template_data,
            Parameters=vpc_params,
            Capabilities=[
                'CAPABILITY_NAMED_IAM'
            ]
        )
        waiter = cf_client.get_waiter('stack_create_complete')
        print("...waiting for stack to be ready...")
        waiter.wait(
            StackName=stack_name,
            WaiterConfig={
                'Delay': 5
            }
        )
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        print(error_message)
    
    subnet_template_data = _parse_template(cf_client,'cloudformation/network/subnet.yaml')
    i = 1
    for subnet in parameters['PublicSubnets']:
        subnet_params=[
            {
                'ParameterKey': 'Project',
                'ParameterValue': parameters['Project']
            },
            {
                'ParameterKey': 'Environment',
                'ParameterValue': parameters['Environment']
            },
            {
                'ParameterKey': 'VpcName',
                'ParameterValue': parameters['VpcName'].replace('-', '_')
            },
            {
                'ParameterKey': 'CidrBlock',
                'ParameterValue': subnet['CIDR']
            },
            {
                'ParameterKey': 'Counter',
                'ParameterValue': str(i)
            },
            {
                'ParameterKey': 'SubnetType',
                'ParameterValue': 'public'
            },
            {
                'ParameterKey': 'AZNo',
                'ParameterValue': str(i-1)
            }
        ]
        try:
            stack_name = parameters['Project'] + '-' + getattr(profile, 'lower')().replace('_', '-')  + '-vpc-public-subnet-' + str(i) + '-' + parameters['Environment']
            print('Creating {}'.format(stack_name))
            response = cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=subnet_template_data,
                Parameters=subnet_params,
                Capabilities=[
                    'CAPABILITY_NAMED_IAM'
                ]
            )
            waiter = cf_client.get_waiter('stack_create_complete')
            print("...waiting for stack to be ready...")
            waiter.wait(
                StackName=stack_name,
                WaiterConfig={
                    'Delay': 5
                }
            )
        except botocore.exceptions.ClientError as ex:
            error_message = ex.response['Error']['Message']
            print(error_message)
        i = i + 1
    
    i = 1
    for subnet in parameters['PrivateSubnets']:
        subnet_params=[
            {
                'ParameterKey': 'Project',
                'ParameterValue': parameters['Project']
            },
            {
                'ParameterKey': 'Environment',
                'ParameterValue': parameters['Environment']
            },
            {
                'ParameterKey': 'VpcName',
                'ParameterValue': parameters['VpcName'].replace('-', '_')
            },
            {
                'ParameterKey': 'CidrBlock',
                'ParameterValue': subnet['CIDR']
            },
            {
                'ParameterKey': 'Counter',
                'ParameterValue': str(i)
            },
            {
                'ParameterKey': 'SubnetType',
                'ParameterValue': 'private'
            },
            {
                'ParameterKey': 'AZNo',
                'ParameterValue': str(i-1)
            }
        ]
        try:
            stack_name = parameters['Project'] + '-' + getattr(profile, 'lower')().replace('_', '-')  + '-vpc-private-subnet-' + str(i) + '-' + parameters['Environment']
            print('Creating {}'.format(stack_name))
            response = cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=subnet_template_data,
                Parameters=subnet_params,
                Capabilities=[
                    'CAPABILITY_NAMED_IAM'
                ]
            )
            waiter = cf_client.get_waiter('stack_create_complete')
            print("...waiting for stack to be ready...")
            waiter.wait(
                StackName=stack_name,
                WaiterConfig={
                    'Delay': 5
                }
            )
        except botocore.exceptions.ClientError as ex:
            error_message = ex.response['Error']['Message']
            print(error_message)
        i = i + 1


    vpc_components_template = _parse_template(cf_client,'cloudformation/network/vpc-components.yaml')
    vpc_components_params=[
        {
            'ParameterKey': 'Project',
            'ParameterValue': parameters['Project']
        },
        {
            'ParameterKey': 'Environment',
            'ParameterValue': parameters['Environment']
        },
        {
            'ParameterKey': 'VpcName',
            'ParameterValue': parameters['VpcName'].replace('-', '_')
        }
    ]
    try:
        stack_name = parameters['Project'] + '-' + getattr(profile, 'lower')().replace('_', '-')  + '-vpc-components-' + parameters['Environment']
        print('Creating {}'.format(stack_name))
        response = cf_client.create_stack(
            StackName=stack_name,
            TemplateBody=vpc_components_template,
            Parameters=vpc_components_params,
            Capabilities=[
                'CAPABILITY_NAMED_IAM'
            ]
        )
        waiter = cf_client.get_waiter('stack_create_complete')
        print("...waiting for stack to be ready...")
        waiter.wait(
            StackName=stack_name,
            WaiterConfig={
                'Delay': 5
            }
        )
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        print(error_message)
    
    route_association_template_data = _parse_template(cf_client,'cloudformation/network/route-association.yaml')
    i = 1
    for route in parameters['PublicSubnets']:
        route_association_params=[
            {
                'ParameterKey': 'Project',
                'ParameterValue': parameters['Project']
            },
            {
                'ParameterKey': 'Environment',
                'ParameterValue': parameters['Environment']
            },
            {
                'ParameterKey': 'Counter',
                'ParameterValue': str(i)
            },
            {
                'ParameterKey': 'SubnetType',
                'ParameterValue': 'public'
            }
        ]
        try:
            stack_name = parameters['Project'] + '-' + getattr(profile, 'lower')().replace('_', '-')  + '-vpc-public-subnet-' + str(i) + '-route-association-' + parameters['Environment']
            print('Creating {}'.format(stack_name))
            response = cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=route_association_template_data,
                Parameters=route_association_params,
                Capabilities=[
                    'CAPABILITY_NAMED_IAM'
                ]
            )
            waiter = cf_client.get_waiter('stack_create_complete')
            print("...waiting for stack to be ready...")
            waiter.wait(
                StackName=stack_name,
                WaiterConfig={
                    'Delay': 5
                }
            )
        except botocore.exceptions.ClientError as ex:
            error_message = ex.response['Error']['Message']
            print(error_message)
        i = i + 1
    
    i = 1
    for route in parameters['PrivateSubnets']:
        route_association_params=[
            {
                'ParameterKey': 'Project',
                'ParameterValue': parameters['Project']
            },
            {
                'ParameterKey': 'Environment',
                'ParameterValue': parameters['Environment']
            },
            {
                'ParameterKey': 'Counter',
                'ParameterValue': str(i)
            },
            {
                'ParameterKey': 'SubnetType',
                'ParameterValue': 'private'
            }
        ]
        try:
            stack_name = parameters['Project'] + '-' + getattr(profile, 'lower')().replace('_', '-')  + '-vpc-private-subnet-' + str(i) + '-route-association-' + parameters['Environment']
            print('Creating {}'.format(stack_name))
            response = cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=route_association_template_data,
                Parameters=route_association_params,
                Capabilities=[
                    'CAPABILITY_NAMED_IAM'
                ]
            )
            waiter = cf_client.get_waiter('stack_create_complete')
            print("...waiting for stack to be ready...")
            waiter.wait(
                StackName=stack_name,
                WaiterConfig={
                    'Delay': 5
                }
            )
        except botocore.exceptions.ClientError as ex:
            error_message = ex.response['Error']['Message']
            print(error_message)
        i = i + 1