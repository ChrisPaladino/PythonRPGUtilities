from dataclasses import dataclass
from random import Random

from ker_nethalas.content.repository import get_creature_actions, load_content_json
from ker_nethalas.core.enums import CheckOutcome, OpposedWinner
from ker_nethalas.core.models import CheckResult
from ker_nethalas.rules.checks import resolve_check, resolve_opposed_check


@dataclass(frozen=True)
class CreatureAction:
    action_id: str
    creature_id: str
    roll_min: int
    roll_max: int
    name: str
    action_type: str
    defense_or_check: str
    damage_die: str
    damage_type: str
    secondary_effect: str


@dataclass(frozen=True)
class CombatRoundState:
    round_number: int
    acting_side: str
    free_action_available: bool
    standard_actions_remaining: int
    reactions_used: int
    charging_ability_id: str | None


@dataclass(frozen=True)
class ReactionUseResult:
    state: CombatRoundState
    applied_modifier: int


@dataclass(frozen=True)
class MinionTargetPrompt:
    minion_id: str
    must_prompt: bool
    reason: str


@dataclass(frozen=True)
class AttackResolution:
    both_failed: bool
    unavoidable_damage_to_defender: int


@dataclass(frozen=True)
class CriticalFailureResolution:
    apply_extra_effects: bool
    notes: str


@dataclass(frozen=True)
class EnemyTargetAssignments:
    enemy_to_target: dict[str, str]
    locked: bool


@dataclass(frozen=True)
class AttackCheckResolution:
    attacker_result: CheckResult
    defender_result: CheckResult
    winner: OpposedWinner
    attacker_hits: bool
    defender_makes_defensive_move: bool
    unavoidable_damage_to_defender: int
    tie_reroll_required: bool
    reason: str


@dataclass(frozen=True)
class InitiativeResolution:
    result: CheckResult
    opponent_result: CheckResult
    winner: OpposedWinner
    tie_reroll_required: bool


@dataclass(frozen=True)
class SurpriseAttemptResolution:
    surprise_success: bool
    tie_reroll_required: bool
    initiative_owner: str | None
    first_attack_bonus: int
    initiative_perception_modifier: int
    reason: str


@dataclass(frozen=True)
class DefensiveMoveOutcome:
    table: str
    roll: int
    effect_id: str
    summary: str


def start_round(round_number: int, acting_side: str) -> CombatRoundState:
    if round_number < 1:
        raise ValueError("Round number must be >= 1.")

    return CombatRoundState(
        round_number=round_number,
        acting_side=acting_side,
        free_action_available=True,
        standard_actions_remaining=1,
        reactions_used=0,
        charging_ability_id=None,
    )


def take_free_action(state: CombatRoundState) -> CombatRoundState:
    if not state.free_action_available:
        raise ValueError("Free Action already used this round.")

    return CombatRoundState(
        round_number=state.round_number,
        acting_side=state.acting_side,
        free_action_available=False,
        standard_actions_remaining=state.standard_actions_remaining,
        reactions_used=state.reactions_used,
        charging_ability_id=state.charging_ability_id,
    )


def spend_standard_action(state: CombatRoundState, amount: int = 1) -> CombatRoundState:
    if amount <= 0:
        raise ValueError("Standard action amount must be positive.")
    if state.standard_actions_remaining < amount:
        raise ValueError("Not enough Standard Actions remaining.")

    return CombatRoundState(
        round_number=state.round_number,
        acting_side=state.acting_side,
        free_action_available=state.free_action_available,
        standard_actions_remaining=state.standard_actions_remaining - amount,
        reactions_used=state.reactions_used,
        charging_ability_id=state.charging_ability_id,
    )


def begin_charging_ability(state: CombatRoundState, ability_id: str, required_actions: int) -> CombatRoundState:
    if required_actions < 2:
        raise ValueError("Charging only applies to abilities requiring 2+ Standard Actions.")
    if not ability_id:
        raise ValueError("Ability id is required.")
    if state.charging_ability_id is not None and state.charging_ability_id != ability_id:
        raise ValueError("Already charging a different ability.")

    after_spend = spend_standard_action(state, amount=1)
    return CombatRoundState(
        round_number=after_spend.round_number,
        acting_side=after_spend.acting_side,
        free_action_available=after_spend.free_action_available,
        standard_actions_remaining=after_spend.standard_actions_remaining,
        reactions_used=after_spend.reactions_used,
        charging_ability_id=ability_id,
    )


def reaction_modifier_for_next_use(state: CombatRoundState) -> int:
    cumulative = -20 * state.reactions_used
    charging_penalty = -10 if state.charging_ability_id is not None else 0
    return cumulative + charging_penalty


def use_reaction(state: CombatRoundState, reaction_ability_id: str | None = None) -> ReactionUseResult:
    if state.charging_ability_id is not None and reaction_ability_id is not None:
        if reaction_ability_id != state.charging_ability_id:
            raise ValueError("Cannot use a different Ability as a Reaction while charging.")

    modifier = reaction_modifier_for_next_use(state)
    updated = CombatRoundState(
        round_number=state.round_number,
        acting_side=state.acting_side,
        free_action_available=state.free_action_available,
        standard_actions_remaining=state.standard_actions_remaining,
        reactions_used=state.reactions_used + 1,
        charging_ability_id=state.charging_ability_id,
    )

    return ReactionUseResult(state=updated, applied_modifier=modifier)


def choose_creature_action(actions: list[CreatureAction], action_roll: int) -> CreatureAction:
    if action_roll < 1 or action_roll > 6:
        raise ValueError("Creature action roll must be in range 1..6.")

    for action in actions:
        if action.roll_min <= action_roll <= action.roll_max:
            return action

    raise ValueError("No creature action matched the roll.")


def minion_target_prompt(minion_id: str, has_valid_target: bool) -> MinionTargetPrompt:
    # User preference: prompt each minion action, even if a previous target exists.
    if has_valid_target:
        return MinionTargetPrompt(minion_id=minion_id, must_prompt=True, reason="prompt_each_minion_action")

    return MinionTargetPrompt(minion_id=minion_id, must_prompt=True, reason="no_valid_target")


def resolve_physical_attack(attacker_succeeded: bool, defender_succeeded: bool) -> AttackResolution:
    """Minimum baseline for TC-004.

    Full combat math is added in later milestones.
    """

    if not attacker_succeeded and not defender_succeeded:
        return AttackResolution(both_failed=True, unavoidable_damage_to_defender=1)

    return AttackResolution(both_failed=False, unavoidable_damage_to_defender=0)


def resolve_attack_check(
    attacker_skill: int,
    defender_skill: int,
    attacker_roll: int,
    defender_roll: int,
    attacker_bonus: int = 10,
    defender_modifier: int = 0,
    weapon_speed: int = 0,
) -> AttackCheckResolution:
    """Resolve a physical attack contest.

    Rules supported:
    - Attacker gets +10 by default.
    - Weapon speed subtracts from defender's relevant defense skill.
    - If both fail (critical or not), defender takes 1 unavoidable damage.
    - Critical success precedence in success branch.
    - Success ties break by higher roll, then higher tested skill, then reroll.
    """

    attacker_result = resolve_check(attacker_skill, attacker_roll, modifiers=[attacker_bonus])
    defender_result = resolve_check(defender_skill, defender_roll, modifiers=[defender_modifier - weapon_speed])

    attacker_critical_success = attacker_result.outcome == CheckOutcome.CRITICAL_SUCCESS
    defender_critical_success = defender_result.outcome == CheckOutcome.CRITICAL_SUCCESS
    attacker_critical_failure = attacker_result.outcome == CheckOutcome.CRITICAL_FAILURE
    defender_critical_failure = defender_result.outcome == CheckOutcome.CRITICAL_FAILURE

    if attacker_critical_failure and not defender_critical_failure:
        return AttackCheckResolution(
            attacker_result=attacker_result,
            defender_result=defender_result,
            winner=OpposedWinner.TARGET,
            attacker_hits=False,
            defender_makes_defensive_move=True,
            unavoidable_damage_to_defender=0,
            tie_reroll_required=False,
            reason="attacker_critical_failure",
        )

    if defender_critical_failure and not attacker_critical_failure:
        return AttackCheckResolution(
            attacker_result=attacker_result,
            defender_result=defender_result,
            winner=OpposedWinner.ACTOR,
            attacker_hits=True,
            defender_makes_defensive_move=False,
            unavoidable_damage_to_defender=0,
            tie_reroll_required=False,
            reason="defender_critical_failure",
        )

    attacker_success = attacker_result.is_success
    defender_success = defender_result.is_success

    if not attacker_success and not defender_success:
        return AttackCheckResolution(
            attacker_result=attacker_result,
            defender_result=defender_result,
            winner=OpposedWinner.TARGET,
            attacker_hits=False,
            defender_makes_defensive_move=False,
            unavoidable_damage_to_defender=1,
            tie_reroll_required=False,
            reason="both_fail_defender_takes_unavoidable_damage",
        )

    if attacker_success and not defender_success:
        return AttackCheckResolution(
            attacker_result=attacker_result,
            defender_result=defender_result,
            winner=OpposedWinner.ACTOR,
            attacker_hits=True,
            defender_makes_defensive_move=False,
            unavoidable_damage_to_defender=0,
            tie_reroll_required=False,
            reason="attacker_success_defender_failure",
        )

    if defender_success and not attacker_success:
        return AttackCheckResolution(
            attacker_result=attacker_result,
            defender_result=defender_result,
            winner=OpposedWinner.TARGET,
            attacker_hits=False,
            defender_makes_defensive_move=True,
            unavoidable_damage_to_defender=0,
            tie_reroll_required=False,
            reason="defender_success_attacker_failure",
        )

    if attacker_critical_success and not defender_critical_success:
        return AttackCheckResolution(
            attacker_result=attacker_result,
            defender_result=defender_result,
            winner=OpposedWinner.ACTOR,
            attacker_hits=True,
            defender_makes_defensive_move=False,
            unavoidable_damage_to_defender=0,
            tie_reroll_required=False,
            reason="attacker_critical_success_precedence",
        )

    if defender_critical_success and not attacker_critical_success:
        return AttackCheckResolution(
            attacker_result=attacker_result,
            defender_result=defender_result,
            winner=OpposedWinner.TARGET,
            attacker_hits=False,
            defender_makes_defensive_move=True,
            unavoidable_damage_to_defender=0,
            tie_reroll_required=False,
            reason="defender_critical_success_precedence",
        )

    if attacker_result.roll > defender_result.roll:
        return AttackCheckResolution(
            attacker_result=attacker_result,
            defender_result=defender_result,
            winner=OpposedWinner.ACTOR,
            attacker_hits=True,
            defender_makes_defensive_move=False,
            unavoidable_damage_to_defender=0,
            tie_reroll_required=False,
            reason="higher_successful_roll",
        )

    if defender_result.roll > attacker_result.roll:
        return AttackCheckResolution(
            attacker_result=attacker_result,
            defender_result=defender_result,
            winner=OpposedWinner.TARGET,
            attacker_hits=False,
            defender_makes_defensive_move=True,
            unavoidable_damage_to_defender=0,
            tie_reroll_required=False,
            reason="higher_successful_roll",
        )

    if attacker_result.target > defender_result.target:
        return AttackCheckResolution(
            attacker_result=attacker_result,
            defender_result=defender_result,
            winner=OpposedWinner.ACTOR,
            attacker_hits=True,
            defender_makes_defensive_move=False,
            unavoidable_damage_to_defender=0,
            tie_reroll_required=False,
            reason="higher_skill_breaks_success_tie",
        )

    if defender_result.target > attacker_result.target:
        return AttackCheckResolution(
            attacker_result=attacker_result,
            defender_result=defender_result,
            winner=OpposedWinner.TARGET,
            attacker_hits=False,
            defender_makes_defensive_move=True,
            unavoidable_damage_to_defender=0,
            tie_reroll_required=False,
            reason="higher_skill_breaks_success_tie",
        )

    return AttackCheckResolution(
        attacker_result=attacker_result,
        defender_result=defender_result,
        winner=OpposedWinner.NONE,
        attacker_hits=False,
        defender_makes_defensive_move=False,
        unavoidable_damage_to_defender=0,
        tie_reroll_required=True,
        reason="tie_reroll_required",
    )


def resolve_initiative_check(
    player_perception: int,
    enemy_mind: int,
    player_roll: int,
    enemy_roll: int,
    player_modifier: int = 0,
) -> InitiativeResolution:
    opposed = resolve_opposed_check(
        actor_skill=player_perception,
        actor_roll=player_roll,
        target_skill=enemy_mind,
        target_roll=enemy_roll,
        actor_modifiers=[player_modifier],
    )
    return InitiativeResolution(
        result=opposed.actor,
        opponent_result=opposed.target,
        winner=opposed.winner,
        tie_reroll_required=opposed.tie_reroll_required,
    )


def resolve_surprise_attempt(
    player_stealth: int,
    enemy_mind: int,
    player_roll: int,
    enemy_roll: int,
    follower_count: int = 0,
) -> SurpriseAttemptResolution:
    follower_penalty = -10 * max(0, follower_count)
    opposed = resolve_opposed_check(
        actor_skill=player_stealth,
        actor_roll=player_roll,
        target_skill=enemy_mind,
        target_roll=enemy_roll,
        actor_modifiers=[follower_penalty],
    )

    if opposed.tie_reroll_required:
        return SurpriseAttemptResolution(
            surprise_success=False,
            tie_reroll_required=True,
            initiative_owner=None,
            first_attack_bonus=0,
            initiative_perception_modifier=0,
            reason="surprise_tie_reroll_required",
        )

    if opposed.winner == OpposedWinner.ACTOR:
        return SurpriseAttemptResolution(
            surprise_success=True,
            tie_reroll_required=False,
            initiative_owner="player_side",
            first_attack_bonus=20,
            initiative_perception_modifier=0,
            reason="surprise_success",
        )

    return SurpriseAttemptResolution(
        surprise_success=False,
        tie_reroll_required=False,
        initiative_owner=None,
        first_attack_bonus=0,
        initiative_perception_modifier=-20,
        reason="surprise_failed_initiative_penalty",
    )


def resolve_mvp_critical_failure() -> CriticalFailureResolution:
    """MVP policy: no additional critical-failure side effects yet."""

    return CriticalFailureResolution(
        apply_extra_effects=False,
        notes="MVP uses normal failure handling; extra fumble effects deferred.",
    )


def _validate_d10_roll(roll: int) -> None:
    if roll < 1 or roll > 10:
        raise ValueError("Defensive Move roll must be in range 1..10.")


def _load_defensive_move_tables() -> dict[str, dict[str, dict[str, str]]]:
    payload = load_content_json("defensive_moves.json")
    return payload


def _resolve_defensive_move(table_name: str, roll: int) -> DefensiveMoveOutcome:
    _validate_d10_roll(roll)
    tables = _load_defensive_move_tables()
    table = tables.get(table_name)
    if table is None:
        raise ValueError(f"Unknown defensive move table: {table_name}")

    entry = table.get(str(roll))
    if entry is None:
        raise ValueError(f"Missing roll {roll} in defensive move table: {table_name}")

    effect_id = entry.get("effect_id", "")
    summary = entry.get("summary", "")
    if not effect_id or not summary:
        raise ValueError(f"Invalid defensive move entry for roll {roll} in table {table_name}")

    return DefensiveMoveOutcome(table=table_name, roll=roll, effect_id=effect_id, summary=summary)


def resolve_player_defensive_move(roll: int) -> DefensiveMoveOutcome:
    return _resolve_defensive_move("player", roll)


def resolve_npc_defensive_move(roll: int) -> DefensiveMoveOutcome:
    return _resolve_defensive_move("npc", roll)


def initiative_target(perception: int, has_quick_weapon: bool) -> int:
    """Minimum baseline for TC-005."""

    return perception + (10 if has_quick_weapon else 0)


def choose_random_target(valid_target_ids: list[str], rng: Random | None = None) -> str:
    if not valid_target_ids:
        raise ValueError("At least one valid target is required.")

    random_source = rng or Random()
    return random_source.choice(valid_target_ids)


def choose_creature_action_for_creature(creature_id: str, action_roll: int) -> CreatureAction:
    action_rows = get_creature_actions(creature_id)
    actions = [
        CreatureAction(
            action_id=row["action_id"],
            creature_id=creature_id,
            roll_min=row["roll_min"],
            roll_max=row["roll_max"],
            name=row["name"],
            action_type=row["action_type"],
            defense_or_check=row["defense_or_check"],
            damage_die=row["damage_die"],
            damage_type=row["damage_type"],
            secondary_effect=row["secondary_effect"],
        )
        for row in action_rows
    ]
    return choose_creature_action(actions, action_roll)


def initialize_enemy_target_assignments(
    enemy_ids: list[str],
    pc_ids: list[str],
    minion_ids: list[str],
    rng: Random | None = None,
) -> EnemyTargetAssignments:
    """Assign enemy targets once at combat start and keep them locked.

    Rule support:
    - Distribute one opponent to each PC/minion while possible.
    - Remaining opponents prioritize PCs over minions.
    - Assignment is intended to remain fixed for the encounter.
    """

    if not enemy_ids:
        return EnemyTargetAssignments(enemy_to_target={}, locked=True)

    defenders = [*pc_ids, *minion_ids]
    if not defenders:
        raise ValueError("At least one PC or minion is required for target assignment.")

    assignments: dict[str, str] = {}
    random_source = rng or Random()

    guaranteed_slots = min(len(enemy_ids), len(defenders))
    for idx in range(guaranteed_slots):
        assignments[enemy_ids[idx]] = defenders[idx]

    remaining_enemies = enemy_ids[guaranteed_slots:]
    preferred_pool = pc_ids if pc_ids else minion_ids
    for enemy_id in remaining_enemies:
        assignments[enemy_id] = random_source.choice(preferred_pool)

    return EnemyTargetAssignments(enemy_to_target=assignments, locked=True)


def get_enemy_assigned_target(enemy_id: str, assignments: EnemyTargetAssignments) -> str:
    if enemy_id not in assignments.enemy_to_target:
        raise ValueError("Enemy has no assigned target in this encounter.")
    return assignments.enemy_to_target[enemy_id]


def get_alive_enemy_target_map(alive_enemy_ids: list[str], assignments: EnemyTargetAssignments) -> dict[str, str]:
    """Return locked assignments for alive enemies only, without re-distribution."""

    return {enemy_id: assignments.enemy_to_target[enemy_id] for enemy_id in alive_enemy_ids if enemy_id in assignments.enemy_to_target}
