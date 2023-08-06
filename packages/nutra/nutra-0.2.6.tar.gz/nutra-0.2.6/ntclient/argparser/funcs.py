# -*- coding: utf-8 -*-
"""
Current home to subparsers and service-level logic.
These functions all return a tuple of (exit_code: int, results: list|dict).

Created on Sat Jul 18 16:30:28 2020 -0400

@author: shane
"""
import argparse
import os
import traceback

from tabulate import tabulate

import ntclient.services.analyze
import ntclient.services.recipe.utils
import ntclient.services.usda
from ntclient import CLI_CONFIG, Gender, activity_factor_from_index
from ntclient.services import calculate as calc


def init(args: argparse.Namespace) -> tuple:
    """Wrapper init method for persistence stuff"""
    return ntclient.services.init(yes=args.yes)


##############################################################################
# Nutrients, search and sort
##############################################################################
def nutrients() -> tuple:
    """List nutrients"""
    return ntclient.services.usda.list_nutrients()


def search(args: argparse.Namespace) -> tuple:
    """Searches all dbs, foods, recipes, recent items and favorites."""
    if args.top:
        return ntclient.services.usda.search(
            words=args.terms, fdgrp_id=args.fdgrp_id, limit=args.top
        )
    return ntclient.services.usda.search(words=args.terms, fdgrp_id=args.fdgrp_id)


def sort(args: argparse.Namespace) -> tuple:
    """Sorts based on nutrient id"""
    if args.top:
        return ntclient.services.usda.sort_foods(
            args.nutr_id, by_kcal=args.kcal, limit=args.top
        )
    return ntclient.services.usda.sort_foods(args.nutr_id, by_kcal=args.kcal)


##############################################################################
# Analysis and Day scoring
##############################################################################
def analyze(args: argparse.Namespace) -> tuple:
    """Analyze a food"""
    # exc: ValueError,
    food_ids = set(args.food_id)
    grams = float(args.grams) if args.grams else 0.0

    return ntclient.services.analyze.foods_analyze(food_ids, grams)


def day(args: argparse.Namespace) -> tuple:
    """Analyze a day's worth of meals"""
    day_csv_paths = [str(os.path.expanduser(x)) for x in args.food_log]
    rda_csv_path = str(os.path.expanduser(args.rda)) if args.rda else str()

    return ntclient.services.analyze.day_analyze(
        day_csv_paths, rda_csv_path=rda_csv_path
    )


##############################################################################
# Recipes
##############################################################################
def recipes_init(args: argparse.Namespace) -> tuple:
    """Copy example/stock data into RECIPE_HOME"""
    _force = args.force

    return ntclient.services.recipe.utils.recipes_init(_force=_force)


def recipes() -> tuple:
    """Show all, in tree or detail view"""
    return ntclient.services.recipe.utils.recipes_overview()


def recipe(args: argparse.Namespace) -> tuple:
    """
    View and analyze a single (or a range)
    @todo: argcomplete based on RECIPE_HOME folder
    @todo: use as default command? Currently this is reached by `nutra recipe anl`
    """
    recipe_path = args.path

    return ntclient.services.recipe.utils.recipe_overview(recipe_path=recipe_path)


##############################################################################
# Calculators
##############################################################################
def calc_1rm(args: argparse.Namespace) -> tuple:
    """Perform 1-rep max calculations"""

    weight = float(args.weight)
    print("Weight: %s" % weight)
    reps = int(args.reps)
    print("Reps:   %s" % reps)

    if weight < 0:
        print("ERROR: weight must be greater than zero")
        return 1, None
    if reps < 1 or reps > 20:
        print("ERROR: reps must be between 1 and 20")
        return 1, None

    _epley = calc.orm_epley(weight, reps)
    _brzycki = calc.orm_brzycki(weight, reps)
    _dos_remedios = calc.orm_dos_remedios(weight, reps)

    result = {"epley": _epley, "brzycki": _brzycki, "dos_remedios": _dos_remedios}

    # TODO: fourth column: average or `avg` column too.
    # Prepare table rows, to display all 3 results in one table
    _all = []
    for _rep in _epley.keys():
        row = [_rep]
        for _calc, _values in result.items():
            # Round down for now
            row.append(int(_values[_rep]))
        _all.append(row)

    # Print results
    print()
    print("Results for: epley, brzycki, and dos_remedios")
    print()
    _table = tabulate(_all, headers=["n", "epl", "brz", "rmds"])
    print(_table)

    return 0, result


def calc_bmr(args: argparse.Namespace) -> tuple:
    """
    Perform BMR & TDEE calculations

    Example POST:
    {
        "weight": 71,
        "height": 177,
        "gender": "MALE",
        "dob": 725864400,
        "bodyFat": 0.14,
        "activityFactor": 0.55
    }
    """

    activity_factor = activity_factor_from_index(args.activity_factor)
    print("Activity factor: %s" % activity_factor)
    weight = float(args.weight)  # kg
    print("Weight: %s kg" % weight)

    # TODO: require these all for any? Or do exception handling & optional args like bf?
    try:
        _katch_mcardle = calc.bmr_katch_mcardle(activity_factor, weight, args=args)
    except (KeyError, TypeError, ValueError):
        _katch_mcardle = {
            "errMsg": "Katch McArdle failed, requires: "
            "activity_factor, weight, body_fat."
        }
    try:
        _cunningham = calc.bmr_cunningham(activity_factor, weight, args=args)
    except (KeyError, TypeError, ValueError):
        _cunningham = {
            "errMsg": "Cunningham failed, requires: activity_factor, weight, body_fat."
        }
    try:
        _mifflin_st_jeor = calc.bmr_mifflin_st_jeor(activity_factor, weight, args=args)
    except (KeyError, TypeError, ValueError):
        _mifflin_st_jeor = {
            "errMsg": "Mifflin St Jeor failed, requires: "
            "activity_factor, weight, gender, height, & age."
        }
    try:
        _harris_benedict = calc.bmr_harris_benedict(activity_factor, weight, args=args)
    except (KeyError, TypeError, ValueError):
        _harris_benedict = {
            "errMsg": "Harris Benedict failed, requires: "
            "activity_factor, weight, gender, height, & age."
        }

    result = {
        "katch_mcardle": _katch_mcardle,
        "cunningham": _cunningham,
        "mifflin_st_jeor": _mifflin_st_jeor,
        "harris_benedict": _harris_benedict,
    }

    # Prepare the table for printing
    headers = ("Equation", "BMR", "TDEE")
    rows = []
    for _equation, _calculation in result.items():
        row = [_equation]
        row.extend(_calculation.values())
        rows.append(row)

    _katch_mcardle_table = tabulate(rows, headers=headers, tablefmt="simple")
    print(_katch_mcardle_table)

    return 0, result


def calc_body_fat(args: argparse.Namespace) -> tuple:
    """
    Perform body fat calculations for Navy, 3-Site, and 7-Site.

    Example POST. @note FEMALE, also includes "hip" (cm)
    {
        "gender": "MALE",
        "age": 29,
        "height": 178,
        "waist": 80,
        "neck": 36.8,
        // also: hip, if FEMALE
        "chest": 5,
        "abd": 6,
        "thigh": 9,
        "tricep": 6,
        "sub": 8,
        "sup": 7,
        "mid": 4
    }
    """

    gender = Gender.FEMALE if args.female_gender else Gender.MALE
    print("Gender: %s" % gender)
    try:
        _navy = calc.bf_navy(gender, args)
    except (TypeError, ValueError):
        print()
        if CLI_CONFIG.debug:
            traceback.print_exc()
        print(
            "WARN: Navy failed, requires: gender, height, waist, neck, "
            "and (if female) hip."
        )
        _navy = 0.0
    try:
        _3site = calc.bf_3site(gender, args)
    except (TypeError, ValueError):
        print()
        if CLI_CONFIG.debug:
            traceback.print_exc()
        print(
            "WARN: 3-Site failed, requires: gender, age, chest (mm), "
            "abdominal (mm), and thigh (mm)."
        )
        _3site = 0.0
    try:
        _7site = calc.bf_7site(gender, args)
    except (TypeError, ValueError):
        print()
        if CLI_CONFIG.debug:
            traceback.print_exc()
        print(
            "WARN: 7-Site failed, requires: gender, age, chest (mm), "
            "abdominal (mm), thigh (mm), tricep (mm), sub (mm), sup (mm), and mid (mm)."
        )
        _7site = 0.0

    _table = tabulate([(_navy, _3site, _7site)], headers=["Navy", "3-Site", "7-Site"])
    print()
    print()
    print(_table)

    return 0, {"navy": _navy, "threeSite": _3site, "sevenSite": _7site}


def calc_lbm_limits(args: argparse.Namespace) -> tuple:
    """
    Perform body fat calculations for Navy, 3-Site, and 7-Site.

    Example POST.
    {
        "height": 179,
        "desired-bf": 0.12,
        "wrist": 17.2,
        "ankle": 21.5
    }
    """

    height = float(args.height)

    # Perform calculations & handle errors
    _berkhan = calc.lbl_berkhan(height)
    _eric_helms = calc.lbl_eric_helms(height, args)
    _casey_butt = calc.lbl_casey_butt(height, args)

    result = {"berkhan": _berkhan, "helms": _eric_helms, "casey": _casey_butt}

    headers = [
        "eq",
        "condition",
        "weight",
        "lbm",
        "chest",
        "arm",
        "forearm",
        "neck",
        "thigh",
        "calf",
    ]
    rows = []
    for _calc, _result in result.items():
        _values = list(_result.values())
        row = [_calc]
        row.extend(_values)
        while len(row) < len(headers):
            row.append(str())
        rows.append(row)

    _table = tabulate(rows, headers=headers, tablefmt="pretty")
    print(_table)

    return 0, result
