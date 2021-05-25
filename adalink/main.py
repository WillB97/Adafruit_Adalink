import logging
import os
import platform
import argparse

from . import __version__
from .core import Core
from .errors import AdaLinkError

# Import all the cores. MUST be a * reference to ensure all the cores are dynamically loaded.
from .cores import *


def main():
    """AdaLink ARM CPU Programmer.

    AdaLink can program different ARM CPUs using programming hardware such as
    the Segger JLink, Native Raspberry Pi or STLink v2 (using OpenOCD).

    To use the JLink programmer you MUST have Segger's JLink tools installed
    and in the system path.

    To use the STLink programmer you MUST have OpenOCD 0.9.0+ installed.

    To use the Raspi programmer you MUST have OpenOCD 0.9.0+ installed on the Pi with --enable-bcm2835gpio compiled.
    """
    # Hack to work-around bug in Mac OSX Yosemite where launchd does not set
    # the patch correctly for GUI apps.  See:
    #   http://apple.stackexchange.com/questions/153402/in-osx-yosemite-why-can-i-set-many-environment-variables-for-gui-apps-but-cann
    if platform.system() == 'Darwin':
        os.environ["PATH"] = os.environ["PATH"] + ':/usr/local/bin'

    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Display verbose output like raw programmer commands.',
    )
    parser.add_argument(
        '--version',
        action='version',
        version=__version__,
    )

    subparsers = parser.add_subparsers(title="Cores", metavar='CORE')

    for core in Core.__subclasses__():
        core().add_subparser(subparsers)

    args = parser.parse_args()

    # Enable verbose debug output if required.
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if 'func' in args:
        try:
            args.func(args)
        except AdaLinkError as e:
            print(e)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
