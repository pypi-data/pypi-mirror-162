"""Temporary [wip] module for more visual (& colorful) RDA output"""


def nutprogbar(food_amts: dict, food_analyses: list, nutrients: dict) -> dict:
    """Returns progress bars, colorized, for foods analyses"""

    def tally() -> None:
        for nut in nut_percs:
            # TODO: get RDA values from nt DB, tree node nested organization
            print(nut)

    food_analyses_dict = {
        x[0]: {y[1]: y[2] for y in food_analyses if y[0] == x[0]} for x in food_analyses
    }

    # print(food_ids)
    # print(food_analyses)

    nut_amts = {}

    for food_id, grams in food_amts.items():
        # r = grams / 100.0
        analysis = food_analyses_dict[food_id]
        for nutrient_id, amt in analysis.items():
            if nutrient_id not in nut_amts:
                nut_amts[nutrient_id] = amt
            else:
                nut_amts[nutrient_id] += amt

    nut_percs = {}

    for nutrient_id, amt in nut_amts.items():
        # TODO: if not rda, show raw amounts?
        if isinstance(nutrients[nutrient_id][1], float):
            nut_percs[nutrient_id] = round(amt / nutrients[nutrient_id][1], 3)

    tally()
    return nut_percs
