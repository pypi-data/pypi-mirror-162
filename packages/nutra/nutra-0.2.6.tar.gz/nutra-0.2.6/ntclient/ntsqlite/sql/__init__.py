#!/usr/bin/env python3
"""Main module for building nt.sqlite3"""

import csv
import os
import sqlite3

NT_DB_NAME = "nt.sqlite3"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DATA_DIR = os.path.join(SCRIPT_DIR, "data")


def build_ntsqlite(verbose: bool = False) -> bool:
    """Builds and inserts stock data into nt.sqlite3"""
    # cd into this script's directory
    os.chdir(SCRIPT_DIR)

    if verbose:
        print("Cleanup...")
    if os.path.isfile(NT_DB_NAME):
        os.remove(NT_DB_NAME)

    if verbose:
        # pylint: disable=consider-using-f-string
        print("\nPack %s" % NT_DB_NAME)
    con = sqlite3.connect(NT_DB_NAME)
    cur = con.cursor()

    if verbose:
        print("\n-> Create tables")
    with open("tables.sql", encoding="utf-8") as tables:
        cur.executescript(tables.read())

    if verbose:
        print("-> Populate data")
    for file_path in os.listdir(CSV_DATA_DIR):
        if not file_path.endswith(".csv"):
            continue
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        file_path_full = os.path.join("data", file_path)
        # print(table_name)

        # Loop over CSV files
        with open(file_path_full, encoding="utf-8") as csv_file:
            dict_reader = csv.DictReader(csv_file)
            values = ",".join("?" * len(dict_reader.fieldnames or []))
            reader = csv.reader(csv_file)
            # pylint: disable=consider-using-f-string
            query = "INSERT INTO {0} VALUES ({1});".format(  # nosec: B608
                table_name, values
            )
            # print(query)
            # exit()
            cur.executemany(query, reader)

    cur.close()
    con.commit()
    con.close()
    if verbose:
        print("\nDone!")
    return True


if __name__ == "__main__":
    build_ntsqlite(verbose=True)
