"""
    Entry point for the launching script of Microsoft Visual Studio.

"""

__author__ = "Maxime Tousignant-Tremblay"
__copyright__ = "Copyright (C) 2022 Maxime Tousignant-Tremblay"
__license__ = "AGPL-3.0"
__status__ = "Prototype"

# Standard library
import sys
from subprocess import Popen

# Local import
from . import __version__


def main():
    Popen(
        ["C:/Program Files/Microsoft Visual Studio/2022/Enterprise/Common7/IDE/devenv.exe"],
    )


if __name__ == "__main__":
    sys.exit(main())
