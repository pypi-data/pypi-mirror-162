# -*- coding: utf-8 -*-
"""
Created on Sat Oct 27 20:28:06 2018

@author: shane
"""

import pydoc

from tabulate import tabulate

from ntclient import (
    CLI_CONFIG,
    DEFAULT_RESULT_LIMIT,
    DEFAULT_SEARCH_H_BUFFER,
    DEFAULT_SORT_H_BUFFER,
    NUTR_ID_KCAL,
    NUTR_IDS_AMINOS,
    NUTR_IDS_FLAVONES,
)
from ntclient.persistence.sql.usda.funcs import (
    sql_analyze_foods,
    sql_food_details,
    sql_nutrients_details,
    sql_nutrients_overview,
    sql_sort_helper1,
)


def list_nutrients() -> tuple:
    """Lists out nutrients with basic details"""

    headers, nutrients = sql_nutrients_details()
    # TODO: include in SQL table cache?
    headers.append("avg_rda")
    nutrients = [list(x) for x in nutrients]
    for nutrient in nutrients:
        rda = nutrient[1]
        val = nutrient[6]
        if rda:
            nutrient.append(round(100 * val / rda, 1))
        else:
            nutrient.append(None)

    table = tabulate(nutrients, headers=headers, tablefmt="simple")
    if CLI_CONFIG.paging:
        pydoc.pager(table)
    else:
        print(table)

    return 0, nutrients


################################################################################
# Sort
################################################################################
def sort_foods(
    nutrient_id: int, by_kcal: bool, limit: int = DEFAULT_RESULT_LIMIT
) -> tuple:
    """Sort, by nutrient, either (amount / 100 g) or (amount / 200 kcal)"""

    # TODO: sub shrt_desc for long if available, and support config.FOOD_NAME_TRUNC

    def print_results(_results: list, _nutrient_id: int) -> list:
        """Prints truncated list for sort"""
        nutrients = sql_nutrients_overview()
        nutrient = nutrients[_nutrient_id]
        unit = nutrient[2]

        val_header = "grams" if by_kcal else "kcal"
        headers = ["food", "fdgrp", "val (%s)" % unit, val_header, "long_desc"]

        table = tabulate(_results, headers=headers, tablefmt="simple")
        print(table)
        return _results

    # Gets values for nutrient_id and kcal=208
    nut_data = sql_sort_helper1(nutrient_id)

    # Assembles duplicate tuples into single dict entry
    food_dat = {}
    for food_id, nutr_id, nutr_val in nut_data:
        entry = nutr_id, nutr_val
        if food_id not in food_dat:
            food_dat[food_id] = [entry]
        else:
            food_dat[food_id].append(entry)

    # Builds main results list
    foods = []
    for food_id, _food in food_dat.items():
        kcal = None
        nutr_val = 0.0
        for _nutr_id, _nutr_val in _food:
            if _nutr_id == NUTR_ID_KCAL:
                kcal = _nutr_val
            else:
                nutr_val = _nutr_val
        food = [food_id, nutr_val, kcal]
        foods.append(food)
    if by_kcal is True:
        foods = list(filter(lambda x: x[2], foods))  # removes kcal = 0 case
        foods = list(
            map(
                lambda x: [x[0], round(x[1] * 200 / x[2], 2), round(200 / x[2] * 100)],
                foods,
            )
        )
    # Sort by nutr_val
    foods.sort(key=lambda x: int(x[1]), reverse=True)
    foods = foods[:limit]

    # Gets fdgrp and long_desc
    food_ids = {x[0] for x in foods}
    food_des = {x[0]: x for x in sql_food_details(food_ids)}
    for food in foods:
        food_id = food[0]
        fdgrp = food_des[food_id][1]
        long_desc = food_des[food_id][2]
        food.insert(1, fdgrp)
        food.append(long_desc[:DEFAULT_SORT_H_BUFFER])

    print_results(foods, nutrient_id)
    return 0, foods  # , nutrient_id


################################################################################
# Search
################################################################################
def search(words: list, fdgrp_id: int = 0, limit: int = DEFAULT_RESULT_LIMIT) -> tuple:
    """Searches foods for input"""

    def tabulate_search(_results: list) -> list:
        """Makes search results more readable"""
        # Current terminal size
        # TODO: display "nonzero/total" report nutrients, aminos, and flavones..
        #  sometimes zero values are not useful
        # TODO: macros, ANDI score, and other metrics on preview

        headers = [
            "food",
            "fdgrp",
            "kcal",
            "food_name",
            "Nutr",
            "Amino",
            "Flav",
        ]
        rows = []
        for i, result in enumerate(_results):
            if i == limit:
                break
            _food_id = result["food_id"]
            # TODO: dynamic buffer
            # food_name = r["long_desc"][:45]
            # food_name = r["long_desc"][:BUFFER_WD]
            food_name = result["long_desc"][:DEFAULT_SEARCH_H_BUFFER]
            # TODO: decide on food group description?
            # fdgrp_desc = r["fdgrp_desc"]
            fdgrp = result["fdgrp_id"]

            nutrients = result["nutrients"]
            kcal = nutrients.get(NUTR_ID_KCAL)
            len_aminos = len(
                [nutrients[n_id] for n_id in nutrients if int(n_id) in NUTR_IDS_AMINOS]
            )
            len_flavones = len(
                [
                    nutrients[n_id]
                    for n_id in nutrients
                    if int(n_id) in NUTR_IDS_FLAVONES
                ]
            )

            row = [
                _food_id,
                fdgrp,
                kcal,
                food_name,
                len(nutrients),
                len_aminos,
                len_flavones,
            ]
            rows.append(row)
            # avail_buffer = bufferwidth - len(food_id) - 15
            # if len(food_name) > avail_buffer:
            #     rows.append([food_id, food_name[:avail_buffer] + "..."])
            # else:
            #     rows.append([food_id, food_name])
        table = tabulate(rows, headers=headers, tablefmt="simple")
        print(table)
        return rows

    ###
    # MAIN SEARCH METHOD
    from fuzzywuzzy import fuzz  # pylint: disable=import-outside-toplevel

    food_des = sql_food_details()
    if fdgrp_id:
        food_des = list(filter(lambda x: x[1] == fdgrp_id, food_des))

    query = " ".join(words)
    _scores = {f[0]: fuzz.token_set_ratio(query, f[2]) for f in food_des}
    # NOTE: fuzzywuzzy reports score as an int, not float
    scores = sorted(_scores.items(), key=lambda x: int(x[1]), reverse=True)
    scores = scores[:limit]

    food_ids = {x[0] for x in scores}
    nut_data = sql_analyze_foods(food_ids)

    # Tally foods
    foods_nutrients = {}
    for food_id, nutr_id, nutr_val in nut_data:
        if food_id not in foods_nutrients:
            foods_nutrients[food_id] = {nutr_id: nutr_val}  # init dict
        else:
            foods_nutrients[food_id][nutr_id] = nutr_val

    def search_results(_scores: list) -> list:
        """
        Generates search results, consumable by tabulate

        @param _scores: List[tuple]
        @return: List[dict]
        """
        _results = []
        for score in _scores:
            _food_id = score[0]
            score = score[1]

            food = food_des_dict[_food_id]
            _fdgrp_id = food[1]
            long_desc = food[2]
            shrt_desc = food[3]

            nutrients = foods_nutrients[_food_id]
            result = {
                "food_id": _food_id,
                "fdgrp_id": _fdgrp_id,
                # TODO: get more details from another function,
                #  maybe enhance food_details() ? Is that useful tho?
                # "fdgrp_desc": cache.fdgrp[fdgrp_id]["fdgrp_desc"],
                # "data_src": cache.data_src[data_src_id]["name"],
                "long_desc": shrt_desc if shrt_desc else long_desc,
                "score": score,
                "nutrients": nutrients,
            }
            _results.append(result)
        return _results

    # TODO: include C/F/P macro ratios as column?
    # TODO: is this defined in the best place? It's accessed once in a helper function.
    food_des_dict = {f[0]: f for f in food_des}
    results = search_results(scores)

    tabulate_search(results)
    return 0, results
