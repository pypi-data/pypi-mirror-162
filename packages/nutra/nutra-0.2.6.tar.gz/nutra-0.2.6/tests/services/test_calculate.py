# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 12:13:01 2022

@author: shane

Tests the "calculate service" for any anomalies.
"""
import pytest

import ntclient.services.calculate as calc


@pytest.mark.parametrize("_eq", ["epley", "brzycki", "dos_remedios"])
@pytest.mark.parametrize(
    "weight,reps",
    [(50.0, x) for x in (1, 2, 3, 5, 6, 8, 10, 12, 15, 20)],
)
def test_000_orm_same_in_same_out(_eq: str, weight: float, reps: int) -> None:
    """Test one rep max: Epley"""
    result = {
        "epley": calc.orm_epley(weight, reps),
        "brzycki": calc.orm_brzycki(weight, reps),
        "dos_remedios": calc.orm_dos_remedios(weight, reps),
    }

    # Check results
    assert result[_eq][reps] == weight
