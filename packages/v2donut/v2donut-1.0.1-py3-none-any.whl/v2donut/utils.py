from __future__ import annotations

import ipaddress


def isipaddress(address: str) -> bool:
    try:
        if "/" in address:
            address = address.split("/")[0]
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False
