import os
import random
import ipaddress
import validators as val
from pydantic import validate_arguments, Field

"""
To obtain available ports
"""


def network_ip() -> str:
    command = "hostname -I"
    retvalue = os.popen(command).readlines()
    return str(retvalue[0][0:-1]).strip()

def isIp(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except Exception as _:
        return False

def isURL(value: str) -> bool:
    return val.url(value)



@validate_arguments
def validURL(value:str) -> bool:
    http_value: str = f"http://{value}"
    https_value: str = f"https://{value}"

    if isIp(value):
        return True
    elif isURL(value):
        return True
    elif isURL(http_value):
        return True
    elif isURL(https_value):
        return True
    else:
        return False

@validate_arguments
def validPORT(value:int) -> bool:
    if 0 <= value <= 65535:
        return True
    else:
        return False
