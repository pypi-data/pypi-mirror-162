"""
    vs_shortcut - Visual Studio IDE shortcut creator for Anaconda-navigator
    =======================================================================

    Provides an application shortcut for Microsoft Visual Studio IDE in
    Anaconda-navigator to automatically activate a given conda environment
    on startup.
    
    The default Visual Studio Developer PowerShell terminal then have full
    access to conda commands like a regular anaconda environment prompt. All
    scripts are then run with that terminal by default.
    
    The vs_shortcut package is designed for Windows OS and uses menuinst to
    create a Start Menu item. Just like Spyder IDE and VS Code shortcuts,
    Visual Studio icon and description is included.

"""

__author__ = "Maxime Tousignant-Tremblay"
__copyright__ = "Copyright (C) 2022 Maxime Tousignant-Tremblay"
__license__ = "AGPL-3.0"
__status__ = "Prototype"
__version__ = "1.0.1"
