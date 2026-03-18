# Todo Items

## 1. Download and bundle all data locally

I do not want to depend on the GitHub repo at runtime — it could go away or change.
`fetch_data.py` should be kept as a **one-time setup tool** (not deleted), and the
`data/` folder should be committed to the repo or clearly documented as required.

Download priority:

1. **Moves — Sundered Isles** (pirates / latest engine)
   - Note: the Datasworn repo only has SI *move enhancements* (`session.yaml`), not the
     full SI move list. Full SI moves are functionally the same as Starforged moves with
     small modifications, so SF moves serve as the SI move base.
2. **Moves — Starforged** (space / sci-fi) ✅ done
3. **Oracles — Sundered Isles** ✅ done (18 YAML files, ~198 tables)
4. **Oracles — Starforged** (15 YAML files: `campaign_launch`, `characters`, `core`,
   `creatures`, `derelicts`, `derelicts_zones`, `factions`, `location_themes`, `misc`,
   `moves`, `planet_types`, `planets`, `settlements`, `space`, `starships`, `vaults`)
   — not yet downloaded
5. **Oracles — Ironsworn Classic** (fantasy / viking)
   - `classic/moves.yaml` and `classic/oracles/` directory exist in Datasworn
   - not yet downloaded

## 2. Dice rolling for moves

Roll **Challenge Dice** (2d10) and an **Action Roll** (1d6 + STAT).

Outcome rules (ties always go to the challenge dice — equal does NOT beat):

| Result | Condition |
|--------|-----------|
| **Strong Hit with a Match** | Action Roll > both challenge dice, AND the two challenge dice show the same number |
| **Strong Hit** | Action Roll > both challenge dice (no match) |
| **Weak Hit** | Action Roll > exactly one challenge die |
| **Miss** | Action Roll does not beat either challenge die |

Additional rule: **Action Roll total is capped at 10**, even if stat + die > 10.

Short-term implementation: prompt the user to enter their STAT value (0–5) when rolling.

Long-term: support a character sheet / stats object so the STAT is pre-filled per move.

## 3. Character stats (longer term)

Store a simple character object with the five stats used for action rolls:

- **Edge** — speed, agility, ranged combat
- **Heart** — courage, social, leadership
- **Iron** — strength, endurance, melee
- **Shadow** — stealth, deception, trickery
- **Wits** — knowledge, perception, crafting

Each stat is a value from 1–3 (occasionally 0 or 4 with assets). Let the user set these
once and have the relevant stat pre-selected when rolling a specific move.