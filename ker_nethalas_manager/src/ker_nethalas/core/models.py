from dataclasses import dataclass, field

from ker_nethalas.core.enums import CheckOutcome, OpposedWinner, RollSource


@dataclass(frozen=True)
class RollResult:
    roll: int
    sides: int
    source: RollSource


@dataclass(frozen=True)
class CheckResult:
    target: int
    roll: int
    outcome: CheckOutcome
    modifiers: list[int] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.outcome in {CheckOutcome.SUCCESS, CheckOutcome.CRITICAL_SUCCESS}


@dataclass(frozen=True)
class OpposedCheckResult:
    actor: CheckResult
    target: CheckResult
    winner: OpposedWinner
    reason: str
    tie_reroll_required: bool = False
