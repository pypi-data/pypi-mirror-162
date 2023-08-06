"""Main SQL persistence module, shared between USDA and NT databases"""
import sqlite3
from collections.abc import Sequence

# ------------------------------------------------
# Entry fetching methods
# ------------------------------------------------
from ntclient import CLI_CONFIG


def sql_entries(sql_result: sqlite3.Cursor) -> list:
    """Formats and returns a `sql_result()` for console digestion and output"""
    # TODO: return object: metadata, command, status, errors, etc?

    rows = sql_result.fetchall()
    return rows


def sql_entries_headers(sql_result: sqlite3.Cursor) -> tuple:
    """Formats and returns a `sql_result()` for console digestion and output"""
    rows = sql_result.fetchall()
    headers = [x[0] for x in sql_result.description]

    return headers, rows


# ------------------------------------------------
# Supporting methods
# ------------------------------------------------
def version(con: sqlite3.Connection) -> str:
    """Gets the latest entry from version table"""

    cur = con.cursor()
    result = cur.execute("SELECT * FROM version;").fetchall()

    close_con_and_cur(con, cur, commit=False)
    return str(result[-1][1])


def close_con_and_cur(
    con: sqlite3.Connection, cur: sqlite3.Cursor, commit: bool = True
) -> None:
    """Cleans up, commits, and closes after an SQL command is run"""

    cur.close()
    if commit:
        con.commit()
    con.close()


# ------------------------------------------------
# Main query methods
# ------------------------------------------------
def _prep_query(
    con: sqlite3.Connection, query: str, db_name: str, values: Sequence = ()
) -> sqlite3.Cursor:
    """
    Run a query and return a cursor object ready for row extraction.
    @param con: sqlite3.Connection object
    @param query: query string, e.g. SELECT * FROM version;
    @param db_name: (nt | usda) database name [TODO: enum]
    @param values: (tuple | list)
        empty for bare queries, tuple for single, and list for many
    @return: A sqlite3.Cursor object with populated return values.
    """

    cur = con.cursor()

    if CLI_CONFIG.debug:
        print("%s.sqlite3: %s" % (db_name, query))
        if values:
            # TODO: better debug logging, more "control-findable",
            #  distinguish from most prints()
            print(values)

    # TODO: separate `entry` & `entries` entity for single vs. bulk insert?
    if values:
        if isinstance(values, list):
            cur.executemany(query, values)
        else:  # tuple
            cur.execute(query, values)
    else:
        cur.execute(query)

    return cur


def _sql(
    con: sqlite3.Connection,
    query: str,
    db_name: str,
    values: Sequence = (),
) -> list:
    """@param values: tuple | list"""

    cur = _prep_query(con, query, db_name, values)

    # TODO: print "<number> SELECTED", or other info
    #  BASED ON command SELECT/INSERT/DELETE/UPDATE
    result = sql_entries(cur)

    close_con_and_cur(con, cur)
    return result


def _sql_headers(
    con: sqlite3.Connection,
    query: str,
    db_name: str,
    values: Sequence = (),
) -> tuple:
    """@param values: tuple | list"""

    cur = _prep_query(con, query, db_name, values)

    result = sql_entries_headers(cur)

    close_con_and_cur(con, cur)
    return result
