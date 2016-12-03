from collections import defaultdict
from contextlib import contextmanager
from functools import lru_cache
from threading import Lock

from mpd import MPDClient

from cleese.config import read_config


class Client(MPDClient):
    def __init__(self, address, port):
        super().__init__()
        self.address = address
        self.port = port

    def connect_default(self):
        self.connect(self.address, self.port)


@lru_cache()
def from_config(server_name):
    configs = read_config()
    address = configs['servers:' + server_name]['address']
    port = int(configs['servers:' + server_name]['port'])

    return address, port


def get_default_client():
    try:
        address, port = from_config('default')
    except KeyError:
        address, port = ('localhost', 6600)

    return Client(address, port)


locks = defaultdict(Lock)


@contextmanager
def connected(client):
    with locks[id(client)]:
        try:
            client.connect_default()
            yield
        finally:
            client.close()
            client.disconnect()
