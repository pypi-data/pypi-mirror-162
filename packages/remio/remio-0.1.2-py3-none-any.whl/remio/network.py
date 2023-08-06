import netifaces


def get_ipv4() -> list:
    """Returns the IPv4 of the current device."""
    ipv4 = []
    for interface in netifaces.interfaces():
        ifaddress = netifaces.ifaddresses(interface).get(netifaces.AF_INET, [])
        if len(ifaddress) > 0:
            ip = ifaddress[0].get('addr', None)
            if ip is not None:
                if ip not in ['0.0.0.0', '127.0.0.1']:
                    ipv4.append(ip)
    return ipv4