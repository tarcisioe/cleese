from mpd import MPDClient, CommandError

from cleese.clients import connected
from cleese.command import command, Arg, fail, command_names
from cleese.utils import exception_converter, printer, fmtsong


client = MPDClient()


@exception_converter(CommandError,
                     'no files found in database matching: {args[1]}',
                     FileNotFoundError)
def add_to(client, song):
    client.add(song.rstrip('/'))


def current_song():
    with connected(client):
        return client.currentsong()


def fmt_current_song():
    try:
        return fmtsong(current_song())
    except KeyError:
        return ''


@command()
def add(what: Arg(type=str, help='What to add.')):
    try:
        with connected(client):
            add_to(client, what)
    except FileNotFoundError as e:
        fail(e)


@command()
def clear():
    with connected(client):
        client.clear()


@command(wrapper=printer)
def current():
    song = fmt_current_song()
    if song:
        return song
    else:
        fail('no song playing.')


@command(names=('next',))
def next_song():
    with connected(client):
        client.next()


@command()
def pause():
    with connected(client):
        client.pause()


@command()
def play():
    with connected(client):
        client.play()


@command()
def playpause():
    if state() == 'stop':
        play()
    else:
        pause()


@command()
def prev():
    with connected(client):
        client.previous()


@command()
def replace(what: Arg(type=str, help='What to replace.')):
    clear()
    add(what)
    play()


@command()
def setvolume(
        volume: Arg(type=int, help='A volume value between 0 and 100.')
        ):
    with connected(client):
        client.setvol(volume)


@command(wrapper=printer)
def state():
    with connected(client):
        return client.status()['state']


@command()
def stop():
    with connected(client):
        client.stop()


@command()
def update():
    with connected(client):
        client.update()


@command(names=('volume', 'vol'), wrapper=printer)
def volume():
    with connected(client):
        return int(client.status()['volume'])


@command()
def playlist():
    with connected(client):
        playlist = client.playlistinfo()
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
    with connected(client):
        files = client.search('file', '')
    files = [song['file'] for song in files if song['file'].startswith(prefix)]

    for completion in files:  # compute_autocomplete(prefix, files):
        print(completion)


@command()
def commands():
    for name in command_names():
        print(name)


@command(wrapper=printer)
def elapsed():
    with connected(client):
        current_time = int(float(client.status()['elapsed']))
    total_time = int(current_song()['time'])
    cm, cs = divmod(current_time, 60)
    tm, ts = divmod(total_time, 60)
    return '{}:{:02}/{}:{:02}'.format(cm, cs, tm, ts)


@command()
def goto(where: Arg(type=int,
                    help='Point in song where to seek to (seconds).')):
    with connected(client):
        client.seekcur(where)


@command()
def seek(step: Arg(type=int,
                   help='How many seconds to advance or backtrack (negative for backtracking')):
    with connected(client):
        client.seekcur('{:+}'.format(step))
