import sys
from collections import OrderedDict
from functools import wraps
from os.path import basename
from inspect import signature, Signature

_commands = OrderedDict()


def empty_args(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if len(args) == 1 and not kwargs and callable(args[0]):
            return f()(args[0])
        else:
            return f(*args, **kwargs)

    return decorator


class Arg:
    def __init__(self, *args, optional=False, **kwargs):
        if args and args[0].startswith('-'):
            optional = True

        self.named = args and isinstance(args[0], str)
        self.optional = optional
        self.args = args

        if 'choices' in kwargs:
            kwargs['choices'] = sorted(kwargs['choices'])

        self.kwargs = kwargs


class CommandOptions:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class SubCommand:
    def __init__(self, names, arg_format, options, function):
        self.names = names
        self.arg_format = arg_format
        self.options = options
        self.function = function

    def attach(self, subparsers):
        name, *names = self.names

        if self.options is Signature.empty:
            if self.function.__doc__:
                description = self.function.__doc__
                self.options = CommandOptions(help=description,
                                              description=description)
            else:
                self.options = CommandOptions()

        if isinstance(self.options, str):
            self.options = CommandOptions(help=self.options,
                                          description=self.options)

        parser = subparsers.add_parser(name, aliases=names,
                                       *self.options.args,
                                       **self.options.kwargs)

        for name, arg, default in self.arg_format:
            if arg is Signature.empty:
                arg = Arg()

            if isinstance(arg, str):
                arg = Arg(help=arg)

            if default is not Signature.empty:
                arg.kwargs['default'] = default
                arg.optional = True

            if arg.optional:
                arg.kwargs['dest'] = name

            name = '--' + name if arg.optional else name
            if not arg.named:
                arg.args = [name] + list(arg.args)
            parser.add_argument(*(arg.args), **(arg.kwargs))

        def call(args):
            arg_dict = {name: getattr(args, name)
                        for name, _, _ in self.arg_format}
            self.function(**arg_dict)

        parser.set_defaults(command=call)


@empty_args
def command(names=(), wrapper=None):
    def inner(f):
        function = wrapper(f) if wrapper else f

        names_tuple = (f.__name__,) if not names else names

        arg_format = [(a.name, a.annotation, a.default)
                      for a in signature(f).parameters.values()]

        options = signature(f).return_annotation

        _commands[names_tuple] = (SubCommand(names_tuple,
                                             arg_format,
                                             options,
                                             function))

        return f
    return inner


def get_command(name):
    return _commands[name]


def command_names():
    return sorted([name for names in _commands for name in names])


def attach_all(subparsers):
    for c in _commands.values():
        c.attach(subparsers)


def fail(message, name=basename(sys.argv[0]), retval=-1):
    print('{}: {}'.format(name, message), file=sys.stderr)
    sys.exit(retval)
