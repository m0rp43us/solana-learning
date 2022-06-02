#!/usr/bin/env python
# encoding: utf-8

import importlib
import pkgutil
import sys
import spl.commands as commands

from argparse import ArgumentParser
from spl.metadata import NAME, VERSION
from spl.errors import CannotGetStateLockException, ExitCode
from spl.spiget import SpiGet


COMMANDS = [m for _, m, _ in pkgutil.walk_packages(commands.__path__) if m[0] != "_"]


def main(argv=None):
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version="{} v{}".format(NAME, VERSION))

    subparsers = parser.add_subparsers()
    for command in COMMANDS:
        subparser = subparsers.add_parser(command)

        command_module = importlib.import_module("spl.commands.{}".format(command))
        if hasattr(command_module, "add_parser_args") and hasattr(command_module, "run"):
            command_module.add_parser_args(subparser)
            subparser.set_defaults(func=command_module.run)

    # Process arguments
    args = parser.parse_args()

    if args.func:
        try:
            spiget = SpiGet()
            return args.func(spiget, args).value
        except CannotGetStateLockException:
            print("Cannot obtain lock (is another spl process running?)")
            return ExitCode.CANNOT_GET_STATE_LOCK.value
    else:
        # argparse should prevent us from getting here
        print("Unrecognised action: {}".format(args.command))
        print("Available actions: {}".format(COMMANDS))
        return ExitCode.UNKNOWN_COMMAND.value

    return ExitCode.OK.value

if __name__ == "__main__":
    sys.exit(main().value)
