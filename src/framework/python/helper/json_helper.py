
import json


def parse(json_path):
    """
    Fetches values from a JSON file.

    Args:
        json_path (str): Path to a JSON file.

    Returns:
        dict: Dict containing parsed values from the give JSON file.
    """

    with open(json_path, 'rb') as f:
        params = json.load(f)

    return params
