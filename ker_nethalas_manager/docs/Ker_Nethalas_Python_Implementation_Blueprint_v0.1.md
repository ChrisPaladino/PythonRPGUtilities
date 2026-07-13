# Ker Nethalas Python Implementation Blueprint v0.1

## Purpose

This document converts the planning package into an implementation-ready plan for a Python 3.12+ digital companion.

Primary source documents reviewed:
- `Ker_Nethalas_Digital_Companion_Requirements_v0.1.docx`
- `Ker_Nethalas_Data_Model_v0.1.xlsx`
- `ker_nethalas_sample_data_v0.1/*.json`

## Recommended Technical Direction

1. Build a headless rules engine and PySide6 shell in parallel.
2. Keep rule logic isolated from UI code.
3. Use Automatic roll mode as the default, with manual entry always available.

Rationale:
- Requirements emphasize transparent rule resolution and undoable event history.
- Parallel UI delivery provides an earlier playable desktop experience.
- Engine isolation still enables regression tests from provided test cases and save state.

## Initial Project Structure

Proposed structure under `src/`:

```text
src/
  ker_nethalas/
    __init__.py
    app/
      services.py
      use_cases.py
    content/
      loader.py
      schemas.py
      validators.py
    core/
      models.py
      enums.py
      events.py
      ids.py
    rules/
      dice.py
      checks.py
      combat.py
      exploration.py
      effects.py
      resources.py
      minions.py
    state/
      reducer.py
      snapshots.py
      undo.py
    persistence/
      save_repo.py
      migrations.py
      autosave.py
    interfaces/
      cli_main.py
      pyqt_main.py
  tests/
    unit/
    integration/
    regression/
```

## Engine Model

### Pattern

Use event-sourced state transitions:

`Intent -> Validate -> RollRequest -> RollResult -> DomainEvents -> Apply -> Autosave`

### Why this matches requirements

- FR-071 event log: each decision/roll/state change becomes an event.
- FR-072 undo: reverse the most recent event group by rolling back to prior snapshot or replay.
- FR-073 mixed roll modes: roll source is metadata on each `RollResult`.

## MVP Functional Slice (Build Order)

### Milestone 1: Core checks, dice, and PySide6 shell

Scope:
- FR-010, FR-011, FR-012, FR-014
- Usage dice support needed for FR-015 (minimum d8->d6->d4 and d4 trigger behavior)

Deliverables:
- `checks.py` with pure functions for core/opposed checks
- `dice.py` with automatic/manual roll support and mode metadata
- Unit tests from TC-001, TC-002, TC-003
- PySide6 app shell with: session header, resource panel, action panel, and roll log panel

### Milestone 2: Combat kernel

Scope:
- FR-031, FR-032, FR-033, FR-034, FR-035, FR-036, FR-037, FR-039, FR-040, FR-041

Deliverables:
- Initiative resolution (including Quick weapon adjustment from TC-005)
- Physical attack both-fail unavoidable damage rule (TC-004)
- Creature action table roll and dispatch
- Damage pipeline: hit location -> armor -> affinities -> health/toughness effects

### Milestone 3: Exploration loop (first Domain)

Scope:
- FR-020 to FR-027 subset for first Domain

Deliverables:
- Room entry sequence with light consumption, Aether refresh, Tension stepping
- Door/trap state machine (`unknown/detected/spent`, `unknown/locked/open/broken`)
- First-domain fixed content from `first_domain.json`

### Milestone 4: Persistence and replay safety

Scope:
- FR-070, FR-071, FR-072, FR-074, FR-080

Deliverables:
- Versioned save schema
- Autosave after committed room entry/combat round/major decision
- One-step undo by event-group rollback
- Serialization roundtrip test for TC-010

### Milestone 5: Playable desktop prototype

Scope:
- Coach Mode + Tabletop Mode + Automatic Mode subset (Automatic default)

Deliverables:
- PySide6-driven gameplay loop backed by the same use-case service layer
- Human-readable roll log and state change stream
- Golden scenario playback from `seraphine_save.json`

## Content and Validation Strategy

1. Keep all static content as JSON with stable IDs.
2. Validate referential integrity at load:
   - Ability mastery IDs must exist.
   - Weapon skill IDs must exist.
   - Creature actions must reference known creature IDs.
3. Store `content_version` in save files.
4. Reject incompatible content/save combinations unless migration exists.

## Test Strategy

### Unit tests

- Dice and check math
- Opposed checks and tie behavior
- Damage selection rules and mitigation order

### Integration tests

- Room-entry sequence (light, Aether, Tension, encounter/event gate)
- Combat round transitions and reaction penalties

### Regression tests

- TC-001..TC-010 from provided test cases
- Golden save replay verification (seeded reproducibility optional for MVP)

## Risks and Mitigations

Risk: Rule ambiguity in edge cases (criticals, ties, stacking timings).
Mitigation: Capture decisions in ADR-style notes and pin them with tests.

Risk: Content growth outpacing code maintainability.
Mitigation: Data-first behavior mapping and strict schema validation.

Risk: UI prematurely coupled to rules.
Mitigation: Keep UI as a thin adapter around use-case functions.

## Immediate Next Build Step

Implement Milestone 1 with tests and a minimal PySide6 shell, then run TC-001/002/003 before wiring combat/exploration flows.
