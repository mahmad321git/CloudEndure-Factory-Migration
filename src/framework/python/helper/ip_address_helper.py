"""
The purpose of this module to simplify IP Address operations.
"""

import ipaddress


def is_valid_ip_address(ip_address: str) -> bool:
    """
    Checks if given IP Address is valid or not.

    Args:
        ip_address (str): IP Address (IPv4 or IPv6)

    Returns:
        bool: Either valid IP Address or not.
    """
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False
