from mpd import CommandError

from cleese.clients import get_default_client
from cleese.command import command, Arg
from cleese.utils import exception_converter, printer, fmtsong


@exception_converter(CommandError,
                     'No files found in database matching: {args[1]}',
                     ValueError)
def add_to(client, song):
    client.add(song)


def get_volume(client):
    return int(client.status()['volume'])


@command()
def add(what: Arg(type=str, help='What to add.')):
    try:
        add_to(get_default_client(), what)
    except ValueError as e:
        print(e)


@command()
def clear():
    get_default_client().clear()


@command()
def current():
    print(fmtsong(get_default_client().currentsong()))


@command(names=['next'])
def next_song():
    get_default_client().next()


@command()
def pause():
    get_default_client().pause()


@command()
def play():
    get_default_client().play()


@command()
def playpause():
    if state() == 'stop':
        play()
    else:
        pause()


@command()
def prev():
    get_default_client().previous()


@command()
def replace(what: Arg(type=str, help='What to replace.')):
    clear()
    add(what)
    play()


@command()
def setvolume(
        volume: Arg(type=int, help='A volume value between 0 and 100.')
):
    get_default_client().setvol(volume)


@command(wrapper=printer)
def state():
    return get_default_client().status()['state']


@command()
def stop():
    get_default_client().stop()


@command()
def update():
    get_default_client().update()


@command(names=['volume', 'vol'])
def volume():
    print(get_volume(get_default_client()))


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
