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
    return('/'.join(songdata[i] for i in ('title', 'album', 'artist')))


def emptyargs(args):
    return []


def play(client):
    client.play()


def pause(client):
    client.pause()


def stop(client):
    client.stop()


def next_song(client):
    client.next()


def prev(client):
    client.previous()


def current(client):
    print(fmtsong(client.currentsong()))


def call_command(client, command, arguments):
    command(*([client] + arguments))


def clear(client):
    client.clear()


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

commands = {'play': (play, emptyargs),
            'pause': (pause, emptyargs),
            'stop': (stop, emptyargs),
            'next': (next_song, emptyargs),
            'previous': (prev, emptyargs),
            'prev': (prev, emptyargs),
            'current': (current, emptyargs),
            'clear': (clear, emptyargs),
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
