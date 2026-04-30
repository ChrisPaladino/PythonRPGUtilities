# Todo Items

## ✅ 1. Dice rolling for moves — DONE

Roll **Challenge Dice** (2d10) and an **Action Roll** (1d6 + STAT).

Outcome rules (ties always go to the challenge dice — equal does NOT beat):

| Result | Condition |
| -------- | ----------- |
| **Strong Hit with a Match** | Action Roll > both challenge dice, AND the two challenge dice show the same number |
| **Strong Hit** | Action Roll > both challenge dice (no match) |
| **Weak Hit** | Action Roll > exactly one challenge die |
| **Miss** | Action Roll does not beat either challenge die |

Additional rule: **Action Roll total is capped at 10**, even if stat + die > 10.

Implemented in two places:
- **Dice tab** — manual stat entry, full roll breakdown
- **Moves tab** — stat buttons auto-populated from active character, result shown inline

## ✅ 2. Character stats — DONE

Full character sheet implemented in the **Character tab** with:

- Name and game system (Starforged / Sundered Isles)
- Stats: Edge, Heart, Iron, Shadow, Wits (each with Roll button)
- Condition meters: Health, Spirit, Supply (each with Roll button)
- Momentum track (−6 to +10) with canvas visualization and color coding
- XP legacy tracks: Quests, Bonds, Discovery (10-box canvas tracks, +/− tick and box buttons)
- Progress tracks: unlimited named tracks with difficulty and canvas visualization, sorted alphabetically
- Assets: full searchable library with ability checkboxes, dark card UI
- Autosave with 250 ms debounce
- Multi-character support with last-used auto-load

## 3. YAML Files Still Needed

- `bundles.yaml` — additional bundle groups (see below)
- `si_oracles/encounters.yaml`
- `si_oracles/other.yaml`
- `si_oracles/plunder.yaml`
- `si_oracles/ruins.yaml`

## 4. Additional Bundles (Sundered Isles)

Continue making bundles of "these usually go together" oracles / rolls:

- Settlement
	- Settlement location: 1 roll
	- Settlement size: 1 roll
	- Settlement aesthetics: 2 rolls
	- Settlement first look: 2 rolls, curse die
	- Settlement Controlling Faction: 1 roll
	- Settlement Disposition: 1 roll
	- Settlement Authority: 1 roll
	- Settlement Focus: 2 rolls, curse die
	- Settlement Details: 2 rolls, curse die
	- Settlement Name: 1 roll, curse die
- Island
	- Island landscape
		- Size: 1 roll
		- Terrain: 1 roll
		- Vitality: 1 roll
		- Visible Habitation: 1 roll
		- Nearby Islands: 1 roll
		- Coastline aspects: 2 rolls
		- Offshore observations: 2 rolls, curse die
		- Island name: 1 roll, curse die
- Character
	- Character first look: 2 rolls, curse die
	- Character disposition: 1 roll
	- Character role: (this has a sub-table)
		- Various sub-tables for Academic, Agent, etc.
	- Trademark accessories: 2 rolls
	- Trademark weapons: 1 roll, curse die
	- Character details: 2 rolls, curse die
	- Character goals: 2 rolls, curse die
	- Character Name: combine given names into 200-entry list, family names into 200-entry list
		- Cursed moniker has sub-tables

## 5. Code / Data — Smaller Items

- Starting Region oracle
- Overland waypoints (p150)
- Moves tab: `progress_roll` and `special_track` move types — currently show outcomes only, no roll mechanic

## Future State

- Rename project to be more appropriate to what it does
- Handle Myriads, Margins, Reaches for various Tables
- Handle Island name based on type of grouping
- Handle Settlement name based on location
- Faction grid