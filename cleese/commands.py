from ampdup import MPDClient, MPDError, Song, URINotFoundError, State

from cleese.utils import fail, fmt_minutes, fmtsong, line_list_printer, printer
from cleese.main import main

from carl import Arg, NotArg


async def _add(client, what):
    '''Add a directory or a file from the library to a client's queue.

    Args:
        c (Client): The client on which to add songs.
        what (str): The directory or file to add to the queue.
    '''
    await client.add(what.rstrip('/'))


async def fmt_current_song(client: MPDClient) -> str:
    '''Get the current song, properly formatted.'''
    try:
        return fmtsong(await client.current_song())
    except KeyError:
        return ''


@main.subcommand
async def add(client: NotArg, what: 'What to add.'):
    '''Add a directory or file from library to the playing queue.'''
    try:
        await _add(client, what)
    except URINotFoundError as e:
        fail(e)


@main.subcommand
async def clear(client: NotArg):
    '''Clear the playing queue.'''
    await client.clear()


@main.subcommand(wrapper=line_list_printer)
async def commands(client: NotArg):
    '''Print all available commands.'''
    return main.subcommands


@main.subcommand(wrapper=printer)
async def current(client: NotArg):
    '''Get the current song.'''
    song = await fmt_current_song(client)
    if song:
        return song
    else:
        fail('no song playing.')


@main.subcommand(wrapper=printer)
async def elapsed(
        client: NotArg,
        seconds: Arg(help='Show in seconds.', action='store_true')=False
):
    '''Get the elapsed time and total time, formatted.'''
    current_time, total = await seconds_elapsed(client)
    if not seconds:
        current_time = fmt_minutes(current_time)
        total = fmt_minutes(total)
    return f'{current_time}/{total}'


@main.subcommand
async def goto(
        client: NotArg,
        where: Arg(type=int,
                   help='Point in song where to seek to (seconds).')
):
    '''Go to a specific point in the current song.'''
    await client.seek_cur(where)


@main.subcommand(wrapper=line_list_printer)
async def idle(client: NotArg):
    '''Waits for the server to signal any events.'''
    return await client.idle()


@main.subcommand(wrapper=printer)
async def index(client: NotArg):
    '''Print current song index on playlist.'''
    return int((await client.current_song()).pos) + 1


@main.subcommand(names=('next',))
async def next_song(client: NotArg):
    '''Go to next song in queue.'''
    await client.next()


@main.subcommand
async def pause(client: NotArg):
    '''Pause playback.'''
    await client.pause(True)


@main.subcommand
async def play(client: NotArg):
    '''Play playback.'''
    await client.play()


@main.subcommand(wrapper=printer)
async def playlist(client: NotArg):
    '''Print the current playlist.'''
    songs = await client.playlist_info()
    current_idx = (await client.current_song()).pos

    songs = [(fmtsong(s), '-> ' if (s.pos == current_idx) else '   ')
             for s in songs]

    width = len(str(len(songs)))

    lines = (f'{marker} {i:#{width}}: {name}'
             for i, (name, marker) in enumerate(songs, 1))
    return '\n'.join(lines)


@main.subcommand
async def playpause(client: NotArg):
    '''Invert current playback state.'''
    if await state(client) in (State.STOP, State.PAUSE):
        await play(client)
    else:
        await pause(client)


@main.subcommand(names=('prefix-search',), wrapper=line_list_printer)
async def prefix_search(
        client: NotArg,
        prefix: 'Prefix to search for.'
):
    '''Search database for a given prefix.'''
    files = await client.search('file', '')

    files = [song.file for song in files if song.file.startswith(prefix)]

    return files


@main.subcommand
async def prev(client: NotArg):
    '''Go to previous song in queue.'''
    await client.previous()


@main.subcommand
async def replace(
        client: NotArg,
        what: 'What to replace.'
):
    '''Replace the current queue by something.'''
    await clear(client)
    await add(client, what)
    await play(client)


@main.subcommand
async def seek(
        client: NotArg,
        step: Arg(type=int,
                  help='How many seconds to advance or backtrack.')
):
    '''Seek forward or backwards. Use negative values to seek backwards.'''
    await client.seek_cur(step)


@main.subcommand
async def setvolume(
        client: NotArg,
        value: Arg(type=int,
                   help='A volume value between 0 and 100.')
):
    '''Set the current volume.'''
    await client.setvol(value)


@main.subcommand(wrapper=printer)
async def state(client: NotArg):
    '''Get the current playback state (play, pause or stop).'''
    return (await client.status()).state


@main.subcommand
async def stop(client: NotArg):
    '''Stop playback.'''
    await client.stop()


@main.subcommand(names=('total-time',), wrapper=printer)
async def total_time(client: NotArg):
    '''Get the total time of the current queue.'''
    songs = await client.playlist_info()

    total = sum(int(song.time) for song in songs)
    return fmt_minutes(total)


@main.subcommand
async def update(client: NotArg):
    '''Update the server database.'''
    await client.update()


@main.subcommand(names=('vol', 'volume'), wrapper=printer)
async def volume(client: NotArg):
    '''Get the current volume.'''
    return int((await client.status()).volume)


@main.subcommand
async def volumestep(
        client: NotArg,
        step: Arg(type=int,
                  help='Step in which to modify volume, positive or negative.')
):
    '''Set volume relative to current value.'''
    attempt = (await volume(client)) + step
    new = min(max(0, attempt), 100)  # clip value between 0 and 100

    try:
        await setvolume(client, new)
    except MPDError:
        fail('cannot set volume outside range 0-100.'
             f' attempt: {attempt}')


async def seconds_elapsed(client: NotArg):
    '''Get the elapsed and total time of the current song.'''
    current_time = int(float((await client.status()).elapsed))

    total = int((await client.current_song()).time)

    return current_time, total
