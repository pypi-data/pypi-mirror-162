# -*- coding: utf-8 -*-
"""
Calculate service for one rep max, BMR, body fat, lean body limit, etc.

Created on Tue Aug 11 20:53:14 2020

@author: shane
"""
import argparse
import math

from ntclient import Gender

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1 rep max
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

common_n_reps = (1, 2, 3, 5, 6, 8, 10, 12, 15, 20)


def orm_epley(weight: float, reps: float) -> dict:
    """
    Returns a dict {n_reps: max_weight, ...}
        for n_reps: (1, 2, 3, 5, 6, 8, 10, 12, 15, 20)

    1 RM = weight * (1 + (reps - 1) / 30)

    Source: https://workoutable.com/one-rep-max-calculator/
    """

    def one_rm() -> float:
        _un_rounded_result = weight * (1 + (reps - 1) / 30)
        return round(_un_rounded_result, 1)

    def weight_max_reps(target_reps: float) -> float:
        _un_rounded_result = one_rm() * 30 / (29 + target_reps)
        return round(_un_rounded_result, 1)

    maxes = {n_reps: weight_max_reps(n_reps) for n_reps in common_n_reps}
    return maxes


def orm_brzycki(weight: float, reps: float) -> dict:
    """
    Returns a dict {n_reps: max_weight, ...}
        for n_reps: (1, 2, 3, 5, 6, 8, 10, 12, 15, 20)

    1 RM = weight * 36 / (37 - reps)

    NOTE: Adjusted formula is below, with quadratic term.

    1 RM = weight * 36 / (37 - reps + 0.005 * reps^2)

    Source: https://workoutable.com/one-rep-max-calculator/
    """

    def _one_rm() -> float:
        _un_rounded_result = weight * 36 / (37 - reps + 0.005 * reps**2)
        return round(_un_rounded_result, 1)

    one_rm = _one_rm()

    def weight_max_reps(target_reps: float) -> float:
        _un_rounded_result = one_rm * (37 - target_reps + 0.005 * target_reps**2) / 36
        return round(_un_rounded_result, 1)

    maxes = {n_reps: weight_max_reps(n_reps) for n_reps in common_n_reps}
    return maxes


def orm_dos_remedios(weight: float, reps: int) -> dict:
    """
    Returns dict {n_reps: max_weight, ...}
        for n_reps: (1, 2, 3, 5, 6, 8, 10, 12, 15, 20)

    Or an {"errMsg": "INVALID_RANGE", ...}

    Source:
        https://www.peterrobertscoaching.com/blog/the-best-way-to-calculate-1-rep-max
    """

    _common_n_reps = {
        1: 1,
        2: 0.92,
        3: 0.9,
        4: 0.89,  # NOTE: I added this
        5: 0.87,
        6: 0.82,
        7: 0.781,  # NOTE: I added this
        8: 0.75,
        9: 0.72375,  # NOTE: I added this
        10: 0.7,
        11: 0.674286,  # NOTE: I added this
        12: 0.65,
        13: 0.628571,  # NOTE: I added this
        14: 0.611429,  # NOTE: I added this
        15: 0.6,
        16: 0.588,  # NOTE: I added this
        17: 0.5775,  # NOTE: I added this
        18: 0.568,  # NOTE: I added this
        19: 0.559,  # NOTE: I added this
        20: 0.55,  # NOTE: I added this, 20 reps is NOT in the original equation.
    }

    def _one_rm() -> float:
        _multiplier = _common_n_reps[reps]
        _un_rounded_result = weight / _multiplier
        return round(_un_rounded_result, 1)

    # Compute the 1-rep max
    one_rm = _one_rm()

    def max_weight(target_reps: int) -> float:
        """Used to calculate max weight based on actual reps, e.g. 5 or 12"""
        _multiplier = _common_n_reps[target_reps]
        _un_rounded_result = one_rm * _multiplier
        return round(_un_rounded_result, 1)

    return {n_reps: max_weight(n_reps) for n_reps in _common_n_reps}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# BMR
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TODO: write true service level calls, which accepts: lbm | (weight & body_fat)
def bmr_katch_mcardle(
    activity_factor: float, weight: float, args: argparse.Namespace
) -> dict:
    """
    BMR = 370 + (21.6 x Lean Body Mass(kg) )

    Source: https://www.calculatorpro.com/calculator/katch-mcardle-bmr-calculator/
    Source: https://tdeecalculator.net/about.php

    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}
    @param weight: kg
    @param args: Namespace containing: body_fat (to calculate lean mass in kg)
    """

    body_fat = float(args.body_fat)
    print("Body fat: %s %%" % (body_fat * 100))

    lbm = weight * (1 - body_fat)
    bmr = 370 + (21.6 * lbm)
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


def bmr_cunningham(
    activity_factor: float, weight: float, args: argparse.Namespace
) -> dict:
    """
    Source: https://www.slideshare.net/lsandon/weight-management-in-athletes-lecture

    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}
    @param weight: kg
    @param args: Namespace containing: body_fat (to calculate lean mass in kg)
    """

    body_fat = float(args.body_fat)

    lbm = weight * (1 - body_fat)
    bmr = 500 + 22 * lbm
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


def bmr_mifflin_st_jeor(
    activity_factor: float, weight: float, args: argparse.Namespace
) -> dict:
    """
    Source: https://www.myfeetinmotion.com/mifflin-st-jeor-equation/

    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}
    @param weight: kg
    @param args: Namespace containing:
        gender: {'MALE', 'FEMALE'}
        height: cm
        age: float (years)
    """

    def gender_specific_bmr(_gender: Gender, _bmr: float) -> float:
        _second_term = {
            Gender.MALE: 5,
            Gender.FEMALE: -161,
        }
        return _bmr + _second_term[_gender]

    gender = Gender.FEMALE if args.female_gender else Gender.MALE
    print()
    print("Gender: %s" % gender)

    height = float(args.height)
    print("Height: %s cm" % height)
    age = float(args.age)
    print("Age: %s years" % age)
    print()

    bmr = 10 * weight + 6.25 + 6.25 * height - 5 * age

    bmr = gender_specific_bmr(gender, bmr)
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


def bmr_harris_benedict(
    activity_factor: float, weight: float, args: argparse.Namespace
) -> dict:
    """
    Harris-Benedict = (13.397m + 4.799h - 5.677a) + 88.362 (MEN)

    Harris-Benedict = (9.247m + 3.098h - 4.330a) + 447.593 (WOMEN)

    m: mass (kg), h: height (cm), a: age (years)

    Source: https://tdeecalculator.net/about.php

    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}
    @param weight: kg
    @param args: Namespace containing:
        gender: {'MALE', 'FEMALE'}
        height: cm
        age: float (years)
    """

    gender = Gender.FEMALE if args.female_gender else Gender.MALE

    height = float(args.height)
    age = float(args.age)

    def gender_specific_bmr(_gender: Gender) -> float:
        _gender_specific_bmr = {
            Gender.MALE: (13.397 * weight + 4.799 * height - 5.677 * age) + 88.362,
            Gender.FEMALE: (9.247 * weight + 3.098 * height - 4.330 * age) + 447.593,
        }
        return _gender_specific_bmr[_gender]

    bmr = gender_specific_bmr(gender)
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Body fat
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def bf_navy(gender: Gender, args: argparse.Namespace) -> float:
    """
    @param gender: MALE or FEMALE
    @param args: argparse namespace dict containing:
        height, waist, neck, and (if female) hip.
        All values are in cm.

    @return: float (e.g. 0.17)

    Source:
        https://www.thecalculator.co/health/Navy-Method-Body-Fat-Measurement-Calculator-1112.html
    """

    # Navy values
    height = float(args.height)
    print()
    print("Height: %s cm" % height)

    waist = float(args.waist)
    print("Waist: %s cm" % waist)
    if gender == Gender.FEMALE:
        hip = float(args.hip)
        print("Hip: %s cm" % hip)
    else:
        hip = 0.0  # placeholder value, not used for men anyway
    neck = float(args.neck)
    print("Neck: %s cm" % neck)

    # Compute values
    _gender_specific_denominator = {
        Gender.MALE: (
            1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)
        ),
        Gender.FEMALE: (
            1.29579
            - 0.35004 * math.log10(waist + hip - neck)
            + 0.22100 * math.log10(height)
        ),
    }

    return round(495 / _gender_specific_denominator[gender] - 450, 2)


def bf_3site(gender: Gender, args: argparse.Namespace) -> float:
    """
    @param gender: MALE or FEMALE
    @param args: dict containing age, and skin manifolds (mm) for
        chest, abdominal, and thigh.

    @return: float (e.g. 0.17)

    Source:
        https://www.thecalculator.co/health/Body-Fat-Percentage-3-Site-Skinfold-Test-1113.html
    """

    # Shared parameters for skin manifold 3 & 7 site tests
    age = float(args.age)
    print()
    print("Age: %s years" % age)

    # 3-Site values
    chest = int(args.chest)
    print("Chest: %s mm" % chest)
    abd = int(args.abd)
    print("Abdominal: %s mm" % abd)
    thigh = int(args.thigh)
    print("Thigh: %s mm" % thigh)

    # Compute values
    st3 = chest + abd + thigh
    _gender_specific_denominator = {
        Gender.MALE: 1.10938
        - 0.0008267 * st3
        + 0.0000016 * st3 * st3
        - 0.0002574 * age,
        Gender.FEMALE: 1.089733
        - 0.0009245 * st3
        + 0.0000025 * st3 * st3
        - 0.0000979 * age,
    }

    return round(495 / _gender_specific_denominator[gender] - 450, 2)


def bf_7site(gender: Gender, args: argparse.Namespace) -> float:
    """
    @param gender: MALE or FEMALE
    @param args: dict containing age, and skin manifolds (mm) for
        chest, abdominal, thigh, triceps, sub, sup, and mid.

    @return: float (e.g. 0.17)

    Source:
        https://www.thecalculator.co/health/Body-Fat-Percentage-7-Site-Skinfold-Calculator-1115.html
    """

    # Shared parameters for skin manifold 3 & 7 site tests
    age = float(args.age)

    # 3-Site values
    chest = int(args.chest)
    abd = int(args.abd)
    thigh = int(args.thigh)

    # 7-Site values
    tricep = int(args.tricep)
    print()
    print("Tricep: %s mm" % tricep)
    sub = int(args.sub)
    print("Sub: %s mm" % sub)
    sup = int(args.sup)
    print("Sup: %s mm" % sup)
    mid = int(args.mid)
    print("Mid: %s mm" % mid)

    # Compute values
    st7 = chest + abd + thigh + tricep + sub + sup + mid

    _gender_specific_denominator = {
        Gender.MALE: 1.112
        - 0.00043499 * st7
        + 0.00000055 * st7 * st7
        - 0.00028826 * age,
        Gender.FEMALE: 1.097
        - 0.00046971 * st7
        + 0.00000056 * st7 * st7
        - 0.00012828 * age,
    }

    return round(495 / _gender_specific_denominator[gender] - 450, 2)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Lean body limits (young men)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def lbl_berkhan(height: float) -> dict:
    """
    Calculate Martin Berkhan's lean body limit for young men.

    Source: https://rippedbody.com/maximum-muscular-potential/

    @param height: cm
    @return: {"condition": "...", weight_range: "abc ~ xyz"}
    """

    _min = round((height - 102) * 2.205, 1)
    _max = round((height - 98) * 2.205, 1)
    return {"condition": "Contest shape (5-6%)", "weight": "%s ~ %s lbs" % (_min, _max)}


def lbl_eric_helms(height: float, args: argparse.Namespace) -> dict:
    """
    Calculate Eric Helm's lean body limit for young men.

    Source:

    @param height: cm
    @param args: Namespace containing desired_bf, e.g. 0.12
    @return: {"condition": "...", weight_range: "abc ~ xyz"}
    """

    try:
        desired_bf = float(args.desired_bf) * 100
    except (KeyError, TypeError):
        return {"errMsg": "Eric Helms failed, requires: height, desired_bf."}

    _min = round(4851.00 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
    _max = round(5402.25 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
    return {
        "condition": "%s%% body fat" % desired_bf,
        "weight": "%s ~ %s lbs" % (_min, _max),
    }


def lbl_casey_butt(height: float, args: argparse.Namespace) -> dict:
    """
    Calculate Casey Butt's lean body limit for young men. Includes muscle measurements.
    Some may find these controversial.

    Source: https://fastfoodmacros.com/maximum-muscular-potential-calculator.asp

    @param height: cm
    @param args: Namespace containing desired_bf, and wrist & ankle circumference.
    @return: dict with lbm, weight, and maximum measurements for muscle groups.
    """

    try:
        height /= 2.54
        desired_bf = float(args.desired_bf)

        wrist = float(args.wrist) / 2.54  # convert cm --> inches
        ankle = float(args.ankle) / 2.54  # convert cm --> inches
    except (KeyError, TypeError):
        return {
            "errMsg": "Casey Butt failed, requires: height, desired_bf, wrist, & ankle."
        }

    lbm = round(
        height ** (3 / 2)
        * (math.sqrt(wrist) / 22.6670 + math.sqrt(ankle) / 17.0104)
        * (1 + desired_bf / 2.24),
        1,
    )
    weight = round(lbm / (1 - desired_bf), 1)

    return {
        "condition": "%s%% body fat" % (desired_bf * 100),
        "weight": "%s lbs" % weight,
        "lbm": "%s lbs" % lbm,
        "chest": round(1.6817 * wrist + 1.3759 * ankle + 0.3314 * height, 2),
        "arm": round(1.2033 * wrist + 0.1236 * height, 2),
        "forearm": round(0.9626 * wrist + 0.0989 * height, 2),
        "neck": round(1.1424 * wrist + 0.1236 * height, 2),
        "thigh": round(1.3868 * ankle + 0.1805 * height, 2),
        "calf": round(0.9298 * ankle + 0.1210 * height, 2),
    }
