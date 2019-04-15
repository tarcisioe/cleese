from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from ampdup import MPDClient, IdleMPDClient, ConnectionFailedError, Subsystem

from .config import read_config


@dataclass
class CleeseClient(MPDClient):
    idle_client: IdleMPDClient = field(default_factory=IdleMPDClient)

    async def connect(self, address: str, port: int):
        await super().connect(address, port)
        await self.idle_client.connect(address, port)

    async def disconnect(self):
        await super().disconnect()
        await self.idle_client.disconnect()

    async def run_command(self, command: str) -> List[str]:
        try:
            return await super().run_command(command)
        except ConnectionFailedError:
            await self._reconnect_no_idle()
            return await super().run_command(command)

    async def idle(
        self,
        *subsystems: Subsystem
    ) -> List[Subsystem]:
        try:
            return await self.idle_client.idle(*subsystems)
        except ConnectionFailedError:
            await self.idle_client.reconnect()
            return await self.idle_client.idle(*subsystems)

    async def _reconnect_no_idle(self):
        if self.details is None:
            raise ConnectionFailedError('Client was not previously connected.')

        await super().disconnect()
        await super().connect(*self.details)


def from_config(server_name: str):
    configs = read_config()
    server_config = configs['servers:' + server_name]

    server_type = server_config.get('type', 'network')

    if server_type == 'network':
        address = server_config['address']
        port = int(server_config['port'])

        return CleeseClient.make(address, port)

    socket = server_config['socket']

    return CleeseClient.make_unix(Path(socket))


def get_default_client():
    try:
        client = from_config('default')
    except (KeyError, FileNotFoundError):
        client = CleeseClient.make('localhost', 6600)

    return client
