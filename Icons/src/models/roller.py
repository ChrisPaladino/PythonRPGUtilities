"""Dice-rolling primitives for Icons hero creation."""

from __future__ import annotations

import random

from data.tables import (
    LEVEL_DETERMINATION,
    NUM_POWERS_TABLE,
    NUM_SPECIALTIES_TABLE,
    ORIGIN_TABLE,
    POWER_SUBTABLES,
    POWER_TYPE_TABLE,
    SPECIALTY_TABLE,
)


def roll(n: int, sides: int) -> int:
    """Roll *n* dice each with *sides* faces and return the total."""
    return sum(random.randint(1, sides) for _ in range(n))


def roll_2d6() -> int:
    return roll(2, 6)


def roll_d6() -> int:
    return random.randint(1, 6)


# ---------------------------------------------------------------------------
# Table-lookup helpers (return raw roll + looked-up result as a 2-tuple)
# ---------------------------------------------------------------------------

def roll_level() -> tuple[int, int]:
    """Return (dice_total, level) from the Level Determination table."""
    r = roll_2d6()
    return r, LEVEL_DETERMINATION[r]


def roll_origin() -> tuple[int, str]:
    """Return (dice_total, origin_name)."""
    r = roll_2d6()
    return r, ORIGIN_TABLE[r]


def roll_num_powers() -> tuple[int, int]:
    """Return (dice_total, num_powers)."""
    r = roll_2d6()
    return r, NUM_POWERS_TABLE[r]


def roll_power_type() -> tuple[int, str]:
    """Return (dice_total, power_type_name)."""
    r = roll_2d6()
    return r, POWER_TYPE_TABLE[r]


def roll_specific_power(power_type: str) -> tuple[int, int, str]:
    """Roll the two-d6 sub-table for *power_type*.

    Returns (first_d6, second_d6, power_name).
    """
    first = roll_d6()
    second = roll_d6()
    return first, second, POWER_SUBTABLES[power_type][(first, second)]


def roll_num_specialties() -> tuple[int, int]:
    """Return (dice_total, num_specialties)."""
    r = roll_2d6()
    return r, NUM_SPECIALTIES_TABLE[r]


def roll_specialty() -> tuple[int, int, str]:
    """Roll the two-d6 specialty table.

    Returns (first_d6, second_d6, specialty_name).
    """
    first = roll_d6()
    second = roll_d6()
    return first, second, SPECIALTY_TABLE[(first, second)]
