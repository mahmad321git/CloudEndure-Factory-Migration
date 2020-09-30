import csv


def parse(csv_path):
    """
    Fetches values from a CSV file.

    Args:
        csv_path (str): Path to a CSV file.

    Returns:
        dict: Dict containing parsed values from the give CSV file.
    """

    with open(csv_path) as f:
        params = csv.DictReader(f.readlines())

    return list(params)
