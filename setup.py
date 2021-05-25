from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

from adalink import __version__


setup(name              = 'adalink',
      version           = __version__,
      author            = 'Tony DiCola',
      author_email      = 'tdicola@adafruit.com',
      description       = 'Cross platform tool for programming ARM chips using a Segger J-link or STLink V2 programmer (with OpenOCD).',
      license           = 'MIT',
      url               = 'https://github.com/adafruit/Adafruit_Adalink',
      install_requires  = [],
      entry_points      = {'console_scripts': ['adalink = adalink.main:main']},
      packages          = find_packages())
