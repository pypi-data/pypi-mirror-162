"""Get files from Beacon."""

import json
import yaml
from typing import Any
from urllib.parse import urlparse

from ._base import BeaconClient


def read_config(url: str) -> Any:
    """
    Read configuration from a url.

    In case of a Beacon url with missing host and port, the Beacon
    server will be found from environment variable `BEACON_HOST`.

    Arguments:
        url: This can be a local yaml file (for example `/path/to/file.yaml`, `file:///path/to/file.yaml`)
             or a Beacon URL (for example `beacon:///counters/p201.yml`, `beacon://id00:25000/counters/p201.yml`).
    Returns:
        A Python dict/list structure
    """
    url = urlparse(url)
    if url.scheme == "beacon":
        if url.netloc:
            host, port = url.netloc.split(":")
            port = int(port)
        else:
            host = None
            port = None
        beacon = BeaconFiles(host=host, port=port)
        try:
            # Bliss < 1.11: Beacon cannot handle leading slashes
            file_path = url.path
            while file_path.startswith("/"):
                file_path = file_path[1:]

            config = beacon.get_config_file(file_path)
            return yaml.safe_load(config)
        finally:
            beacon.close()
    elif url.scheme in ("file", ""):
        with open(url.path, "r") as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(f"Configuration URL scheme '{url.scheme}' is not supported")


class BeaconFiles(BeaconClient):
    """Provides the API to read files managed by Beacon."""

    CONFIG_GET_FILE = 50
    CONFIG_GET_FILE_FAILED = 51
    CONFIG_GET_FILE_OK = 52

    CONFIG_GET_DB_TREE = 86
    CONFIG_GET_DB_TREE_FAILED = 87
    CONFIG_GET_DB_TREE_OK = 88

    def get_config_file(self, file_path: str) -> str:
        """Returns the content of a file from the Beacon configuration."""
        return self.get_raw_file(file_path).decode()

    def get_raw_file(self, file_path: str) -> bytes:
        """Returns the binary content of a file from the Beacon configuration."""
        with self._lock:
            response = self._request(self.CONFIG_GET_FILE, file_path)
            response_type, data = response.read()
            if response_type == self.CONFIG_GET_FILE_OK:
                return data
            elif response_type == self.CONFIG_GET_FILE_FAILED:
                raise RuntimeError(data.decode())
            raise RuntimeError(f"Unexpected Beacon response type {response_type}")

    def get_config_db_tree(self, base_path: str = "") -> dict:
        """Returns the file tree from a base path from the Beacon configuration.

        Return: A nested dictionary structure, where a file is a mapping
                `filename: None`, an a directory is mapping of a dirname and a
                nested dictionary.
        """
        with self._lock:
            response = self._request(self.CONFIG_GET_DB_TREE, base_path)
            response_type, data = response.read()
            if response_type == self.CONFIG_GET_DB_TREE_OK:
                return json.loads(data)
            elif response_type == self.CONFIG_GET_DB_TREE_FAILED:
                raise RuntimeError(data.decode())
            raise RuntimeError(f"Unexpected Beacon response type {response_type}")
