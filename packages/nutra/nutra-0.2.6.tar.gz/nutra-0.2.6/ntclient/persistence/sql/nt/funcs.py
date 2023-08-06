"""nt.sqlite3 functions module"""
from ntclient.persistence.sql.nt import sql


def sql_nt_next_index(table: str) -> int:
    """Used for previewing inserts"""
    # noinspection SqlResolve
    query = "SELECT MAX(id) as max_id FROM %s;" % table  # nosec: B608
    return int(sql(query)[0]["max_id"])
