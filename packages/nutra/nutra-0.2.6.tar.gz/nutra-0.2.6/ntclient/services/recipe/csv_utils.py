# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 15:33:57 2022

@author: shane
CSV utilities for reading and processing recipes.

TODO: copy to & cache in sqlite3, only look to CSV if it doesn't exist?
 Well then what if they edit CSV... gah.
"""
import glob

from ntclient.services.recipe import RECIPE_HOME
from ntclient.utils import tree


def csv_files() -> list:
    """Returns full filenames for everything under RECIPE_HOME'"""
    return glob.glob(RECIPE_HOME + "/**/*.csv", recursive=True)


def csv_recipe_print_tree() -> None:
    """Print off the recipe tree"""
    tree.print_dir(RECIPE_HOME)


def csv_print_details() -> None:
    """Print off details (as table)"""
    print("Not implemented!")


def csv_recipes() -> tuple:
    """
    Return overview & analysis of a selected recipe
    TODO: separate methods to search by uuid OR file_name
    """
    _csv_files = csv_files()
    print(_csv_files)
    return tuple(_csv_files)
