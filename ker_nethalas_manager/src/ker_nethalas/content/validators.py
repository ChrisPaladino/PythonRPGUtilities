from __future__ import annotations

from typing import Any


class ContentValidationError(ValueError):
    pass


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ContentValidationError(message)


def _ensure_int(value: Any, field: str, context: str) -> None:
    _ensure(isinstance(value, int), f"{context}: '{field}' must be an integer")


def _ensure_str(value: Any, field: str, context: str) -> None:
    _ensure(isinstance(value, str) and value != "", f"{context}: '{field}' must be a non-empty string")


def _validate_defensive_moves(payload: dict[str, Any]) -> None:
    context = "defensive_moves"
    for table_name in ["player", "npc"]:
        table = payload.get(table_name)
        _ensure(isinstance(table, dict), f"{context}: missing object '{table_name}'")
        for roll in range(1, 11):
            key = str(roll)
            row = table.get(key)
            _ensure(isinstance(row, dict), f"{context}.{table_name}: missing row '{key}'")
            _ensure_str(row.get("effect_id"), "effect_id", f"{context}.{table_name}.{key}")
            _ensure_str(row.get("summary"), "summary", f"{context}.{table_name}.{key}")


def _validate_enemies(payload: dict[str, Any]) -> None:
    context = "enemies"
    creatures = payload.get("creatures")
    _ensure(isinstance(creatures, dict) and creatures, f"{context}: 'creatures' must be a non-empty object")

    for creature_id, creature in creatures.items():
        _ensure_str(creature_id, "creature_id", context)
        _ensure(isinstance(creature, dict), f"{context}.{creature_id}: creature entry must be an object")
        _ensure_str(creature.get("name"), "name", f"{context}.{creature_id}")
        actions = creature.get("actions")
        _ensure(isinstance(actions, list) and actions, f"{context}.{creature_id}: 'actions' must be a non-empty array")

        seen = set()
        for idx, action in enumerate(actions):
            row_ctx = f"{context}.{creature_id}.actions[{idx}]"
            _ensure(isinstance(action, dict), f"{row_ctx}: action entry must be an object")
            for field in [
                "action_id",
                "name",
                "action_type",
                "defense_or_check",
                "damage_die",
                "damage_type",
                "secondary_effect",
            ]:
                if field in ["damage_die", "damage_type", "secondary_effect"]:
                    _ensure(isinstance(action.get(field), str), f"{row_ctx}: '{field}' must be a string")
                else:
                    _ensure_str(action.get(field), field, row_ctx)

            _ensure_int(action.get("roll_min"), "roll_min", row_ctx)
            _ensure_int(action.get("roll_max"), "roll_max", row_ctx)
            roll_min = action["roll_min"]
            roll_max = action["roll_max"]
            _ensure(1 <= roll_min <= 6, f"{row_ctx}: 'roll_min' out of range 1..6")
            _ensure(1 <= roll_max <= 6, f"{row_ctx}: 'roll_max' out of range 1..6")
            _ensure(roll_min <= roll_max, f"{row_ctx}: 'roll_min' cannot exceed 'roll_max'")

            for point in range(roll_min, roll_max + 1):
                _ensure(point not in seen, f"{row_ctx}: overlapping roll range at {point}")
                seen.add(point)

        # Action table should map full d6 range.
        _ensure(seen == {1, 2, 3, 4, 5, 6}, f"{context}.{creature_id}: action ranges must cover 1..6 exactly")


def _validate_difficulty(payload: dict[str, Any]) -> None:
    context = "difficulty_modifiers"
    _ensure(payload.get("die") == "d8", f"{context}: 'die' must be 'd8'")
    entries = payload.get("entries")
    _ensure(isinstance(entries, list) and entries, f"{context}: 'entries' must be a non-empty array")

    seen = set()
    for idx, entry in enumerate(entries):
        row_ctx = f"{context}.entries[{idx}]"
        _ensure(isinstance(entry, dict), f"{row_ctx}: entry must be an object")
        _ensure_int(entry.get("roll_min"), "roll_min", row_ctx)
        _ensure_int(entry.get("roll_max"), "roll_max", row_ctx)
        _ensure_str(entry.get("name"), "name", row_ctx)
        _ensure_int(entry.get("modifier"), "modifier", row_ctx)

        roll_min = entry["roll_min"]
        roll_max = entry["roll_max"]
        _ensure(1 <= roll_min <= 8, f"{row_ctx}: 'roll_min' out of range 1..8")
        _ensure(1 <= roll_max <= 8, f"{row_ctx}: 'roll_max' out of range 1..8")
        _ensure(roll_min <= roll_max, f"{row_ctx}: 'roll_min' cannot exceed 'roll_max'")

        for point in range(roll_min, roll_max + 1):
            _ensure(point not in seen, f"{row_ctx}: overlapping roll range at {point}")
            seen.add(point)

    _ensure(seen == {1, 2, 3, 4, 5, 6, 7, 8}, f"{context}: entries must cover 1..8 exactly")


def _validate_critical_effects(payload: dict[str, Any]) -> None:
    context = "critical_effects"
    effects = payload.get("effects")
    _ensure(isinstance(effects, dict) and effects, f"{context}: 'effects' must be a non-empty object")

    for skill_id, skill_effects in effects.items():
        row_ctx = f"{context}.{skill_id}"
        _ensure_str(skill_id, "skill_id", context)
        _ensure(isinstance(skill_effects, dict), f"{row_ctx}: entry must be an object")
        _ensure_str(skill_effects.get("critical_success"), "critical_success", row_ctx)
        _ensure_str(skill_effects.get("critical_failure"), "critical_failure", row_ctx)


def validate_content_payload(filename: str, payload: dict[str, Any]) -> None:
    _ensure(isinstance(payload, dict), f"{filename}: root must be an object")

    if filename == "defensive_moves.json":
        _validate_defensive_moves(payload)
        return

    if filename == "enemies.json":
        _validate_enemies(payload)
        return

    if filename == "difficulty_modifiers.json":
        _validate_difficulty(payload)
        return

    if filename == "critical_effects.json":
        _validate_critical_effects(payload)
        return

    raise ContentValidationError(f"No validator configured for file: {filename}")
