# Atmel SAMD21 core implementation.
# See chip summary at:
#   http://www.atmel.com/Images/Atmel-42181-SAM-D21_Summary.pdf
#
# Author: Tony DiCola
import os

from ..core import Core
from ..errors import AdaLinkError
from ..programmers import JLink, STLink, RasPi2

# DEVICE SELECTION register value to name mapping
DEVSEL_CHIPNAME_LOOKUP = {
    0x0: 'SAMD21J18A',
    0x1: 'SAMD21J17A',
    0x2: 'SAMD21J16A',
    0x3: 'SAMD21J15A',

    0x5: 'SAMD21G18A',
    0x6: 'SAMD21G17A',
    0x7: 'SAMD21G16A',
    0x8: 'SAMD21G15A',

    0xA: 'SAMD21E18A',
    0xB: 'SAMD21E17A',
    0xC: 'SAMD21E16A',
    0xD: 'SAMD21E15A',
}

VARIANT_LOOKUP = {
    'samd21e15': ('atsamd21e15', 'at91samd21e15'),
    'samd21e16': ('atsamd21e16', 'at91samd21e16'),
    'samd21e17': ('atsamd21e17', 'at91samd21e17'),
    'samd21e18': ('atsamd21e18', 'at91samd21e18'),

    'samd21g15': ('atsamd21g15', 'at91samd21g15'),
    'samd21g16': ('atsamd21g16', 'at91samd21g16'),
    'samd21g17': ('atsamd21g17', 'at91samd21g17'),
    'samd21g18': ('atsamd21g18', 'at91samd21g18'),

    'samd21j15': ('atsamd21j15', 'at91samd21j15'),
    'samd21j16': ('atsamd21j16', 'at91samd21j16'),
    'samd21j17': ('atsamd21j17', 'at91samd21j17'),
    'samd21j18': ('atsamd21j18', 'at91samd21j18'),
}


class STLink_SAMD21(STLink):
    # SAMD21-specific STLink-based programmer.  Required to add custom
    # wipe function, and to use the load_image command for programming (the
    # flash write_image function doesn't seem to work because of OpenOCD bugs).

    def __init__(self, chipname='at91samd21g18'):
        # Call base STLink initializer and set it up to program the SAMD21.
        super(STLink_SAMD21, self).__init__(params=(
            '-f interface/stlink-v2.cfg '
            '-c "set CHIPNAME {}; set ENDIAN little; set CPUTAPID 0x0bc11477; source [find target/at91samdXX.cfg]"'
        ).format(chipname))

    def wipe(self):
        # Run OpenOCD command to wipe SAMD21 memory.
        commands = [
            'init',
            'reset init',
            'at91samd chip-erase',
            'exit'
        ]
        self.run_commands(commands)

    def program(self, hex_files=[], bin_files=[]):
        # Program the SAMD21 with the provided hex/bin files.
        print('WARNING: Make sure the provided hex/bin files are padded with ' \
            'at least 64 bytes of blank (0xFF) data!  This will work around a cache bug with OpenOCD 0.9.0.')
        commands = [
            'init',
            'reset init'
        ]
        # Program each hex file.
        for f in hex_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('load_image {0} 0 ihex'.format(f))
        # Program each bin file.
        for f, addr in bin_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('load_image {0} 0x{1:08X} bin'.format(f, addr))
        # Verify each hex file.
        for f in hex_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('verify_image {0} 0 ihex'.format(f))
        # Verify each bin file.
        for f, addr in bin_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('verify_image {0} 0x{1:08X} bin'.format(f, addr))
        commands.append('reset run')
        commands.append('exit')
        # Run commands.
        output = self.run_commands(commands)
        # Check that expected number of files were verified.  Look for output lines
        # that start with 'verified ' to signal OpenOCD output that the verification
        # succeeded.  Count up these lines and expect they match the number of
        # programmed files.
        verified = len(filter(lambda x: x.startswith('verified '), output.splitlines()))
        if verified != (len(hex_files) + len(bin_files)):
            raise AdaLinkError('Failed to verify all files were programmed!')

class RasPi2_SAMD21(RasPi2):
    # SAMD21-specific Raspi2 native-based programmer.  Required to add custom
    # wipe function, and to use the load_image command for programming (the
    # flash write_image function doesn't seem to work because of OpenOCD bugs).

    def __init__(self, chipname='at91samd21g18'):
        # Call base Raspi initializer and set it up to program the SAMD21.
        super(RasPi2_SAMD21, self).__init__(params=(
            '-f interface/raspberrypi2-native.cfg '
            '-c "transport select swd; set CHIPNAME {}; adapter_nsrst_delay 100; '
            'adapter_nsrst_assert_width 100; source [find target/at91samdXX.cfg]"'
        ).format(chipname))

    def wipe(self):
        # Run OpenOCD command to wipe SAMD21 memory.
        commands = [
            'init',
            'reset init',
            'at91samd chip-erase',
            'exit'
        ]
        self.run_commands(commands)

    def program(self, hex_files=[], bin_files=[]):
        # Program the SAMD21 with the provided hex/bin files.
        print('WARNING: Make sure the provided hex/bin files are padded with ' \
            'at least 64 bytes of blank (0xFF) data!  This will work around a cache bug with OpenOCD 0.9.0.')
        commands = [
            'init',
            'reset init'
        ]
        # Program each hex file.
        for f in hex_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('load_image {0} 0 ihex'.format(f))
        # Program each bin file.
        for f, addr in bin_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('load_image {0} 0x{1:08X} bin'.format(f, addr))
        # Verify each hex file.
        for f in hex_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('verify_image {0} 0 ihex'.format(f))
        # Verify each bin file.
        for f, addr in bin_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('verify_image {0} 0x{1:08X} bin'.format(f, addr))
        commands.append('reset run')
        commands.append('exit')
        # Run commands.
        output = self.run_commands(commands)
        # Check that expected number of files were verified.  Look for output lines
        # that start with 'verified ' to signal OpenOCD output that the verification
        # succeeded.  Count up these lines and expect they match the number of
        # programmed files.
        verified = len(filter(lambda x: x.startswith('verified '), output.splitlines()))
        if verified != (len(hex_files) + len(bin_files)):
            raise AdaLinkError('Failed to verify all files were programmed!')

class SAMD21(Core):
    """Atmel SAMD21 CPU."""
    # Note that the docstring will be used as the short help description.

    def __init__(self):
        # Call base class constructor--MUST be done!
        super(SAMD21, self).__init__()

    def list_programmers(self):
        """Return a list of the programmer names supported by this CPU."""
        return ['jlink', 'stlink', "raspi2"]

    def create_programmer(self, programmer):
        """Create and return a programmer instance that will be used to program
        the core.  Must be implemented by subclasses!
        """
        if programmer == 'jlink':
            return JLink(
                'Cortex-M0 r0p1, Little endian',
                params='-device {} -if swd -speed 1000'.format(
                    VARIANT_LOOKUP.get(self.variant, ('ATSAMD21G18',))[0]
                )
            )
        elif programmer == 'stlink':
            return STLink_SAMD21(VARIANT_LOOKUP.get(self.variant, ('', 'at91samd21g18'))[1])
        elif programmer == 'raspi2':
            return RasPi2_SAMD21(VARIANT_LOOKUP.get(self.variant, ('', 'at91samd21g18'))[1])

    def add_subparser(self, subparsers):
        "Add the variant option to the bottom of the standard list of options"
        parser = super().add_subparser(subparsers)
        parser.add_argument(
            '-V', '--variant',
            help='Set the particular chip variant being used (default is samd21g18)',
            choices=VARIANT_LOOKUP.keys(),
            default='samd21g18',
            metavar='VARIANT',
        )

    def _callback(self, args):
        "Capture the value of the variant argument for use in create_programmer"
        self.variant = args.variant
        super()._callback(args)

    def info(self, programmer):
        """Display info about the device."""
        print('Serial No.: {0:04X}:{1:04X}:{2:04X}:{3:04X}:{4:04X}:{5:04X}:{6:04X}:{7:04X}'.format(
            programmer.readmem16(0x0080A00E),
            programmer.readmem16(0x0080A00C),
            programmer.readmem16(0x0080A042),
            programmer.readmem16(0x0080A040),
            programmer.readmem16(0x0080A046),
            programmer.readmem16(0x0080A044),
            programmer.readmem16(0x0080A04A),
            programmer.readmem16(0x0080A048),
        ))
        print('Device ID : {0}'.format(DEVSEL_CHIPNAME_LOOKUP.get(
                programmer.readmem8(0x41002018), 'Reserved')))
