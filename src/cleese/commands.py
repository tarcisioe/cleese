from mpd import CommandError

from cleese.clients import get_default_client
from cleese.command import command
from cleese.utils import exception_converter, printer, fmtsong


def empty_args(args):
    return []


@command()
def play(_):
    get_default_client().play()


@command()
def pause(_):
    get_default_client().pause()


@command()
def stop(_):
    get_default_client().stop()


@command(names=['next'])
def next_song(_):
    get_default_client().next()


@command()
def prev(_):
    get_default_client().previous()


@command()
def clear(_):
    get_default_client().clear()


@command([('volume', int)])
def setvolume(args):
    get_default_client().setvol(args.volume)


@command(wrapper=printer)
def state(_):
    return get_default_client().status()['state']


def get_volume(client):
    return int(client.status()['volume'])


@command(names=['volume', 'vol'])
def volume(_):
    print(get_volume(get_default_client()))


@command()
def playpause(_):
    client = get_default_client()
    if state(client) == 'stop':
        play(client)
    else:
        pause(client)


@command()
def current(_):
    print(fmtsong(get_default_client().currentsong()))


@exception_converter(CommandError,
                     'No files found in database matching: {args[1]}',
                     ValueError)
def add_to(client, song):
    client.add(song)


@command([('what', str)])
def add(args):
    add_to(get_default_client(), args.what)


@command([('what', str)])
def replace(args):
    client = get_default_client()
    client.clear()
    add_to(client, args.what)
    client.play()


@command([('step', int)])
def volumestep(args):
    client = get_default_client()
    try:
        client.setvol(get_volume(client) + args.step)
    except CommandError:
        pass
