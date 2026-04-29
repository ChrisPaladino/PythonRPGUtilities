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

Store a simple character object with

- Name
- Stats (see below)
- Assets (from the assets yaml), typical characters start with 3
- Condition meters (Health, Spirit, Supply - all start at 5, and can go down to 0)
- Momentum (starts at +2, can go from -6 to +10), Max Momentum (starts at 10), Momentum Reset (starts at +2)
- Quests XP (a 10 box tracker that can be incremented in between 1 and 4 ticks - 4 filling the box completely -
  dependant on the difficulty of the achieved quest. Each full box grants 2 experience points.
- Bonds XP (another 10 box tracker that can be incretemented and each full box gives 2 xp)
- Discovery XP (you see the pattern here, same - it's a 3rd track)
- Progress tracks (between 0 and a theoretical infinite amount of 10 box tracks that can be incremented between 1 and 4
  ticks. 4 ticks being a full box). Note this tracker does have text associated with it (the vow name, the journey, the
  goal) and a difficulty: Troublesome (3 full boxes per milestone), Dangerous (2 full boxes per progress milestone),
  Formidable (1 full box per progress milestone), Extreme (2 ticks per progress milestone) and Epic (1 tick for passing
  a milestone)


The five stats used for action rolls. These stats typically range from 1 to 3 (although rare
occurances could allow slightly lower or higher). The typical score array for new characters is 3, 2, 2, 1, 1

- **Edge** — speed, agility, ranged combat
- **Heart** — courage, social, leadership
- **Iron** — strength, endurance, melee
- **Shadow** — stealth, deception, trickery
- **Wits** — knowledge, perception, crafting

Each stat is a value from 1–3 (occasionally 0 or 4 with assets). Let the user set these
once and have the relevant stat pre-selected when rolling a specific move.

## 1. YAML Files

- bundles.yaml
- si_assets\companion.yaml
- si_oracles\encounters.yaml
- si_oracles\other.yaml
- si_oracles\plunder.yaml
- si_oracles\ruins.yaml

# Code
- Starting Region
- Overland waypoints (p150)

Let's continue making bundles of "these usually go together" oracles / rolls in Sundered Isles:
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
	- Character Name: need to discuss this one - the given name (first name) and family name (last name) is there twice (1-100), and Moniker uses a Curse die. My suggestion would be to combine the given names into a big 200 entry list, and combine family name into a big 200 entry list.
		- Cursed moniker has sub-tables

Future state
- Rename project to be more appropriate to what it does
- Handle Myriads, Margins, Reaches for various Tables?
- Handle Island name based on type of grouping
- Handle Settlement name based on location
- Faction grid