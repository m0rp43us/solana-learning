import importlib
from bunch import Bunch


def delegate(command, spiget, **kwargs):
    """Delegates to another named command with the given keyword arguments as args."""
    command_module = importlib.import_module("spl.commands.{}".format(command))
    if hasattr(command_module, "run"):
        return command_module.run(spiget, Bunch(kwargs))
