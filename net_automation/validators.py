import ipaddress

def is_valid_address(addr):
    """
    Returns True if the address is a valid IP address.
        Works with IPv4 and IPv6.

    :param str addr: IP address.
    """
    try:
        ipaddress.ip_address(addr)
        return True
    except ValueError:
        return False

def is_valid_network(addr):
    """
    Returns True if the address is a valid IP address or subnet.
        Works with IPv4 and IPv6.

    :param str addr: address/subnet.
    """
    try:
        ipaddress.ip_network(addr)
        return True
    except ValueError:
        return False