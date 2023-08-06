from __future__ import annotations

import ipaddress
import json

from pkg_resources import resource_stream


def isipaddress(address: str) -> bool:
    try:
        if "/" in address:
            address = address.split("/")[0]
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


def get_default_conf() -> dict:
    with resource_stream("v2donut", "v2donut.json") as s:
        return json.load(s)
