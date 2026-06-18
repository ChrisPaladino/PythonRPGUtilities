from dataclasses import dataclass, field


@dataclass
class Trait:
    name: str
    type: str  # "edge" or "connection"
    used_in_scene: bool = False
