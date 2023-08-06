# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 09:28:33 2022

@author: shane
"""
import unittest

import pytest

from ntclient.services.recipe import RECIPE_STOCK
from ntclient.utils import tree


class TestTree(unittest.TestCase):
    """Try to test remaining bits of tree.py"""

    def test_tree_main(self):
        """Tests the main function (mostly a command line utility) for tree.py"""
        with pytest.raises(FileNotFoundError):
            tree.main_tree()

    def test_tree_main_with_args(self):
        """Tests the main function (mostly a command line utility) for tree.py"""
        exit_code = tree.main_tree(_args=["tree.py", RECIPE_STOCK])
        assert exit_code == 0
