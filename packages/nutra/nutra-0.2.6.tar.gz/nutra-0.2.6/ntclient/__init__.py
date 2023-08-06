# -*- coding: utf-8 -*-
"""
Package info, database targets, paging/debug flags, PROJECT_ROOT,
    and other configurations.

Created on Fri Jan 31 16:01:31 2020

@author: shane
"""
import argparse
import os
import platform
import shutil
import sys
from enum import Enum

from ntclient.ntsqlite.sql import NT_DB_NAME
from ntclient.utils import colors

# Package info
__title__ = "nutra"
__version__ = "0.2.6"
__author__ = "Shane Jaroch"
__email__ = "chown_tee@proton.me"
__license__ = "GPL v3"
__copyright__ = "Copyright 2018-2022 Shane Jaroch"
__url__ = "https://github.com/nutratech/cli"

# Sqlite target versions
__db_target_nt__ = "0.0.6"
__db_target_usda__ = "0.0.8"
USDA_XZ_SHA256 = "25dba8428ced42d646bec704981d3a95dc7943240254e884aad37d59eee9616a"

# Global variables
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
NUTRA_HOME = os.getenv("NUTRA_HOME", os.path.join(os.path.expanduser("~"), ".nutra"))
USDA_DB_NAME = "usda.sqlite"
# NOTE: NT_DB_NAME = "nt.sqlite3" is defined in ntclient.ntsqlite.sql

NTSQLITE_BUILDPATH = os.path.join(PROJECT_ROOT, "ntsqlite", "sql", NT_DB_NAME)
NTSQLITE_DESTINATION = os.path.join(NUTRA_HOME, NT_DB_NAME)

# Check Python version
PY_MIN_VER = (3, 4, 3)
PY_SYS_VER = sys.version_info[0:3]
PY_MIN_STR = ".".join(str(x) for x in PY_MIN_VER)
PY_SYS_STR = ".".join(str(x) for x in PY_SYS_VER)
if PY_SYS_VER < PY_MIN_VER:
    # TODO: make this testable with: `class CliConfig`?
    raise RuntimeError(
        "ERROR: %s requires Python %s or later to run" % (__title__, PY_MIN_STR),
        "HINT:  You're running Python %s" % PY_SYS_STR,
    )

# Console size, don't print more than it
BUFFER_WD = shutil.get_terminal_size()[0]
BUFFER_HT = shutil.get_terminal_size()[1]

DEFAULT_RESULT_LIMIT = BUFFER_HT - 4

DEFAULT_DAY_H_BUFFER = BUFFER_WD - 4 if BUFFER_WD > 12 else 8

# TODO: keep one extra row on winXP / cmd.exe, it cuts off
DECREMENT = 1 if platform.system() == "Windows" else 0
DEFAULT_SORT_H_BUFFER = (
    BUFFER_WD - (38 + DECREMENT) if BUFFER_WD > 50 else (12 - DECREMENT)
)
DEFAULT_SEARCH_H_BUFFER = (
    BUFFER_WD - (50 + DECREMENT) if BUFFER_WD > 70 else (20 - DECREMENT)
)


################################################################################
# CLI config class (settings & preferences / defaults)
################################################################################
class RdaColors(Enum):
    """
    Stores values for report colors.
    Default values:
        Acceptable     =Cyan
        Overage        =Magenta (Dim)
        Low            =Yellow
        Critically Low =Red (Dim)
    TODO: make configurable in SQLite or prefs.json
    """

    THRESH_WARN = 0.7
    THRESH_CRIT = 0.4
    THRESH_OVER = 1.9

    COLOR_WARN = colors.COLOR_WARN
    COLOR_CRIT = colors.COLOR_CRIT
    COLOR_OVER = colors.COLOR_OVER

    COLOR_DEFAULT = colors.COLOR_DEFAULT

    STYLE_RESET_ALL = colors.STYLE_RESET_ALL

    # Used in macro bars
    COLOR_YELLOW = colors.COLOR_YELLOW
    COLOR_BLUE = colors.COLOR_BLUE
    COLOR_RED = colors.COLOR_RED


class _CliConfig:
    """Mutable global store for configuration values"""

    def __init__(self, debug: bool = False, paging: bool = True) -> None:
        self.debug = debug
        self.paging = paging

        # TODO: respect a prefs.json, or similar config file.
        self.thresh_warn = RdaColors.THRESH_WARN.value
        self.thresh_crit = RdaColors.THRESH_CRIT.value
        self.thresh_over = RdaColors.THRESH_OVER.value

        self.color_warn = RdaColors.COLOR_WARN.value
        self.color_crit = RdaColors.COLOR_CRIT.value
        self.color_over = RdaColors.COLOR_OVER.value
        self.color_default = RdaColors.COLOR_DEFAULT.value

        self.style_reset_all = RdaColors.STYLE_RESET_ALL.value

        self.color_yellow = RdaColors.COLOR_YELLOW.value
        self.color_red = RdaColors.COLOR_RED.value
        self.color_blue = RdaColors.COLOR_BLUE.value

    def set_flags(self, args: argparse.Namespace) -> None:
        """
        Sets flags:
          {DEBUG, PAGING}
            from main (after arg parse). Accessible throughout package.
            Must be re-imported globally.
        """

        self.debug = args.debug
        self.paging = not args.no_pager

        if self.debug:
            print("Console size: %sh x %sw" % (BUFFER_HT, BUFFER_WD))


# Create the shared instance object
CLI_CONFIG = _CliConfig()


# TODO:
#  Nested nutrient tree, like:
#       http://www.whfoods.com/genpage.php?tname=nutrientprofile&dbid=132
#  Attempt to record errors in failed try/catch block (bottom of __main__.py)
#  Make use of argcomplete.warn(msg) ?


################################################################################
# Validation Enums
################################################################################
class Gender(Enum):
    """
    A validator and Enum class for gender inputs; used in several calculations.
    @note: floating point -1 to 1, or 0 to 1... for non-binary?
    """

    MALE = "m"
    FEMALE = "f"


class ActivityFactor(Enum):
    """
    Used in BMR calculations.
    Different activity levels: {0.200, 0.375, 0.550, 0.725, 0.900}

    Activity Factor\n
    ------------------------\n
    0.200 = sedentary (little or no exercise)

    0.375 = lightly active
        (light exercise/sports 1-3 days/week, approx. 590 Cal/day)

    0.550 = moderately active
        (moderate exercise/sports 3-5 days/week, approx. 870 Cal/day)

    0.725 = very active
        (hard exercise/sports 6-7 days a week, approx. 1150 Cal/day)

    0.900 = extremely active
        (very hard exercise/sports and physical job, approx. 1580 Cal/day)

    @todo: Verify the accuracy of these "names". Access by index?
    """

    SEDENTARY = {1: 0.2}
    MILDLY_ACTIVE = {2: 0.375}
    ACTIVE = {3: 0.55}
    HIGHLY_ACTIVE = {4: 0.725}
    INTENSELY_ACTIVE = {5: 0.9}


def activity_factor_from_index(activity_factor: int) -> float:
    """
    Gets ActivityFactor Enum by float value if it exists, else raise ValueError.
    Basically just verifies the float is among the allowed values, and re-returns it.
    """
    for enum_entry in ActivityFactor:
        if activity_factor in enum_entry.value:
            return float(enum_entry.value[activity_factor])
    # TODO: custom exception. And handle in main file?
    raise ValueError("No such ActivityFactor for value: %s" % activity_factor)


################################################################################
# Nutrient IDs
################################################################################
NUTR_ID_KCAL = 208

NUTR_ID_PROTEIN = 203

NUTR_ID_CARBS = 205
NUTR_ID_SUGAR = 269
NUTR_ID_FIBER = 291

NUTR_ID_FAT_TOT = 204
NUTR_ID_FAT_SAT = 606
NUTR_ID_FAT_MONO = 645
NUTR_ID_FAT_POLY = 646

NUTR_IDS_FLAVONES = [
    710,
    711,
    712,
    713,
    714,
    715,
    716,
    734,
    735,
    736,
    737,
    738,
    731,
    740,
    741,
    742,
    743,
    745,
    749,
    750,
    751,
    752,
    753,
    755,
    756,
    758,
    759,
    762,
    770,
    773,
    785,
    786,
    788,
    789,
    791,
    792,
    793,
    794,
]

NUTR_IDS_AMINOS = [
    501,
    502,
    503,
    504,
    505,
    506,
    507,
    508,
    509,
    510,
    511,
    512,
    513,
    514,
    515,
    516,
    517,
    518,
    521,
]
