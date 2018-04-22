from carl import command, Arg, STOP, REQUIRED
from ampdup import ConnectionFailedError, IdleMPDClient

from .utils import fail
from .clients import get_default_client, from_config, MPDClient


@command
async def main(
        address: 'Address to connect to.' = None,
        port: Arg(type=int, help='Port to connect to.')=None,
        server: 'Server to connect to (specified in the config file).' = None,
        subcommand=(STOP | REQUIRED)
):
    '''An MPD client written in Python.'''

    cmd, args, name = subcommand

    factory = MPDClient if name != 'idle' else IdleMPDClient

    if server is not None:
        get_client = from_config(server, factory)
    elif address is None and port is None:
        get_client = get_default_client(factory)
    else:
        address = 'localhost' if address is None else address
        port = 6600 if port is None else port
        get_client = factory.make(address, port)

    try:
        async with get_client as client:
            await cmd.resume_async(args, client=client)
    except ConnectionFailedError:
        fail("Unable to connect to server.")
