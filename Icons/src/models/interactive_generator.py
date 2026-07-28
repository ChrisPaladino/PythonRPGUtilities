"""Interactive hero generation with user choices at each step."""

from __future__ import annotations

from dataclasses import dataclass, field

from models.character import Character, Power
from models.roller import (
    roll_2d6,
    roll_d6,
    roll_level,
    roll_num_powers,
    roll_num_specialties,
    roll_power_type,
    roll_specific_power,
    roll_specialty,
)
from data.tables import (
    ATTRIBUTES,
    MENTAL_ATTRIBUTES,
    ORIGIN_TABLE,
    ORIGIN_DESCRIPTIONS,
)


@dataclass
class WizardState:
    """Tracks hero generation state and user choices through the wizard."""

    # Phase 1: Origin
    origin_roll: int = 0
    origin: str = ""

    # Phase 2: Attributes
    attribute_rolls: dict[str, int] = field(default_factory=dict)
    attribute_total: int = 0
    attributes_final: dict[str, int] = field(default_factory=dict)

    # Phase 3: Origin modifiers
    origin_choice_pending: str = ""  # e.g., "Transformed", "Birthright"
    origin_choice_value: str = ""  # e.g., attribute name or "extra_power"

    # Phase 3b: Powers
    num_powers_roll: int = 0
    num_powers: int = 0
    powers: list[Power] = field(default_factory=list)

    # Phase 4: Specialties
    num_specialties_roll: int = 0
    num_specialties: int = 0
    specialties: list[str] = field(default_factory=list)

    # Phase 5: User-entered description
    name: str = ""
    civilian_identity: str = ""
    description: str = ""
    background: str = ""
    qualities: list[str] = field(default_factory=lambda: ["", "", ""])

    def to_character(self) -> Character:
        """Convert wizard state to a Character object."""
        return Character(
            name=self.name,
            civilian_identity=self.civilian_identity,
            origin=self.origin,
            attributes=self.attributes_final,
            powers=self.powers,
            specialties=self.specialties,
            qualities=self.qualities,
            description=self.description,
            background=self.background,
        )


class InteractiveGenerator:
    """Stateful generator that supports user choices."""

    def __init__(self):
        self.state = WizardState()

    # -----------------------------------------------------------------------
    # Phase 1: Origin Selection
    # -----------------------------------------------------------------------

    def get_origin_options(self) -> list[tuple[int, str, str]]:
        """Return list of (roll_result, origin_name, description) for user to choose."""
        options = []
        for roll_result, origin_name in ORIGIN_TABLE.items():
            desc = ORIGIN_DESCRIPTIONS.get(origin_name, "")
            options.append((roll_result, origin_name, desc))

        # Deduplicate and sort by roll result
        seen = set()
        unique = []
        for roll_result, origin_name, desc in options:
            if origin_name not in seen:
                seen.add(origin_name)
                unique.append((roll_result, origin_name, desc))

        return sorted(unique, key=lambda x: x[0])

    def choose_origin(self, origin: str) -> None:
        """User chooses an origin."""
        self.state.origin = origin
        self.state.origin_roll = next(
            roll for roll, name in ORIGIN_TABLE.items() if name == origin
        )

    # -----------------------------------------------------------------------
    # Phase 2: Attributes (roll + assignment)
    # -----------------------------------------------------------------------

    def roll_attributes(self) -> dict[str, int]:
        """Roll six attributes and return them (not yet assigned)."""
        self.state.attribute_rolls = {}
        for attr in ATTRIBUTES:
            _, level = roll_level()
            self.state.attribute_rolls[attr] = level

        self.state.attribute_total = sum(self.state.attribute_rolls.values())
        return self.state.attribute_rolls.copy()

    def assign_attributes_swap(self, attr1: str, attr2: str) -> None:
        """Swap two attributes and finalize assignment."""
        attrs = self.state.attribute_rolls.copy()
        attrs[attr1], attrs[attr2] = attrs[attr2], attrs[attr1]
        self.state.attributes_final = attrs

    def assign_attributes_ala_carte(self, ordered_values: list[int]) -> None:
        """Assign rolled values to attributes in custom order.

        ordered_values: list of levels in order [Prowess, Coordination, ..., Willpower]
        """
        if len(ordered_values) != len(ATTRIBUTES):
            raise ValueError(f"Expected {len(ATTRIBUTES)} values, got {len(ordered_values)}")
        self.state.attributes_final = {
            attr: val for attr, val in zip(ATTRIBUTES, ordered_values)
        }

    # -----------------------------------------------------------------------
    # Phase 2b: Origin Modifiers (attributes)
    # -----------------------------------------------------------------------

    def apply_origin_modifier_attributes(self) -> None:
        """Apply origin modifiers to attributes. Auto-selects when necessary."""
        if self.state.origin == "Transformed":
            # Boost one attribute by +2 (auto-pick first one)
            attr_to_boost = ATTRIBUTES[0]
            self.state.attributes_final[attr_to_boost] = min(
                self.state.attributes_final[attr_to_boost] + 2, 10
            )

        elif self.state.origin == "Gimmick":
            # Boost one mental attribute by +2 (auto-pick first mental one)
            mental = MENTAL_ATTRIBUTES[0]
            self.state.attributes_final[mental] = min(
                self.state.attributes_final[mental] + 2, 10
            )

        elif self.state.origin == "Artificial":
            # Strength +2 (automatic)
            self.state.attributes_final["Strength"] = min(
                self.state.attributes_final["Strength"] + 2, 10
            )

        elif self.state.origin == "Unearthly":
            # Boost two highest attributes by +2 each
            sorted_attrs = sorted(
                self.state.attributes_final.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for i in range(min(2, len(sorted_attrs))):
                attr_name = sorted_attrs[i][0]
                self.state.attributes_final[attr_name] = min(
                    self.state.attributes_final[attr_name] + 2, 10
                )

    def choose_origin_attribute_boost(self, attribute: str) -> None:
        """User chooses which attribute to boost for Transformed/Gimmick/Unearthly."""
        if self.state.origin == "Transformed":
            self.state.attributes_final[attribute] = min(
                self.state.attributes_final[attribute] + 2, 10
            )
            self.state.origin_choice_pending = ""

        elif self.state.origin == "Gimmick":
            if attribute not in MENTAL_ATTRIBUTES:
                raise ValueError(f"{attribute} is not a mental attribute")
            self.state.attributes_final[attribute] = min(
                self.state.attributes_final[attribute] + 2, 10
            )
            self.state.origin_choice_pending = ""

        elif self.state.origin == "Unearthly":
            # For Unearthly, user chooses 2 attributes; track in a list
            if not hasattr(self.state, "_unearthly_boosts"):
                self.state._unearthly_boosts = []
            self.state._unearthly_boosts.append(attribute)
            if len(self.state._unearthly_boosts) == 2:
                for attr in self.state._unearthly_boosts:
                    self.state.attributes_final[attr] = min(
                        self.state.attributes_final[attr] + 2, 10
                    )
                self.state.origin_choice_pending = ""
                del self.state._unearthly_boosts

    # -----------------------------------------------------------------------
    # Phase 3: Powers
    # -----------------------------------------------------------------------

    def roll_powers(self) -> tuple[int, list[Power]]:
        """Roll number and contents of powers."""
        # Clear any previous powers (in case of reroll)
        self.state.powers = []
        
        num_powers_roll, num_powers = roll_num_powers()
        self.state.num_powers_roll = num_powers_roll
        self.state.num_powers = num_powers

        # Apply Trained/Birthright modifiers
        if self.state.origin == "Birthright":
            self.state.origin_choice_pending = "Birthright"
            return num_powers_roll, []  # Wait for user choice

        if self.state.origin == "Artificial":
            # Add Life Support first
            life_support_level_roll, life_support_level = roll_level()
            life_support = Power(
                type="Defensive",
                name="Life Support",
                level=life_support_level,
                device=False,
            )
            self.state.powers.append(life_support)

        # Roll the powers themselves
        for _ in range(num_powers):
            power_type_roll, power_type = roll_power_type()
            first_d6, second_d6, power_name = roll_specific_power(power_type)
            level_roll, level = roll_level()

            power = Power(
                type=power_type,
                name=power_name,
                level=level,
                device=(self.state.origin == "Gimmick"),
            )
            self.state.powers.append(power)

        return num_powers_roll, self.state.powers.copy()

    def choose_birthright_option(self, choice: str) -> None:
        """User chooses: "extra_power" or "boost_power" for Birthright origin."""
        if choice == "extra_power":
            # Roll an extra power
            power_type_roll, power_type = roll_power_type()
            first_d6, second_d6, power_name = roll_specific_power(power_type)
            level_roll, level = roll_level()

            power = Power(
                type=power_type,
                name=power_name,
                level=level,
                device=False,
            )
            self.state.powers.insert(0, power)
            self.state.num_powers += 1

        elif choice == "boost_power":
            # Will be applied after rolling powers (boost first power by +2)
            pass

        self.state.origin_choice_pending = ""

    def boost_first_power(self) -> None:
        """Boost the first rolled power by +2 (for Birthright if user chose that)."""
        if self.state.powers:
            self.state.powers[0].level = min(self.state.powers[0].level + 2, 10)

    # -----------------------------------------------------------------------
    # Phase 4: Specialties
    # -----------------------------------------------------------------------

    def roll_specialties(self) -> tuple[int, list[str]]:
        """Roll number and contents of specialties."""
        num_spec_roll, num_specialties = roll_num_specialties()
        self.state.num_specialties_roll = num_spec_roll
        self.state.num_specialties = num_specialties

        # Apply Trained modifier
        if self.state.origin == "Trained":
            self.state.num_specialties += 2

        # Roll each specialty
        for _ in range(self.state.num_specialties):
            first_d6, second_d6, specialty_name = roll_specialty()
            self.state.specialties.append(specialty_name)

        return num_spec_roll, self.state.specialties.copy()

    # -----------------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------------

    def get_attribute_total(self) -> int:
        """Return current attribute total."""
        return sum(self.state.attributes_final.values())

    def is_attribute_total_valid(self) -> bool:
        """Check if attribute total >= 20."""
        return self.get_attribute_total() >= 20
