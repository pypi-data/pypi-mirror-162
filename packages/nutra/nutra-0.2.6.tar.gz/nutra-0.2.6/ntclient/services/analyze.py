# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 23:57:03 2018

@author: shane
"""

import csv
from collections import OrderedDict

from tabulate import tabulate

from ntclient import (
    BUFFER_WD,
    CLI_CONFIG,
    NUTR_ID_CARBS,
    NUTR_ID_FAT_TOT,
    NUTR_ID_FIBER,
    NUTR_ID_KCAL,
    NUTR_ID_PROTEIN,
)
from ntclient.persistence.sql.usda.funcs import (
    sql_analyze_foods,
    sql_food_details,
    sql_nutrients_overview,
    sql_servings,
)


################################################################################
# Foods
################################################################################
def foods_analyze(food_ids: set, grams: float = 0) -> tuple:
    """
    Analyze a list of food_ids against stock RDA values
    TODO: from ntclient.utils.nutprogbar import nutprogbar
    TODO: support -t (tabular/non-visual) output flag
    """

    ################################################################################
    # Get analysis
    ################################################################################
    raw_analyses = sql_analyze_foods(food_ids)
    analyses = {}
    for analysis in raw_analyses:
        food_id = analysis[0]
        if grams:
            anl = (analysis[1], round(analysis[2] * grams / 100, 2))
        else:
            anl = (analysis[1], analysis[2])
        if food_id not in analyses:
            analyses[food_id] = [anl]
        else:
            analyses[food_id].append(anl)

    serving = sql_servings(food_ids)
    food_des_rows = sql_food_details(food_ids)
    food_des = {x[0]: x for x in food_des_rows}
    nutrients = sql_nutrients_overview()
    rdas = {x[0]: x[1] for x in nutrients.values()}

    ################################################################################
    # Food-by-food analysis (w/ servings)
    ################################################################################
    servings_rows = []
    nutrients_rows = []
    for food_id, nut_val_tuples in analyses.items():
        food_name = food_des[food_id][2]
        print(
            "\n======================================\n"
            + "==> {0} ({1})\n".format(food_name, food_id)
            + "======================================\n"
        )
        print("\n=========================\nSERVINGS\n=========================\n")

        ################################################################################
        # Serving table
        ################################################################################
        headers = ["msre_id", "msre_desc", "grams"]
        serving_rows = [(x[1], x[2], x[3]) for x in serving if x[0] == food_id]
        # Print table
        servings_table = tabulate(serving_rows, headers=headers, tablefmt="presto")
        print(servings_table)
        servings_rows.append(serving_rows)

        refuse = next(
            ((x[7], x[8]) for x in food_des.values() if x[0] == food_id and x[7]), None
        )
        if refuse:
            print("\n=========================\nREFUSE\n=========================\n")
            print(refuse[0])
            print("    ({0}%, by mass)".format(refuse[1]))

        print("\n=========================\nNUTRITION\n=========================\n")

        ################################################################################
        # Nutrient table
        ################################################################################
        headers = ["id", "nutrient", "rda", "amount", "units"]
        nutrient_rows = []
        for nutrient_id, amount in nut_val_tuples:
            # Skip zero values
            if not amount:
                continue

            nutr_desc = nutrients[nutrient_id][4] or nutrients[nutrient_id][3]
            unit = nutrients[nutrient_id][2]

            # Insert RDA % into row
            if rdas[nutrient_id]:
                rda_perc = str(round(amount / rdas[nutrient_id] * 100, 1)) + "%"
            else:
                rda_perc = None
            row = [nutrient_id, nutr_desc, rda_perc, round(amount, 2), unit]

            nutrient_rows.append(row)

        ################################################################################
        # Print table
        ################################################################################
        table = tabulate(nutrient_rows, headers=headers, tablefmt="presto")
        print(table)
        nutrients_rows.append(nutrient_rows)

    return 0, nutrients_rows, servings_rows


################################################################################
# Day
################################################################################
def day_analyze(day_csv_paths: list, rda_csv_path: str = str()) -> tuple:
    """Analyze a day optionally with custom RDAs,
    e.g.  nutra day ~/.nutra/rocky.csv -r ~/.nutra/dog-rdas-18lbs.csv
    TODO: Should be a subset of foods_analyze
    """

    if rda_csv_path:
        with open(rda_csv_path, encoding="utf-8") as file_path:
            rda_csv_input = csv.DictReader(
                row for row in file_path if not row.startswith("#")
            )
            rdas = list(rda_csv_input)
    else:
        rdas = []

    logs = []
    food_ids = set()
    for day_csv_path in day_csv_paths:
        with open(day_csv_path, encoding="utf-8") as file_path:
            rows = [row for row in file_path if not row.startswith("#")]
            day_csv_input = csv.DictReader(rows)
            log = list(day_csv_input)
        for entry in log:
            if entry["id"]:
                food_ids.add(int(entry["id"]))
        logs.append(log)

    # Inject user RDAs
    nutrients_lists = [list(x) for x in sql_nutrients_overview().values()]
    for rda in rdas:
        nutrient_id = int(rda["id"])
        _rda = float(rda["rda"])
        for _nutrient in nutrients_lists:
            if _nutrient[0] == nutrient_id:
                _nutrient[1] = _rda
                if CLI_CONFIG.debug:
                    substr = "{0} {1}".format(_rda, _nutrient[2]).ljust(12)
                    print("INJECT RDA: {0} -->  {1}".format(substr, _nutrient[4]))
    nutrients = {x[0]: x for x in nutrients_lists}

    # Analyze foods
    foods_analysis = {}
    for food in sql_analyze_foods(food_ids):
        food_id = food[0]
        anl = food[1], food[2]
        if food_id not in foods_analysis:
            foods_analysis[food_id] = [anl]
        else:
            foods_analysis[food_id].append(anl)

    # Compute totals
    nutrients_totals = []
    for log in logs:
        nutrient_totals = OrderedDict()  # dict()/{} is NOT ORDERED before 3.6/3.7
        for entry in log:
            if entry["id"]:
                food_id = int(entry["id"])
                grams = float(entry["grams"])
                for _nutrient2 in foods_analysis[food_id]:
                    nutr_id = _nutrient2[0]
                    nutr_per_100g = _nutrient2[1]
                    nutr_val = grams / 100 * nutr_per_100g
                    if nutr_id not in nutrient_totals:
                        nutrient_totals[nutr_id] = nutr_val
                    else:
                        nutrient_totals[nutr_id] += nutr_val
        nutrients_totals.append(nutrient_totals)

    #######
    # Print
    buffer = BUFFER_WD - 4 if BUFFER_WD > 4 else BUFFER_WD
    for analysis in nutrients_totals:
        day_format(analysis, nutrients, buffer=buffer)
    return 0, nutrients_totals


# TODO: why not this...? nutrients: Mapping[int, tuple]
def day_format(analysis: dict, nutrients: dict, buffer: int = 0) -> None:
    """Formats day analysis for printing to console"""

    def print_header(header: str) -> None:
        print(CLI_CONFIG.color_default, end="")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("--> %s" % header)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(CLI_CONFIG.style_reset_all)

    def print_macro_bar(
        _fat: float, _net_carb: float, _pro: float, _kcals_max: float, _buffer: int = 0
    ) -> None:
        _kcals = fat * 9 + net_carb * 4 + _pro * 4

        p_fat = (_fat * 9) / _kcals
        p_car = (_net_carb * 4) / _kcals
        p_pro = (_pro * 4) / _kcals

        # TODO: handle rounding cases, tack on to, or trim off FROM LONGEST ?
        mult = _kcals / _kcals_max
        n_fat = round(p_fat * _buffer * mult)
        n_car = round(p_car * _buffer * mult)
        n_pro = round(p_pro * _buffer * mult)

        # Headers
        f_buf = " " * (n_fat // 2) + "Fat" + " " * (n_fat - n_fat // 2 - 3)
        c_buf = " " * (n_car // 2) + "Carbs" + " " * (n_car - n_car // 2 - 5)
        p_buf = " " * (n_pro // 2) + "Pro" + " " * (n_pro - n_pro // 2 - 3)
        print(
            "  "
            + CLI_CONFIG.color_yellow
            + f_buf
            + CLI_CONFIG.color_blue
            + c_buf
            + CLI_CONFIG.color_red
            + p_buf
            + CLI_CONFIG.style_reset_all
        )

        # Bars
        print(" <", end="")
        print(CLI_CONFIG.color_yellow + "=" * n_fat, end="")
        print(CLI_CONFIG.color_blue + "=" * n_car, end="")
        print(CLI_CONFIG.color_red + "=" * n_pro, end="")
        print(CLI_CONFIG.style_reset_all + ">")

        # Calorie footers
        k_fat = str(round(fat * 9))
        k_car = str(round(net_carb * 4))
        k_pro = str(round(pro * 4))
        f_buf = " " * (n_fat // 2) + k_fat + " " * (n_fat - n_fat // 2 - len(k_fat))
        c_buf = " " * (n_car // 2) + k_car + " " * (n_car - n_car // 2 - len(k_car))
        p_buf = " " * (n_pro // 2) + k_pro + " " * (n_pro - n_pro // 2 - len(k_pro))
        print(
            "  "
            + CLI_CONFIG.color_yellow
            + f_buf
            + CLI_CONFIG.color_blue
            + c_buf
            + CLI_CONFIG.color_red
            + p_buf
            + CLI_CONFIG.style_reset_all
        )

    def print_nute_bar(_n_id: int, amount: float, _nutrients: dict) -> tuple:
        nutrient = _nutrients[_n_id]
        rda = nutrient[1]
        tag = nutrient[3]
        unit = nutrient[2]
        # anti = nutrient[5]

        if not rda:
            return False, nutrient
        attain = amount / rda
        perc = round(100 * attain, 1)

        if attain >= CLI_CONFIG.thresh_over:
            color = CLI_CONFIG.color_over
        elif attain <= CLI_CONFIG.thresh_crit:
            color = CLI_CONFIG.color_crit
        elif attain <= CLI_CONFIG.thresh_warn:
            color = CLI_CONFIG.color_warn
        else:
            color = CLI_CONFIG.color_default

        # Print
        detail_amount = "{0}/{1} {2}".format(round(amount, 1), rda, unit).ljust(18)
        detail_amount = "{0} -- {1}".format(detail_amount, tag)
        left_index = 20
        left_pos = round(left_index * attain) if attain < 1 else left_index
        print(" {0}<".format(color), end="")
        print("=" * left_pos + " " * (left_index - left_pos) + ">", end="")
        print(" {0}%\t[{1}]".format(perc, detail_amount), end="")
        print(CLI_CONFIG.style_reset_all)

        return True, perc

    # Actual values
    kcals = round(analysis[NUTR_ID_KCAL])
    pro = analysis[NUTR_ID_PROTEIN]
    net_carb = analysis[NUTR_ID_CARBS] - analysis[NUTR_ID_FIBER]
    fat = analysis[NUTR_ID_FAT_TOT]
    kcals_449 = round(4 * pro + 4 * net_carb + 9 * fat)

    # Desired values
    kcals_rda = round(nutrients[NUTR_ID_KCAL][1])
    pro_rda = nutrients[NUTR_ID_PROTEIN][1]
    net_carb_rda = nutrients[NUTR_ID_CARBS][1] - nutrients[NUTR_ID_FIBER][1]
    fat_rda = nutrients[NUTR_ID_FAT_TOT][1]

    # Print calories and macronutrient bars
    print_header("Macronutrients")
    kcals_max = max(kcals, kcals_rda)
    rda_perc = round(kcals * 100 / kcals_rda, 1)
    print(
        "Actual:    {0} kcal ({1}% RDA), {2} by 4-4-9".format(
            kcals, rda_perc, kcals_449
        )
    )
    print_macro_bar(fat, net_carb, pro, kcals_max, _buffer=buffer)
    print(
        "\nDesired:   {0} kcal ({1} kcal)".format(
            kcals_rda, "%+d" % (kcals - kcals_rda)
        )
    )
    print_macro_bar(
        fat_rda,
        net_carb_rda,
        pro_rda,
        kcals_max,
        _buffer=buffer,
    )

    # Nutrition detail report
    print_header("Nutrition detail report")
    for n_id in analysis:
        print_nute_bar(n_id, analysis[n_id], nutrients)
    # TODO: below
    print(
        "work in progress... "
        "some minor fields with negligible data, they are not shown here"
    )
