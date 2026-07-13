# Ker Nethalas Engine Data Contracts v0.1

## Objective

Define Python-side data contracts that mirror current sample JSON and support forward-compatible save files.

## Core Types

```python
from dataclasses import dataclass
from typing import Literal, Optional

RollMode = Literal["manual", "automatic"]
CheckOutcome = Literal["success", "failure", "critical_success", "critical_failure"]

@dataclass(frozen=True)
class CheckResult:
    target: int
    roll: int
    outcome: CheckOutcome
    effective_modifiers: list[int]
```

## Static Content Contracts

Minimum expected fields (based on sample pack):

1. SkillDefinition
- id: str
- name: str
- base_score: int
- category: str
- notes: str

2. ResistanceDefinition
- id: str
- name: str
- low_start: int
- high_start: int
- hard_cap: int
- notes: str

3. MasteryDefinition
- id: str
- name: str
- feature_name: str
- feature_summary: str
- starting_ability_id: str
- source_page: int

4. AbilityDefinition
- id: str
- mastery_id: str
- tier: int
- name: str
- action_type: str
- actions_required: int
- check_type: str
- aether_cost: int
- health_cost: int
- exhaustion_cost: int
- sustained: bool
- requirements: str
- effect_summary: str
- source_page: int

5. WeaponDefinition
- id: str
- name: str
- skill_id: str
- hands: int
- base_damage: str
- damage_type: str
- speed: int
- traits: str
- weight: str
- cost: int
- source_page: int

6. ArmorDefinition
- id: str
- name: str
- slot: str
- protection: int
- integrity_die: str
- maneuverability_mod: int
- perception_mod: int
- weight: str
- cost: int
- source_page: int

7. CreatureDefinition
- id: str
- name: str
- type: str
- number: int
- mind: int
- endurance: int
- body: int
- health: int
- hit_location_table: str
- weak_spot: str
- armor: str
- combat_skill: int
- magic_resistance: int
- traits: str
- source_page: int

8. CreatureActionDefinition
- id: str
- creature_id: str
- roll_min: int
- roll_max: int
- name: str
- action_type: str
- defense_or_check: str
- damage_die: str
- damage_type: str
- secondary_effect: str
- summary: str

## Runtime State Contracts

1. CharacterState
- identity: name, level
- resources: health, toughness, aether, sanity (current/max), exhaustion
- resistances: endurance, resolve, spellward
- skill scores map
- mastery IDs
- active minions

2. DomainState
- domain_id, room pointer, visited room flags
- tension die stage (d8|d6|d4)
- torch/light remaining in room-steps
- lair/exit flags
- lock/trap states per door/container

3. EncounterState
- round number
- initiative winner
- combatants and targets
- action economy state
- reaction penalties
- effect stacks with durations

4. SessionState
- content_version
- schema_version
- rng_seed and rng_index
- current mode (coach/tabletop/automatic)
- event_log cursor and undo stack metadata

## Event Contracts

Each committed event should include:
- event_id
- timestamp
- event_type
- actor_id
- payload
- rules_reference (FR id and optional page)
- undo_group_id

Recommended event categories:
- `DecisionEvent`
- `RollRequestedEvent`
- `RollResolvedEvent`
- `StateChangeEvent`
- `CombatTransitionEvent`
- `ExplorationTransitionEvent`

## Save File Envelope

```json
{
  "schema_version": "0.1.0",
  "content_version": "0.1.0",
  "rng": {"seed": 20260713, "index": 0},
  "mode": "tabletop",
  "session_state": {},
  "event_log": []
}
```

## Validation Rules (must fail fast)

1. All FK-style IDs exist in loaded static definitions.
2. Numeric fields are bounded (e.g., scores 0..100 unless explicitly extended).
3. Dice notation is from approved grammar (`d4`, `d6`, `d8`, `d10`, `d12`, optional pool list).
4. Creature action roll ranges cannot overlap for the same creature unless explicitly flagged.
5. Save schema/content versions must be compatible with loaded migration set.

## Compatibility Policy

1. Static IDs are permanent once released.
2. Display names and summaries may change without migration.
3. Field additions are backward compatible when defaults are defined.
4. Field removals or semantic changes require explicit migration functions.
