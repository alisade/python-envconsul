__version__ = '0.0.1'

__all__ = [
    '__version__',
]

import collections

from envconsul import utils

from consulate import Consulate
import requests


LIST_DELIM = ','
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8500


class ConsulConnectionFailed(Exception):
    pass


class EnvConsul(collections.Mapping):
    """Collect Consul key/value data into a dict"""

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, service_name=None, *args, **kwargs):
        self._d = dict(*args, **kwargs)

        self.consul = False
        try:
            self.consul = Consulate(host, port)
            self.consul.kv.items() # Force connection, to test host/port
        except Exception as e:
            raise ConsulConnectionFailed(e)

        if service_name and self.consul:
            self._d.update(utils.get_settings_for(self.consul, service_name))

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def get_bool(self, key, default=None):
        return bool(self._d.get(key, default))

    def get_str(self, key, default=None):
        return str(self._d.get(key, default))

    def get_tuple(self, key, default=[]):
        return tuple(self.get_list(key, default))

    def get_list(self, key, default=[]):
        data = self._d.get(key, default)
        if data and LIST_DELIM in data:
            data = data.split(LIST_DELIM)
            data = [str(d.strip()) for d in data]
        return data