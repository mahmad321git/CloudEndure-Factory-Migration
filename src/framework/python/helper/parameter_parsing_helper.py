import sys
sys.path.insert(1, '.\\python')
sys.path.insert(1, '.\\src\\framework\\python')
from helper import aws_parameter_store_helper  # noqa


def _get_parameter(key: str, config_path='config\\config.json',profile=None) -> str:
    return aws_parameter_store_helper.get_parameter(key, config_path,profile)


def fetch_parameter(parameter_name: str, config_path='config\\config.json',profile=None):
    """
        API Endpoint parameter workflow.

        Args:
            parameter_name (str): str containg name of the parameter to fetch
            value from.

        Returns:
            str: parameter value for API Endpoint.
        """
    return _get_parameter(parameter_name, config_path,profile)
