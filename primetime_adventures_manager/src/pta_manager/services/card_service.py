"""
Card service — manages a simulated shuffled standard deck for Card Mode.

Red cards (hearts, diamonds) = successes (equivalent to even dice).
Black cards (clubs, spades) = failures (equivalent to odd dice).
"""
import random

SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = list(range(1, 14))  # 1 (Ace) through 13 (King)
RED_SUITS = {"hearts", "diamonds"}


def _build_deck() -> list[dict]:
    return [{"rank": r, "suit": s} for s in SUITS for r in RANKS]


class CardDeck:
    def __init__(self):
        self._deck: list[dict] = []
        self.shuffle()

    def shuffle(self):
        self._deck = _build_deck()
        random.shuffle(self._deck)

    def draw(self, count: int) -> list[dict]:
        """Draw count cards from the top of the deck. Reshuffles if needed."""
        if count > len(self._deck):
            self.shuffle()
        drawn = self._deck[:count]
        self._deck = self._deck[count:]
        return drawn

    @property
    def remaining(self) -> int:
        return len(self._deck)


def is_red(card: dict) -> bool:
    return card["suit"] in RED_SUITS


def card_value(card: dict) -> int:
    """Numeric rank for highest-card comparison."""
    return card["rank"]
