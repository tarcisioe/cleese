#!/usr/bin/env python3

import sys

import mpd


def song_retriever(args):
    try:
        arguments = [args[0]]
    except IndexError:
        raise IndexError('This command needs arguments.')
    else:
        return arguments


def fmtsong(songdata):
    return('/'.join(songdata[i] for i in ('artist', 'album', 'title')))


def empty_args(args):
    return []


def state(client):
    return client.status()['state']


def play(client):
    client.play()


def playpause(client):
    if state(client) == 'stop':
        play(client)
    else:
        pause(client)


def pause(client):
    client.pause()


def stop(client):
    client.stop()


def next_song(client):
    client.next()


def prev(client):
    client.previous()


def current(client):
    return fmtsong(client.currentsong())


def call_command(client, command, arguments):
    command(*([client] + arguments))


def clear(client):
    client.clear()


def printer(function):
    def print_return(*args):
        print(function(*args))
    return print_return


def add(client, to_add):
    try:
        client.add(to_add)
    except mpd.CommandError:
        raise ValueError("No files found in database matching your arguments: "
                         + to_add)


def replace(client, to_replace):
    clear(client)
    add(client, to_replace)
    play(client)

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
            'add': (add, song_retriever),
            'replace': (replace, song_retriever), }

if __name__ == '__main__':
    client = mpd.MPDClient()
    client.connect('localhost', 6600)

    args = sys.argv[:]

    try:
        command, argretriever = commands[args[1]]
    except IndexError:
        print('Please specify a command: ',
              ', '.join(sorted(commands)),
              '.', sep="")
        exit(-1)

    try:
        call_command(client, command, argretriever(args[2:]))
    except Exception as e:
        print(e)
