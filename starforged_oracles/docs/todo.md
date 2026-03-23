# Todo Items

## 1. Dice rolling for moves

Roll **Challenge Dice** (2d10) and an **Action Roll** (1d6 + STAT).

Outcome rules (ties always go to the challenge dice — equal does NOT beat):

| Result | Condition |
| -------- | ----------- |
| **Strong Hit with a Match** | Action Roll > both challenge dice, AND the two challenge dice show the same number |
| **Strong Hit** | Action Roll > both challenge dice (no match) |
| **Weak Hit** | Action Roll > exactly one challenge die |
| **Miss** | Action Roll does not beat either challenge die |

Additional rule: **Action Roll total is capped at 10**, even if stat + die > 10.

Short-term implementation: prompt the user to enter their STAT value (0–5) when rolling.

Long-term: support a character sheet / stats object so the STAT is pre-filled per move.

## 2. Character stats (longer term)

Store a simple character object with the five stats used for action rolls:

- **Edge** — speed, agility, ranged combat
- **Heart** — courage, social, leadership
- **Iron** — strength, endurance, melee
- **Shadow** — stealth, deception, trickery
- **Wits** — knowledge, perception, crafting

Each stat is a value from 1–3 (occasionally 0 or 4 with assets). Let the user set these
once and have the relevant stat pre-selected when rolling a specific move.
