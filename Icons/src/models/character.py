"""Character data model for Icons: Assembled Edition."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Power:
    type: str = ""
    name: str = ""
    level: int = 1
    extras: list[str] = field(default_factory=list)
    limits: list[str] = field(default_factory=list)
    device: bool = False


@dataclass
class Character:
    name: str = ""
    civilian_identity: str = ""
    origin: str = ""
    attributes: dict[str, int] = field(default_factory=lambda: {
        "Prowess":      1,
        "Coordination": 1,
        "Strength":     1,
        "Intellect":    1,
        "Awareness":    1,
        "Willpower":    1,
    })
    powers: list[Power] = field(default_factory=list)
    specialties: list[str] = field(default_factory=list)
    qualities: list[str] = field(default_factory=lambda: ["", "", ""])
    description: str = ""
    background: str = ""

    # Runtime-only: not serialised to JSON
    file_path: str = field(default="", compare=False, repr=False)

    # ------------------------------------------------------------------
    # Derived stats
    # ------------------------------------------------------------------

    @property
    def stamina(self) -> int:
        """Stamina = Strength + Willpower."""
        return (
            self.attributes.get("Strength", 1)
            + self.attributes.get("Willpower", 1)
        )

    @property
    def determination(self) -> int:
        """Determination = max(1, 6 - power_cost).

        power_cost = number of powers
                   + count of attributes whose level is > 6
        (Extras / limits that shift this cost are tracked as free-text
        and not automated in this version.)
        """
        power_cost = len(self.powers)
        power_cost += sum(1 for v in self.attributes.values() if v > 6)
        return max(1, 6 - power_cost)

    @property
    def display_name(self) -> str:
        return self.name.strip() if self.name.strip() else "Unnamed Hero"
