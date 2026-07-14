# Ker Nethalas MVP Decisions v0.1

Decisions confirmed on 2026-07-13:

1. Interface first: PySide6 immediately.
2. Default roll mode: Automatic.
3. Undo scope: One-step undo.
4. Persistence: JSON save plus append-only event log.
5. Rules text policy: Include longer verbatim text where useful (subject to your legal/usage rights for source material).
6. Determinism requirement for automatic rolls: No hard requirement.
7. Opposed checks: critical success precedence is enabled.
8. Exact successful ties: always require reroll.
9. Condition timing default: start of affected actor turn.
10. Minion targeting: prompt each minion action.
11. Next build slice priority: combat round engine first.
12. Free Action limit: one per round.
13. Standard Actions default: one per round unless modified by item/ability.
14. Reactions: unlimited per round, with cumulative -20 after the first until next round.
15. Multi-action charging: while charging, reactions suffer additional -10 and no different reaction Ability may be used.
16. Opposed checks tie-break order: higher roll, then higher tested Skill, then reroll.
17. Both-fail opposed checks: highest failed roll wins; then highest tested Skill; then reroll.
18. Critical definitions: doubles below tested Skill are Critical Success; doubles above tested Skill are Critical Failure.
19. Critical failure extra consequences: not in MVP (normal failure handling for now).
20. Enemy target policy for MVP: assign once at combat start, prioritize PCs over minions for extra enemies, and keep assignments fixed until encounter end.
21. Attack check baseline: attacker gets +10, weapon speed subtracts from defender defense skill, defender win triggers Defensive Move roll.
22. Attack both-fail override: defender suffers 1 unavoidable damage regardless of critical status.
23. Initiative check: player Perception vs highest enemy Mind as an opposed check.
24. Surprise check: player Stealth vs highest enemy Mind, with follower penalty (-10 each); on success initiative is player side and first attack gets +20; on failure apply -20 to subsequent initiative Perception check.
25. Defensive Move tables: both Player and NPC/Monster D10 tables are implemented as explicit effect mappings, ready for turn-resolution hooks.
26. Rules tables should default to JSON content files, with code acting as resolvers/validators.
27. Creature action tables are content-driven per creature in `content/enemies.json`.
28. Difficulty modifiers are content-driven in `content/difficulty_modifiers.json` and resolved via D8 roll mapping.
29. Critical success/failure effects are content-driven in `content/critical_effects.json`, keyed by check/skill id.
30. Content JSON files are schema-validated at load and on app startup; malformed content fails fast with explicit errors.
31. Encounter prototype includes explicit `EncounterState` and `CombatantState` models with locked enemy target assignments.
32. Enemy-turn resolver now executes: creature action roll -> assigned target -> physical/magical resolution -> optional Defensive Move application -> combat log append.
33. Effect application currently includes core status/modifier effects and placeholder hooks for pending systems (full damage pool, location-aware armor, turn scheduler immediates).

## Implementation Impact

- UI adapter and screens are included in Milestone 1 planning, not deferred.
- Dice service supports both automatic and manual roll inputs, with Automatic selected by default in new sessions.
- Undo system targets single event-group rollback only in MVP.
- Save envelope remains JSON with a separate event stream.
- RNG seed is still stored for diagnostics and reproducibility when desired, but exact replay is not mandatory in all flows.
- Opposed check resolver supports critical precedence and tie-reroll outcomes.
- Combat flow will surface per-action minion target prompts instead of target lock automation.
- Combat action economy enforces one Free Action, one default Standard Action, cumulative reaction penalties, and charging restrictions.
- Opposed check resolver now follows full procedure text, including tie-break hierarchy and reroll trigger.
- Combat policy now includes fixed start-of-encounter enemy assignments with PC-priority overflow, plus deferred fumble extras.
- Combat rules now include implemented attack contest resolution, weapon speed defense penalty, initiative checks, and surprise attempt outcomes.
- Defensive Move D10 outcomes are now available as resolvers for both player and NPC defenders.
- Defensive Move data is now loaded from JSON content files to keep rules data separate from engine logic.
- Enemy actions, difficulty modifiers, and critical effect text are now JSON-backed content, resolved by thin Python helpers.
- Loader validation now enforces structural integrity of content tables before gameplay starts.
- Engine now has an integration-level enemy-turn pipeline suitable for scenario tests and UI wiring.

## Compliance Note

If this project is distributed publicly, avoid embedding large copyrighted rulebook text unless you have explicit permission. A safer baseline is paraphrased summaries with edition and page references.
