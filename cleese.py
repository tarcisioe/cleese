#!/usr/bin/env python3

import sys

from functools import wraps
from command import command, get_command, command_names
from mpd import MPDClient, CommandError


def exception_converter(exception_type,
                        message,
                        new_exception_type=None):
    if new_exception_type is None:
        new_exception_type = exception_type

    def exception_converter_inner(f):
        @wraps(f)
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


@command(empty_args)
def play(client):
    client.play()


@command(empty_args)
def pause(client):
    client.pause()


@command(empty_args)
def stop(client):
    client.stop()


@command(empty_args, names=['next'])
def next_song(client):
    client.next()


@command(empty_args)
def prev(client):
    client.previous()


@command(empty_args)
def clear(client):
    client.clear()


@command(volume_retriever)
def setvolume(client):
    client.setvol()


@command(empty_args)
def state(client):
    return client.status()['state']


@command(empty_args, names=['volume', 'vol'], wrapper=printer)
def volume(client):
    return int(client.status()['volume'])


@command(empty_args)
def playpause(client):
    if state(client) == 'stop':
        play(client)
    else:
        pause(client)


@command(empty_args, wrapper=printer)
def current(client):
    return fmtsong(client.currentsong())


@command(single_argument_retriever)
@exception_converter(CommandError,
                     'No files found in database matching: {args[1]}',
                     ValueError)
def add(client, to_add):
    client.add(to_add)


@command(single_argument_retriever)
def replace(client, to_replace):
    clear(client)
    add(client, to_replace)
    play(client)


@command(volume_retriever)
def volumestep(client, step):
    try:
        client.setvol(volume(client) + step)
    except CommandError:
        pass


def call_command(client, command, arguments):
    command(*([client] + arguments))


if __name__ == '__main__':
    client = MPDClient()
    client.connect('localhost', 6600)

    args = sys.argv[:]

    try:
        command_function, argretriever = get_command(args[1])
    except (IndexError, KeyError):
        print('Please specify a command from: ',
              ', '.join(sorted(command_names())),
              '.', sep="")
        exit(-1)

    try:
        call_command(client, command_function, argretriever(args[2:]))
    except (IndexError, ValueError) as e:
        print(e)
