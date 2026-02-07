"""
Data models for Microscope Solo Play Application
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from uuid import UUID, uuid4
from constants import Tone


@dataclass
class Palette:
    """Yes/No items that constrain history creation"""
    yes_items: List[str] = field(default_factory=list)
    no_items: List[str] = field(default_factory=list)
    is_locked: bool = False
    
    def add_yes(self, item: str) -> None:
        """Add item to Yes list"""
        if not self.is_locked and item not in self.yes_items:
            self.yes_items.append(item)
    
    def add_no(self, item: str) -> None:
        """Add item to No list"""
        if not self.is_locked and item not in self.no_items:
            self.no_items.append(item)
    
    def lock(self) -> None:
        """Lock palette after setup completion"""
        self.is_locked = True
    
    def to_dict(self) -> dict:
        return {
            "yes_items": self.yes_items,
            "no_items": self.no_items,
            "is_locked": self.is_locked
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Palette':
        palette = Palette()
        palette.yes_items = data.get("yes_items", [])
        palette.no_items = data.get("no_items", [])
        palette.is_locked = data.get("is_locked", False)
        return palette


@dataclass
class Character:
    """Character appearing in a Scene"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Character':
        return Character(
            id=UUID(data["id"]),
            name=data["name"],
            description=data.get("description", "")
        )


@dataclass
class Scene:
    """A scene nested under an Event"""
    id: UUID = field(default_factory=uuid4)
    question: str = ""
    event_id: Optional[UUID] = None
    is_dictated: bool = False
    stage_description: str = ""
    characters: List[Character] = field(default_factory=list)
    revealed_thoughts: Dict[UUID, str] = field(default_factory=dict)  # Character ID -> thought
    answer: str = ""
    is_complete: bool = False
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "question": self.question,
            "event_id": str(self.event_id) if self.event_id else None,
            "is_dictated": self.is_dictated,
            "stage_description": self.stage_description,
            "characters": [c.to_dict() for c in self.characters],
            "revealed_thoughts": {str(k): v for k, v in self.revealed_thoughts.items()},
            "answer": self.answer,
            "is_complete": self.is_complete
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Scene':
        return Scene(
            id=UUID(data["id"]),
            question=data["question"],
            event_id=UUID(data["event_id"]) if data.get("event_id") else None,
            is_dictated=data.get("is_dictated", False),
            stage_description=data.get("stage_description", ""),
            characters=[Character.from_dict(c) for c in data.get("characters", [])],
            revealed_thoughts={UUID(k): v for k, v in data.get("revealed_thoughts", {}).items()},
            answer=data.get("answer", ""),
            is_complete=data.get("is_complete", False)
        )


@dataclass
class Event:
    """An Event nested under a Period"""
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    tone: Tone = Tone.LIGHT
    period_id: Optional[UUID] = None
    chronological_index: int = 0
    scenes: List[Scene] = field(default_factory=list)
    
    def add_scene(self, scene: Scene) -> None:
        """Add a scene to this event"""
        scene.event_id = self.id
        self.scenes.append(scene)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "tone": self.tone.value,
            "period_id": str(self.period_id) if self.period_id else None,
            "chronological_index": self.chronological_index,
            "scenes": [s.to_dict() for s in self.scenes]
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Event':
        return Event(
            id=UUID(data["id"]),
            title=data["title"],
            description=data["description"],
            tone=Tone(data["tone"]),
            period_id=UUID(data["period_id"]) if data.get("period_id") else None,
            chronological_index=data.get("chronological_index", 0),
            scenes=[Scene.from_dict(s) for s in data.get("scenes", [])]
        )


@dataclass
class Period:
    """A Period in the timeline"""
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    tone: Tone = Tone.LIGHT
    chronological_index: int = 0
    events: List[Event] = field(default_factory=list)
    is_bookend: bool = False  # True for start/end periods
    
    def add_event(self, event: Event) -> None:
        """Add an event to this period"""
        event.period_id = self.id
        self.events.append(event)
        # Re-sort events by chronological index
        self.events.sort(key=lambda e: e.chronological_index)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "tone": self.tone.value,
            "chronological_index": self.chronological_index,
            "events": [e.to_dict() for e in self.events],
            "is_bookend": self.is_bookend
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Period':
        return Period(
            id=UUID(data["id"]),
            title=data["title"],
            description=data["description"],
            tone=Tone(data["tone"]),
            chronological_index=data.get("chronological_index", 0),
            events=[Event.from_dict(e) for e in data.get("events", [])],
            is_bookend=data.get("is_bookend", False)
        )


@dataclass
class Focus:
    """A Focus declared at the start of each round"""
    id: UUID = field(default_factory=uuid4)
    description: str = ""
    chosen_at_turn: int = 0
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "description": self.description,
            "chosen_at_turn": self.chosen_at_turn
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Focus':
        return Focus(
            id=UUID(data["id"]),
            description=data["description"],
            chosen_at_turn=data.get("chosen_at_turn", 0)
        )


@dataclass
class Legacy:
    """A Legacy created from played content"""
    id: UUID = field(default_factory=uuid4)
    description: str = ""
    origin_focus_id: UUID = field(default_factory=uuid4)
    origin_element_id: Optional[UUID] = None  # Period, Event, or Scene ID
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "description": self.description,
            "origin_focus_id": str(self.origin_focus_id),
            "origin_element_id": str(self.origin_element_id) if self.origin_element_id else None
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Legacy':
        return Legacy(
            id=UUID(data["id"]),
            description=data["description"],
            origin_focus_id=UUID(data["origin_focus_id"]),
            origin_element_id=UUID(data["origin_element_id"]) if data.get("origin_element_id") else None
        )


@dataclass
class History:
    """The complete game history"""
    big_picture: str = ""
    start_period_id: Optional[UUID] = None
    end_period_id: Optional[UUID] = None
    palette: Palette = field(default_factory=Palette)
    periods: List[Period] = field(default_factory=list)
    foci: List[Focus] = field(default_factory=list)
    legacies: List[Legacy] = field(default_factory=list)
    current_lens_index: int = 0  # Always 0 for solo
    turn_counter: int = 0
    
    def add_period(self, period: Period) -> None:
        """Add a period and re-sort timeline"""
        self.periods.append(period)
        self.periods.sort(key=lambda p: p.chronological_index)
    
    def get_period(self, period_id: UUID) -> Optional[Period]:
        """Find period by ID"""
        return next((p for p in self.periods if p.id == period_id), None)
    
    def get_event(self, event_id: UUID) -> Optional[Event]:
        """Find event by ID across all periods"""
        for period in self.periods:
            for event in period.events:
                if event.id == event_id:
                    return event
        return None
    
    def get_scene(self, scene_id: UUID) -> Optional[Scene]:
        """Find scene by ID across all events"""
        for period in self.periods:
            for event in period.events:
                for scene in event.scenes:
                    if scene.id == scene_id:
                        return scene
        return None
    
    def to_dict(self) -> dict:
        return {
            "big_picture": self.big_picture,
            "start_period_id": str(self.start_period_id) if self.start_period_id else None,
            "end_period_id": str(self.end_period_id) if self.end_period_id else None,
            "palette": self.palette.to_dict(),
            "periods": [p.to_dict() for p in self.periods],
            "foci": [f.to_dict() for f in self.foci],
            "legacies": [l.to_dict() for l in self.legacies],
            "current_lens_index": self.current_lens_index,
            "turn_counter": self.turn_counter
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'History':
        history = History()
        history.big_picture = data.get("big_picture", "")
        history.start_period_id = UUID(data["start_period_id"]) if data.get("start_period_id") else None
        history.end_period_id = UUID(data["end_period_id"]) if data.get("end_period_id") else None
        history.palette = Palette.from_dict(data.get("palette", {}))
        history.periods = [Period.from_dict(p) for p in data.get("periods", [])]
        history.foci = [Focus.from_dict(f) for f in data.get("foci", [])]
        history.legacies = [Legacy.from_dict(l) for l in data.get("legacies", [])]
        history.current_lens_index = data.get("current_lens_index", 0)
        history.turn_counter = data.get("turn_counter", 0)
        return history
