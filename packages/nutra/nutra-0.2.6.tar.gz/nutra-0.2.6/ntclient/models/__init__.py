# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 15:34:07 2022

@author: shane
Classes, structures for storing, displaying, and editing data.
"""
import csv

from ntclient import CLI_CONFIG


class Recipe:
    """Allows reading up CSV, filtering by UUID, and displaying detail view"""

    def __init__(self, file_path: str) -> None:
        """Initialize entity"""

        self.file_path = file_path
        self.csv_reader = csv.DictReader(str())

        # Defined now, populated later
        self.headers = tuple()  # type: ignore
        self.rows = tuple()  # type: ignore

        self.uuid = str()

        self.food_data = {}  # type: ignore

    def process_data(self) -> None:
        """
        Parses out the raw CSV input read in during self.__init__()
        TODO: test this with an empty CSV file
        @todo: CliConfig class, to avoid these non top-level import shenanigans
        """

        # Read into memory
        print("Processing recipe file: %s" % self.file_path)
        with open(self.file_path, "r", encoding="utf-8") as _file:
            self.csv_reader = csv.DictReader(_file)
            self.rows = tuple(self.csv_reader)

        # Validate data
        uuids = {x["recipe_id"] for x in self.rows}
        if len(uuids) != 1:
            print("Found %s keys: %s" % (len(uuids), uuids))
            raise KeyError("FATAL: must have exactly 1 uuid per recipe CSV file!")
        self.uuid = list(uuids)[0]

        # exc: ValueError (could not cast int / float)
        self.food_data = {int(x["food_id"]): float(x["grams"]) for x in self.rows}

        if CLI_CONFIG.debug:
            print("Finished with recipe.")

    def print_analysis(self) -> None:
        """Run analysis on a single recipe"""
