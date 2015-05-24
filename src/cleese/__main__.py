#!/usr/bin/env python
import sys

from argparse import ArgumentParser, REMAINDER, SUPPRESS

from mpd import MPDClient

from cleese.command import attach_all


def main(arguments):
    arg_parser = ArgumentParser(prog='cleese')

    subparsers = arg_parser.add_subparsers()

    attach_all(subparsers)

    args = arg_parser.parse_args(arguments)

    try:
        args.command(args)
    except AttributeError:
        arg_parser.print_usage()
        exit(1)
    except ConnectionRefusedError:
        print("Cannot connect to mpd server")
        exit(1)


def run():
    main(sys.argv[1:])


if __name__ == '__main__':
    run()
