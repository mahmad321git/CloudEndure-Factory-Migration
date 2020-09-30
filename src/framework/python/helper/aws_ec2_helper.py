import boto3
from helper import json_helper


def _get_boto3_client(profile, service='ec2'):
    """
    Creates a client object for the provided service name.

    Args:
        service (str): Name of an AWS service.

    Returns:
        botocore.client: Client of the service.
    """

    session = boto3.Session(profile_name=profile)
    client = session.client(service_name=service)
    return client


def _serialize_filter(filters):
    serialized_filters = []
    for key in filters.keys():
        if key.lower() == 'tags':
            tags = filters[key]
            for tag in tags.keys():
                serialized_filters.append({
                    'Name': f'tag:{tag}',
                    'Values': tags[tag]
                })
        else:
            serialized_filters.append({
                'Name': key,
                'Values': filters[key]
            })

    return serialized_filters


def get_instances(filters, profile=None, config_path='config\\config.json'):
    """
    Fetch and return parameters from the parameters store

    Args:
        filters (dict): Filters and their values (values must be in a list).
                        For tags, create a dict against 'tags' key with the
                        same format.

    Returns:
        str: EC2 Instance.
    """

    if profile:
        ec2 = _get_boto3_client(profile=profile)
    else:
        configs = json_helper.parse(config_path)
        ec2 = _get_boto3_client(profile=configs['AWS_DR_PROFILE'])

    serialized_filters = _serialize_filter(filters)
    instances = ec2.describe_instances(Filters=serialized_filters)

    if instances['Reservations']:
        if 'Instances' in instances['Reservations'][0]:
            return instances['Reservations'][0]['Instances']
