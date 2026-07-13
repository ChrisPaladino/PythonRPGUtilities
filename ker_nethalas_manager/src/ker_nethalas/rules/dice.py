from random import Random

from ker_nethalas.core.enums import RollSource
from ker_nethalas.core.models import RollResult


class DiceService:
    """Roll provider that supports automatic and manual entry modes."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = Random(seed)

    def roll(self, sides: int = 100) -> RollResult:
        if sides < 2:
            raise ValueError("Die must have at least 2 sides.")
        return RollResult(roll=self._rng.randint(1, sides), sides=sides, source=RollSource.AUTOMATIC)

    def manual(self, value: int, sides: int = 100) -> RollResult:
        if value < 1 or value > sides:
            raise ValueError(f"Manual roll must be in range 1..{sides}.")
        return RollResult(roll=value, sides=sides, source=RollSource.MANUAL)
