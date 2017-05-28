from carl import command, Arg, STOP, REQUIRED
from mpd import ConnectionError

from .utils import fail
from cleese.clients import get_default_client, from_config, Client


@command
def main(address: 'Address to connect to.'=None,
         port: Arg(type=int, help='Port to connect to.')=None,
         server: 'Server to connect to (specified in the config file).'=None,
         subcommand=(STOP | REQUIRED)):
    '''An MPD client written in Python.'''

    if server is not None:
        client = from_config(server)
    elif address is None and port is None:
        client = get_default_client()
    else:
        address = 'localhost' if address is None else address
        port = 6600 if port is None else port
        client = Client(address, port)

    cmd, args = subcommand
    try:
        cmd.resume(args, client=client)
    except ConnectionError:
        fail("Unable to connect to server.")
