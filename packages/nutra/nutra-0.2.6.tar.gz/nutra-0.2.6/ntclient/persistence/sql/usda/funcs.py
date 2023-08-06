"""usda.sqlite functions module"""
from ntclient import NUTR_ID_KCAL
from ntclient.persistence.sql.usda import sql, sql_headers


################################################################################
# Basic functions
################################################################################
def sql_fdgrp() -> dict:
    """Shows food groups"""

    query = "SELECT * FROM fdgrp;"
    result = sql(query)
    return {x[0]: x for x in result}


def sql_food_details(_food_ids: set = None) -> list:
    """Readable human details for foods"""

    if not _food_ids:
        query = "SELECT * FROM food_des;"
    else:
        # TODO: does sqlite3 driver support this? cursor.executemany() ?
        query = "SELECT * FROM food_des WHERE id IN (%s);"
        food_ids = ",".join(str(x) for x in set(_food_ids))
        query = query % food_ids

    return sql(query)


def sql_nutrients_overview() -> dict:
    """Shows nutrients overview"""

    query = "SELECT * FROM nutrients_overview;"
    result = sql(query)
    return {x[0]: x for x in result}


def sql_nutrients_details() -> tuple:
    """Shows nutrients 'details'"""

    query = "SELECT * FROM nutrients_overview;"
    return sql_headers(query)


def sql_servings(_food_ids: set) -> list:
    """Food servings"""
    # TODO: apply connective logic from `sort_foods()` IS ('None') ?
    query = """
SELECT
  serv.food_id,
  serv.msre_id,
  serv_desc.msre_desc,
  serv.grams
FROM
  serving serv
  LEFT JOIN serv_desc ON serv.msre_id = serv_desc.id
WHERE
  serv.food_id IN (%s);
"""
    # FIXME: support this kind of thing by library code & parameterized queries
    food_ids = ",".join(str(x) for x in set(_food_ids))
    return sql(query % food_ids)


def sql_analyze_foods(food_ids: set) -> list:
    """Nutrient analysis for foods"""
    query = """
SELECT
  id,
  nutr_id,
  nutr_val
FROM
  food_des
  INNER JOIN nut_data ON food_des.id = nut_data.food_id
WHERE
  food_des.id IN (%s);
"""
    # TODO: parameterized queries
    food_ids_concat = ",".join(str(x) for x in set(food_ids))
    return sql(query % food_ids_concat)


################################################################################
# Sort
################################################################################
def sql_sort_helper1(nutrient_id: int) -> list:
    """Selects relevant bits from nut_data for sorting"""

    query = """
SELECT
  food_id,
  nutr_id,
  nutr_val
FROM
  nut_data
WHERE
  nutr_id = %s
  OR nutr_id = %s
ORDER BY
  food_id;
"""

    return sql(query % (NUTR_ID_KCAL, nutrient_id))


def sql_sort_foods(nutr_id: int) -> list:
    """Sort foods by nutr_id per 100 g"""

    query = """
SELECT
  nut_data.food_id,
  fdgrp_id,
  nut_data.nutr_val,
  kcal.nutr_val AS kcal,
  long_desc
FROM
  nut_data
  INNER JOIN food_des food ON food.id = nut_data.food_id
  INNER JOIN nutr_def ndef ON ndef.id = nut_data.nutr_id
  INNER JOIN fdgrp ON fdgrp.id = fdgrp_id
  LEFT JOIN nut_data kcal ON food.id = kcal.food_id
    AND kcal.nutr_id = 208
WHERE
  nut_data.nutr_id = %s
ORDER BY
  nut_data.nutr_val DESC;
"""

    return sql(query % nutr_id)


def sql_sort_foods_by_kcal(nutr_id: int) -> list:
    """Sort foods by nutr_id per 200 kcal"""

    # TODO: use parameterized queries
    query = """
SELECT
  nut_data.food_id,
  fdgrp_id,
  ROUND((nut_data.nutr_val * 200 / kcal.nutr_val), 2) AS nutr_val,
  kcal.nutr_val AS kcal,
  long_desc
FROM
  nut_data
  INNER JOIN food_des food ON food.id = nut_data.food_id
  INNER JOIN nutr_def ndef ON ndef.id = nut_data.nutr_id
  INNER JOIN fdgrp ON fdgrp.id = fdgrp_id
  -- filter out NULL kcal
  INNER JOIN nut_data kcal ON food.id = kcal.food_id
    AND kcal.nutr_id = 208
    AND kcal.nutr_val > 0
WHERE
  nut_data.nutr_id = %s
ORDER BY
  (nut_data.nutr_val / kcal.nutr_val) DESC;
"""

    return sql(query % nutr_id)
