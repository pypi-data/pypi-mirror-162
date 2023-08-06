"""Nutratracker DB specific sqlite module"""
import os
import sqlite3
from collections.abc import Sequence

from ntclient import (
    NT_DB_NAME,
    NTSQLITE_BUILDPATH,
    NTSQLITE_DESTINATION,
    NUTRA_HOME,
    __db_target_nt__,
)
from ntclient.persistence.sql import _sql, _sql_headers, version
from ntclient.utils.exceptions import SqlConnectError, SqlInvalidVersionError


def nt_ver() -> str:
    """Gets version string for nt.sqlite3 database"""

    con = nt_sqlite_connect(version_check=False)
    return version(con)


def nt_init() -> None:
    """
    Similar to usda_init(). This builds the nt.sqlite3 image, and copies into ~/.nutra
    """

    # TODO: don't overwrite,
    #  verbose toggle for download,
    #  option to upgrade
    if os.path.isfile(NTSQLITE_DESTINATION):
        if nt_ver() != __db_target_nt__:
            # TODO: hard requirement? raise error?
            print(
                "WARN: upgrades/downgrades not supported "
                + "(actual: {0} vs. target: {1}), ".format(nt_ver(), __db_target_nt__)
                + "please remove `~/.nutra/nt.sqlite3` file or ignore this warning"
            )
        print("..DONE!")
        os.remove(NTSQLITE_BUILDPATH)  # clean up
    else:
        # TODO: is this logic (and these error messages) the best?
        #  what if .isdir() == True ? Fails with stacktrace?
        os.rename(NTSQLITE_BUILDPATH, NTSQLITE_DESTINATION)
        if nt_ver() != __db_target_nt__:
            raise SqlInvalidVersionError(
                "ERROR: nt target [{0}] mismatch actual [{1}], ".format(
                    __db_target_nt__, nt_ver()
                )
                + ", please contact support or try again"
            )
        print("..DONE!")


# ------------------------------------------------
# SQL connection & utility methods
# ------------------------------------------------
def nt_sqlite_connect(version_check: bool = True) -> sqlite3.Connection:
    """Connects to the nt.sqlite3 file, or throws an exception"""

    db_path = os.path.join(NUTRA_HOME, NT_DB_NAME)
    if os.path.isfile(db_path):
        con = sqlite3.connect(db_path)
        con.row_factory = sqlite3.Row

        # Verify version
        if version_check and nt_ver() != __db_target_nt__:
            raise SqlInvalidVersionError(
                "ERROR: nt target [{0}] mismatch actual [{1}] ".format(
                    __db_target_nt__, nt_ver()
                )
                + "upgrades not supported, please remove '~/.nutra/nt.sqlite3'"
                "and re-run 'nutra init'"
            )
        return con

    # Else it's not on disk
    raise SqlConnectError("ERROR: nt database doesn't exist, please run `nutra init`")


def sql(query: str, values: Sequence = ()) -> list:
    """Executes a SQL command to nt.sqlite3"""

    con = nt_sqlite_connect()
    return _sql(con, query, db_name="nt", values=values)


def sql_headers(query: str, values: Sequence = ()) -> tuple:
    """Executes a SQL command to nt.sqlite3"""

    con = nt_sqlite_connect()
    return _sql_headers(con, query, db_name="nt", values=values)
