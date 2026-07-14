from ker_nethalas.content.validators import ContentValidationError, validate_content_payload


def test_validate_difficulty_payload_ok() -> None:
    payload = {
        "die": "d8",
        "entries": [
            {"roll_min": 1, "roll_max": 1, "name": "A", "modifier": 30},
            {"roll_min": 2, "roll_max": 2, "name": "B", "modifier": 20},
            {"roll_min": 3, "roll_max": 3, "name": "C", "modifier": 10},
            {"roll_min": 4, "roll_max": 5, "name": "D", "modifier": 0},
            {"roll_min": 6, "roll_max": 6, "name": "E", "modifier": -10},
            {"roll_min": 7, "roll_max": 7, "name": "F", "modifier": -20},
            {"roll_min": 8, "roll_max": 8, "name": "G", "modifier": -30},
        ],
    }

    validate_content_payload("difficulty_modifiers.json", payload)


def test_validate_difficulty_payload_overlap_fails() -> None:
    payload = {
        "die": "d8",
        "entries": [
            {"roll_min": 1, "roll_max": 2, "name": "A", "modifier": 30},
            {"roll_min": 2, "roll_max": 8, "name": "B", "modifier": 0},
        ],
    }

    try:
        validate_content_payload("difficulty_modifiers.json", payload)
        assert False, "Expected ContentValidationError"
    except ContentValidationError as exc:
        assert "overlapping" in str(exc)


def test_validate_enemies_payload_missing_roll_coverage_fails() -> None:
    payload = {
        "creatures": {
            "dummy": {
                "name": "Dummy",
                "actions": [
                    {
                        "action_id": "a1",
                        "roll_min": 1,
                        "roll_max": 5,
                        "name": "Action",
                        "action_type": "physical",
                        "defense_or_check": "attack",
                        "damage_die": "d6",
                        "damage_type": "slashing",
                        "secondary_effect": "",
                    }
                ],
            }
        }
    }

    try:
        validate_content_payload("enemies.json", payload)
        assert False, "Expected ContentValidationError"
    except ContentValidationError as exc:
        assert "cover 1..6" in str(exc)


def test_validate_critical_effects_missing_field_fails() -> None:
    payload = {
        "effects": {
            "perception": {
                "critical_success": "ok"
            }
        }
    }

    try:
        validate_content_payload("critical_effects.json", payload)
        assert False, "Expected ContentValidationError"
    except ContentValidationError as exc:
        assert "critical_failure" in str(exc)
