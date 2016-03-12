from contextlib import contextmanager
from functools import lru_cache

from cleese.config import read_config


@lru_cache()
def from_config(server_name):
    configs = read_config()
    address = configs['servers:' + server_name]['address']
    port = int(configs['servers:' + server_name]['port'])

    return address, port


def get_default_server():
    try:
        default = from_config('default')
    except KeyError:
        default = ('localhost', 6600)

    return default


@contextmanager
def connected(client, where=get_default_server()):
    address, port = where
    try:
        client.connect(address, port)
        yield
    finally:
        client.close()
        client.disconnect()
