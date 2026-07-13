# Ker Nethalas Clarifying Questions v0.1

These are the key decisions needed before coding Milestone 1-3.

## Rules Resolution Questions

1. Critical handling policy:
- Should doubles always map to critical outcomes for all check types, or only when explicitly defined by the subsystem?

2. Opposed check tie-breakers:
- For equal successful rolls, do we always favor the acting side, or does context (attack vs defense, initiative, social checks) change tie resolution?

3. Advantage/disadvantage application:
- Should digit-flip apply only to d100 checks, and can multiple sources stack or collapse to single advantage/disadvantage?

4. Damage pool choice UX:
- In Automatic Mode, should the engine auto-pick highest die by default, or prompt with a deterministic strategy setting?

5. Both-fail physical attack rule:
- Confirm this applies universally to all physical attacks, including creature actions and improvised attacks.

## Combat and Effects Questions

6. Condition timing:
- Should condition ticks happen at start of owner turn, end of owner turn, or vary by condition with explicit metadata?

7. Reaction penalties:
- Is cumulative reaction penalty reset at round start or at each actor turn start?

8. Minion targeting behavior:
- For autonomous minions (e.g., raised skeleton), should user be prompted every turn for target, or can target lock persist until invalid?

9. Fear/Frightening trait:
- Do Frightening checks happen once on encounter start, once per target acquisition, or once per round in sight?

## Exploration Questions

10. Tension/Growing Darkness content source:
- Do you already have complete tables digitized, or should we implement placeholders plus hooks first?

11. Retracing and event gating:
- On revisits, are there any room-specific exceptions that still allow events beyond tension rolls?

12. Rest cadence:
- For first MVP, should we fully implement Breather/Camp frequencies now, or defer Camp and keep Breather only?

## Product and UX Questions

13. First playable interface priority:
- Do you want terminal CLI first (fastest), or should we start directly with PySide6 despite slower iteration?

14. Roll mode default:
- Should new sessions default to Tabletop Mode (manual dice entry) or Automatic Mode?

15. Rule transparency level:
- Should every result display full formula details by default, or use collapsible detail lines to keep logs compact?

## Content and Legal Questions

16. Source-text usage policy:
- Should we keep all in-app rule text paraphrased only, with page references, to avoid embedding long verbatim rulebook text?

17. Content pack ownership:
- Will this remain private/personal use, or should we design from day one for publicly shareable community content packs?

## Engineering Questions

18. Persistence preference:
- JSON-only saves plus append-only event logs, or JSON save snapshots with optional SQLite history later?

19. Undo scope:
- Is one-step undo sufficient for MVP, or should we provide multi-step undo immediately?

20. Determinism guarantee:
- Should seed + index reproducibility be treated as a hard requirement for all automated rolls in every mode?

## Recommended Default Decisions If Unanswered

If you want me to proceed immediately, I can assume:
- doubles are subsystem-specific criticals,
- acting side wins exact ties only where rules are ambiguous,
- single-level advantage/disadvantage (non-stacking),
- CLI first,
- JSON saves + event log,
- one-step undo in MVP,
- strict deterministic RNG for automatic rolls.
