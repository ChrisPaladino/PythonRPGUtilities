from dataclasses import dataclass, field


@dataclass
class DieResult:
    value: int
    source: str  # "screen_presence", "trait", "fan_mail"


@dataclass
class ResolutionResult:
    protagonist_id: str
    even_count_protagonist: int
    even_count_producer: int
    highest_die_protagonist: int
    highest_die_producer: int
    outcome: str  # "YES AND", "YES BUT", "NO BUT", "NO AND"

    def to_dict(self) -> dict:
        return {
            "protagonist_id": self.protagonist_id,
            "even_count_protagonist": self.even_count_protagonist,
            "even_count_producer": self.even_count_producer,
            "highest_die_protagonist": self.highest_die_protagonist,
            "highest_die_producer": self.highest_die_producer,
            "outcome": self.outcome,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResolutionResult":
        return cls(**data)
