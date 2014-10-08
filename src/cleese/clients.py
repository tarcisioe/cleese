from functools import lru_cache

from mpd import MPDClient

from cleese.config import read_config


_default_client = None


@lru_cache()
def get_client(server_name):
    configs = read_config()
    address = configs['servers:' + server_name]['address']
    port = int(configs['servers:' + server_name]['port'])

    client = MPDClient()
    client.connect(address, port)

    return client


def get_default_client():
    if _default_client is not None:
        return _default_client

    try:
        default = get_client('default')
    except KeyError:
        default = standard_mpd_client()

    return default


def standard_mpd_client():
    client = MPDClient()
    client.connect('localhost', 6600)

    return client
