# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 15:14:00 2020

@author: shane
"""
import os

from ntclient import NUTRA_HOME, PROJECT_ROOT

RECIPE_STOCK = os.path.join(PROJECT_ROOT, "resources", "recipe")

_RECIPE_SUB_PATH = "recipe"
RECIPE_HOME = os.path.join(NUTRA_HOME, _RECIPE_SUB_PATH)
