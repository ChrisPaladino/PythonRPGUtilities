"""
Dice service — rolls dice and returns tagged DieResult objects.
"""
import random
from pta_manager.models.resolution import DieResult


def roll_dice(num_dice: int, source: str) -> list[DieResult]:
    """Roll num_dice d10s, tagging each result with its source."""
    return [DieResult(value=random.randint(1, 10), source=source) for _ in range(num_dice)]
