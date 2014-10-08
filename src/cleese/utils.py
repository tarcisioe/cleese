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
    def print_return(*args):
        print(function(*args))
    return print_return


def fmtsong(songdata):
    return('/'.join(songdata[i] for i in ('artist', 'album', 'title')))
