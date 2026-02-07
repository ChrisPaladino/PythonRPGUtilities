"""
Constants and enums for Microscope Solo Play Application
"""
from enum import Enum


class Tone(Enum):
    """Period/Event tone: Light or Dark"""
    LIGHT = "Light"
    DARK = "Dark"


class GamePhase(Enum):
    """Current phase of the game"""
    SETUP_BIG_PICTURE = "Setup: Big Picture"
    SETUP_BOOKENDS = "Setup: Bookend Periods"
    SETUP_PALETTE = "Setup: Palette"
    SETUP_FIRST_PASS = "Setup: First Pass"
    PLAY_DECLARE_FOCUS = "Play: Declare Focus"
    PLAY_MAKE_HISTORY = "Play: Make History"
    PLAY_LENS_ACTION = "Play: Lens Final Action"
    PLAY_CREATE_LEGACY = "Play: Create Legacy"
    PLAY_EXPLORE_LEGACY = "Play: Explore Legacy"
    GAME_COMPLETE = "Game Complete"


class ActionType(Enum):
    """Available player actions during Make History"""
    CREATE_PERIOD = "Create Period"
    CREATE_EVENT = "Create Event"
    CREATE_SCENE = "Create Scene"
    COMPLETE_FOCUS = "Complete Focus"


# UI Colors
LIGHT_COLOR = "#F0E68C"  # Khaki/light yellow
DARK_COLOR = "#708090"   # Slate gray
NEUTRAL_COLOR = "#F5F5DC"  # Beige
FOCUS_COLOR = "#FFD700"  # Gold highlight
LEGACY_COLOR = "#DDA0DD"  # Plum
