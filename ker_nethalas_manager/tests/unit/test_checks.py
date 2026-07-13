from ker_nethalas.core.enums import CheckOutcome, OpposedWinner
from ker_nethalas.rules.checks import (
    get_critical_effect_text,
    resolve_check,
    resolve_opposed_check,
    resolve_random_difficulty,
)


def test_tc001_core_check_success() -> None:
    result = resolve_check(skill=50, roll=50)
    assert result.outcome in {CheckOutcome.SUCCESS, CheckOutcome.CRITICAL_SUCCESS}


def test_tc002_core_check_failure() -> None:
    result = resolve_check(skill=50, roll=51)
    assert result.outcome in {CheckOutcome.FAILURE, CheckOutcome.CRITICAL_FAILURE}


def test_tc003_opposed_both_succeed_higher_successful_roll_wins() -> None:
    result = resolve_opposed_check(actor_skill=60, actor_roll=44, target_skill=50, target_roll=38)
    assert result.winner == OpposedWinner.ACTOR
    assert result.reason == "actor_critical_success_precedence"


def test_opposed_exact_tie_requires_reroll() -> None:
    result = resolve_opposed_check(actor_skill=60, actor_roll=34, target_skill=60, target_roll=34)
    assert result.winner == OpposedWinner.NONE
    assert result.tie_reroll_required is True
    assert result.reason == "tie_reroll_required"


def test_double_equal_to_skill_is_regular_success_not_critical() -> None:
    result = resolve_check(skill=44, roll=44)
    assert result.outcome == CheckOutcome.SUCCESS


def test_success_tie_uses_higher_skill_before_reroll() -> None:
    result = resolve_opposed_check(actor_skill=65, actor_roll=34, target_skill=60, target_roll=34)
    assert result.winner == OpposedWinner.ACTOR
    assert result.reason == "higher_skill_breaks_success_tie"


def test_both_fail_higher_roll_wins() -> None:
    result = resolve_opposed_check(actor_skill=20, actor_roll=70, target_skill=25, target_roll=65)
    assert result.winner == OpposedWinner.ACTOR
    assert result.reason == "higher_failed_roll"


def test_both_fail_tie_uses_higher_skill() -> None:
    result = resolve_opposed_check(actor_skill=30, actor_roll=70, target_skill=25, target_roll=70)
    assert result.winner == OpposedWinner.ACTOR
    assert result.reason == "higher_skill_breaks_failure_tie"


def test_difficulty_roll_maps_to_normal() -> None:
    name, modifier = resolve_random_difficulty(4)
    assert name == "Normal"
    assert modifier == 0


def test_difficulty_roll_maps_to_impossible() -> None:
    name, modifier = resolve_random_difficulty(8)
    assert name == "Impossible"
    assert modifier == -30


def test_critical_effect_text_for_perception_success() -> None:
    text = get_critical_effect_text("perception", CheckOutcome.CRITICAL_SUCCESS)
    assert text is not None
    assert "Advantage" in text


def test_critical_effect_text_for_non_critical_is_none() -> None:
    text = get_critical_effect_text("perception", CheckOutcome.SUCCESS)
    assert text is None
