from mpd import CommandError

from cleese.clients import connected
from cleese.utils import (exception_converter, fail, fmt_minutes, fmtsong,
                          line_list_printer, printer)
from cleese.main import main

from carl import Arg, NotArg


@exception_converter(CommandError,
                     'no files found in database matching: {args[1]}',
                     FileNotFoundError)
def _add(client, what):
    '''Add a directory or a file from the library to a client's queue.

    Args:
        c (MPDClient): The client on which to add songs.
        what (str): The directory or file to add to the queue.
    '''
    client.add(what.rstrip('/'))


def current_song(client):
    '''Get the current song from the default server.'''
    with connected(client):
        return client.currentsong()


def fmt_current_song(client):
    '''Get the current song, properly formatted.'''
    try:
        return fmtsong(current_song(client))
    except KeyError:
        return ''


@main.subcommand
def add(client: NotArg, what: 'What to add.'):
    '''Add a directory or file from library to the playing queue.'''
    try:
        with connected(client):
            _add(client, what)
    except FileNotFoundError as e:
        fail(e)


@main.subcommand
def clear(client: NotArg):
    '''Clear the playing queue.'''
    with connected(client):
        client.clear()


@main.subcommand(wrapper=line_list_printer)
def commands(_: NotArg):
    '''Print all available commands.'''
    return main.subcommands


@main.subcommand(wrapper=printer)
def current(client: NotArg):
    '''Get the current song.'''
    song = fmt_current_song(client)
    if song:
        return song
    else:
        fail('no song playing.')


@main.subcommand(wrapper=printer)
def elapsed(client: NotArg,
            seconds: Arg(help='Show in seconds.', action='store_true')=False):
    '''Get the elapsed time and total time, formatted.'''
    current_time, total = seconds_elapsed(client)
    if not seconds:
        current_time = fmt_minutes(current_time)
        total = fmt_minutes(total)
    return '{}/{}'.format(current_time, total)


@main.subcommand
def goto(client: NotArg,
         where: Arg(type=int,
                    help='Point in song where to seek to (seconds).')):
    '''Go to a specific point in the current song.'''
    with connected(client):
        client.seekcur(where)


@main.subcommand(wrapper=line_list_printer)
def idle(client: NotArg):
    '''Waits for the server to signal any events.'''
    with connected(client):
        return client.idle()


@main.subcommand(names=('next',))
def next_song(client: NotArg):
    '''Go to next song in queue.'''
    with connected(client):
        client.next()


@main.subcommand
def pause(client: NotArg):
    '''Pause playback.'''
    with connected(client):
        client.pause()


@main.subcommand
def play(client: NotArg):
    '''Play playback.'''
    with connected(client):
        client.play()


@main.subcommand(wrapper=printer)
def playlist(client: NotArg):
    '''Print the current playlist.'''
    with connected(client):
        songs = client.playlistinfo()
    current_idx = current_song(client)['pos']

    songs = [(fmtsong(s), '-> ' if (s['pos'] == current_idx) else '   ')
             for s in songs]

    width = len(str(len(songs)))

    lines = ('{m} {i:#{w}}: {n}'.format(m=marker, i=i, n=name, w=width)
             for i, (name, marker) in enumerate(songs, 1))
    return '\n'.join(lines)


@main.subcommand
def playpause(client: NotArg):
    '''Invert current playback state.'''
    if state(client) == 'stop':
        play(client)
    else:
        pause(client)


@main.subcommand(names=('prefix-search',), wrapper=line_list_printer)
def prefix_search(client: NotArg,
                  prefix: 'Prefix to search for.'):
    '''Search database for a given prefix.'''
    with connected(client):
        files = client.search('file', '')
    files = [song['file'] for song in files if song['file'].startswith(prefix)]

    return files


@main.subcommand
def prev(client: NotArg):
    '''Go to previous song in queue.'''
    with connected(client):
        client.previous()


@main.subcommand
def replace(client: NotArg,
            what: 'What to replace.'):
    '''Replace the current queue by something.'''
    clear(client)
    add(client, what)
    play(client)


@main.subcommand
def seek(client: NotArg,
         step: Arg(type=int,
                   help='How many seconds to advance or backtrack.')):
    '''Seek forward or backwards. Use negative values to seek backwards.'''
    with connected(client):
        client.seekcur('{:+}'.format(step))


@main.subcommand
def setvolume(client: NotArg,
              value: Arg(type=int,
                         help='A volume value between 0 and 100.')):
    '''Set the current volume.'''
    with connected(client):
        client.setvol(value)


@main.subcommand(wrapper=printer)
def state(client: NotArg):
    '''Get the current playback state (play, pause or stop).'''
    with connected(client):
        return client.status()['state']


@main.subcommand
def stop(client: NotArg):
    '''Stop playback.'''
    with connected(client):
        client.stop()


@main.subcommand(names=('total-time',), wrapper=printer)
def total_time(client: NotArg):
    '''Get the total time of the current queue.'''
    with connected(client):
        songs = client.playlistinfo()

    total = sum(int(song['time']) for song in songs)
    return fmt_minutes(total)


@main.subcommand
def update(client: NotArg):
    '''Update the server database.'''
    with connected(client):
        client.update()


@main.subcommand(names=('vol', 'volume'), wrapper=printer)
def volume(client: NotArg):
    '''Get the current volume.'''
    with connected(client):
        return int(client.status()['volume'])


@main.subcommand
def volumestep(
        client: NotArg,
        step: Arg(type=int,
                  help='Step in which to modify volume, positive or negative.')
):
    '''Set volume relative to current value.'''
    attempt = volume(client) + step
    new = min(max(0, attempt), 100)  # clip value between 0 and 100

    try:
        setvolume(client, new)
    except CommandError:
        fail('cannot set volume outside range 0-100.'
             ' attempt: {}'.format(attempt))


def seconds_elapsed(client: NotArg):
    '''Get the elapsed and total time of the current song.'''
    with connected(client):
        current_time = int(float(client.status()['elapsed']))
    total = int(current_song(client)['time'])

    return current_time, total
