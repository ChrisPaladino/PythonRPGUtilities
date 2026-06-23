"""
Application state container shared across all UI panels.
"""
from dataclasses import dataclass, field
from pta_manager.models import Protagonist, Scene
from pta_manager.services.card_service import CardDeck


@dataclass
class AppState:
    mode: str = "DICE_MODE"  # "DICE_MODE" or "CARD_MODE"
    protagonists: list[Protagonist] = field(default_factory=list)
    producer_budget: int = 3
    audience_pool: int = 0  # shared fan mail pool
    scenes: list[Scene] = field(default_factory=list)
    current_scene_id: str = ""
    episode_info: dict = field(default_factory=dict)
    deck: CardDeck = field(default_factory=CardDeck)
    save_name: str = ""
