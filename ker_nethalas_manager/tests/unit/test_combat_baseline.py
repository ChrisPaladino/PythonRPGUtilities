from random import Random

from ker_nethalas.rules.combat import (
    CreatureAction,
    choose_creature_action,
    choose_random_target,
    begin_charging_ability,
    get_alive_enemy_target_map,
    get_enemy_assigned_target,
    initialize_enemy_target_assignments,
    initiative_target,
    minion_target_prompt,
    reaction_modifier_for_next_use,
    resolve_mvp_critical_failure,
    resolve_physical_attack,
    spend_standard_action,
    start_round,
    take_free_action,
    use_reaction,
)


def test_tc004_attack_both_fail_causes_unavoidable_damage() -> None:
    result = resolve_physical_attack(attacker_succeeded=False, defender_succeeded=False)
    assert result.both_failed is True
    assert result.unavoidable_damage_to_defender == 1


def test_tc005_quick_weapon_initiative_target() -> None:
    assert initiative_target(perception=40, has_quick_weapon=True) == 50


def test_round_start_defaults() -> None:
    state = start_round(round_number=1, acting_side="player_side")
    assert state.free_action_available is True
    assert state.standard_actions_remaining == 1
    assert state.reactions_used == 0


def test_reaction_penalty_stacks_negative_20_after_first() -> None:
    state = start_round(round_number=1, acting_side="player_side")
    first = use_reaction(state)
    assert first.applied_modifier == 0

    second = use_reaction(first.state)
    assert second.applied_modifier == -20

    third = use_reaction(second.state)
    assert third.applied_modifier == -40


def test_free_action_only_once_per_round() -> None:
    state = start_round(round_number=1, acting_side="player_side")
    used = take_free_action(state)
    assert used.free_action_available is False


def test_standard_action_spend_from_single_default() -> None:
    state = start_round(round_number=1, acting_side="player_side")
    spent = spend_standard_action(state)
    assert spent.standard_actions_remaining == 0


def test_charging_adds_flat_negative_10_to_reactions() -> None:
    state = start_round(round_number=1, acting_side="player_side")
    charging = begin_charging_ability(state, ability_id="raise_skeleton", required_actions=2)
    assert reaction_modifier_for_next_use(charging) == -10


def test_charging_blocks_different_reaction_ability() -> None:
    state = start_round(round_number=1, acting_side="player_side")
    charging = begin_charging_ability(state, ability_id="raise_skeleton", required_actions=2)

    try:
        use_reaction(charging, reaction_ability_id="evasive_strike")
        assert False, "Expected ValueError for different reaction ability while charging"
    except ValueError as exc:
        assert "different Ability" in str(exc)


def test_creature_action_table_selection() -> None:
    actions = [
        CreatureAction(
            action_id="horror_cursed_slash",
            creature_id="skeletal_horror",
            roll_min=1,
            roll_max=2,
            name="Cursed Slash",
            action_type="physical",
            defense_or_check="attack",
            damage_die="d6",
            damage_type="slashing",
            secondary_effect="",
        ),
        CreatureAction(
            action_id="horror_haunting_wail",
            creature_id="skeletal_horror",
            roll_min=5,
            roll_max=5,
            name="Haunting Wail",
            action_type="magical",
            defense_or_check="resolve",
            damage_die="",
            damage_type="",
            secondary_effect="stunned_1_on_fail",
        ),
    ]
    chosen = choose_creature_action(actions, action_roll=5)
    assert chosen.action_id == "horror_haunting_wail"


def test_minion_always_prompts_for_target_selection() -> None:
    prompt = minion_target_prompt("raised_skeleton", has_valid_target=True)
    assert prompt.must_prompt is True
    assert prompt.reason == "prompt_each_minion_action"


def test_random_target_policy_is_select_from_valid_targets() -> None:
    rng = Random(7)
    target = choose_random_target(["seraphine", "skeleton"], rng=rng)
    assert target in {"seraphine", "skeleton"}


def test_mvp_critical_failure_has_no_extra_effects() -> None:
    resolved = resolve_mvp_critical_failure()
    assert resolved.apply_extra_effects is False


def test_enemy_target_assignment_gives_one_each_then_pc_priority() -> None:
    assignments = initialize_enemy_target_assignments(
        enemy_ids=["horror_a", "horror_b", "horror_c"],
        pc_ids=["seraphine"],
        minion_ids=["raised_skeleton"],
        rng=Random(3),
    )

    assert assignments.locked is True
    assert assignments.enemy_to_target["horror_a"] == "seraphine"
    assert assignments.enemy_to_target["horror_b"] == "raised_skeleton"
    assert assignments.enemy_to_target["horror_c"] == "seraphine"


def test_enemy_target_assignment_extra_enemies_choose_from_pcs_only() -> None:
    assignments = initialize_enemy_target_assignments(
        enemy_ids=["h1", "h2", "h3", "h4"],
        pc_ids=["seraphine", "ally_pc"],
        minion_ids=["raised_skeleton"],
        rng=Random(1),
    )

    assert assignments.enemy_to_target["h1"] == "seraphine"
    assert assignments.enemy_to_target["h2"] == "ally_pc"
    assert assignments.enemy_to_target["h3"] == "raised_skeleton"
    assert assignments.enemy_to_target["h4"] in {"seraphine", "ally_pc"}


def test_enemy_target_assignment_stays_fixed_for_alive_subset() -> None:
    assignments = initialize_enemy_target_assignments(
        enemy_ids=["horror_a", "horror_b", "horror_c"],
        pc_ids=["seraphine"],
        minion_ids=["raised_skeleton"],
        rng=Random(2),
    )

    alive_map = get_alive_enemy_target_map(["horror_a", "horror_c"], assignments)
    assert alive_map == {
        "horror_a": assignments.enemy_to_target["horror_a"],
        "horror_c": assignments.enemy_to_target["horror_c"],
    }


def test_get_enemy_assigned_target_returns_locked_target() -> None:
    assignments = initialize_enemy_target_assignments(
        enemy_ids=["horror_a"],
        pc_ids=["seraphine"],
        minion_ids=["raised_skeleton"],
    )
    assert get_enemy_assigned_target("horror_a", assignments) == "seraphine"
