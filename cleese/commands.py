from mpd import MPDClient, CommandError

from cleese.clients import connected
from cleese.command import command, Arg, fail, command_names
from cleese.utils import (exception_converter, fmt_minutes, fmtsong,
                          line_list_printer, printer)


client = MPDClient()


@exception_converter(CommandError,
                     'no files found in database matching: {args[1]}',
                     FileNotFoundError)
def _add(what):
    '''Add a directory or a file from the library to a client's queue.

    Args:
        c (MPDClient): The client on which to add songs.
        what (str): The directory or file to add to the queue.
    '''
    client.add(what.rstrip('/'))


def current_song():
    '''Get the current song from the default server.'''
    with connected(client):
        return client.currentsong()


def fmt_current_song():
    '''Get the current song, properly formatted.'''
    try:
        return fmtsong(current_song())
    except KeyError:
        return ''


@command
def add(what: 'What to add.'):
    '''Add a directory or file from library to the playing queue.'''
    try:
        with connected(client):
            _add(what.rstrip('/'))
    except FileNotFoundError as e:
        fail(e)


@command
def clear():
    '''Clear the playing queue.'''
    with connected(client):
        client.clear()


@command(wrapper=line_list_printer)
def commands():
    '''Print all available commands.'''
    return command_names()


@command(wrapper=printer)
def current():
    '''Get the current song.'''
    song = fmt_current_song()
    if song:
        return song
    else:
        fail('no song playing.')


@command(wrapper=printer)
def elapsed(seconds: Arg(help='Show in seconds.', action='store_true')=False):
    '''Get the elapsed time and total time, formatted.'''
    current_time, total = seconds_elapsed()
    if not seconds:
        current_time = fmt_minutes(current_time)
        total = fmt_minutes(total)
    return '{}/{}'.format(current_time, total)


@command
def goto(where: Arg(type=int,
                    help='Point in song where to seek to (seconds).')):
    '''Go to a specific point in the current song.'''
    with connected(client):
        client.seekcur(where)


@command(wrapper=line_list_printer)
def idle():
    '''Waits for the server to signal any events.'''
    idle_client = MPDClient()
    with connected(idle_client):
        return idle_client.idle()


@command(names=('next',))
def next_song():
    '''Go to next song in queue.'''
    with connected(client):
        client.next()


@command
def pause():
    '''Pause playback.'''
    with connected(client):
        client.pause()


@command
def play():
    '''Play playback.'''
    with connected(client):
        client.play()


@command
def playlist():
    '''Print the current playlist.'''
    with connected(client):
        songs = client.playlistinfo()
    current_idx = current_song()['pos']

    songs = [(fmtsong(s), '-> ' if (s['pos'] == current_idx) else '   ')
             for s in songs]

    width = len(str(len(songs)))

    lines = ('{m} {i:#{w}}: {n}'.format(m=marker, i=i, n=name, w=width)
             for i, (name, marker) in enumerate(songs, 1))
    print('\n'.join(lines))


@command
def playpause():
    '''Invert current playback state.'''
    if state() == 'stop':
        play()
    else:
        pause()


@command(names=('prefix-search',), wrapper=line_list_printer)
def prefix_search(prefix: 'Prefix to search for.'):
    '''Search database for a given prefix.'''
    with connected(client):
        files = client.search('file', '')
    files = [song['file'] for song in files if song['file'].startswith(prefix)]

    return files


@command
def prev():
    '''Go to previous song in queue.'''
    with connected(client):
        client.previous()


@command
def replace(what: 'What to replace.'):
    '''Replace the current queue by something.'''
    clear()
    add(what)
    play()


@command
def seek(step: Arg(type=int,
                   help='How many seconds to advance or backtrack.')):
    '''Seek forward or backwards. Use negative values to seek backwards.'''
    with connected(client):
        client.seekcur('{:+}'.format(step))


@command
def setvolume(value: Arg(type=int,
                         help='A volume value between 0 and 100.')):
    '''Set the current volume.'''
    with connected(client):
        client.setvol(value)


@command(wrapper=printer)
def state():
    '''Get the current playback state (play, pause or stop).'''
    with connected(client):
        return client.status()['state']


@command
def stop():
    '''Stop playback.'''
    with connected(client):
        client.stop()


@command(names=('total-time',), wrapper=printer)
def total_time():
    '''Get the total time of the current queue.'''
    with connected(client):
        songs = client.playlistinfo()

    total = sum(int(song['time']) for song in songs)
    return fmt_minutes(total)


@command
def update():
    '''Update the server database.'''
    with connected(client):
        client.update()


@command(names=('vol', 'volume'), wrapper=printer)
def volume():
    '''Get the current volume.'''
    with connected(client):
        return int(client.status()['volume'])


@command
def volumestep(
        step: Arg(type=int,
                  help='Step in which to modify volume, positive or negative.')
):
    '''Set volume relative to current value.'''
    attempt = volume() + step
    new = min(max(0, attempt), 100)  # clip value between 0 and 100

    try:
        setvolume(new)
    except CommandError:
        fail('cannot set volume outside range 0-100.'
             ' attempt: {}'.format(attempt))


def seconds_elapsed():
    '''Get the elapsed and total time of the current song.'''
    with connected(client):
        current_time = int(float(client.status()['elapsed']))
    total = int(current_song()['time'])

    return current_time, total
