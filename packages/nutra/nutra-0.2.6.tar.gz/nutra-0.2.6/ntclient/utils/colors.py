# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 14:35:43 2022

@author: shane

Allows the safe avoidance of ImportError on non-colorama capable systems.
"""

try:
    from colorama import Fore, Style
    from colorama import init as colorama_init

    # Made it this far, so run the init function (which is needed on Windows)
    colorama_init()

    # Styles
    STYLE_BRIGHT = Style.BRIGHT
    STYLE_DIM = Style.DIM
    STYLE_RESET_ALL = Style.RESET_ALL

    # Colors
    COLOR_WARN = Fore.YELLOW
    COLOR_CRIT = Style.DIM + Fore.RED
    COLOR_OVER = Style.DIM + Fore.MAGENTA

    COLOR_DEFAULT = Fore.CYAN

    # Used in macro bars
    COLOR_YELLOW = Fore.YELLOW
    COLOR_BLUE = Fore.BLUE
    COLOR_RED = Fore.RED

    # Used by `tree.py` utility
    COLOR_GREEN = Fore.GREEN
    COLOR_CYAN = Fore.CYAN

except ImportError:
    # These will all just be empty strings if colorama isn't installed

    # Styles
    STYLE_BRIGHT = str()
    STYLE_DIM = str()
    STYLE_RESET_ALL = str()

    # Colors
    COLOR_WARN = str()
    COLOR_CRIT = str()
    COLOR_OVER = str()

    COLOR_DEFAULT = str()

    COLOR_YELLOW = str()
    COLOR_BLUE = str()
    COLOR_RED = str()

    COLOR_GREEN = str()
    COLOR_CYAN = str()
