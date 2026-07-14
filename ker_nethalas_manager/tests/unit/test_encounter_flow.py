from random import Random

from ker_nethalas.rules.combat import (
    CombatantState,
    EncounterState,
    EnemyTargetAssignments,
    apply_defensive_move_effect,
    resolve_player_defensive_move,
    resolve_enemy_turn,
)


def _build_base_encounter() -> EncounterState:
    combatants = {
        "horror_a": CombatantState(
            combatant_id="horror_a",
            side="enemy",
            creature_id="skeletal_horror",
            health_current=8,
            toughness_current=0,
            combat_skill=40,
            dodge_skill=0,
            spellward=0,
        ),
        "seraphine": CombatantState(
            combatant_id="seraphine",
            side="pc",
            creature_id=None,
            health_current=15,
            toughness_current=3,
            combat_skill=60,
            dodge_skill=40,
            spellward=20,
        ),
        "raised_skeleton": CombatantState(
            combatant_id="raised_skeleton",
            side="minion",
            creature_id="raised_skeleton",
            health_current=4,
            toughness_current=0,
            combat_skill=20,
            dodge_skill=20,
            spellward=0,
        ),
    }

    assignments = EnemyTargetAssignments(enemy_to_target={"horror_a": "seraphine"}, locked=True)
    return EncounterState(round_number=1, combatants=combatants, target_assignments=assignments, combat_log=[])


def test_enemy_turn_physical_hit_applies_placeholder_damage() -> None:
    encounter = _build_base_encounter()

    result = resolve_enemy_turn(
        encounter=encounter,
        enemy_id="horror_a",
        action_roll=1,
        attacker_roll=30,
        defender_roll=95,
    )

    assert result.action_type == "physical"
    assert result.attack_resolution is not None
    assert result.attack_resolution.attacker_hits is True
    assert encounter.combatants["seraphine"].toughness_current == 2


def test_enemy_turn_defender_wins_triggers_player_defensive_move() -> None:
    encounter = _build_base_encounter()

    result = resolve_enemy_turn(
        encounter=encounter,
        enemy_id="horror_a",
        action_roll=1,
        attacker_roll=95,
        defender_roll=20,
        defensive_move_roll=9,
        rng=Random(5),
    )

    assert result.attack_resolution is not None
    assert result.attack_resolution.defender_makes_defensive_move is True
    assert result.defensive_move is not None
    assert result.defensive_move.effect_id == "recover_2_toughness"
    assert encounter.combatants["seraphine"].toughness_current == 5


def test_enemy_turn_magical_action_uses_spellward() -> None:
    encounter = _build_base_encounter()

    result = resolve_enemy_turn(
        encounter=encounter,
        enemy_id="horror_a",
        action_roll=5,
        attacker_roll=None,
        defender_roll=10,
    )

    assert result.action_type == "magical"
    assert result.attack_resolution is None
    assert encounter.combatants["seraphine"].health_current == 15


def test_apply_defensive_move_bleeding_effect() -> None:
    encounter = _build_base_encounter()
    effect = resolve_player_defensive_move(3)

    lines = apply_defensive_move_effect(
        encounter=encounter,
        effect=effect,
        defender_id="seraphine",
        opponent_id="horror_a",
    )

    assert encounter.combatants["horror_a"].bleeding == 1
    assert len(lines) >= 1
