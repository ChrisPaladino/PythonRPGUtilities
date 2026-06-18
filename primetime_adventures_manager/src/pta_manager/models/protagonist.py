from dataclasses import dataclass, field
from .trait import Trait


@dataclass
class Protagonist:
    id: str
    name: str
    issue: str
    impulse: str
    # Legacy field kept for save compatibility; scene resolution uses screen_presence_track.
    screen_presence: int = 1
    screen_presence_track: list[int] = field(default_factory=lambda: [1, 2, 3, 2, 1])
    fan_mail: int = 0
    traits: list[Trait] = field(default_factory=list)  # exactly 3

    def get_screen_presence_for_scene(self, scene_number: int) -> int:
        if not self.screen_presence_track:
            return max(1, min(3, self.screen_presence))
        index = max(0, min(scene_number - 1, len(self.screen_presence_track) - 1))
        return max(1, min(3, int(self.screen_presence_track[index])))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "issue": self.issue,
            "impulse": self.impulse,
            "screen_presence": self.screen_presence,
            "screen_presence_track": self.screen_presence_track,
            "fan_mail": self.fan_mail,
            "traits": [
                {"name": t.name, "type": t.type, "used_in_scene": t.used_in_scene}
                for t in self.traits
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Protagonist":
        traits = [Trait(**t) for t in data.get("traits", [])]
        track = data.get("screen_presence_track")
        if not track:
            # Backwards-compatible default if loading old saves.
            base = int(data.get("screen_presence", 1))
            track = [base, base, base, base, base]
        return cls(
            id=data["id"],
            name=data["name"],
            issue=data["issue"],
            impulse=data["impulse"],
            screen_presence=int(data.get("screen_presence", 1)),
            screen_presence_track=track,
            fan_mail=data.get("fan_mail", 0),
            traits=traits,
        )
