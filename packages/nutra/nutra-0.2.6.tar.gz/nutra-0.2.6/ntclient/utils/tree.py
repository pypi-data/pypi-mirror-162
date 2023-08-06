"""Python 3 re-implementation of the Linux 'tree' utility"""

import os
import sys

from ntclient.utils import colors

chars = {"nw": "\u2514", "nws": "\u251c", "ew": "\u2500", "ns": "\u2502"}

strs = [
    chars["ns"] + "   ",
    chars["nws"] + chars["ew"] * 2 + " ",
    chars["nw"] + chars["ew"] * 2 + " ",
    "    ",
]

# Colors and termination strings
COLOR_DIR = colors.STYLE_BRIGHT + colors.COLOR_BLUE
COLOR_EXEC = colors.STYLE_BRIGHT + colors.COLOR_GREEN
COLOR_LINK = colors.STYLE_BRIGHT + colors.COLOR_CYAN
COLOR_DEAD_LINK = colors.STYLE_BRIGHT + colors.COLOR_RED


def colorize(path: str, full: bool = False) -> str:
    """Returns string with color / bold"""
    file = path if full else os.path.basename(path)

    if os.path.islink(path):
        return "".join(
            [
                COLOR_LINK,
                file,
                colors.STYLE_RESET_ALL,
                " -> ",
                colorize(os.readlink(path), full=True),
            ]
        )

    if os.path.isdir(path):
        return "".join([COLOR_DIR, file, colors.STYLE_RESET_ALL])

    if os.access(path, os.X_OK):
        return "".join([COLOR_EXEC, file, colors.STYLE_RESET_ALL])

    return file


# Tree properties - display / print
SHOW_HIDDEN = False
SHOW_SIZE = False
FOLLOW_SYMLINKS = False


def print_dir(_dir: str, pre: str = str()) -> tuple:
    """
    Prints the whole tree

    TODO: integrate with data sources to display more than just filenames
    TODO: hide non-CSV files, and don't show *.csv extension (just file name)
    """
    n_dirs = 0
    n_files = 0
    n_size = 0

    if not pre:
        print(COLOR_DIR + _dir + colors.STYLE_RESET_ALL)

    dir_len = len(os.listdir(_dir)) - 1
    for i, file in enumerate(sorted(os.listdir(_dir), key=str.lower)):
        path = os.path.join(_dir, file)
        if file.startswith(".") and not SHOW_HIDDEN:
            continue
        if os.path.isdir(path):
            print(pre + strs[2 if i == dir_len else 1] + colorize(path))
            if os.path.islink(path):
                n_dirs += 1
            else:
                n_d, n_f, n_s = print_dir(path, pre + strs[3 if i == dir_len else 0])
                n_dirs += n_d + 1
                n_files += n_f
                n_size += n_s
        else:
            n_files += 1
            n_size += os.path.getsize(path)
            print(
                pre
                + strs[2 if i == dir_len else 1]
                + ("[{:>11}]  ".format(n_size) if SHOW_SIZE else "")
                + colorize(path)
            )

    # noinspection PyRedundantParentheses
    return (n_dirs, n_files, n_size)


def main_tree(_args: list = None) -> int:
    """Handle input arguments, print off tree"""
    n_dirs = 0
    n_files = 0

    if not _args:
        _args = sys.argv

    if len(_args) == 1:
        # Used for development
        n_dirs, n_files, _size = print_dir("../resources")
    else:
        for _dir in _args[1:]:
            n_d, n_f, _size = print_dir(_dir)
            n_dirs += n_d
            n_files += n_f

    print()
    print(
        "{} director{}, {} file{}".format(
            n_dirs, "ies" if n_dirs > 1 else "y", n_files, "s" if n_files > 1 else ""
        )
    )
    return 0
