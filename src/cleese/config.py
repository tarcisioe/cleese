from configparser import ConfigParser
from functools import lru_cache
from os.path import expanduser, join


@lru_cache()
def read_config():
    parser = ConfigParser()
    parser.read(join(expanduser('~'), '.cleeserc'))

    return parser
