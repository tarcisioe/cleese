from mpd import CommandError

from cleese.clients import get_default_client
from cleese.command import command, Arg
from cleese.utils import exception_converter, printer, fmtsong


def empty_args(args):
    return []


@command()
def play():
    get_default_client().play()


@command()
def pause():
    get_default_client().pause()


@command()
def stop():
    get_default_client().stop()


@command(names=['next'])
def next_song():
    get_default_client().next()


@command()
def prev():
    get_default_client().previous()


@command()
def clear(_):
    get_default_client().clear()


@command()
def setvolume(
        volume: Arg(type=int, help='A volume value between 0 and 100.')
):
    get_default_client().setvol(volume)


@command(wrapper=printer)
def state():
    return get_default_client().status()['state']


def get_volume(client):
    return int(client.status()['volume'])


@command(names=['volume', 'vol'])
def volume():
    print(get_volume(get_default_client()))


@command()
def playpause():
    client = get_default_client()
    if state(client) == 'stop':
        play(client)
    else:
        pause(client)


@command()
def current():
    print(fmtsong(get_default_client().currentsong()))


@exception_converter(CommandError,
                     'No files found in database matching: {args[1]}',
                     ValueError)
def add_to(client, song):
    client.add(song)


@command()
def replace(what: Arg(type=str, help='What to replace.')):
    client = get_default_client()
    client.clear()
    add_to(client, what)
    client.play()


@command()
def add(what: Arg(type=str, help='What to add.')):
    add_to(get_default_client(), what)


@command()
def volumestep(
        step: Arg(type=int,
                  help='Step in which to modify volume, positive or negative.')
):
    client = get_default_client()
    try:
        client.setvol(get_volume(client) + step)
    except CommandError:
        pass

@command()
def update():
    get_default_client().update()
