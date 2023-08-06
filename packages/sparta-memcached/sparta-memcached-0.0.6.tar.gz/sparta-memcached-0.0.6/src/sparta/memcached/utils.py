import socket
import typing
import re

# Solution copied from this lab https://www.cloudskillsboost.google/focuses/615?parent=catalog


def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def _resolve_ips(hostname: str) -> typing.List[str]:
    assert isinstance(hostname, str)
    if not is_valid_hostname(hostname):
        raise ValueError(f"Invalid hostname 'f{hostname}'")
    _, _, ips = socket.gethostbyname_ex(hostname)
    return [ip for ip in ips]


def resolve_ips(
    hostnames: typing.Union[str, typing.List[str]]
) -> typing.List[str]:
    if isinstance(hostnames, str):
        return _resolve_ips(hostnames)
    return [x for hostname in hostnames for x in _resolve_ips(hostname)]
