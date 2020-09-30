import boto3
from helper import json_helper


def _get_boto3_client(profile, service='ssm'):
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


def get_parameter(parameter_name, config_path='config\\config.json',
                  profile=None):
    """
    Fetch and return parameters from the parameters store

    Args:
        parameter_name (str): Name of the parameter to be fetched from
        parameter store.

    Returns:
        str: Value of the fetched parameter.
    """
    if profile:
        ssm = _get_boto3_client(profile)
    else:
        configs = json_helper.parse(config_path)
        ssm = _get_boto3_client(configs['AWS_MIGRATION_PROFILE'])

    params = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return params['Parameter']['Value']
