#!/usr/bin/env python3

import sys

from mpd import MPDClient, CommandError


def exception_converter(exception_type,
                        message,
                        new_exception_type=None):
    if new_exception_type is None:
        new_exception_type = exception_type

    def exception_converter_inner(f):
        def rethrower(*args):
            try:
                retval = f(*args)
            except exception_type:
                raise new_exception_type(message.format(args=args))
            else:
                return retval
        return rethrower
    return exception_converter_inner


def printer(function):
    def print_return(*args):
        print(function(*args))
    return print_return


@exception_converter(IndexError, 'Command expects an argument.')
def single_argument_retriever(args):
    return [args[0]]


@exception_converter(ValueError,
                     'Cannot make a number out of "{args[0][0]}".')
def volume_retriever(args):
    return [int(i) for i in single_argument_retriever(args)]


def empty_args(args):
    return []


def fmtsong(songdata):
    return('/'.join(songdata[i] for i in ('artist', 'album', 'title')))


play = MPDClient.play
pause = MPDClient.pause
stop = MPDClient.stop
next_song = MPDClient.next
prev = MPDClient.previous
clear = MPDClient.clear
setvolume = MPDClient.setvol


def state(client):
    return client.status()['state']


def playpause(client):
    if state(client) == 'stop':
        play(client)
    else:
        pause(client)


def current(client):
    return fmtsong(client.currentsong())


def volume(client):
    return int(client.status()['volume'])


@exception_converter(CommandError,
                     'No files found in database matching: {args[1]}',
                     ValueError)
def add(client, to_add):
    client.add(to_add)


def replace(client, to_replace):
    clear(client)
    add(client, to_replace)
    play(client)


def volumestep(client, step):
    try:
        client.setvol(volume(client) + step)
    except CommandError:
        pass


def call_command(client, command, arguments):
    command(*([client] + arguments))


commands = {'state': (printer(state), empty_args),
            'play': (play, empty_args),
            'playpause': (playpause, empty_args),
            'pause': (pause, empty_args),
            'stop': (stop, empty_args),
            'next': (next_song, empty_args),
            'previous': (prev, empty_args),
            'prev': (prev, empty_args),
            'current': (printer(current), empty_args),
            'clear': (clear, empty_args),
            'volume': (printer(volume), empty_args),
            'vol': (printer(volume), empty_args),
            'add': (add, single_argument_retriever),
            'replace': (replace, single_argument_retriever),
            'setvolume': (setvolume, volume_retriever),
            'volumestep': (volumestep, volume_retriever), }

if __name__ == '__main__':
    client = MPDClient()
    client.connect('localhost', 6600)

    args = sys.argv[:]

    try:
        command, argretriever = commands[args[1]]
    except (IndexError, KeyError):
        print('Please specify a command from: ',
              ', '.join(sorted(commands)),
              '.', sep="")
        exit(-1)

    try:
        call_command(client, command, argretriever(args[2:]))
    except (IndexError, ValueError) as e:
        print(e)
