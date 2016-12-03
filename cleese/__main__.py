#!/usr/bin/env python
import sys

from cleese.commands import main


def run():
    main.run(sys.argv[1:])


if __name__ == '__main__':
    run()
