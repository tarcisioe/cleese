from mpd import CommandError

from cleese.clients import get_default_client
from cleese.command import command, Arg, fail, command_names
from cleese.utils import exception_converter, printer, fmtsong


@exception_converter(CommandError,
                     'no files found in database matching: {args[1]}',
                     FileNotFoundError)
def add_to(client, song):
    client.add(song)


def current_song():
    return get_default_client().currentsong()


@command()
def add(what: Arg(type=str, help='What to add.')):
    try:
        add_to(get_default_client(), what.rstrip('/'))
    except FileNotFoundError as e:
        fail(e)


@command()
def clear():
    get_default_client().clear()


@command(wrapper=printer)
def current():
    try:
        return fmtsong(current_song())
    except:
        fail('no song playing.')


@command(names=('next',))
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


@command(names=('volume', 'vol'), wrapper=printer)
def volume():
    return int(get_default_client().status()['volume'])


@command()
def playlist():
    playlist = get_default_client().playlistinfo()
    current_idx = current_song()['pos']

    songs = [(fmtsong(s), '-> ' if (s['pos'] == current_idx) else '   ')
             for s in playlist]

    width = len(str(len(songs)))

    lines = ('{m} {i:#{w}}: {n}'.format(m=marker, i=i, n=name, w=width)
             for i, (name, marker) in enumerate(songs, 1))
    print('\n'.join(lines))


@command()
def volumestep(
        step: Arg(type=int,
                  help='Step in which to modify volume, positive or negative.')
        ):
    attempt = volume() + step
    new = min(max(0, attempt), 100)  # clip value between 0 and 100

    try:
        setvolume(new)
    except CommandError:
        fail('cannot set volume outside range 0-100.'
             ' attempt: {}'.format(attempt))


@command(names=('prefix-search',))
def prefix_search(prefix: Arg(type=str,
                              help='Prefix to search for.')):
    files = get_default_client().search('file', '')
    files = [song['file'] for song in files if song['file'].startswith(prefix)]

    for completion in files:  # compute_autocomplete(prefix, files):
        print(completion)


@command()
def commands():
    for name in command_names():
        print(name)


@command(wrapper=printer)
def elapsed():
    client = get_default_client()
    current_time = int(float(client.status()['elapsed']))
    total_time = int(current_song()['time'])
    cm, cs = divmod(current_time, 60)
    tm, ts = divmod(total_time, 60)
    return '{}:{:02}/{}:{:02}'.format(cm, cs, tm, ts)
