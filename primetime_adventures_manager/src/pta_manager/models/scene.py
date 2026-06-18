from dataclasses import dataclass, field
from .resolution import ResolutionResult


@dataclass
class Scene:
    id: str
    title: str
    scene_type: str  # "character" or "plot"
    question: str
    participant_ids: list[str] = field(default_factory=list)
    producer_budget_spent: int = 0
    results: dict[str, ResolutionResult] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "scene_type": self.scene_type,
            "question": self.question,
            "participant_ids": self.participant_ids,
            "producer_budget_spent": self.producer_budget_spent,
            "results": {k: v.to_dict() for k, v in self.results.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Scene":
        results = {
            k: ResolutionResult.from_dict(v)
            for k, v in data.get("results", {}).items()
        }
        return cls(
            id=data["id"],
            title=data["title"],
            scene_type=data["scene_type"],
            question=data["question"],
            participant_ids=data.get("participant_ids", []),
            producer_budget_spent=data.get("producer_budget_spent", 0),
            results=results,
        )
