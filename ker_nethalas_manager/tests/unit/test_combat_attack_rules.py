from ker_nethalas.core.enums import OpposedWinner
from ker_nethalas.rules.combat import (
    resolve_npc_defensive_move,
    resolve_attack_check,
    resolve_initiative_check,
    resolve_player_defensive_move,
    resolve_surprise_attempt,
)


def test_attack_both_fail_causes_unavoidable_damage_to_defender() -> None:
    result = resolve_attack_check(
        attacker_skill=20,
        defender_skill=25,
        attacker_roll=90,
        defender_roll=80,
    )
    assert result.unavoidable_damage_to_defender == 1
    assert result.attacker_hits is False
    assert result.defender_makes_defensive_move is False


def test_attack_attacker_success_can_hit() -> None:
    result = resolve_attack_check(
        attacker_skill=60,
        defender_skill=40,
        attacker_roll=35,
        defender_roll=90,
    )
    assert result.winner == OpposedWinner.ACTOR
    assert result.attacker_hits is True


def test_attack_defender_wins_and_rolls_defensive_move() -> None:
    result = resolve_attack_check(
        attacker_skill=45,
        defender_skill=60,
        attacker_roll=65,
        defender_roll=42,
    )
    assert result.winner == OpposedWinner.TARGET
    assert result.defender_makes_defensive_move is True


def test_attack_critical_success_precedence() -> None:
    result = resolve_attack_check(
        attacker_skill=70,
        defender_skill=80,
        attacker_roll=22,
        defender_roll=50,
    )
    assert result.reason == "attacker_critical_success_precedence"
    assert result.attacker_hits is True


def test_attack_critical_vs_critical_uses_higher_roll_then_skill() -> None:
    result = resolve_attack_check(
        attacker_skill=70,
        defender_skill=80,
        attacker_roll=22,
        defender_roll=33,
    )
    assert result.winner == OpposedWinner.TARGET
    assert result.reason == "higher_successful_roll"


def test_weapon_speed_penalizes_defender_skill() -> None:
    result = resolve_attack_check(
        attacker_skill=50,
        defender_skill=50,
        attacker_roll=45,
        defender_roll=48,
        weapon_speed=10,
    )
    assert result.attacker_hits is True
    assert result.reason == "attacker_success_defender_failure"


def test_initiative_check_returns_winner_side() -> None:
    result = resolve_initiative_check(
        player_perception=50,
        enemy_mind=40,
        player_roll=35,
        enemy_roll=45,
    )
    assert result.winner == OpposedWinner.ACTOR


def test_surprise_success_grants_first_attack_bonus() -> None:
    result = resolve_surprise_attempt(
        player_stealth=60,
        enemy_mind=40,
        player_roll=35,
        enemy_roll=80,
        follower_count=1,
    )
    assert result.surprise_success is True
    assert result.first_attack_bonus == 20
    assert result.initiative_owner == "player_side"


def test_surprise_failure_applies_initiative_penalty() -> None:
    result = resolve_surprise_attempt(
        player_stealth=40,
        enemy_mind=60,
        player_roll=70,
        enemy_roll=40,
        follower_count=0,
    )
    assert result.surprise_success is False
    assert result.initiative_perception_modifier == -20


def test_player_defensive_move_roll_1() -> None:
    outcome = resolve_player_defensive_move(1)
    assert outcome.table == "player"
    assert outcome.effect_id == "next_attack_plus_10"


def test_player_defensive_move_roll_10() -> None:
    outcome = resolve_player_defensive_move(10)
    assert outcome.effect_id == "next_called_shot_no_disadvantage"


def test_npc_defensive_move_roll_1() -> None:
    outcome = resolve_npc_defensive_move(1)
    assert outcome.table == "npc"
    assert outcome.effect_id == "next_attack_plus_10_or_spellward_minus_10"


def test_npc_defensive_move_roll_10() -> None:
    outcome = resolve_npc_defensive_move(10)
    assert outcome.effect_id == "immediate_new_turn"


def test_defensive_move_invalid_roll_raises() -> None:
    try:
        resolve_player_defensive_move(0)
        assert False, "Expected ValueError for invalid d10 roll"
    except ValueError as exc:
        assert "1..10" in str(exc)
