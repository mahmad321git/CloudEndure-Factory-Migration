"""
TODO add docstring
"""

from helper import aws_ec2_helper


def get_replication_server_ip():
    """
    Fetches Replication Server IP address.

    Returns:
        str: Replication Server Public IP Address.
    """
    filters = {
        'instance-state-name': ['running'],
        'tags': {
            'Name': ['CloudEndure Replication Server con17'],
            'management': ['con17'],
            'CloudEndure_Name': ['CloudEndure Replication Server con17'],
            'CloudEndure_Replication_Service': ['true']
        }
    }
    instances = aws_ec2_helper.get_instances(filters=filters)

    if instances:
        cloudendure_replication_server_ip = instances[0]['NetworkInterfaces'][
            0]['Association']['PublicIp']

        return cloudendure_replication_server_ip
