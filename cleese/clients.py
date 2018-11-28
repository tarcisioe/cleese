from ampdup import MPDClient

from .config import read_config


def from_config(server_name: str, factory=MPDClient):
    configs = read_config()
    address = configs['servers:' + server_name]['address']
    port = int(configs['servers:' + server_name]['port'])

    return factory.make(address, port)


def get_default_client(factory=MPDClient):
    try:
        client = from_config('default')
    except (KeyError, FileNotFoundError):
        client = factory.make('localhost', 6600)

    return client
