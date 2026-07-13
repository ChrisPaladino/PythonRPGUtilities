from ker_nethalas.core.enums import CheckOutcome, OpposedWinner
from ker_nethalas.core.models import CheckResult, OpposedCheckResult
from ker_nethalas.content.repository import get_critical_effect, get_difficulty_for_d8_roll


def _is_double(roll: int) -> bool:
    return 10 <= roll <= 99 and (roll // 10) == (roll % 10)


def resolve_check(skill: int, roll: int, modifiers: list[int] | None = None) -> CheckResult:
    effective_modifiers = modifiers or []
    target = max(0, min(100, skill + sum(effective_modifiers)))

    if roll < 1 or roll > 100:
        raise ValueError("Percentile roll must be in range 1..100.")

    success = roll <= target
    doubled = _is_double(roll)

    # Rules text: doubles below the tested score are critical success,
    # doubles above it are critical failure.
    if doubled and roll < target:
        outcome = CheckOutcome.CRITICAL_SUCCESS
    elif doubled and roll > target:
        outcome = CheckOutcome.CRITICAL_FAILURE
    elif success:
        outcome = CheckOutcome.SUCCESS
    else:
        outcome = CheckOutcome.FAILURE

    return CheckResult(target=target, roll=roll, outcome=outcome, modifiers=effective_modifiers)


def resolve_opposed_check(
    actor_skill: int,
    actor_roll: int,
    target_skill: int,
    target_roll: int,
    actor_modifiers: list[int] | None = None,
    target_modifiers: list[int] | None = None,
) -> OpposedCheckResult:
    actor_result = resolve_check(actor_skill, actor_roll, actor_modifiers)
    target_result = resolve_check(target_skill, target_roll, target_modifiers)

    actor_success = actor_result.is_success
    target_success = target_result.is_success

    actor_critical_success = actor_result.outcome == CheckOutcome.CRITICAL_SUCCESS
    target_critical_success = target_result.outcome == CheckOutcome.CRITICAL_SUCCESS
    actor_critical_failure = actor_result.outcome == CheckOutcome.CRITICAL_FAILURE
    target_critical_failure = target_result.outcome == CheckOutcome.CRITICAL_FAILURE

    # If one side has a critical failure, it loses immediately.
    if actor_critical_failure and not target_critical_failure:
        return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.TARGET, reason="actor_critical_failure")

    if target_critical_failure and not actor_critical_failure:
        return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.ACTOR, reason="target_critical_failure")

    if actor_success and not target_success:
        return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.ACTOR, reason="actor_success_target_failure")

    if target_success and not actor_success:
        return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.TARGET, reason="target_success_actor_failure")

    # If only one side has a critical success, it wins.
    if actor_critical_success and not target_critical_success:
        return OpposedCheckResult(
            actor=actor_result,
            target=target_result,
            winner=OpposedWinner.ACTOR,
            reason="actor_critical_success_precedence",
        )

    if target_critical_success and not actor_critical_success:
        return OpposedCheckResult(
            actor=actor_result,
            target=target_result,
            winner=OpposedWinner.TARGET,
            reason="target_critical_success_precedence",
        )

    if actor_success and target_success:
        if actor_result.roll > target_result.roll:
            return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.ACTOR, reason="higher_successful_roll")

        if target_result.roll > actor_result.roll:
            return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.TARGET, reason="higher_successful_roll")

        if actor_result.target > target_result.target:
            return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.ACTOR, reason="higher_skill_breaks_success_tie")

        if target_result.target > actor_result.target:
            return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.TARGET, reason="higher_skill_breaks_success_tie")

        return OpposedCheckResult(
            actor=actor_result,
            target=target_result,
            winner=OpposedWinner.NONE,
            reason="tie_reroll_required",
            tie_reroll_required=True,
        )

    # Both failed: highest roll wins, then highest skill, then reroll.
    if actor_result.roll > target_result.roll:
        return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.ACTOR, reason="higher_failed_roll")

    if target_result.roll > actor_result.roll:
        return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.TARGET, reason="higher_failed_roll")

    if actor_result.target > target_result.target:
        return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.ACTOR, reason="higher_skill_breaks_failure_tie")

    if target_result.target > actor_result.target:
        return OpposedCheckResult(actor=actor_result, target=target_result, winner=OpposedWinner.TARGET, reason="higher_skill_breaks_failure_tie")

    return OpposedCheckResult(
        actor=actor_result,
        target=target_result,
        winner=OpposedWinner.NONE,
        reason="tie_reroll_required",
        tie_reroll_required=True,
    )


def resolve_random_difficulty(roll: int) -> tuple[str, int]:
    entry = get_difficulty_for_d8_roll(roll)
    return entry["name"], entry["modifier"]


def get_critical_effect_text(check_id: str, outcome: CheckOutcome) -> str | None:
    if outcome == CheckOutcome.CRITICAL_SUCCESS:
        return get_critical_effect(check_id, "critical_success")
    if outcome == CheckOutcome.CRITICAL_FAILURE:
        return get_critical_effect(check_id, "critical_failure")
    return None
