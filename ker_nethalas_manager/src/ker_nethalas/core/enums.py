from enum import Enum


class RollSource(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"


class CheckOutcome(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    CRITICAL_SUCCESS = "critical_success"
    CRITICAL_FAILURE = "critical_failure"


class OpposedWinner(str, Enum):
    ACTOR = "actor"
    TARGET = "target"
    NONE = "none"
