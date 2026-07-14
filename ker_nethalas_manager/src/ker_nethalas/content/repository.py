from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

from ker_nethalas.content.validators import validate_content_payload


SUPPORTED_CONTENT_FILES = (
    "defensive_moves.json",
    "enemies.json",
    "difficulty_modifiers.json",
    "critical_effects.json",
)


def _content_dir() -> Path:
    return Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def load_content_json(filename: str) -> dict:
    path = _content_dir() / filename
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    validate_content_payload(filename, payload)
    return payload


def validate_all_content() -> None:
    for filename in SUPPORTED_CONTENT_FILES:
        load_content_json(filename)


def get_creature_actions(creature_id: str) -> list[dict]:
    payload = load_content_json("enemies.json")
    creatures = payload.get("creatures", {})
    creature = creatures.get(creature_id)
    if creature is None:
        raise ValueError(f"Unknown creature id: {creature_id}")

    actions = creature.get("actions", [])
    if not actions:
        raise ValueError(f"Creature has no actions: {creature_id}")

    return actions


def get_difficulty_for_d8_roll(roll: int) -> dict:
    if roll < 1 or roll > 8:
        raise ValueError("Difficulty roll must be in range 1..8.")

    payload = load_content_json("difficulty_modifiers.json")
    for entry in payload.get("entries", []):
        if entry["roll_min"] <= roll <= entry["roll_max"]:
            return entry

    raise ValueError("Difficulty table is missing a mapping for this roll.")


def get_critical_effect(skill_id: str, outcome: str) -> str | None:
    payload = load_content_json("critical_effects.json")
    effects = payload.get("effects", {})
    skill = effects.get(skill_id)
    if skill is None:
        return None

    text = skill.get(outcome)
    if isinstance(text, str) and text:
        return text
    return None
