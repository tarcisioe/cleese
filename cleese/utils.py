import sys

from os.path import basename

from wrapt import decorator


def exception_converter(exception_type,
                        message,
                        new_exception_type=None):
    if new_exception_type is None:
        new_exception_type = exception_type
    '''Make a decorator to convert between exception types.'''

    @decorator
    def rethrower(f, _, args, kwargs):
        '''Convert the requested exception type to the new exception type.'''
        try:
            retval = f(*args, **kwargs)
        except exception_type as e:
            raise new_exception_type(message.format(args=args,
                                                    kwargs=kwargs)) from e
        else:
            return retval
    return rethrower


@decorator
def printer(f, _, args, kwargs):
    '''Print the return of a function f.'''
    print(f(*args, **kwargs))


@decorator
def line_list_printer(f, _, args, kwargs):
    '''Print the return of a function f as a list of lines.'''
    for line in f(*args, **kwargs):
        print(line)


def fmtsong(songdata):
    '''Format song artist, album and title data.'''
    artist = songdata.get('artist', '')
    album = songdata.get('album', '')
    title = songdata.get('title', '')
    return '/'.join((artist, album, title))


def fmt_minutes(seconds):
    '''Format seconds as minutes and seconds.

    Args:
        seconds (int): The number of seconds.

    Returns:
        str: The value formatted as `mm:ss`.
    '''
    m, s = divmod(seconds, 60)
    return '{}:{:02}'.format(m, s)


def fail(message, name=basename(sys.argv[0]), retval=-1):
    '''Exit with non-zero code printing a message to stderr.'''
    print('{}: {}'.format(name, message), file=sys.stderr)
    sys.exit(retval)
