# Atmel ATSAMD21G18 core implementation.
# See chip summary at:
#   http://www.atmel.com/Images/Atmel-42181-SAM-D21_Summary.pdf
#
# Author: Tony DiCola
import os

from ..core import Core
from ..errors import AdaLinkError
from ..programmers import JLink, STLink, RasPi2


class STLink_ATSAMD21G18(STLink):
    # ATSAMD21G18-specific STLink-based programmer.  Required to add custom
    # wipe function, and to use the load_image command for programming (the
    # flash write_image function doesn't seem to work because of OpenOCD bugs).

    def __init__(self):
        # Call base STLink initializer and set it up to program the ATSAMD21G18.
        super(STLink_ATSAMD21G18, self).__init__(params='-f interface/stlink-v2.cfg ' \
            '-c "set CHIPNAME at91samd21g18; set ENDIAN little; set CPUTAPID 0x0bc11477; source [find target/at91samdXX.cfg]"')

    def wipe(self):
        # Run OpenOCD command to wipe ATSAMD21G18 memory.
        commands = [
            'init',
            'reset init',
            'at91samd chip-erase',
            'exit'
        ]
        self.run_commands(commands)

    def program(self, hex_files=[], bin_files=[]):
        # Program the ATSAMD21G18 with the provided hex/bin files.
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

class RasPi2_ATSAMD21G18(RasPi2):
    # ATSAMD21G18-specific Raspi2 native-based programmer.  Required to add custom
    # wipe function, and to use the load_image command for programming (the
    # flash write_image function doesn't seem to work because of OpenOCD bugs).

    def __init__(self):
        # Call base Raspi initializer and set it up to program the ATSAMD21G18.
        super(RasPi2_ATSAMD21G18, self).__init__(params='-f interface/raspberrypi2-native.cfg ' \
            '-c "transport select swd; set CHIPNAME at91samd21g18; adapter_nsrst_delay 100; adapter_nsrst_assert_width 100; source [find target/at91samdXX.cfg]"')

    def wipe(self):
        # Run OpenOCD command to wipe ATSAMD21G18 memory.
        commands = [
            'init',
            'reset init',
            'at91samd chip-erase',
            'exit'
        ]
        self.run_commands(commands)

    def program(self, hex_files=[], bin_files=[]):
        # Program the ATSAMD21G18 with the provided hex/bin files.
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

class ATSAMD21G18(Core):
    """Atmel ATSAMD21G18 CPU."""
    # Note that the docstring will be used as the short help description.

    def __init__(self):
        # Call base class constructor--MUST be done!
        super(ATSAMD21G18, self).__init__()

    def list_programmers(self):
        """Return a list of the programmer names supported by this CPU."""
        return ['jlink', 'stlink', "raspi2"]

    def create_programmer(self, programmer):
        """Create and return a programmer instance that will be used to program
        the core.  Must be implemented by subclasses!
        """
        if programmer == 'jlink':
            return JLink('Cortex-M0 r0p1, Little endian',
                         params='-device ATSAMD21G18 -if swd -speed 1000')
        elif programmer == 'stlink':
            return STLink_ATSAMD21G18()
        elif programmer == 'raspi2':
            return RasPi2_ATSAMD21G18()

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
