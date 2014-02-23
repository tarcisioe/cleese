_commands = {}


def command(argument_retriever, names=[], wrapper=None):
    def inner(f):
        function = wrapper(f) if wrapper else f

        names_list = [f.__name__] if not names else names

        new_commands = [(name, (function, argument_retriever))
                        for name in names_list]

        _commands.update(new_commands)

        return f
    return inner


def get_command(name):
    return _commands[name]


def command_names():
    return _commands.keys()
