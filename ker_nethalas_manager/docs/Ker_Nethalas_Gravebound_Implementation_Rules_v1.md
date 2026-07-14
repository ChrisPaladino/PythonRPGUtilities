# Ker Nethalas: Gravebound Edition - Rules Engine Implementation Guide

**Target:** Python 3.12+  
**Purpose:** A code-oriented, paraphrased rules reference for implementing a digital companion or computerized version.  
**Source:** *Ker Nethalas: Into the Midnight Throne - Gravebound Edition*, Version 1 (2026).  
**Scope:** Core mechanics and state transitions. Content tables, prose descriptions, art, and most individual Mastery/creature/item entries are intentionally omitted.

> This is an independent implementation guide, not a replacement for the rulebook. Keep page references in your code and use the owned PDF to resolve unclear content. Do not ship extracted rulebook prose or artwork in a public build.

---

## Table of Contents

1. [Implementation principles](#1-implementation-principles)
2. [Global conventions](#2-global-conventions)
3. [Character creation](#3-character-creation)
4. [Character resources and derived state](#4-character-resources-and-derived-state)
5. [Core d100 checks](#5-core-d100-checks)
6. [Opposed checks](#6-opposed-checks)
7. [Advantage and Disadvantage](#7-advantage-and-disadvantage)
8. [Criticals, failures, and Skill Improvement](#8-criticals-failures-and-skill-improvement)
9. [Usage Dice](#9-usage-dice)
10. [Masteries and Abilities](#10-masteries-and-abilities)
11. [Combat state machine](#11-combat-state-machine)
12. [Physical attack resolution](#12-physical-attack-resolution)
13. [Magical and special action resolution](#13-magical-and-special-action-resolution)
14. [Damage Pool and damage application](#14-damage-pool-and-damage-application)
15. [Hit Locations, Weak Spots, and Armor](#15-hit-locations-weak-spots-and-armor)
16. [Damage types and affinities](#16-damage-types-and-affinities)
17. [Combat criticals and fumbles](#17-combat-criticals-and-fumbles)
18. [Conditions](#18-conditions)
19. [Healing, death, and the Rot](#19-healing-death-and-the-rot)
20. [Exhaustion](#20-exhaustion)
21. [Sanity and Madness](#21-sanity-and-madness)
22. [Minions, multiple opponents, and targeting](#22-minions-multiple-opponents-and-targeting)
23. [Domain exploration state machine](#23-domain-exploration-state-machine)
24. [Light sources](#24-light-sources)
25. [Scavenging and hidden containers](#25-scavenging-and-hidden-containers)
26. [Doors, locks, and traps](#26-doors-locks-and-traps)
27. [Tension and Growing Darkness](#27-tension-and-growing-darkness)
28. [Resting and Camp](#28-resting-and-camp)
29. [Inventory, equipment, and encumbrance](#29-inventory-equipment-and-encumbrance)
30. [Weapons, shields, and armor traits](#30-weapons-shields-and-armor-traits)
31. [Encounter construction and creature scaling](#31-encounter-construction-and-creature-scaling)
32. [Loot, Attunement, Potions, and Traders](#32-loot-attunement-potions-and-traders)
33. [Progression](#33-progression)
34. [First-run rules](#34-first-run-rules)
35. [Recommended event model](#35-recommended-event-model)
36. [Recommended save-state fields](#36-recommended-save-state-fields)
37. [Ambiguities and recommended rulings](#37-ambiguities-and-recommended-rulings)
38. [Minimum regression tests](#38-minimum-regression-tests)
39. [Source-page map](#39-source-page-map)

---

# 1. Implementation principles

Use a **headless rules engine**. The UI should submit player intents and dice results, but should not directly mutate game state.

Recommended pipeline:

```text
Intent
  -> validate legal action
  -> request required roll(s)
  -> accept manual or generated roll(s)
  -> resolve rules
  -> emit domain events
  -> apply events
  -> append log
  -> autosave
```

Example:

```text
UseAbility(evasive_strike, target=horror_a)
  -> request physical attack roll pair
  -> resolve opposed attack
  -> emit DamageApplied or DefensiveMoveRolled
  -> emit AbilityFollowupApplied if attack hit
  -> commit transaction
```

Keep these separate:

- **Static content:** Skills, Masteries, Abilities, weapons, armor, creatures, action tables, traps, events, loot tables.
- **Campaign state:** Character, permanent advancement, inventory, goals, discovered Domains.
- **Domain state:** Room graph, visited rooms, doors, locks, traps, Tension, Lair die, Exit die, Overseer, Influence, persistent effects.
- **Encounter state:** Combatants, targets, initiative side, round, available actions, reactions used, conditions, pending multi-action abilities.
- **Audit state:** Dice values, modifiers, player decisions, event history, RNG seed/index.

---

# 2. Global conventions

## 2.1 Dice notation

Standard dice include d4, d6, d8, d10, d12, d20, and d100.

For a d100:

- One d10 is tens and one is ones.
- `00` represents `100`.
- Store the two digits as well as the numeric result. You need the digits to detect doubles and to reverse them for Advantage/Disadvantage.

Suggested model:

```python
@dataclass(frozen=True)
class D100Roll:
    tens: int   # 0..9
    ones: int   # 0..9

    @property
    def value(self) -> int:
        raw = self.tens * 10 + self.ones
        return 100 if raw == 0 else raw

    @property
    def is_double(self) -> bool:
        return self.tens == self.ones
```

## 2.2 Rounding

Whenever division produces a fraction, round **up**.

```python
from math import ceil
half_level = ceil(level / 2)
```

## 2.3 Modifier timing

Unless a rule says otherwise:

1. Start with the relevant Skill, Resistance, or creature stat.
2. Apply permanent character/item modifiers.
3. Apply equipment modifiers.
4. Apply temporary effects.
5. Apply situational modifiers and Difficulty.
6. Apply reaction penalties.
7. Roll against the final effective score.

Do not clamp Skills to 80 after item or situational modifiers. Natural advancement is capped at 80, but temporary/equipment modifiers can exceed it. Resistances always cap at 80.

## 2.4 Direct versus persistent damage

Track a damage source as one of:

- `direct`: an attack, spell, trap, or immediate effect.
- `condition_tick`: Bleeding, Burning, Poisoned, etc.
- `environmental`: falls, hazards, starvation-like effects.
- `unavoidable`: explicit damage that cannot be reduced or prevented.

This distinction matters for Vulnerability/Resistance and Armor.

## 2.5 Temporary values

A temporary bonus lasts until spent or until a rest, as appropriate. Temporary values may exceed normal maxima.

Recommended approach:

```python
effective_toughness = base_current_toughness + temporary_toughness
```

Spend temporary points before ordinary points unless a specific effect states otherwise.

---

# 3. Character creation

**Source: pp. 15-21, 67.**

## 3.1 Attributes

Starting values:

```text
Health     = d6 + 10
Toughness  = 3d6 + 20
Aether     = d6 + 8
Sanity     = d6 + 10
Exhaustion = 0
Level      = 1
```

At creation, current values begin at their maxima before first-run penalties.

## 3.2 Base Skills and allotments

Base scores:

```text
Acrobatics 10
Athletics 10
Dodge 10
Perception 20
All other listed Skills 0
```

Then assign:

```text
+60 to one weapon Skill
+40 to a different weapon Skill
+30 to three Skills
+20 to two Skills
+10 to three Skills
```

Rules:

- A Skill cannot receive two creation allotments.
- Natural Skill scores normally cannot rise above 80.
- Item and circumstantial modifiers may make an effective score exceed 80.
- There is no general ranged-weapon Skill in the core rules.

## 3.3 Resistances

The three Resistances are:

- Endurance
- Resolve
- Spellward

Starting allocation:

```text
One Resistance at 40
The other two at 20
```

Rules:

- Resistances use d100 checks like Skills.
- They are not Skills.
- They do not improve through Skill Improvement.
- They remain usable even when the character cannot actively act.
- They can never exceed 80, including equipment and other bonuses.

## 3.4 Starting Masteries

A new character receives 2 Ability Points and must spend them on two different Masteries.

Each selected Mastery grants:

- Its Mastery Feature.
- Its Tier 1 Ability.

Limits:

- Two normal Masteries maximum.
- A third Mastery may be active through an Amulet.
- Ability tiers must be unlocked in order within a Mastery.

## 3.5 Personal Goals

- Track exactly two active Personal Goals.
- Once selected, a goal cannot be changed until completed.
- Each Personal Goal may be completed only once.
- On completion, apply its reward and allow selection of a replacement goal.

Keep goal progress as structured counters, not free text.

---

# 4. Character resources and derived state

**Source: pp. 13, 18, 21, 81, 86-87.**

## 4.1 Health and Toughness

Incoming damage is applied in this order:

```text
Temporary Toughness
-> current Toughness
-> current Health
```

Health at 0 means death unless an optional death rule is enabled.

## 4.2 Aether

Aether is the resource used by many Abilities.

- Entering a new room replenishes current Aether to the character's currently usable maximum.
- Sustained effects reserve Aether and reduce the usable maximum.
- Sustained effects can normally be toggled only outside combat.

Recommended fields:

```python
aether_base_max: int
aether_permanent_mod: int
aether_reserved: int
aether_current: int
```

```python
usable_aether_max = max(0, aether_base_max + aether_permanent_mod - aether_reserved)
```

Activation of a Sustained Ability:

```text
validate current Aether >= cost
current Aether -= cost
reserved Aether += cost
usable maximum drops by cost
```

Ending a Sustained Ability:

```text
reserved Aether -= cost
current Aether += cost
cap current at newly restored usable maximum
```

Entering a room:

```text
current Aether = usable maximum
```

## 4.3 Sanity

Sanity at 0 triggers a Madness roll, then lost Sanity is restored according to the Madness rules unless the result ends the character.

## 4.4 Exhaustion

Exhaustion is cumulative and has threshold effects. It can kill the character at 21+.

---

# 5. Core d100 checks

**Source: pp. 69-74.**

A standard check succeeds when:

```python
roll.value <= effective_score
```

Suggested result:

```python
@dataclass(frozen=True)
class CheckResult:
    roll: D100Roll
    base_score: int
    modifiers: tuple[int, ...]
    effective_score: int
    success: bool
    critical_success: bool
    critical_failure: bool
```

Critical classification:

```python
is_critical_success = roll.is_double and roll.value <= effective_score
is_critical_failure = roll.is_double and roll.value > effective_score
```

A doubles roll on a Skill check also marks that Skill for Improvement, whether the check succeeded or failed.

---

# 6. Opposed checks

**Source: p. 70.**

Both sides make a normal check against their own effective scores.

Resolve in this priority order:

1. If exactly one side has a Critical Success, that side wins.
2. If one side has a Critical Failure, that side loses.
3. If exactly one side succeeds, the successful side wins.
4. If both succeed, the higher numeric roll wins.
5. If both fail, the higher numeric roll wins.
6. If rolls tie, the higher effective score wins.
7. If still tied, reroll.

Pseudocode:

```python
def resolve_opposed(a: CheckResult, b: CheckResult) -> str:
    if a.critical_success != b.critical_success:
        return "a" if a.critical_success else "b"

    if a.critical_failure != b.critical_failure:
        return "b" if a.critical_failure else "a"

    if a.success != b.success:
        return "a" if a.success else "b"

    if a.roll.value != b.roll.value:
        return "a" if a.roll.value > b.roll.value else "b"

    if a.effective_score != b.effective_score:
        return "a" if a.effective_score > b.effective_score else "b"

    return "reroll"
```

Combat attacks have a special both-fail result; see the combat sections.

---

# 7. Advantage and Disadvantage

**Source: p. 70.**

Advantage/Disadvantage uses the same two d10 digits, read in the more favorable or less favorable orientation.

Example digits `6` and `2`:

```text
26 or 62
Advantage -> 26
Disadvantage -> 62
```

Implementation:

```python
def oriented_d100(tens: int, ones: int, mode: str) -> int:
    a_raw = tens * 10 + ones
    b_raw = ones * 10 + tens
    a = 100 if a_raw == 0 else a_raw
    b = 100 if b_raw == 0 else b_raw

    if mode == "advantage":
        return min(a, b)
    if mode == "disadvantage":
        return max(a, b)
    return a
```

Store the original digits and selected orientation in the event log.

The PDF does not explicitly define stacking or cancellation. See [Ambiguities](#37-ambiguities-and-recommended-rulings).

---

# 8. Criticals, failures, and Skill Improvement

**Source: pp. 71-74, 83-85; progression p. 62.**

## 8.1 Non-combat criticals

For non-combat checks by a player character:

- Doubles at or below the score trigger the critical-success entry for that check type.
- Doubles above the score trigger the critical-failure entry.
- Use a data-driven critical table keyed by Skill or Resistance.
- Non-combat critical consequences are applied only to player characters.

Do not hard-code the full critical table into the generic resolver. Emit:

```text
CriticalEffectRequested(check_type, success_or_failure)
```

Then look up and execute the corresponding content entry.

## 8.2 Skill Improvement mark

Whenever a **Skill** check rolls doubles:

```text
skill.improvement_marked = True
```

This happens whether the roll succeeds or fails.

Do not mark Resistances, creature attributes, or other non-Skill values.

## 8.3 Combat criticals

Combat attack criticals use the combat rules rather than non-combat critical effects.

- Critical attack success normally becomes a Critical Strike.
- Attack fumbles use player or NPC fumble tables.
- A combat roll may still mark a player Skill for Improvement.

---

# 9. Usage Dice

**Source: p. 74.**

Usage-die chain:

```text
d20 -> d12 -> d10 -> d8 -> d6 -> d4
```

When a usage check is required:

```text
Roll current die.
1-2:
    if current die is larger than d4:
        step down one die
    else:
        trigger the procedure's depletion event
Any other result:
    no change
```

Generic function:

```python
USAGE_CHAIN = [20, 12, 10, 8, 6, 4]

@dataclass
class UsageDie:
    sides: int

def check_usage(die: UsageDie, roll: int) -> tuple[UsageDie, bool]:
    if roll not in (1, 2):
        return die, False

    idx = USAGE_CHAIN.index(die.sides)
    if die.sides == 4:
        return die, True

    return UsageDie(USAGE_CHAIN[idx + 1]), False
```

Each subsystem defines what happens when d4 depletes:

- Tension: Growing Darkness, then reset to d8.
- Lair/Exit: current room becomes the target location.
- Armor Integrity: item becomes unusable at d4 depletion.
- Other content: charges or events as specified.

---

# 10. Masteries and Abilities

**Source: p. 21 and individual Mastery pages.**

## 10.1 Ability categories

An Ability may specify:

- Free Action
- Reaction
- Standard Action
- Multiple Standard Actions
- Passive
- Aether cost
- Health cost
- Exhaustion cost
- Sustained cost
- Required weapon/Skill/corpse/item/condition
- Physical attack check
- Magical resolution
- Explicitly unopposed behavior

## 10.2 Magical Abilities

Most spell-like Abilities:

- Manifest automatically for the player.
- Do not require a player casting check.
- Allow an enemy Magic Resistance check unless the Ability says otherwise.

## 10.3 Attack-based Abilities

If an Ability requires a weapon or combat check:

- Use ordinary attack procedures.
- Respect action type, weapon traits, reaction penalties, hit locations, Armor, and criticals unless the Ability overrides them.
- If it says the target cannot defend, perform only the attacker's Skill check.

## 10.4 Sustained Abilities

- Reserve Aether while active.
- Can normally be switched on or off outside combat.
- End when explicitly dismissed, the source is destroyed, or the Ability's stated end condition occurs.
- Releasing the effect returns the reserved portion of the pool.

## 10.5 Multi-action Abilities

If an Ability requires more Standard Actions than the character has in one round:

- Track progress over consecutive turns.
- While charging, the character cannot perform other normal actions.
- They suffer an additional -10 on Reactions.
- They cannot use a different Ability as a Reaction.
- The rules do not state that taking damage automatically interrupts the charge.

Suggested state:

```python
@dataclass
class PendingAction:
    ability_id: str
    actions_required: int
    actions_spent: int
    target_ids: list[str]
```

---

# 11. Combat state machine

**Source: pp. 75-85, 91-93, 129-133.**

## 11.1 Encounter initialization

Recommended sequence:

1. Instantiate each creature separately.
2. Apply creature-type defaults.
3. Apply level adaptation.
4. Apply Overseer Influence and persistent Domain effects.
5. Apply encounter-start traits and effects.
6. Resolve Sanity threat once for the encounter.
7. Assign enemy targets.
8. Resolve surprise attempt if chosen and legal.
9. Otherwise resolve initiative.
10. Set round to 1.
11. Reset each combatant's per-round counters.

## 11.2 Sanity threat at start

- Frightening: Resolve check or lose 2 Sanity.
- Horrifying: Resolve check or lose 4 Sanity.
- With several enemies, roll once for the encounter and use the highest potential Sanity loss.
- Enemy-type immunity may suppress these traits.

## 11.3 Initiative

Initiative is an opposed check:

```text
Player Perception versus enemy Mind
```

Winner acts first for the whole encounter.

Player critical effects:

- Critical success: next attack has Advantage.
- Critical failure: lose first turn.

Surprise option:

```text
Player Stealth versus enemy Mind
```

- Use the highest Mind among several opponents.
- With multiple PCs, use the lowest Stealth on the player side.
- A solo PC suffers -10 Stealth per follower.
- Success: player side wins initiative and first attack gets +20.
- Failure: make normal Initiative, but player Perception suffers -20.
- Alert enemies cannot be surprised.

For a solo implementation, use one initiative contest for the encounter, not separate initiative per monster.

## 11.4 Turn and round structure

- A **turn** is one combatant's opportunity to act.
- A **round** ends after all combatants have received their turns/activations.
- A round represents roughly 10 seconds.
- Minions act during the PC side's turn, in any player-chosen order.
- Creatures with extra activations act the specified number of times.

At start of each round:

```text
free_actions_used = 0
reaction_count = 0
reset round-duration flags
```

## 11.5 Action economy

Each ordinary PC receives:

- 1 Standard Action per round.
- 1 Free Action per round.
- Any number of Reactions, with cumulative penalties.

Reaction penalty:

```text
First Reaction: 0
Second Reaction: -20
Third Reaction: -40
Fourth Reaction: -60
...
```

Reset at the start of the next round.

## 11.6 Common Standard Actions

- Basic weapon attack.
- Standard-action Ability.
- Flee.
- Use an unequipped/non-Belt item.
- Swap weapons.
- Interact with an object.
- Assist an ally.
- Begin/continue a multi-action Ability.

Items stored in an equipped Belt may be used or drawn as a Free Action.

## 11.7 Flee

- Spend a Standard Action.
- Make a Dodge check.
- Success: retreat to the previous room.
- Failure: remain in combat.
- Returning later finds the enemies still present at full Health.

## 11.8 End of combat

When all opponents are defeated or the PC successfully flees:

If victorious:

1. Mark room encounter cleared.
2. Apply defeat-triggered effects.
3. Award XP.
4. Update Personal Goals.
5. Recover d4 Toughness for each PC.
6. Heal each surviving Minion to full Health once the room is cleared.
7. Make Armor/Shield Integrity checks for pieces that saw use.
8. Enable spoils/loot interactions.
9. End combat-duration effects.
10. Reset once-per-combat flags.

If fled:

- Do not award victory XP or spoils.
- Enemies reset to full Health when the PC returns.
- Decide whether combat-duration effects end when leaving; normally they do.

---

# 12. Physical attack resolution

**Source: pp. 75, 77-81.**

## 12.1 Attack check

A physical attack is an opposed check between:

```text
Attacker:
    PC weapon Skill, unarmed Skill, or creature Combat Skill

Defender:
    creature Combat Skill
    OR PC Dodge
    OR PC weapon Skill when a legal Parry is available
```

Attacker receives `+10` to the attack score.

## 12.2 Legal PC defenses

A PC may choose:

- Dodge.
- Parry with the equipped weapon's Skill if the weapon has **Parrying**.
- Parry while using a shield, even if the weapon lacks Parrying.

Additional restrictions:

- A creature with **Savage** cannot be parried; only Dodge is legal.
- Some actions explicitly require Dodge.
- A Stunned target cannot actively defend.
- A Paralyzed or Sleeping target is hit automatically.
- Weapon Speed and other modifiers affect the defensive score.

## 12.3 Weapon Speed

A weapon's Speed is subtracted from the target's Combat/defense score when attacked by that weapon.

```python
defender_effective_score -= attacker_weapon.speed
```

## 12.4 Physical attack outcomes

Use the combat-specific outcome rules:

```text
Attacker wins:
    hit
Defender wins:
    no damage; defender rolls on appropriate Defensive Move table
Both fail:
    defender suffers exactly 1 unavoidable damage
```

Critical success rules take priority.

Important:

- The both-fail 1 damage cannot be reduced or prevented unless an explicit ability says so.
- If the attacker also rolled a combat fumble, resolve the fumble in addition to the both-fail damage.
- A defender does not receive a Defensive Move after a both-fail result.

## 12.5 Simultaneous rolling

The book encourages rolling:

- attacker d100,
- defender d100,
- and optional d20 Hit Location

at the same time. The code may request all rolls together and ignore Hit Location if the attack misses.

---

# 13. Magical and special action resolution

**Source: pp. 21, 74, 79, 131.**

## 13.1 PC versus enemy

A player Magical Ability generally:

```text
No casting roll
-> target rolls Magic Resistance
-> success avoids/resists as described
-> failure receives effect
```

Individual Abilities can override this.

## 13.2 Enemy versus PC

An enemy Action tagged Magical generally:

```text
No enemy casting roll
-> PC rolls Spellward
-> success avoids/resists
-> failure receives effect
```

## 13.3 Untagged actions

If a creature action is neither Physical nor Magical:

- Execute the action's specific instructions.
- It may call for Endurance, Resolve, Dodge, Athletics, or another check.

## 13.4 Area effects

Harmful PC area effects affect enemies, not allies, unless explicitly stated.

Harmful enemy area effects affect PCs and their allies, not the monsters' own side, unless explicitly stated.

---

# 14. Damage Pool and damage application

**Source: pp. 81-83.**

## 14.1 Building the Damage Pool

The Damage Pool contains dice contributed by:

- Base weapon.
- Mastery Feature.
- Active Ability.
- Item effect.
- Temporary effect.
- Situational bonus.

For ordinary non-magical weapons, base damage is d6.

Do **not** add all rolled dice together. Roll every die in the pool, then select one result.

## 14.2 Who selects the die

Player character:

- The player chooses one rolled die.
- If the dice have different damage types, the chosen die also selects the damage type.

NPC or Minion:

- Use the highest rolled die.
- If tied and the damage types differ, define a deterministic tie-breaker or request player choice. The book only requires choosing the highest result.

## 14.3 Fixed modifiers

Apply fixed modifiers such as `+1`, `+2`, or `+3` to the chosen die.

When several fixed modifiers are present, sum them unless their source states otherwise.

## 14.4 Spend Exhaustion for damage

After a PC attack has successfully hit, the player may spend:

```text
2 Exhaustion -> +1 damage
```

This applies only to a melee, non-Ability attack.

## 14.5 Recommended damage pipeline

```text
1. Build pool components.
2. Roll all pool dice.
3. PC chooses one die; NPC uses highest.
4. Add fixed modifiers to chosen result.
5. Apply Critical Strike multiplier if any.
6. Apply special critical additions, such as Piercing +2.
7. Determine Hit Location if required.
8. Calculate effective Armor.
9. Subtract Armor.
10. Apply post-Armor damage-type rules.
11. Apply Vulnerable/Resistant/Immune/Restored.
12. Apply explicit damage reduction.
13. Apply result to Temporary Toughness, Toughness, then Health.
14. Apply secondary effects and condition riders.
```

Never allow final damaging harm to drop below 0.

---

# 15. Hit Locations, Weak Spots, and Armor

**Source: pp. 80, 83, 210-211.**

## 15.1 Hit Locations

Use the target's anatomy table.

Hit Locations are used for ordinary physical/melee hits. They are not used for:

- Magical attacks.
- Condition ticks.
- Most out-of-combat damage.
- Effects that explicitly bypass locations.

## 15.2 Weak Spots

- Each anatomy may define a Weak Spot.
- Humanoid PCs have the head as a Weak Spot.
- Hitting a Weak Spot is an automatic Critical Strike.
- A player may target a chosen Hit Location/Weak Spot with Disadvantage.
- A Critical Success while already targeting a Weak Spot does not create triple damage; it remains one Critical Strike.

## 15.3 Armor

Armor is location-based.

```text
damage_after_armor = max(0, damage_before_armor - effective_armor)
```

Armor applies only in combat. Traps and external hazards normally ignore it unless explicitly stated otherwise.

Track:

- Base protection.
- Temporary location protection.
- Acid damage to protection.
- Combat-only reduction from Defensive Moves.
- Penetration and damage-type bypass.
- Integrity usage.

## 15.4 Armor Integrity

Each armor piece and shield has an Integrity Usage Die.

After combat, for each equipped piece that saw use:

- Roll its current Integrity die.
- On 1-2, step down one die.
- On 1-2 while at d4, the item is destroyed and discarded.

Repair:

- Raises Integrity by one die step.
- Cannot exceed the item's original maximum.
- Repairs other listed damage such as Acid-reduced Armor points.

Looted armor/shields begin one Integrity step below maximum.

Recommended `saw_use` rules:

- Armor piece saw use if an attack hit a location it protects, even if damage was 0.
- Shield saw use if its Parry bonus or critical-sacrifice function was used.
- Record this per encounter.

## 15.5 Sacrificing equipment against a Critical Strike

When about to receive a Critical Strike, a character may sacrifice the current weapon or shield:

- Negate all damage from that Critical Strike.
- The sacrificed item becomes broken.
- It cannot be used until repaired at Camp.

---

# 16. Damage types and affinities

**Source: pp. 82-83.**

## 16.1 Type-specific Armor behavior

| Damage type | Core behavior |
|---|---|
| Acid | Uses Armor normally; if the target is damaged, reduce Armor on that Hit Location by 1 until repaired. |
| Arcane | Ignores Armor. |
| Bludgeoning | Ignores 1 Armor. |
| Cold | Ignores Armor. |
| Fire | Ignores Armor. |
| Force | Ignores Armor. |
| Holy | Ignores Armor. |
| Infernal | Ignores Armor. |
| Lightning | Ignores Armor. |
| Necrotic | Ignores Armor. |
| Piercing | On a Critical Strike, add +2 damage after doubling; the +2 is not doubled. |
| Poison | Ignores Armor. |
| Psychic | Ignores Armor. |
| Slashing | If final post-Armor damage is 3 or less, add +1 damage. |

## 16.2 Affinities

A creature may be:

- Vulnerable: double damage received.
- Resistant: halve damage received.
- Immune: take no damage.
- Restored: recover Wounds equal to the damage.

For Vulnerable and Resistant:

- Apply only to direct damage.
- Apply after Armor.
- Use integer rounding up when halving, because the global rule says to round up.

```python
resistant_damage = ceil(damage / 2)
```

If a creature is both Vulnerable and Resistant to the same type, they cancel and damage is normal.

Recommended priority:

```text
Restored -> heal instead of harm
Immune -> 0
Vulnerable + Resistant -> normal
Vulnerable -> x2
Resistant -> ceil(x/2)
normal -> unchanged
```

Then apply explicit damage reduction after Armor/affinity as the rules specify.

---

# 17. Combat criticals and fumbles

**Source: pp. 83-85.**

## 17.1 Critical attack success

A combat Critical Success:

- Automatically wins unless the opponent also rolls a Critical Success.
- If both are critical, higher roll wins, then higher score, then reroll.
- On a hit, becomes a Critical Strike.

Critical Strike damage:

```text
(chosen die + fixed modifiers) x 2
```

Then add any explicitly non-doubled additions, such as Piercing's +2.

Critical Strikes do not stack.

## 17.2 Player attack fumble

When a PC rolls a Critical Failure while attacking with a weapon or unarmed:

- Roll the Player Fumble table.
- Apply the result even if the defender also failed and suffers the 1 unavoidable damage.
- A lamp set on the ground has a special fumble interaction: the lamp is kicked over, remaining oil is lost, and the PC becomes Blinded instead of rolling the normal fumble table.

## 17.3 NPC/monster fumble

When an NPC or monster attacks with a Critical Failure:

- Roll on the NPC/Monster Fumble table.
- Apply its result.
- Keep creature effects data-driven.

## 17.4 Defensive Moves

When a defender wins a physical opposed attack:

- A PC defender rolls on the Player Defensive Move table.
- An NPC/monster defender rolls on the NPC & Monster Defensive Move table.
- Apply the resulting effect, duration, target, and trigger.

Defensive Move effects can alter:

- Next attack.
- Armor.
- Conditions.
- Damage Pool.
- Advantage.
- Future defense.
- Recovery.
- Immediate turns.

---

# 18. Conditions

**Source: pp. 88-89.**

Model every condition as structured state:

```python
@dataclass
class ConditionInstance:
    condition_id: str
    source_id: str | None
    magnitude: int | None
    duration_rounds: int | None
    applied_round: int
    stacks: int
    metadata: dict
```

## 18.1 Bleeding (X)

- Deal X damage each combat round.
- Cumulative; add magnitudes.
- Ignores Armor.
- Out of combat: deal 1 Health damage per room.
- Removal out of combat: spend 1 Bandage and pass Medicine.

## 18.2 Blinded

- Disadvantage on all Skill checks except Reason.
- Only basic melee attacks are available.
- Cannot target Hit Locations.
- Cannot use Mastery Abilities.

## 18.3 Burning

- Deal 1 Fire damage each round.
- Not cumulative.
- Ignores Armor.
- Remove in combat by spending 1 Standard Action.
- Remove out of combat by gaining 2 Exhaustion.
- Out of combat: 1 Health damage per room.

## 18.4 Charmed

- Cannot attack or use harmful abilities against the charmer.

## 18.5 Concealed

- An attacker must first pass Perception or Mind to attack the target.
- Can function in or out of combat.
- Attacking or being harmed ends Concealed.

## 18.6 Cursed

- Execute the curse-specific effect.
- Persists until removed.
- Can be cumulative when the curse says so.

## 18.7 Dazed (X)

- Cannot initiate attacks for X rounds.
- Reapplication stacks remaining duration.
- Other non-attack actions remain possible unless prohibited elsewhere.

## 18.8 Freezing

- -10 to all Skills.
- Acts last in combat.
- Starting after the first round, make Endurance each round at no action cost.
- Success removes Freezing.
- Out of combat, make one Endurance check per room to remove it.
- After 5 rooms while Freezing: hypothermia, -50 to all actions.
- After 10 rooms while Freezing: death.

## 18.9 Frightened (XX)

- Reduce physical attack Skills used against the source by XX.
- At end of each afflicted turn, reduce magnitude by 10.
- Ends at 0.
- Cumulative.

## 18.10 Paralyzed

- Cannot move or speak.
- Incapacitated.
- Attacks hit automatically with no Skill check.

## 18.11 Poisoned (X)

- Deal X damage each combat round.
- Cumulative.
- Ignores Armor.
- Starting the round after application, the afflicted may make Endurance/Body as a Free Action each turn to remove/resist the condition.
- Out of combat: 1 Health damage per room.
- Out-of-combat removal: spend 1 Bandage and pass Medicine.

## 18.12 Prone

- Standing is a Free Action.
- When a creature stands, its opponents immediately roll on their Defensive Move table.
- Attacks against Prone have Advantage.
- Attacks made while Prone have Disadvantage.
- While Prone, only basic melee attacks are allowed.
- Cannot target Hit Locations.
- Cannot use Mastery Abilities.

## 18.13 Restrained

- Cannot move.
- -20 to Acrobatics, weapon Skills, Dodge, and Athletics/Body.
- Free Action: Athletics/Body check to remove.
- Standard Action instead: same check with +20.

## 18.14 Sickened (XX)

- Apply `-XX` to all checks.
- Cumulative.

## 18.15 Sleeping

- Immediately Prone.
- Attacks hit automatically.
- Wakes immediately after being hit.

## 18.16 Stunned (X)

- Cannot act for X turns.
- Cannot actively defend against Physical attacks.
- Attacker must still pass an unopposed attack check.
- Reapplication stacks duration.

## 18.17 Enemy condition-removal behavior

Enemies only actively attempt to remove:

- Prone.
- Poisoned.
- Restrained.

Other conditions expire or persist according to their normal rules.

## 18.18 Tick timing recommendation

The book states “each round” but does not assign a universal timing. Use:

```text
Condition damage ticks at the start of the afflicted creature's first activation each round.
```

This prevents multiple ticks on creatures with extra activations.

---

# 19. Healing, death, and the Rot

**Source: pp. 86-87.**

## 19.1 Wounds

“Recover X Wounds” means:

```text
Restore missing Toughness first.
Any remaining healing restores Health.
```

An effect that explicitly heals Toughness or Health does only that resource.

## 19.2 Automatic post-combat recovery

After a victorious fight:

```text
recover d4 Toughness
```

## 19.3 Bandages

Outside combat, once per room:

```text
Spend 1 Bandage
Pass Medicine
Success -> recover d4 Toughness
```

Bandage + Medicine can also remove Bleeding or Poisoned out of combat.

## 19.4 Death

At Health 0, the character dies.

Optional forgiving rule:

- Recover 2d6 Sanity.
- Recover 2d6 Health.
- Restore full Toughness.
- If enemies caused death, they leave and the room becomes clear.
- Lose two unlocked Mastery Abilities of the player's choice.
- Never reduce a Mastery below one Ability.

Store optional-rule selection in campaign settings.

## 19.5 The Rot

Exposure:

```text
Endurance success -> not infected
Endurance failure -> infected at stage 0
```

Each time the infected character rests:

```text
Endurance success -> no advancement
Endurance failure -> Rot stage +1
```

Stages are cumulative and data-driven. Stage 8 removes the character from play.

A rest should include both Taking a Breather and Camp unless a house ruling says otherwise.

---

# 20. Exhaustion

**Source: p. 90.**

Thresholds are cumulative:

| Exhaustion | Effect |
|---:|---|
| 0-10 | No mechanical penalty. |
| 11-15 | All Wound healing is halved. |
| 16-20 | Disadvantage on all checks. |
| 21+ | Death. |

Apply the threshold immediately after any Exhaustion change.

## 20.1 Reducing Exhaustion

- Consume Ration outside combat: -1.
- Take a Breather: -2.
- Camp benefits: -10.
- Eat 1 raw Cooking Ingredient: -1, but make Endurance or suffer 1 Health damage.

Never let current Exhaustion drop below 0.

## 20.2 Healing at 11-15

When healing Wounds:

```python
healing = healing // 2
```

The rules specify halving. Use round down for this specific rule.

---

# 21. Sanity and Madness

**Source: pp. 91-92.**

## 21.1 Resisting Sanity loss

When an effect would cause Sanity loss:

```text
Resolve success -> no Sanity lost
Resolve failure -> lose specified amount
```

Some effects may explicitly bypass this.

## 21.2 Several enemies

When several enemies threaten Sanity:

- Make one Resolve check for the whole encounter.
- On failure, use the highest Sanity-loss value among them.

## 21.3 Reaching 0 Sanity

When Sanity reaches 0:

1. Roll on Madness table.
2. Apply permanent or immediate result.
3. Unless the result ends the character, restore all lost Sanity.

Track cumulative Madness modifiers and permanent penalties.

## 21.4 Recovering Sanity

Common recovery:

- Camp: d4.
- Defeat Overseer: d4.
- Spells or events.
- Madness episode: restore lost Sanity.

---

# 22. Minions, multiple opponents, and targeting

**Source: p. 93, pp. 131-133.**

## 22.1 Minions

- Attack and defend like creatures.
- Heal all Health when a room is cleared.
- Ignore Sanity rules.
- Act during the PC's turn in player-chosen order.
- Cannot equip gear unless a specific effect says otherwise.
- Do not normally level with the PC.

## 22.2 Target assignment

At encounter start:

1. Distribute opponents as evenly as possible among PCs and Minions.
2. Prioritize PCs over Minions when opponents remain.
3. Randomize ties.
4. Lock assignments until opponents die.

When a target dies:

- Reassign its opponent according to the same priority rules.

## 22.3 Extra creature activations

`Ruthlessness(X)` grants X additional activations each round.

If the creature loses actions to Stunned/Paralyzed-like effects:

- Remove one activation per applicable stack/turn lost.
- Remaining activations still occur.
- Decrement the condition as activations are consumed.

## 22.4 Other creature traits

Implement creature traits declaratively:

- Alert: cannot be surprised.
- Frightening: start-combat Resolve or 2 Sanity loss.
- Horrifying: start-combat Resolve or 4 Sanity loss.
- Pack: +5 Combat Skill per other living similar Pack creature.
- Penetrating(X): ignore X Armor.
- Ruthlessness(X): X extra activations.
- Savage: attacks cannot be parried.
- Swift: ignores Reaction penalties.
- Venomous: when it deals damage, Endurance or Poisoned(1).

Creature-type immunities and affinities must be applied before combat begins.

---

# 23. Domain exploration state machine

**Source: pp. 95-100.**

## 23.1 Domain initialization

On first entering a Domain:

1. Generate/assign Overseer.
2. Generate/assign Overseer Influence.
3. Apply Influence to ordinary creatures in that Domain, not the Overseer.
4. Set Tension die to d8.
5. Set Lair die to d10.
6. Mark Exit search inactive.
7. Create empty persistent Growing Darkness list.
8. Award Domain-entry XP once.

If the Overseer is defeated:

- Remove its Influence from all remaining opponents in that Domain.

## 23.2 New-location entry sequence

Recommended order when moving into a location:

```text
1. Commit movement.
2. Spend one room of light.
3. Refresh Aether to usable maximum.
4. Apply out-of-combat condition ticks.
5. If no light, apply Blinded and make Resolve check.
6. If newly generated, determine room/corridor shape.
7. If newly generated, optionally generate description.
8. Resolve Lair or Exit Usage Die check as applicable.
9. Determine special location state: ordinary/lair/exit.
10. Make Tension check.
11. If new and not a lair, check random Combat Encounter.
12. If a new room has no Combat Encounter, roll Event.
13. Discover/check doors as appropriate.
14. Mark location entered and autosave.
```

## 23.3 Room versus corridor

For generated locations:

```text
d100 01-25 -> corridor
d100 26-100 -> room
```

If generation would leave no possible continuation, reroll for a shape with another exit.

## 23.4 Lair search

- Roll Lair Usage Die only when placing a new **room**.
- Starts at d10.
- When d4 depletes, the current room is the Overseer's Lair.
- Optional failsafe: if 15 rooms exist without a lair, the next room is the lair.
- Once found, stop Lair checks.

## 23.5 Exit search

After the Lair is found:

- Begin Domain Exit Usage Die at d8.
- Check it when entering each new room or corridor.
- d4 depletion means the current location is the Domain Exit.
- The Exit otherwise behaves as an ordinary location, including Tension and encounter/event checks.
- The player may leave or continue exploring.
- Normal Domains may be revisited.

## 23.6 Random encounters

After Tension:

```text
New room: encounter on d20 >= 10
New corridor: encounter on d20 >= 15
Overseer Lair: do not roll random encounter
```

If a room has no encounter, roll an Event. Corridors do not receive ordinary Event rolls.

## 23.7 Retracing

When entering a previously cleared location:

- Spend light.
- Refresh Aether.
- Tick out-of-combat effects.
- Make Tension check.
- Do not roll a new Combat Encounter.
- Do not roll an Event.

Persistent room hazards still apply if their description says so.

## 23.8 Doors

If the map does not specify doors:

```text
d10 1-5 -> door
d10 6-10 -> no door
```

Each door has persistent state:

```python
@dataclass
class DoorState:
    id: str
    lock_state: str       # unknown, unlocked, locked, open, broken
    trap_state: str       # unknown, none, detected, spent
    trap_id: str | None
    investigation_done: bool
    lock_difficulty: int
    disarm_difficulty: int | None
```

---

# 24. Light sources

**Source: p. 96.**

## 24.1 Standard duration

- Ordinary Torch: 20 rooms.
- Ordinary Lamp fill: 20 rooms.
- Candle: 10 rooms.
- Specific items may differ.

Decrease duration once per room/location entered, including retracing.

## 24.2 Hands

A Torch or normal Lamp requires a free hand.

Exceptions include:

- Belt Lamp.
- Magical light.
- Other explicitly hands-free sources.

## 24.3 No light

While no source is active:

- Character is Blinded.
- Each new room entry requires Resolve.
- Failure loses 1 Sanity.

## 24.4 Setting down a Lamp in combat

A carried Lamp may be placed on the floor with a Standard Action so the PC can use the freed hand.

While the Lamp is on the floor:

- It still lights the combat.
- If the PC rolls an attack fumble, replace the ordinary fumble with:
  - Lamp is kicked over.
  - All remaining oil is lost.
  - Character becomes Blinded.

---

# 25. Scavenging and hidden containers

**Source: p. 116.**

## 25.1 Scavenge

Once per room:

```text
Make Scavenge check.
Success -> roll Scavenging table.
Failure -> room's ordinary Scavenge attempt is spent.
```

Store `room.scavenge_attempted`.

## 25.2 Deep search

Once per room, separately from Scavenge:

Costs immediately:

```text
Make Tension check.
Gain 2 Exhaustion.
```

Then resolve the found hidden container using lock/trap rules.

After opening:

```text
d10 1-5 -> empty
d10 6-10 -> Container Loot table
```

Store `room.deep_search_attempted`.

---

# 26. Doors, locks, and traps

**Source: pp. 117-119.**

Use a two-phase state machine.

## 26.1 Phase 1: Investigation

### Trap investigation

1. Roll random Difficulty.
2. Make Perception check.

If Perception succeeds:

```text
Roll d10.
7-10 -> trapped and detected; roll trap type now.
1-6  -> no trap.
```

If Perception fails:

```text
Player chooses:
- leave it alone
- interact
```

On interaction:

```text
Roll d10.
7-10 -> trapped and immediately triggered.
1-6  -> no trap.
```

### Lock determination

Roll once:

```text
Door: d20 >= 12 -> locked
Container: d20 >= 10 -> locked
```

Lock state is independent of trap state.

## 26.2 Phase 2A: Detected trap

Player options:

### Disarm

Requirements:

- Thieves' Toolkit.
- Thievery check at random Difficulty.

Results:

```text
Success -> trap spent/disabled
Failure -> trigger trap
```

### Bypass environmental trap

Only for room/corridor environmental traps.

- Make listed avoidance Skill check at +20.
- Success:
  - May exit or interact with doors.
  - Cannot scavenge or interact with other objects in that location.
  - Future bypass attempts against this trap are Effortless (+20).
- Failure: trigger trap.

### Voluntarily trigger

- Make avoidance check at +20.
- Success: trap fires with no consequence.
- Failure: suffer effect.
- Trap becomes spent either way.

## 26.3 Phase 2B: Lock

Only after traps are absent or disarmed.

### Pick lock

Requirements:

- 1 Lockpick.
- Thievery check.

Results:

```text
Success -> open
Failure -> Lockpick breaks
           future attempt reduces Difficulty by one step
```

The PDF does not clearly assign the initial lock Difficulty. Use Normal unless content specifies otherwise.

### Brute force

- Athletics check.
- Success: open/break feature.
- Failure: remains closed.
- Each later attempt gains cumulative +20.
- Every attempt makes noise and triggers a Tension check, success or failure.

## 26.4 Trap triggering

A triggered trap:

1. Determine trap type if not already known.
2. Make the listed avoidance check.
3. If the trap was previously detected, avoidance receives +20.
4. Success avoids all consequences.
5. Failure applies trap effect.
6. Trap triggers only once, then becomes spent/disarmed.

Failed Perception causes triggering when the PC:

- Opens an unlocked trapped feature.
- Attempts lockpicking.
- Attempts brute force.
- Interacts in an environmental-trap location.
- Performs any action prohibited by a bypass.

Keep trap effects in data.

---

# 27. Tension and Growing Darkness

**Source: pp. 120-122.**

## 27.1 Tension die

Chain:

```text
d8 -> d6 -> d4
```

Tension check:

- On 1-2, step down.
- On 1-2 at d4:
  - roll Growing Darkness.
  - apply persistent Domain effect.
  - reset Tension to d8.

## 27.2 Tension triggers

At minimum:

- Moving to another room/corridor.
- Making significant noise.
- Deep searching.
- Brute-forcing a lock.
- Specific events/creatures.
- Any rule that explicitly calls for it.

## 27.3 Persistence

Growing Darkness results:

- Affect only the current Domain.
- Persist when leaving and returning.
- Stack unless their entry says otherwise.
- Some modify future checks, monsters, resources, light, Camp, Tension, or encounter XP.

Reset Tension to d8 when entering a new Domain for the first time. Do not delete the previous Domain's persistent effects.

---

# 28. Resting and Camp

**Source: pp. 123-125.**

## 28.1 Taking a Breather

Outside combat:

```text
Recover d10 + 2 Toughness
Recover 1 Health
Reduce Exhaustion by 2
Reduce light duration by 5
Step Tension die down one stage
```

This is a rest for once-per-rest effects and Rot checks.

If a rule causes a special Tension check after Breather, apply it after stepping the die.

## 28.2 Setting Camp

Camp consists of:

1. Choose activities.
2. Pay resources and Exhaustion.
3. Modify Camp Check.
4. Consume 1 Ration.
5. Roll Camp Check once.
6. On failure, resolve encounter.
7. Apply benefits, possibly reduced.

Base Camp Check:

```text
d20 >= 12 -> safe
d20 <= 11 -> encounter
```

On failed Camp Check:

- Roll encounter.
- If the character survives, Camp benefits are halved, rounding down.

No Ration:

- Camp is still possible.
- Camp benefits are halved, rounding down.
- Cooking may create and immediately consume the Ration.

If both penalties apply, the wording suggests both reductions apply. See Ambiguities.

## 28.3 Base Camp benefits

```text
Restore full Toughness
Recover 1 Health
Recover d4 Sanity
Reduce Exhaustion by 10
```

Apply Exhaustion healing penalties as appropriate.

## 28.4 Camp activities

Store activities as data with costs and effects. Core activities include:

- Attune magic item.
- Barricade.
- Cook Rations.
- Craft Bandages.
- Craft Lamp Oil.
- Craft Lockpicks.
- Craft Torches.
- Remove conditions.
- Repair gear.
- Sleep.
- Swap Mastery Amulet.

Important interactions:

### Barricade

Per Crafting Supply:

```text
+1 Exhaustion
+5 Camp Check
```

### Cooking

Convert each Cooking Ingredient into one Ration.

For crafting any amount:

```text
+1 Exhaustion
-1 Camp Check
```

### Craft Bandages

```text
1 Crafting Supply -> 1 Bandage
Any amount crafted:
    +1 Exhaustion
    -1 Camp Check
```

### Craft Lamp Oil

```text
2 Crafting Supplies -> 1 Lamp Oil
Any amount crafted:
    +1 Exhaustion
    -2 Camp Check
```

### Craft Lockpicks

```text
1 Crafting Supply -> 1 Lockpick
Any amount crafted:
    +1 Exhaustion
    -2 Camp Check
```

### Craft Torches

```text
1 Crafting Supply -> 1 Torch
Any amount crafted:
    +1 Exhaustion
    -2 Camp Check
```

### Heal Condition

Per removable condition:

```text
Spend 1 Bandage
+1 Exhaustion
No Medicine check
```

### Repair

Per item:

```text
Spend 2 Crafting Supplies
```

For repairing any number of items:

```text
+2 Exhaustion
-2 Camp Check
```

Repair broken weapons, Integrity, Acid loss, and similar item damage.

### Sleep

- Cannot combine with activities other than Barricade.
- Additional effects:

```text
-5 Exhaustion
+1 Health
+2 Camp Check
```

These are in addition to ordinary Camp benefits.

## 28.5 Frequency reset

- `once_per_rest`: reset after the next Breather or Camp, whichever comes first.
- `once_per_camp_rest`: reset only after Camp.

---

# 29. Inventory, equipment, and encumbrance

**Source: pp. 206, 212.**

## 29.1 Equipment slots

Maximum equipped body slots:

```text
Main Hand
Off Hand
Belt
Helmet/Head
Armor
Gloves
Boots
Amulet
Ring 1
Ring 2
```

A Two-Handed weapon occupies both hands, effectively leaving 9 equipped items maximum.

Piecemeal torso/vambrace/greave components collectively occupy the Armor body slot.

## 29.2 Carried capacity

Base carried capacity:

```text
10 item slots
```

Equipped items do not count.

Weights:

- Non-encumbering: no slot.
- Light: up to 10 identical/similar light items per slot.
- Normal: 1 slot.
- Heavy: 2 slots.
- Coins/gems: 1 slot per 100 pieces, round up.

Containers:

- Backpack: +20 slots; one equipped maximum.
- Pouch: +5 slots; three equipped maximum.
- No nesting a Backpack/Pouch inside another container to multiply capacity.

## 29.3 Belt

An equipped Belt has four quickslots.

- Drawing or using an item from the Belt is a Free Action.
- A Belt Check rolls d4; the item in that indexed slot is destroyed.

Represent empty Belt slots explicitly.

---

# 30. Weapons, shields, and armor traits

**Source: pp. 207, 210.**

## 30.1 Weapon traits

- Defensive: +10 to defense when used with a shield.
- Quick: +10 Initiative.
- Parrying: allows weapon-Skill defense.
- Powerful: +1 damage.
- Simple: +10 weapon Skill.
- Two-Handed: requires both hands; +2 damage.
- Versatile: +1 damage when wielded with two hands.

## 30.2 Dual wielding

Two One-Handed weapons:

Benefits:

- One free Parry Reaction per round.
- +1 damage.

Costs:

- All attacks at -40.
- Choose a dominant weapon at start of combat.
- Only dominant weapon traits/effects apply.

Track whether the free Parry has been spent.

## 30.3 Shields

- Permit Parry even if weapon lacks Parrying.
- Add shield's Parry bonus to defensive check.
- Defensive weapon trait applies while defending with a shield.
- Shield can be sacrificed to negate a Critical Strike.
- Shield has Integrity.

## 30.4 Armor maneuverability and perception

If armor lists Maneuverability penalty, apply it to:

- Acrobatics.
- Dodge.
- Stealth.

Helmet Perception penalty applies while equipped.

---

# 31. Encounter construction and creature scaling

**Source: pp. 129-133.**

## 31.1 Creature instance

Each creature instance needs:

```python
@dataclass
class CreatureState:
    instance_id: str
    definition_id: str
    current_health: int
    max_health: int
    body: int
    mind: int
    combat_skill: int
    endurance: int
    magic_resistance: int
    armor_by_location: dict[str, int]
    traits: list[str]
    affinities: dict[str, str]
    conditions: list[ConditionInstance]
    target_id: str | None
    reaction_count: int
    activations_remaining: int
```

## 31.2 Level adaptation

When creating an encounter:

- Apply every adaptation threshold up to the PC's current level.
- Adaptations are cumulative.
- Do not mutate static creature definitions; build an encounter instance.

## 31.3 Creature type defaults

Apply type-based rules:

- Animal: no universal modifier.
- Astral: immune to Bleeding, Poisoned, Sickened, Frightened.
- Construct: immune to Charmed, Poisoned, Bleeding, Sickened, Frightened, Sleeping.
- Demon: Restored by Infernal, Vulnerable to Holy, immune to Poisoned.
- Elemental: Restored by its element; immune to Bleeding, Sickened, Poisoned.
- Humanoid: no universal modifier.
- Plant: Vulnerable to Fire; immune to Frightened and Blinded.
- Undead: Vulnerable to Holy; Restored by Necrotic; immune to Bleeding, Sickened, Poisoned, Frightened.

For multi-type creatures, merge type effects. Resolve conflicting affinities using the normal cancellation rule.

## 31.4 Number

When an encounter says multiple creatures:

- Create separate instances.
- Track Health, conditions, actions, targets, and loot separately.
- Recalculate Pack bonuses whenever one dies.

## 31.5 Enemy action selection

On each enemy activation:

1. Roll its Action table.
2. Read action tags.
3. Validate current conditions.
4. Resolve Physical, Magical, or custom check.
5. Apply action result.
6. Decrement durations/end-turn effects.

---

# 32. Loot, Attunement, Potions, and Traders

**Source: pp. 205, 213-221, 126-127.**

## 32.1 Spoils

After victory, each creature's definition determines its spoils procedure.

- Loot is not automatic unless stated.
- Use table IDs rather than embedding table logic in combat code.

## 32.2 Attunement

A magic item behaves as its mundane counterpart until attuned.

At Camp:

```text
Spend 1 Attunement Crystal
Gain 1 Exhaustion
Reveal and activate item's magical properties
```

Track:

- identified.
- attuned.
- attuned character.
- permanent generated properties.
- content version.

## 32.3 Fragments

- One-use magical items.
- Do not require attunement.
- Execute their table-defined effect and consume.

## 32.4 Potions

Identification:

```text
Medicine success -> identify before use
Medicine failure -> remain unknown until consumed
```

After identification or drinking:

1. Determine potion type if still unknown.
2. Roll Potion Aging.
3. Modify potency, duration, or behavior.
4. Apply effect.
5. Consume item.

Permanent aging result requires converting temporary parameters into permanent character modifiers.

## 32.5 Traders

- A discovered Trader remains in that Domain location.
- Ordinary items sell for 50% listed price.
- Magic items sell at rarity-based fixed prices.
- Amulets cannot be sold.
- Trader inventory is table-driven.

---

# 33. Progression

**Source: pp. 62-67.**

## 33.1 XP awards

Core awards:

```text
Open locked door/container: +10 XP
Successfully dismantle trap: +10 XP
Find Lore Book: +10 XP
Enter new Domain: +50 XP
Defeat regular Combat Encounter: +50 XP
Defeat Overseer: +200 XP
```

Award event-based XP exactly once.

## 33.2 Level up

Every 1,000 XP:

- Increase level.
- Gain 1 Ability Point.
- Choose one level-up benefit from the level-up table.
- Preserve surplus XP unless the intended table implementation says to reset; use a running total and `level = 1 + xp // 1000`.

Ability Points unlock Abilities in tier order.

## 33.3 Skill Improvement

At Camp, for each marked Skill:

```text
Roll d100.
Roll > current Skill:
    increase by d4
Roll <= current Skill:
    increase by 1
Cap natural score at 80
Clear improvement mark after resolution
```

This is intentionally a roll-over check, unlike ordinary checks.

## 33.4 Amulet Mastery swapping

At Camp:

- Swap active Mastery Amulet.
- Number of unlocked tiers in the Amulet-granted Mastery is preserved as a count.
- New Amulet Mastery activates the same number of tiers from Tier 1 upward.
- Mastery Feature is active while the Amulet is equipped.
- Ordinary two Masteries remain unchanged.

Store per-Amulet-Mastery unlock count or a shared Amulet-tier count according to the desired interpretation.

## 33.5 Perks and Personal Goals

- Perks are passive rules hooks.
- Goal progress updates from emitted events.
- Apply reward exactly once.
- Completed goals cannot be selected again.

Examples of useful event types:

```text
DamageDealt(type, amount)
OpponentDefeated(type, weapon_skill)
CriticalStrikeDealt
TrapDismantled
RoomScavenged
OverseerDefeated
LoreBookFound
DoorOpened(method)
```

---

# 34. First-run rules

**Source: pp. 243-246.**

## 34.1 Hard Beginnings

After normal character creation:

```text
Suffer d6 damage
Lose d4 Sanity
Gain 1 Exhaustion
```

Starting damage comes from Toughness before Health.

## 34.2 Tutorial Domain overrides

The First Domain:

- Uses a fixed map.
- Uses a special encounter table.
- Has a fixed visible exit; no Domain Exit Usage Die.
- Still checks Tension in every room.
- Still checks each door for lock/trap state.
- Still generates its Overseer and Influence before exploration.
- Cannot be returned to after leaving.

Use scenario data to override ordinary generation on a per-room basis.

---

# 35. Recommended event model

Use immutable events to make logging, undo, and testing easier.

Suggested events:

```text
RollRequested
RollEntered
CheckResolved
OpposedCheckResolved
SkillImprovementMarked
ResourceChanged
TemporaryResourceChanged
AetherReserved
AetherReleased
ConditionApplied
ConditionRemoved
ConditionTicked
DamagePoolRolled
DamageDieSelected
ArmorReduced
ArmorIntegrityStepped
ItemBroken
CreatureDefeated
TargetAssigned
RoundStarted
TurnStarted
ActionSpent
ReactionSpent
CombatEnded
RoomEntered
LightSpent
AetherRefreshed
TensionChecked
UsageDieStepped
GrowingDarknessApplied
DoorInvestigated
TrapTriggered
LockAttempted
CampActivityCompleted
CampCheckResolved
XpAwarded
LevelGained
GoalProgressed
SaveCheckpoint
```

Each event should store:

- event ID.
- transaction/group ID.
- timestamp.
- source and target IDs.
- input rolls.
- before/after values.
- source page.
- content version.

---

# 36. Recommended save-state fields

Minimum root structure:

```json
{
  "schema_version": "1.0.0",
  "content_version": "gravebound-v1",
  "application_version": "0.1.0",
  "rng": {
    "mode": "manual",
    "seed": 0,
    "position": 0
  },
  "campaign": {},
  "character": {},
  "inventory": {},
  "domains": {},
  "current_domain_id": "domain-001",
  "current_room_id": "room-002",
  "encounter": {},
  "pending_roll_request": null,
  "event_log_checkpoint": 1234
}
```

## 36.1 Character state

Store:

```text
Base maxima and current resources
Temporary resources
Permanent modifiers
Skills and improvement marks
Resistances
Masteries and unlocked tiers
Ability Points
Active Sustained effects and reserved Aether
Conditions
Madness results
Rot stage
XP and level
Personal Goals and progress
Perks
Equipment and inventory
Once-per-rest/combat usage flags
```

## 36.2 Domain state

Store:

```text
Overseer and defeated state
Influence
Tension die
Lair die and found status
Exit die and found status
Growing Darkness effects
Room graph
Room visited/cleared/scavenged/deep-searched flags
Door/lock/trap states
Trader locations
Persistent hazards
```

## 36.3 Encounter state

Store:

```text
Round
Initiative winner
Current side/combatant
Target assignments
Each combatant's current Health
Conditions and durations
Reaction count
Actions remaining
Pending multi-action abilities
Damage/defense bonuses
Once-per-combat flags
Integrity-use flags
```

Save at every decision boundary, especially before and after rolls.

---

# 37. Ambiguities and recommended rulings

The PDF has several places where software needs a precise answer that tabletop play can resolve informally. Keep these in a `rulings.md` or configuration file.

## 37.1 Advantage and Disadvantage together

**Not explicitly defined.**

Recommended:

```text
One instance of Advantage cancels one instance of Disadvantage.
Additional instances do not stack; final state is normal/advantage/disadvantage.
```

## 37.2 Initial lockpicking Difficulty

The lock section lowers Difficulty after failed attempts but does not clearly establish the initial roll.

Recommended:

```text
Initial lock Difficulty is Normal unless an Event, item, or scenario specifies otherwise.
```

## 37.3 Initiative against several enemies

Surprise explicitly uses highest enemy Mind; Initiative does not restate it.

Recommended:

```text
Use highest enemy Mind for the encounter-wide Initiative check.
```

## 37.4 Condition tick timing

“Each round” has no universal phase.

Recommended:

```text
Tick ongoing damage at the start of the afflicted creature's first activation each round.
```

This avoids extra ticks from Ruthlessness.

## 37.5 Poison resistance wording

Poisoned says an Endurance/Body check can “resist its effects.”

Recommended:

```text
A successful check removes the entire Poisoned condition.
```

## 37.6 Ending Sustained effects

The rules say the cost is subtracted until the Ability stops.

Recommended:

```text
When the effect ends, immediately release reserved Aether and add it to current Aether, capped by the restored usable maximum.
```

## 37.7 Camp penalties stacking

Failed Camp Check and no Ration each halve benefits.

Recommended strict reading:

```text
Apply both multipliers: full -> half -> quarter, rounding down at each step.
```

A more forgiving mode can apply only one halving. Make it a campaign setting.

## 37.8 Armor “saw use”

Recommended:

```text
Roll Integrity only for a piece that protected a struck location or a shield used to defend/sacrifice.
```

## 37.9 Acid Armor loss

Recommended:

```text
Reduce location Armor by 1 only when at least 1 Acid damage is actually received after Armor and immunity.
```

## 37.10 Slashing +1 order

Recommended:

```text
Subtract Armor.
If remaining Slashing damage is 1-3, add +1.
Then apply Vulnerability/Resistance.
```

## 37.11 Affinity and persistent damage

The PDF explicitly limits Vulnerability/Resistance to direct damage, but is less explicit for Immunity/Restored.

Recommended:

```text
Vulnerable/Resistant: direct damage only.
Immune: blocks matching damage from any source.
Restored: direct damage only unless an effect explicitly feeds healing over time.
```

## 37.12 Multi-action interruption

No general interruption rule is given.

Recommended:

```text
Damage alone does not interrupt charging.
Losing the ability to act pauses or cancels according to the condition.
Leaving combat cancels the pending action.
```

## 37.13 Deep search container existence

The text describes a deep search “to see if” a container exists but supplies no existence roll.

Recommended:

```text
A deep search always finds one hidden container, then the empty/loot roll determines value.
```

## 37.14 Level XP accounting

The rule says accrue 1,000 XP to level.

Recommended:

```text
Use cumulative lifetime/current XP with a threshold every 1,000 and preserve surplus.
```

## 37.15 Both-fail plus attacker fumble

Recommended strict reading:

```text
Defender suffers 1 unavoidable damage.
Attacker also resolves the fumble.
```

## 37.16 Stunned target defense

Recommended:

```text
Attacker makes an unopposed attack check.
No attacker +10 opposed-check advantage is needed unless treating it as an ordinary attack modifier.
On success, resolve hit normally.
```

The PDF says the attacker must still pass an attack check but does not explicitly remove the usual +10. Retaining the standard +10 is the most consistent implementation.

---

# 38. Minimum regression tests

These tests should exist before UI work.

## 38.1 Core checks

```text
Score 50, roll 50 -> success
Score 50, roll 51 -> failure
Score 50, roll 44 -> critical success
Score 40, roll 55 -> critical failure
Doubles Skill roll -> Improvement marked
Doubles Resistance roll -> no Improvement mark
```

## 38.2 Advantage

```text
Digits 6 and 2:
advantage -> 26
disadvantage -> 62
Digits 0 and 0 -> 100
```

## 38.3 Opposed checks

```text
Both succeed -> higher successful roll wins
One succeeds -> success wins
Both fail -> higher failed roll wins outside combat
Critical success beats ordinary success
Critical failure loses
Exact tie -> higher score, then reroll
```

## 38.4 Physical combat

```text
Attacker score 80, roll 92
Defender score 40, roll 66
-> both fail
-> defender suffers 1 unavoidable damage
-> no Defensive Move
```

```text
Defender wins
-> no damage
-> correct Defensive Move table requested
```

```text
Second defense in same round -> -20
Third defense -> -40
New round -> reset
```

## 38.5 Damage Pool

```text
PC rolls d6=3 and d4=4 -> may choose 4
NPC rolls d6=3 and d4=4 -> automatically choose 4
Critical with chosen 4 and +1 -> 10
Piercing critical -> add +2 after doubling
```

## 38.6 Armor and affinities

```text
6 Slashing vs Armor 2 -> 4 damage; no Slashing +1
4 Slashing vs Armor 2 -> 2 then +1 -> 3
6 Bludgeoning vs Armor 2 -> effective Armor 1 -> 5
5 Holy vs Armor 99 -> 5
5 Holy vs Vulnerable Undead -> 10
5 Necrotic vs Resistant -> ceil(2.5) = 3
Vulnerable + Resistant -> 5
```

## 38.7 Aether

```text
Base 14, reserve 2 -> usable 12
Spend 4 -> current 8
Enter new room -> current 12
Sustained effect ends -> usable 14; current 14
```

## 38.8 Conditions

```text
Bleeding(1) + Bleeding(2) -> Bleeding(3)
Burning reapplied -> still one Burning
Dazed(2) + Dazed(1) -> 3 rounds
Frightened(20) -> 10 after one turn -> removed after second
Restrained Standard Action escape -> +20
Stunned target -> no defense roll
```

## 38.9 Tension

```text
d8 roll 2 -> d6
d6 roll 3 -> d6
d4 roll 1 -> Growing Darkness + reset d8
New Domain -> d8
```

## 38.10 Locks and traps

```text
Failed Perception + interact + trap roll 10 -> trap triggered
Detected trap + failed disarm -> avoidance at +20
Trap triggered -> spent afterward
Failed lockpick -> consume Lockpick and reduce next Difficulty one step
Brute force attempt -> always Tension check
```

## 38.11 Camp

```text
Safe Camp with Ration -> full benefits
Failed Camp -> encounter then half benefits
No Ration -> half benefits
Sleep -> only Barricade may coexist
```

## 38.12 Save/reload

Save and reload at:

- Pending manual roll.
- Mid opposed check.
- Between player and enemy side.
- During multi-action Ability.
- After trap identified but before decision.
- After Camp activities but before Camp Check.

The loaded state must request the exact same next intent/roll.

---

# 39. Source-page map

Use these page references in tooltips, logs, and developer diagnostics.

| System | Gravebound pages |
|---|---:|
| Character creation and Attributes | 15-21 |
| Character progression | 62-67 |
| Core checks | 69-74 |
| Combat | 75-85 |
| Healing, Rot, Conditions, Exhaustion, Sanity | 86-92 |
| Minions and co-op | 93 |
| Exploration and Domain generation | 95-100 |
| Scavenging | 116 |
| Locks and traps | 117-119 |
| Tension and Growing Darkness | 120-122 |
| Rest and Camp | 123-125 |
| Potions and Traders | 126-127 |
| Encounter construction | 129-135 |
| Creature definitions | 136-203 |
| Encumbrance and equipment | 205-212 |
| Loot and Attunement | 213-223 |
| Magic item generation | 224-242 |
| First Domain | 243-246 |

---

## Suggested module split

```text
src/kn_companion/
    dice.py
    checks.py
    usage_die.py
    resources.py
    abilities.py
    effects.py
    combat.py
    damage.py
    inventory.py
    exploration.py
    obstacles.py
    rest.py
    progression.py
    content.py
    events.py
    saves.py
```

Build in this order:

1. Dice and CheckResolver.
2. Resources and Aether reservation.
3. Physical combat.
4. Damage, Armor, and conditions.
5. Creature actions and targeting.
6. Save/reload.
7. Room entry and Tension.
8. Locks/traps.
9. Camp and progression.
10. Remaining content tables and UI.

The first vertical slice should load Seraphine's paused encounter and resolve the two Skeletal Horror activations through manually entered dice.
