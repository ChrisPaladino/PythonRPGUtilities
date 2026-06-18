"""
Resolution service — core conflict resolution logic.

Accepts either dice results (DieResult list) or card results (card dict list)
and applies the PTA outcome table.
"""
from pta_manager.models.resolution import DieResult, ResolutionResult
from pta_manager.services.card_service import is_red, card_value


def _count_evens_dice(rolls: list[DieResult]) -> int:
    return sum(1 for r in rolls if r.value % 2 == 0)


def _highest_die(rolls: list[DieResult]) -> int:
    return max((r.value for r in rolls), default=0)


def _count_red_cards(cards: list[dict]) -> int:
    return sum(1 for c in cards if is_red(c))


def _highest_card(cards: list[dict]) -> int:
    return max((card_value(c) for c in cards), default=0)


def _determine_outcome(
    protagonist_successes: int,
    producer_successes: int,
    protagonist_highest: int,
    producer_highest: int,
) -> str:
    more_successes = protagonist_successes > producer_successes
    higher_die = protagonist_highest > producer_highest

    if more_successes and higher_die:
        return "YES AND"
    if more_successes and not higher_die:
        return "YES BUT"
    if not more_successes and higher_die:
        return "NO BUT"
    return "NO AND"


def resolve_dice(
    protagonist_id: str,
    protagonist_rolls: list[DieResult],
    producer_rolls: list[DieResult],
) -> ResolutionResult:
    p_evens = _count_evens_dice(protagonist_rolls)
    prod_evens = _count_evens_dice(producer_rolls)
    p_high = _highest_die(protagonist_rolls)
    prod_high = _highest_die(producer_rolls)
    outcome = _determine_outcome(p_evens, prod_evens, p_high, prod_high)
    return ResolutionResult(
        protagonist_id=protagonist_id,
        even_count_protagonist=p_evens,
        even_count_producer=prod_evens,
        highest_die_protagonist=p_high,
        highest_die_producer=prod_high,
        outcome=outcome,
    )


def resolve_cards(
    protagonist_id: str,
    protagonist_cards: list[dict],
    producer_cards: list[dict],
) -> ResolutionResult:
    p_reds = _count_red_cards(protagonist_cards)
    prod_reds = _count_red_cards(producer_cards)
    p_high = _highest_card(protagonist_cards)
    prod_high = _highest_card(producer_cards)
    outcome = _determine_outcome(p_reds, prod_reds, p_high, prod_high)
    return ResolutionResult(
        protagonist_id=protagonist_id,
        even_count_protagonist=p_reds,
        even_count_producer=prod_reds,
        highest_die_protagonist=p_high,
        highest_die_producer=prod_high,
        outcome=outcome,
    )
