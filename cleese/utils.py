from functools import wraps


def exception_converter(exception_type,
                        message,
                        new_exception_type=None):
    if new_exception_type is None:
        new_exception_type = exception_type

    def exception_converter_inner(f):
        @wraps(f)
        def rethrower(*args):
            try:
                retval = f(*args)
            except exception_type as e:
                raise new_exception_type(message.format(args=args)) from e
            else:
                return retval
        return rethrower
    return exception_converter_inner


def printer(function):
    @wraps(function)
    def print_return(*args, **kwargs):
        print(function(*args, **kwargs))
    return print_return


def line_list_printer(function):
    from functools import wraps

    @wraps(function)
    def print_return(*args, **kwargs):
        for line in function(*args, **kwargs):
            print(line)
    return print_return


def fmtsong(songdata):
    '''Format song artist, album and title data.'''
    return '/'.join(songdata[i] for i in ('artist', 'album', 'title'))


def fmt_minutes(seconds):
    '''Format seconds as minutes and seconds.

    Args:
        seconds (int): The number of seconds.

    Returns:
        str: The value formatted as `mm:ss`.
    '''
    m, s = divmod(seconds, 60)
    return '{}:{:02}'.format(m, s)
