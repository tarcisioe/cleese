#!/usr/bin/env python
import sys

from argparse import ArgumentParser, REMAINDER, SUPPRESS

from mpd import MPDClient

from cleese.command import get_command, command_names


def call_command(client, command, arguments):
    command(*([client] + arguments))


def main(arguments):
    client = MPDClient()
    client.connect('localhost', 6600)

    arg_parser = ArgumentParser()
    arg_parser.add_argument('command')
    arg_parser.add_argument('args', nargs=REMAINDER, help=SUPPRESS)

    args = arg_parser.parse_args(arguments)

    try:
        command_function, argretriever = get_command(args.command)
    except (IndexError, KeyError):
        print('Please specify a command from: ',
              ', '.join(sorted(command_names())),
              '.', sep="")
        exit(-1)

    try:
        call_command(client, command_function, argretriever(args.args))
    except (IndexError, ValueError) as e:
        print(e)

def run():
    main(sys.argv[1:])

if __name__ == '__main__':
    run()
