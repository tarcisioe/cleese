from contextlib import contextmanager

from ampdup import MPDClient

from cleese.config import read_config


def from_config(server_name):
    configs = read_config()
    address = configs['servers:' + server_name]['address']
    port = int(configs['servers:' + server_name]['port'])

    return MPDClient.make(address, port)


def get_default_client():
    try:
        client = from_config('default')
    except (KeyError, FileNotFoundError):
        client = MPDClient.make('localhost', 6600)

    return client
