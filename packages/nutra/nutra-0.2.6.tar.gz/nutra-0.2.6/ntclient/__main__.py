# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
"""
Main module which is called by scripts.
Top-level argument parsing logic; error handling.

Created on Fri Jan 31 16:02:19 2020

@author: shane
"""
import argparse
import time
from urllib.error import HTTPError, URLError

import argcomplete

from ntclient import (
    CLI_CONFIG,
    __db_target_nt__,
    __db_target_usda__,
    __email__,
    __title__,
    __url__,
    __version__,
)
from ntclient.argparser import build_subcommands
from ntclient.utils.exceptions import SqlException


def build_arg_parser() -> argparse.ArgumentParser:
    """Adds all subparsers and parsing logic"""

    arg_parser = argparse.ArgumentParser(prog=__title__)
    arg_parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="{0} cli version {1} ".format(__title__, __version__)
        + "[DB usda v{0}, nt v{1}]".format(__db_target_usda__, __db_target_nt__),
    )

    arg_parser.add_argument(
        "-d", "--debug", action="store_true", help="enable detailed error messages"
    )
    arg_parser.add_argument(
        "--no-pager", action="store_true", help="disable paging (print full output)"
    )

    # Subparsers
    subparsers = arg_parser.add_subparsers(title="%s subcommands" % __title__)
    build_subcommands(subparsers)

    return arg_parser


def main(args: list = None) -> int:
    """
    Main method for CLI

    @param args: List[str]
    """

    start_time = time.time()
    arg_parser = build_arg_parser()
    argcomplete.autocomplete(arg_parser)

    def parse_args() -> argparse.Namespace:
        """Returns parsed args"""
        if args is None:
            return arg_parser.parse_args()
        return arg_parser.parse_args(args=args)

    def func(parser: argparse.Namespace) -> tuple:
        """Executes a function for a given argument call to the parser"""
        if hasattr(parser, "func"):
            # Print help for nested commands
            if parser.func.__name__ == "print_help":
                return 0, parser.func()

            # Collect non-default args
            args_dict = dict(vars(parser))
            for expected_arg in ["func", "debug", "no_pager"]:
                args_dict.pop(expected_arg)

            # Run function
            if args_dict:
                # Make sure the parser.func() always returns: Tuple[Int, Any]
                return parser.func(args=parser)  # type: ignore
            return parser.func()  # type: ignore

        # Otherwise print help
        arg_parser.print_help()
        return 0, None

    # Build the parser, set flags
    _parser = parse_args()
    CLI_CONFIG.set_flags(_parser)

    # Try to run the function
    exit_code = 1
    try:
        exit_code, *_results = func(_parser)
    except SqlException as sql_exception:
        print("Issue with an sqlite database: " + repr(sql_exception))
        if CLI_CONFIG.debug:
            raise
    except HTTPError as http_error:
        err_msg = "{0}: {1}".format(http_error.code, repr(http_error))
        print("Server response error, try again: " + err_msg)
        if CLI_CONFIG.debug:
            raise
    except URLError as url_error:
        print("Connection error, check your internet: " + repr(url_error.reason))
        if CLI_CONFIG.debug:
            raise
    except Exception as exception:  # pylint: disable=broad-except
        print("Unforeseen error, run with -d for more info: " + repr(exception))
        print("You can open an issue here: %s" % __url__)
        print("Or send me an email with the debug output: %s" % __email__)
        if CLI_CONFIG.debug:
            raise
    finally:
        if CLI_CONFIG.debug:
            exc_time = time.time() - start_time
            print("\nExecuted in: %s ms" % round(exc_time * 1000, 1))
            print("Exit code: %s" % exit_code)

    return exit_code
