#!/usr/bin/env python
import sys

from argparse import ArgumentParser, REMAINDER, SUPPRESS

from mpd import MPDClient

from cleese.command import attach_all


def call_command(client, command, arguments):
    command(*([client] + arguments))


def main(arguments):
    client = MPDClient()
    client.connect('localhost', 6600)

    arg_parser = ArgumentParser()

    subparsers = arg_parser.add_subparsers()

    attach_all(subparsers)

    args = arg_parser.parse_args(arguments)


    args.command(args)


def run():
    main(sys.argv[1:])


if __name__ == '__main__':
    run()
