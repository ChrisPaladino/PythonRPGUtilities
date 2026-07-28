"""All rollable tables for Icons: Assembled Edition hero creation.

Source: Icons Assembled - Hero Creation Rules and Tables.md (pages 54-68)
"""

from __future__ import annotations

# Ordered list of the six hero attributes
ATTRIBUTES: list[str] = [
    "Prowess",
    "Coordination",
    "Strength",
    "Intellect",
    "Awareness",
    "Willpower",
]

# Mental attributes (relevant for Gimmick origin modifier)
MENTAL_ATTRIBUTES: list[str] = ["Intellect", "Awareness", "Willpower"]

# ---------------------------------------------------------------------------
# Level Determination Table (2d6 → level 1–8)
# Used whenever a level is randomly determined.
# ---------------------------------------------------------------------------
LEVEL_DETERMINATION: dict[int, int] = {
    2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 4,
    7: 5,
    8: 5,
    9: 6,
    10: 6,
    11: 7,
    12: 8,
}

# ---------------------------------------------------------------------------
# Origin Table (2d6 → origin name)
# ---------------------------------------------------------------------------
ORIGIN_TABLE: dict[int, str] = {
    2:  "Trained",
    3:  "Trained",
    4:  "Trained",
    5:  "Transformed",
    6:  "Transformed",
    7:  "Birthright",
    8:  "Gimmick",
    9:  "Gimmick",
    10: "Artificial",
    11: "Unearthly",
    12: "Unearthly",
}

# Human-readable descriptions of each origin modifier (for display in UI)
ORIGIN_DESCRIPTIONS: dict[str, str] = {
    "Trained": (
        "Highly skilled individual. Apparent powers come from training or equipment. "
        "+2 additional specialties. May trade 1 rolled power for 2 more specialties."
    ),
    "Transformed": (
        "Once normal, became superhuman through outside agency. "
        "Increase one attribute or power by +2 (max 10)."
    ),
    "Birthright": (
        "Born with or destined to develop powers. "
        "Choose: 1 additional innate power OR +2 to one rolled power (max 10). "
        "Additional power should not be a device."
    ),
    "Gimmick": (
        "All powers come from devices. "
        "Increase one mental attribute by +2 (max 10)."
    ),
    "Artificial": (
        "Robot or other construct. "
        "Strength +2, plus gain Life Support in addition to rolled powers."
    ),
    "Unearthly": (
        "Alien, elemental, or being from another world. "
        "Increase two attributes or powers by +2 each; OR roll twice on Origin table "
        "(ignore 11–12 and duplicates) and apply both origins."
    ),
}

# ---------------------------------------------------------------------------
# Number of Powers Table (2d6 → count)
# ---------------------------------------------------------------------------
NUM_POWERS_TABLE: dict[int, int] = {
    2:  2,
    3:  2,
    4:  2,
    5:  3,
    6:  3,
    7:  3,
    8:  4,
    9:  4,
    10: 4,
    11: 5,
    12: 5,
}

# ---------------------------------------------------------------------------
# Power Type Table (2d6 → type name)
# ---------------------------------------------------------------------------
POWER_TYPE_TABLE: dict[int, str] = {
    2:  "Mental",
    3:  "Mental",
    4:  "Control",
    5:  "Control",
    6:  "Defensive",
    7:  "Offensive",
    8:  "Movement",
    9:  "Alteration",
    10: "Alteration",
    11: "Sensory",
    12: "Sensory",
}

# ---------------------------------------------------------------------------
# Power sub-tables: (first_d6, second_d6) → power name
# ---------------------------------------------------------------------------

def _build_table(
    entries: list[tuple[tuple[int, ...], tuple[int, ...], str]],
) -> dict[tuple[int, int], str]:
    """Expand range tuples into a flat (first_d6, second_d6) → name dict."""
    result: dict[tuple[int, int], str] = {}
    for first_range, second_range, name in entries:
        for f in first_range:
            for s in second_range:
                result[(f, s)] = name
    return result


ALTERATION_POWERS: dict[tuple[int, int], str] = _build_table([
    ((1, 2),    (1,),          "Ability Boost"),
    ((1, 2),    (2,),          "Ability Increase"),
    ((1, 2),    (3,),          "Alter Ego"),
    ((1, 2),    (4,),          "Alternate Form"),
    ((1, 2),    (5,),          "Aquatic"),
    ((1, 2),    (6,),          "Density"),
    ((3, 4),    (1,),          "Duplication"),
    ((3, 4),    (2,),          "Extra Body Parts"),
    ((3, 4),    (3,),          "Growth"),
    ((3, 4),    (4,),          "Invisibility"),
    ((3, 4),    (5,),          "Phasing"),
    ((3, 4),    (6,),          "Shrinking"),
    ((5, 6),    (1,),          "Animal Mimicry"),
    ((5, 6),    (2,),          "Material Mimicry"),
    ((5, 6),    (3,),          "Plant Mimicry"),
    ((5, 6),    (4,),          "Power Mimicry"),
    ((5, 6),    (5,),          "Stretching"),
    ((5, 6),    (6,),          "Transformation"),
])

CONTROL_POWERS: dict[tuple[int, int], str] = _build_table([
    ((1, 2),    (1, 2),        "Alteration Ray"),
    ((1, 2),    (3, 4),        "Element Control"),
    ((1, 2),    (5,),          "Probability Control"),
    ((1, 2),    (6,),          "Time Control"),
    ((3, 4),    (1, 2),        "Energy Control"),
    ((3, 4),    (3,),          "Healing"),
    ((3, 4),    (4, 5),        "Telekinesis"),
    ((3, 4),    (6,),          "Transmutation"),
    ((5, 6),    (1,),          "Cosmic Power"),
    ((5, 6),    (2, 3),        "Gadgets"),
    ((5, 6),    (4,),          "Magic"),
    ((5, 6),    (5,),          "Nullification"),
    ((5, 6),    (6,),          "Servant"),
])

DEFENSIVE_POWERS: dict[tuple[int, int], str] = _build_table([
    ((1, 2),    (1, 2),        "Absorption"),
    ((1, 2),    (3,),          "Adaptation"),
    ((1, 2),    (4, 5, 6),     "Force Field"),
    ((3, 4),    (1,),          "Immortality"),
    ((3, 4),    (2, 3, 4),     "Life Support"),
    ((3, 4),    (5, 6),        "Reflection"),
    ((5, 6),    (1, 2),        "Regeneration"),
    ((5, 6),    (3, 4, 5, 6),  "Resistance"),
])

MENTAL_POWERS: dict[tuple[int, int], str] = _build_table([
    ((1, 2, 3), (1,),          "Astral Projection"),
    ((1, 2, 3), (2,),          "Dream Control"),
    ((1, 2, 3), (3, 4),        "Emotion Control"),
    ((1, 2, 3), (5,),          "Illusion"),
    ((1, 2, 3), (6,),          "Images"),
    ((4, 5, 6), (1, 2),        "Mental Blast"),
    ((4, 5, 6), (3,),          "Mind Control"),
    ((4, 5, 6), (4,),          "Mind Shield"),
    ((4, 5, 6), (5, 6),        "Telepathy"),
])

OFFENSIVE_POWERS: dict[tuple[int, int], str] = _build_table([
    ((1, 2, 3), (1,),          "Affliction"),
    ((1, 2, 3), (2,),          "Binding"),
    ((1, 2, 3), (3, 4),        "Blast"),
    ((1, 2, 3), (5, 6),        "Strike"),
    ((4, 5, 6), (1,),          "Aura"),
    ((4, 5, 6), (2, 3),        "Dazzle"),
    ((4, 5, 6), (4,),          "Energy Drain"),
    ((4, 5, 6), (5,),          "Fast Attack"),
    ((4, 5, 6), (6,),          "Stunning"),
])

MOVEMENT_POWERS: dict[tuple[int, int], str] = _build_table([
    ((1, 2, 3), (1,),          "Burrowing"),
    ((1, 2, 3), (2,),          "Dimensional Travel"),
    ((1, 2, 3), (3, 4),        "Flight"),
    ((1, 2, 3), (5, 6),        "Leaping"),
    ((4, 5, 6), (1,),          "Spinning"),
    ((4, 5, 6), (2, 3),        "Super-Speed"),
    ((4, 5, 6), (4,),          "Swinging"),
    ((4, 5, 6), (5,),          "Teleportation"),
    ((4, 5, 6), (6,),          "Wall-Crawling"),
])

SENSORY_POWERS: dict[tuple[int, int], str] = _build_table([
    ((1, 2, 3), (1, 2),        "Detection"),
    ((1, 2, 3), (3,),          "ESP"),
    ((1, 2, 3), (4, 5, 6),     "Super-Senses"),
    ((4, 5, 6), (1, 2),        "Danger Sense"),
    ((4, 5, 6), (3,),          "Interface"),
    ((4, 5, 6), (4,),          "Postcognition"),
    ((4, 5, 6), (5, 6),        "Precognition"),
])

# Lookup by type name
POWER_SUBTABLES: dict[str, dict[tuple[int, int], str]] = {
    "Alteration": ALTERATION_POWERS,
    "Control":    CONTROL_POWERS,
    "Defensive":  DEFENSIVE_POWERS,
    "Mental":     MENTAL_POWERS,
    "Offensive":  OFFENSIVE_POWERS,
    "Movement":   MOVEMENT_POWERS,
    "Sensory":    SENSORY_POWERS,
}

# ---------------------------------------------------------------------------
# Number of Specialties Table (2d6 → count)
# ---------------------------------------------------------------------------
NUM_SPECIALTIES_TABLE: dict[int, int] = {
    2:  1,
    3:  1,
    4:  1,
    5:  2,
    6:  2,
    7:  2,
    8:  3,
    9:  3,
    10: 3,
    11: 4,
    12: 4,
}

# ---------------------------------------------------------------------------
# Specialty Table (first_d6, second_d6) → specialty name
# ---------------------------------------------------------------------------
SPECIALTY_TABLE: dict[tuple[int, int], str] = _build_table([
    ((1,), (1,),       "Aerial Combat"),
    ((1,), (2,),       "Art"),
    ((1,), (3, 4),     "Athletics"),
    ((1,), (5,),       "Business"),
    ((1,), (6,),       "Drive"),
    ((2,), (1, 2),     "Investigation"),
    ((2,), (3,),       "Law"),
    ((2,), (4, 5),     "Leadership"),
    ((2,), (6,),       "Linguistics"),
    ((3,), (1, 2),     "Martial Arts"),
    ((3,), (3,),       "Medicine"),
    ((3,), (4, 5),     "Mental Resistance"),
    ((3,), (6,),       "Military"),
    ((4,), (1,),       "Occult"),
    ((4,), (2,),       "Performance"),
    ((4,), (3,),       "Pilot"),
    ((4,), (4, 5, 6),  "Power"),
    ((5,), (1,),       "Psychiatry"),
    ((5,), (2, 3),     "Science"),
    ((5,), (4,),       "Sleight of Hand"),
    ((5,), (5, 6),     "Stealth"),
    ((6,), (1, 2),     "Technology"),
    ((6,), (3,),       "Underwater Combat"),
    ((6,), (4, 5),     "Weapons"),
    ((6,), (6,),       "Wrestling"),
])

# Flat sorted list of all specialties (for manual-add dropdowns)
ALL_SPECIALTIES: list[str] = sorted(set(SPECIALTY_TABLE.values()))
