"""
Game State Manager for Microscope Solo Play
Handles phase transitions, rule enforcement, and state validation
"""
from typing import Optional, List, Tuple
from models import History, Period, Event, Scene, Focus, Legacy, Palette, Character
from constants import GamePhase, Tone
from uuid import UUID


class GameState:
    """Manages game state and phase transitions"""
    
    def __init__(self):
        self.history = History()
        self.current_phase = GamePhase.SETUP_BIG_PICTURE
        self.current_focus: Optional[Focus] = None
        self.pending_legacy: Optional[Legacy] = None
        
    # ===== Setup Phase Methods =====
    
    def set_big_picture(self, big_picture: str) -> bool:
        """Set the Big Picture and advance to bookends"""
        if self.current_phase != GamePhase.SETUP_BIG_PICTURE:
            return False
        if not big_picture.strip():
            return False
        
        self.history.big_picture = big_picture
        self.current_phase = GamePhase.SETUP_BOOKENDS
        return True
    
    def create_bookend_period(self, title: str, description: str, tone: Tone, is_start: bool) -> Optional[UUID]:
        """Create a start or end Period"""
        if self.current_phase != GamePhase.SETUP_BOOKENDS:
            return None
        
        period = Period(
            title=title,
            description=description,
            tone=tone,
            is_bookend=True,
            chronological_index=0 if is_start else 1000000  # Start at 0, end at large number
        )
        
        self.history.add_period(period)
        
        if is_start:
            self.history.start_period_id = period.id
        else:
            self.history.end_period_id = period.id
        
        # If both bookends created, advance to palette
        if self.history.start_period_id and self.history.end_period_id:
            self.current_phase = GamePhase.SETUP_PALETTE
        
        return period.id
    
    def add_to_palette(self, item: str, is_yes: bool) -> bool:
        """Add item to Yes or No palette"""
        if self.current_phase != GamePhase.SETUP_PALETTE:
            return False
        
        if is_yes:
            self.history.palette.add_yes(item)
        else:
            self.history.palette.add_no(item)
        return True
    
    def complete_palette(self) -> bool:
        """Lock palette and advance to First Pass"""
        if self.current_phase != GamePhase.SETUP_PALETTE:
            return False
        
        self.history.palette.lock()
        self.current_phase = GamePhase.SETUP_FIRST_PASS
        return True
    
    def complete_first_pass(self) -> bool:
        """Complete First Pass and advance to Play phase"""
        if self.current_phase != GamePhase.SETUP_FIRST_PASS:
            return False
        
        self.current_phase = GamePhase.PLAY_DECLARE_FOCUS
        return True
    
    # ===== Play Phase Methods =====
    
    def declare_focus(self, description: str) -> Optional[UUID]:
        """Declare a new Focus and enter Make History"""
        if self.current_phase != GamePhase.PLAY_DECLARE_FOCUS:
            return None
        if not description.strip():
            return None
        
        focus = Focus(
            description=description,
            chosen_at_turn=self.history.turn_counter
        )
        self.history.foci.append(focus)
        self.current_focus = focus
        self.current_phase = GamePhase.PLAY_MAKE_HISTORY
        return focus.id
    
    def create_period(self, title: str, description: str, tone: Tone, insert_after_index: int) -> Optional[UUID]:
        """Create a new Period during play"""
        allowed_phases = [GamePhase.SETUP_FIRST_PASS, GamePhase.PLAY_MAKE_HISTORY]
        if self.current_phase not in allowed_phases:
            return None
        
        # Calculate chronological index
        # Insert between the period at insert_after_index and the next one
        periods = self.history.periods
        if insert_after_index < 0 or insert_after_index >= len(periods):
            return None
        
        prev_period = periods[insert_after_index]
        next_period = periods[insert_after_index + 1] if insert_after_index + 1 < len(periods) else None
        
        if next_period:
            new_index = (prev_period.chronological_index + next_period.chronological_index) // 2
        else:
            new_index = prev_period.chronological_index + 1000
        
        period = Period(
            title=title,
            description=description,
            tone=tone,
            chronological_index=new_index
        )
        
        self.history.add_period(period)
        return period.id
    
    def create_event(self, title: str, description: str, tone: Tone, period_id: UUID) -> Optional[UUID]:
        """Create a new Event within a Period"""
        allowed_phases = [GamePhase.SETUP_FIRST_PASS, GamePhase.PLAY_MAKE_HISTORY]
        if self.current_phase not in allowed_phases:
            return None
        
        period = self.history.get_period(period_id)
        if not period:
            return None
        
        # Calculate chronological index within period
        if period.events:
            new_index = max(e.chronological_index for e in period.events) + 1
        else:
            new_index = 0
        
        event = Event(
            title=title,
            description=description,
            tone=tone,
            chronological_index=new_index
        )
        
        period.add_event(event)
        self.history.turn_counter += 1
        return event.id
    
    def create_scene(self, scene: Scene, event_id: UUID) -> Optional[UUID]:
        """Create a new Scene within an Event"""
        if self.current_phase != GamePhase.PLAY_MAKE_HISTORY:
            return None
        
        event = self.history.get_event(event_id)
        if not event:
            return None
        
        event.add_scene(scene)
        self.history.turn_counter += 1
        return scene.id
    
    def complete_focus(self) -> bool:
        """Complete the current Focus and move to Legacy creation"""
        if self.current_phase != GamePhase.PLAY_MAKE_HISTORY:
            return False
        
        self.current_phase = GamePhase.PLAY_CREATE_LEGACY
        return True
    
    def create_legacy(self, description: str, origin_element_id: UUID) -> Optional[UUID]:
        """Create a Legacy from played content"""
        if self.current_phase != GamePhase.PLAY_CREATE_LEGACY:
            return None
        if not self.current_focus:
            return None
        
        legacy = Legacy(
            description=description,
            origin_focus_id=self.current_focus.id,
            origin_element_id=origin_element_id
        )
        
        self.history.legacies.append(legacy)
        self.pending_legacy = legacy
        self.current_phase = GamePhase.PLAY_EXPLORE_LEGACY
        return legacy.id
    
    def skip_legacy_creation(self) -> bool:
        """Skip legacy creation and go to next Focus"""
        if self.current_phase != GamePhase.PLAY_CREATE_LEGACY:
            return False
        
        self.current_focus = None
        self.current_phase = GamePhase.PLAY_DECLARE_FOCUS
        return True
    
    def complete_legacy_exploration(self) -> bool:
        """Complete Legacy exploration and return to Focus declaration"""
        if self.current_phase != GamePhase.PLAY_EXPLORE_LEGACY:
            return False
        
        self.pending_legacy = None
        self.current_focus = None
        self.current_phase = GamePhase.PLAY_DECLARE_FOCUS
        return True
    
    # ===== Validation Methods =====
    
    def validate_palette_compliance(self, content: str) -> Tuple[bool, str]:
        """Check if content violates the palette"""
        content_lower = content.lower()
        
        # Check No items
        for no_item in self.history.palette.no_items:
            if no_item.lower() in content_lower:
                return False, f"Content violates Palette: '{no_item}' is in the No list"
        
        return True, "Palette compliant"
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions for current phase"""
        phase_actions = {
            GamePhase.SETUP_BIG_PICTURE: ["Enter Big Picture"],
            GamePhase.SETUP_BOOKENDS: ["Create Start Period", "Create End Period"],
            GamePhase.SETUP_PALETTE: ["Add to Yes List", "Add to No List", "Complete Palette"],
            GamePhase.SETUP_FIRST_PASS: ["Create Period", "Create Event", "Complete First Pass"],
            GamePhase.PLAY_DECLARE_FOCUS: ["Declare Focus"],
            GamePhase.PLAY_MAKE_HISTORY: ["Create Period", "Create Event", "Create Scene", "Complete Focus"],
            GamePhase.PLAY_CREATE_LEGACY: ["Create Legacy", "Skip Legacy"],
            GamePhase.PLAY_EXPLORE_LEGACY: ["Explore Legacy (Create Event/Scene)"],
        }
        
        return phase_actions.get(self.current_phase, [])
    
    def get_phase_instructions(self) -> str:
        """Get instructions for current phase"""
        instructions = {
            GamePhase.SETUP_BIG_PICTURE: "Enter the Big Picture: A brief description of your history (1-2 sentences).",
            GamePhase.SETUP_BOOKENDS: "Create the Start and End Periods that bookend your history. Each needs a title, description, and tone (Light/Dark).",
            GamePhase.SETUP_PALETTE: "Build your Palette. Add items to the 'Yes' list (things that must exist) and 'No' list (things that cannot exist). Click 'Complete Palette' when done.",
            GamePhase.SETUP_FIRST_PASS: "First Pass: Add some Periods and Events to flesh out your timeline. No Scenes yet. Click 'Complete First Pass' when ready to begin play.",
            GamePhase.PLAY_DECLARE_FOCUS: "Declare a Focus: Choose a theme, question, or element to explore in this round.",
            GamePhase.PLAY_MAKE_HISTORY: "Make History: Create Periods, Events, or Scenes related to your Focus. Click 'Complete Focus' when done exploring this Focus.",
            GamePhase.PLAY_CREATE_LEGACY: "Create a Legacy based on what you discovered during this Focus, or skip to next Focus.",
            GamePhase.PLAY_EXPLORE_LEGACY: "Explore your Legacy by creating an Event or dictated Scene related to it.",
        }
        
        return instructions.get(self.current_phase, "")
    
    # ===== Persistence Methods =====
    
    def to_dict(self) -> dict:
        """Serialize game state to dict"""
        return {
            "history": self.history.to_dict(),
            "current_phase": self.current_phase.value,
            "current_focus": self.current_focus.to_dict() if self.current_focus else None,
            "pending_legacy": self.pending_legacy.to_dict() if self.pending_legacy else None
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'GameState':
        """Deserialize game state from dict"""
        state = GameState()
        state.history = History.from_dict(data["history"])
        state.current_phase = GamePhase(data["current_phase"])
        
        if data.get("current_focus"):
            state.current_focus = Focus.from_dict(data["current_focus"])
        
        if data.get("pending_legacy"):
            state.pending_legacy = Legacy.from_dict(data["pending_legacy"])
        
        return state
