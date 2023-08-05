"""Beacon configuration"""

import os
from typing import Tuple


def get_beacon_address() -> Tuple[str, int]:
    """Beacon address in the current environment. For example `('foobar', 25000)`."""
    beacon_host = os.environ.get("BEACON_HOST")
    if beacon_host is None:
        raise RuntimeError("BEACON_HOST is not specified")
    host, port = beacon_host.split(":")
    return host, int(port)
