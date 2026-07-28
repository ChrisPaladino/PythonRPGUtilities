"""Random hero generation for Icons: Assembled Edition.

Implements the seven-phase creation process from the rulebook.
"""

from __future__ import annotations

from models.character import Character, Power
from models.roller import (
    roll_d6,
    roll_level,
    roll_num_powers,
    roll_num_specialties,
    roll_origin,
    roll_power_type,
    roll_specific_power,
    roll_specialty,
)
from data.tables import ATTRIBUTES, MENTAL_ATTRIBUTES


def generate_random_hero() -> Character:
    """Generate a fully random Icons hero through all seven creation phases.

    Returns a Character with all fields populated, ready for display/editing.
    """
    hero = Character()

    # Phase 1: Origin
    origin_roll, hero.origin = roll_origin()

    # Phase 2 & onwards depend on the origin, so we create a context
    origin_modifiers = OriginModifiers(hero.origin)

    # Phase 2: Attributes
    _phase_attributes(hero, origin_modifiers)

    # Phase 3: Powers
    _phase_powers(hero, origin_modifiers)

    # Phase 4: Specialties
    _phase_specialties(hero, origin_modifiers)

    # Phase 5: Description (no random content, user fills in later)
    hero.name = ""
    hero.civilian_identity = ""
    hero.description = ""
    hero.background = ""

    # Phase 6: Qualities (3 empty strings; user fills in)
    hero.qualities = ["", "", ""]

    # Derived stats calculated automatically via properties

    return hero


def _phase_attributes(hero: Character, modifiers: OriginModifiers) -> None:
    """Roll and assign the six attributes. Handle origin modifiers.

    If total < 20 after modifiers, the caller should retry.
    (This function assumes the caller will handle validation.)
    """
    attribute_rolls: dict[str, int] = {}

    for attr in ATTRIBUTES:
        _, level = roll_level()
        attribute_rolls[attr] = level

    # Apply origin modifiers
    if modifiers.origin == "Transformed":
        # Choose which attribute/power to boost
        attr_to_boost = modifiers.boost_choice or ATTRIBUTES[0]
        attribute_rolls[attr_to_boost] = min(attribute_rolls[attr_to_boost] + 2, 10)

    elif modifiers.origin == "Gimmick":
        # Boost one mental attribute
        mental = modifiers.boost_choice or MENTAL_ATTRIBUTES[0]
        attribute_rolls[mental] = min(attribute_rolls[mental] + 2, 10)

    elif modifiers.origin == "Artificial":
        # Strength +2
        attribute_rolls["Strength"] = min(attribute_rolls["Strength"] + 2, 10)

    hero.attributes = attribute_rolls


def _phase_powers(hero: Character, modifiers: OriginModifiers) -> None:
    """Roll and generate powers. Handle origin power modifiers."""
    num_powers_roll, num_powers = roll_num_powers()

    # Apply origin modifiers
    if modifiers.origin == "Trained":
        # May trade 1 power for 2 specialties (handled in Phase 4)
        pass

    elif modifiers.origin == "Birthright":
        # May choose 1 additional innate power
        if modifiers.birthright_extra_power:
            num_powers += 1

    elif modifiers.origin == "Artificial":
        # Gain Life Support in addition to rolled powers
        life_support = Power(
            type="Defensive",
            name="Life Support",
            level=1,  # Will be rolled next
            device=False,
        )
        _, level = roll_level()
        life_support.level = level
        hero.powers.append(life_support)

    # Roll each power
    for _ in range(num_powers):
        power_type_roll, power_type = roll_power_type()
        first_d6, second_d6, power_name = roll_specific_power(power_type)
        level_roll, level = roll_level()

        power = Power(
            type=power_type,
            name=power_name,
            level=level,
            device=(modifiers.origin == "Gimmick"),
        )
        hero.powers.append(power)


def _phase_specialties(hero: Character, modifiers: OriginModifiers) -> None:
    """Roll and generate specialties. Handle origin modifiers."""
    num_spec_roll, num_specialties = roll_num_specialties()

    # Apply origin modifiers
    if modifiers.origin == "Trained":
        num_specialties += 2

    # Roll each specialty randomly
    specialties: list[str] = []
    for _ in range(num_specialties):
        first_d6, second_d6, specialty_name = roll_specialty()
        specialties.append(specialty_name)

    hero.specialties = specialties


# ---------------------------------------------------------------------------
# Origin Modifier Context
# ---------------------------------------------------------------------------

class OriginModifiers:
    """Holds state for origin choices that might require user input.

    For simplicity in this implementation, we auto-pick defaults; the UI
    can replay generation with different choices if desired.
    """

    def __init__(self, origin: str) -> None:
        self.origin = origin
        self.boost_choice: str | None = None
        self.birthright_extra_power: bool = True

    def set_boost_choice(self, choice: str) -> None:
        self.boost_choice = choice

    def set_birthright_extra_power(self, use_extra: bool) -> None:
        self.birthright_extra_power = use_extra
