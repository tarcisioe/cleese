#!/usr/bin/env python
import sys

from mpd import MPDClient

from cleese.command import get_command, command_names


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
