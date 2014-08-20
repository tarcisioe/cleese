#!/usr/bin/env python

import sys

from command import command, get_command, command_names
from utils import exception_converter, printer, fmtsong
from mpd import MPDClient, CommandError


@exception_converter(IndexError, 'Command expects an argument.')
def single_argument_retriever(args):
    return args[:1]


@exception_converter(ValueError,
                     'Cannot make a number out of "{args[0][0]}".')
def volume_retriever(args):
    return [int(i) for i in single_argument_retriever(args)]


def empty_args(args):
    return []


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
def setvolume(client, volume):
    client.setvol(volume)


@command(empty_args, wrapper=printer)
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


def main():
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

if __name__ == '__main__':
    main()
