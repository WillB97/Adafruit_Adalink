# Core base class
import os
import functools
import argparse

from .errors import AdaLinkError

class PathType:
    "An argparse type to test if files exist"
    def __init__(self, exists=True):
        self._exists = exists
        self._type = type

    def __call__(self, string):
        e = os.path.exists(string)
        if self._exists==True:
            if not e:
                raise argparse.ArgumentTypeError("path does not exist: '{}'".format(string))

            if not os.path.isfile(string):
                raise argparse.ArgumentTypeError("path is not a file: '{}'".format(string))
        else:
            p = os.path.dirname(os.path.normpath(string)) or '.'

            if not os.path.exists(p) or not os.path.isdir(p):
                raise argparse.ArgumentTypeError("parent directory does not exist: '{}'".format(p))
        return string


class ProgramBinArgs(argparse.Action):
    "Action to process argument pairs as File, int and append them"
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            items = getattr(namespace, self.dest, None)
            if items is None:
                items = []
            items.append((PathType(exists=True)(values[0]), int(values[1], base=0)))
            setattr(namespace, self.dest, items)
        except argparse.ArgumentTypeError as e:  # in actions ArgumentTypeError is not formatted correctly
            raise argparse.ArgumentError(self, e)


class Core:
    def __init__(self, name=None):
        # Default to the name of the class if one isn't specified.
        if name is None:
            name = self.__class__.__name__.lower()
        self.name = name

    def _callback(self, args):
        # Create the programmer that was specified.
        programmer = self.create_programmer(args.programmer)
        # Check that programmer is connected to device.
        if not programmer.is_connected():
            raise AdaLinkError('Could not find {0}, is it connected?'.format(self.name))
        # Wipe flash memory if requested.
        if args.wipe:
            programmer.wipe()
        # Program any specified hex/bin files.
        program_hex = [] if args.program_hex is None else args.program_hex
        program_bin = [] if args.program_bin is None else args.program_bin

        if len(program_hex) > 0 or len(program_bin) > 0:
            programmer.program(program_hex, program_bin)
        # Display information if requested.
        if args.info:
            self.info(programmer)
        # Read and print out memory if requested.
        # First make sure only one read memory command was requested (otherwise
        # it's ambiguous which one to use or the order to return results).
        f = [x for x in [args.read_mem_8, args.read_mem_16, args.read_mem_32] if x != None]
        if len(f) > 1:
            raise AdaLinkError('Only one read memory command can be specified at a time.')
        if args.read_mem_8 is not None:
            value = programmer.readmem8(args.read_mem_8)
            print('0x{0:0X}'.format(value))
        if args.read_mem_16 is not None:
            value = programmer.readmem16(args.read_mem_16)
            print('0x{0:0X}'.format(value))
        if args.read_mem_32 is not None:
            value = programmer.readmem32(args.read_mem_32)
            print('0x{0:0X}'.format(value))

    def add_subparser(self, subparsers):
        "Build the standard list of parameters that a core can take."
        parser = subparsers.add_parser(
            self.name,
            help=self.__doc__,
            description=self.__doc__,
            usage='%(prog)s [OPTIONS]',
            add_help=False,
        )
        parser.add_argument(  # Redefine help to free up -h
            '--help',
            action='help',
            help='show this help message and exit'
        )
        parser.add_argument(
            '-p', '--programmer',
            required=True,
            choices=self.list_programmers(),
            help='Programmer type.',
        )
        parser.add_argument(
            '-w', '--wipe',
            help='Wipe flash memory before programming.',
            action='store_true',
        )
        parser.add_argument(
            '-i', '--info',
            help='Display information about the core.',
            action='store_true',
        )
        parser.add_argument(
            '-h', '--program-hex',
            action='append',
            type=PathType(exists=True),
            help='Program the specified .hex file. Can be specified multiple times.',
        )
        parser.add_argument(
            '-b', '--program-bin',
            nargs=2,
            metavar=('PATH', 'ADDRESS'),
            action=ProgramBinArgs,
            help=(
                'Program the specified .bin file at the provided address. '
                'Address can be specified in hex, like 0x00FF.  Can be specified multiple times.'
            ),
        )
        parser.add_argument(
            '-r8', '--read-mem-8',
            type=functools.partial(int, base=0),
            metavar='ADDRESS',
            help='Read 1 byte of memory from the specified address (can be hex, like 0x1234ABCD).',
        )
        parser.add_argument(
            '-r16', '--read-mem-16',
            type=functools.partial(int, base=0),
            metavar='ADDRESS',
            help='Read 2 bytes of memory from the specified address (can be hex, like 0x1234ABCD).',
        )
        parser.add_argument(
            '-r32', '--read-mem-32',
            type=functools.partial(int, base=0),
            metavar='ADDRESS',
            help='Read 4 bytes of memory from the specified address (can be hex, like 0x1234ABCD).',
        )
        parser.set_defaults(func=self._callback)
        return parser

    def list_programmers(self):
        """Return a list of the programmer names supported by this CPU.  These
        names will be exposed by the --programmer option values, and the chosen
        one will be passed to create_programmer."""
        raise NotImplementedError

    def create_programmer(self, programmer):
        """Create and return a programmer instance that will be used to program
        the core.  Must be implemented by subclasses!  The p
        """
        raise NotImplementedError

    def info(self, programmer):
        """Display information about the device.  Will be passed an instance
        of the programmer created by create_programmer.  The programmer can be
        used to read memory and use it to display information."""
        # Default implementation does nothing, subclasses should override.
        pass
