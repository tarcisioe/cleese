_commands = []


class SubCommand:
    def __init__(self, names, arg_format, function):
        self.names = names
        self.arg_format = arg_format
        self.function = function

    def attach(self, subparsers):
        name, *names = self.names
        parser = subparsers.add_parser(name, aliases=names)
        for arg_name, arg_type in self.arg_format:
            parser.add_argument(arg_name, type=arg_type)
        parser.set_defaults(command=self.function)


def command(arg_format=[], names=[], wrapper=None):
    def inner(f):
        function = wrapper(f) if wrapper else f

        names_list = [f.__name__] if not names else names

        _commands.append(SubCommand(names_list, arg_format, function))

        return f
    return inner


def get_command(name):
    return _commands[name]


def command_names():
    return _commands.keys()


def attach_all(subparsers):
    for command in _commands:
        command.attach(subparsers)
