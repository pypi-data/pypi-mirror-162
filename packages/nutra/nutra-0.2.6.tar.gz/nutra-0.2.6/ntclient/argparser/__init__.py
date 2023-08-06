# -*- coding: utf-8 -*-
"""
Created on Tue May 25 13:08:55 2021 -0400

@author: shane
Main module for things related to argparse
"""
import argparse

from ntclient.argparser import funcs as parser_funcs
from ntclient.argparser import types


# noinspection PyUnresolvedReferences,PyProtectedMember
def build_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Attaches subcommands to main parser"""

    build_init_subcommand(subparsers)
    build_nt_subcommand(subparsers)
    build_search_subcommand(subparsers)
    build_sort_subcommand(subparsers)
    build_analyze_subcommand(subparsers)
    build_day_subcommand(subparsers)
    build_recipe_subcommand(subparsers)
    build_calc_subcommand(subparsers)


################################################################################
# Methods to build subparsers, and attach back to main arg_parser
################################################################################
# noinspection PyUnresolvedReferences,PyProtectedMember
def build_init_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Self running init command"""

    init_parser = subparsers.add_parser(
        "init", help="setup profiles, USDA and NT database"
    )
    init_parser.add_argument(
        "-y",
        dest="yes",
        action="store_true",
        help="automatically agree to (potentially slow) USDA download",
    )
    init_parser.set_defaults(func=parser_funcs.init)


# noinspection PyUnresolvedReferences,PyProtectedMember
def build_nt_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Lists out nutrients details with computed totals and averages"""

    nutrient_parser = subparsers.add_parser(
        "nt", help="list out nutrients and their info"
    )
    nutrient_parser.set_defaults(func=parser_funcs.nutrients)


# noinspection PyUnresolvedReferences,PyProtectedMember
def build_search_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Search: terms [terms ... ]"""

    search_parser = subparsers.add_parser(
        "search", help="search foods by name, list overview info"
    )
    search_parser.add_argument(
        "terms",
        nargs="+",
        help='search query, e.g. "grass fed beef" or "ultraviolet mushrooms"',
    )
    search_parser.add_argument(
        "-t",
        dest="top",
        metavar="N",
        type=int,
        help="show top N results (defaults to console height)",
    )
    search_parser.add_argument(
        "-g",
        dest="fdgrp_id",
        type=int,
        help="filter by a specific food group ID",
    )
    search_parser.set_defaults(func=parser_funcs.search)


# noinspection PyUnresolvedReferences,PyProtectedMember
def build_sort_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Sort foods ranked by nutr_id, per 100g or 200kcal"""

    sort_parser = subparsers.add_parser("sort", help="sort foods by nutrient ID")

    sort_parser.add_argument(
        "-c",
        dest="kcal",
        action="store_true",
        help="sort by value per 200 kcal, instead of per 100 g",
    )
    sort_parser.add_argument(
        "-t",
        dest="top",
        metavar="N",
        type=int,
        help="show top N results (defaults to console height)",
    )
    sort_parser.add_argument("nutr_id", type=int)
    sort_parser.set_defaults(func=parser_funcs.sort)


# noinspection PyUnresolvedReferences,PyProtectedMember
def build_analyze_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Analyzes (foods only for now)"""

    analyze_parser = subparsers.add_parser("anl", help="analyze food(s)")

    analyze_parser.add_argument(
        "-g",
        dest="grams",
        type=float,
        help="scale to custom number of grams (default is 100g)",
    )
    analyze_parser.add_argument("food_id", type=int, nargs="+")
    analyze_parser.set_defaults(func=parser_funcs.analyze)


# noinspection PyUnresolvedReferences,PyProtectedMember
def build_day_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Analyzes a DAY.csv, uses new colored progress bar spec"""

    day_parser = subparsers.add_parser(
        "day", help="analyze a DAY.csv file, RDAs optional"
    )
    day_parser.add_argument(
        "food_log",
        metavar="food_log.csv",
        nargs="+",
        type=types.file_or_dir_path,
        help="path to CSV file of food log",
    )
    day_parser.add_argument(
        "-r",
        dest="rda",
        metavar="rda.csv",
        type=types.file_path,
        help="provide a custom RDA file in csv format",
    )
    day_parser.set_defaults(func=parser_funcs.day)


# noinspection PyUnresolvedReferences,PyProtectedMember
def build_recipe_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """View, add, edit, delete recipes"""

    recipe_parser = subparsers.add_parser("recipe", help="list and analyze recipes")
    recipe_parser.set_defaults(func=parser_funcs.recipes)

    recipe_subparsers = recipe_parser.add_subparsers(title="recipe subcommands")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Init
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    recipe_init_parser = recipe_subparsers.add_parser(
        "init", help="create recipe folder, copy stock data in"
    )
    recipe_init_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="forcibly remove and re-copy stock/core data",
    )
    recipe_init_parser.set_defaults(func=parser_funcs.recipes_init)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Analyze
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # TODO: tab-completion for not just cwd, but also inject for RECIPE_HOME
    # TODO: support analysis for multiple file path(s) in one call
    recipe_anl_parser = recipe_subparsers.add_parser(
        "anl", help="view and analyze for recipe"
    )
    recipe_anl_parser.add_argument(
        "path", type=str, help="view (and analyze) recipe by file path"
    )
    recipe_anl_parser.set_defaults(func=parser_funcs.recipe)


# noinspection PyUnresolvedReferences,PyProtectedMember
def build_calc_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """BMR, 1 rep-max, and other calculators"""

    calc_parser = subparsers.add_parser(
        "calc", help="calculate 1-rep max, body fat, BMR, etc."
    )

    calc_subparsers = calc_parser.add_subparsers(title="recipe subcommands")
    calc_parser.set_defaults(func=calc_parser.print_help)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # 1-rep max
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    calc_1rm_parser = calc_subparsers.add_parser(
        "1rm", help="calculate 1 rep maxes, by different equations"
    )
    calc_1rm_parser.add_argument("weight", type=float, help="weight (lbs or kg)")
    calc_1rm_parser.add_argument("reps", type=int, help="number of reps performed")
    calc_1rm_parser.set_defaults(func=parser_funcs.calc_1rm)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # BMR
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    calc_bmr_parser = calc_subparsers.add_parser(
        "bmr", help="calculate BMR and TDEE values"
    )
    calc_bmr_parser.add_argument(
        "-F", dest="female_gender", action="store_true", help="Female gender"
    )
    # TODO: optional (union) with age / dob
    calc_bmr_parser.add_argument("-a", type=str, dest="age", help="e.g. 95")
    calc_bmr_parser.add_argument("-ht", type=float, dest="height", help="height (cm)")
    calc_bmr_parser.add_argument("-bf", dest="body_fat", type=float, help="e.g. 0.16")
    calc_bmr_parser.add_argument(
        "-wt", dest="weight", type=float, required=True, help="weight (kg)"
    )
    calc_bmr_parser.add_argument(
        "-x",
        type=int,
        dest="activity_factor",
        required=True,
        help="1 thru 5, sedentary thru intense",
    )
    calc_bmr_parser.set_defaults(func=parser_funcs.calc_bmr)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Body fat
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    calc_bf_parser = calc_subparsers.add_parser(
        "bf",
        help="calculate body fat %% with Navy, 3-Site, 7-Site",
    )
    calc_bf_parser.add_argument(
        "-F", dest="female_gender", action="store_true", help="Female gender"
    )
    calc_bf_parser.add_argument(
        "-a", type=int, dest="age", help="e.g. 95 [3-Site & 7-Site]"
    )
    calc_bf_parser.add_argument(
        "-ht", type=float, dest="height", help="height (cm) [Navy]"
    )

    calc_bf_parser.add_argument(
        "-w", type=float, dest="waist", help="waist (cm) [Navy]"
    )
    calc_bf_parser.add_argument("-n", type=float, dest="neck", help="neck (cm) [Navy]")
    calc_bf_parser.add_argument(
        "-hip", type=float, dest="hip", help="hip (cm) [Navy / FEMALE only]"
    )

    calc_bf_parser.add_argument(
        "chest",
        type=int,
        nargs="?",
        help="pectoral (mm) -[3-Site skin caliper measurement]",
    )
    calc_bf_parser.add_argument(
        "abd",
        type=int,
        nargs="?",
        help="abdominal (mm) [3-Site skin caliper measurement]",
    )
    calc_bf_parser.add_argument(
        "thigh",
        type=int,
        nargs="?",
        help="thigh (mm) --- [3-Site skin caliper measurement]",
    )
    calc_bf_parser.add_argument(
        "tricep",
        type=int,
        nargs="?",
        help="triceps (mm) - [7-Site skin caliper measurement]",
    )
    calc_bf_parser.add_argument(
        "sub",
        type=int,
        nargs="?",
        help="sub (mm) ----- [7-Site skin caliper measurement]",
    )
    calc_bf_parser.add_argument(
        "sup",
        type=int,
        nargs="?",
        help="sup (mm) ----- [7-Site skin caliper measurement]",
    )
    calc_bf_parser.add_argument(
        "mid",
        type=int,
        nargs="?",
        help="mid (mm) ----- [7-Site skin caliper measurement]",
    )
    calc_bf_parser.set_defaults(func=parser_funcs.calc_body_fat)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Lean body limits (young male)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    calc_lbl_parser = calc_subparsers.add_parser(
        "lbl", help="lean body limits (young, male)"
    )
    calc_lbl_parser.add_argument("height", type=float, help="height (cm)")
    calc_lbl_parser.add_argument(
        "desired_bf",
        type=float,
        nargs="?",
        help="e.g. 0.12 -[eric_helms & casey_butt]",
    )
    calc_lbl_parser.add_argument(
        "wrist", type=float, nargs="?", help="wrist (cm) [casey_butt]"
    )
    calc_lbl_parser.add_argument(
        "ankle", type=float, nargs="?", help="ankle (cm) [casey_butt]"
    )
    calc_lbl_parser.set_defaults(func=parser_funcs.calc_lbm_limits)
