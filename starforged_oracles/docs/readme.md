# Starforged / Sundered Isles Reference

A Tkinter GUI reference and play tool for *Ironsworn: Starforged* and *Ironsworn: Sundered Isles* covering moves, oracles, dice, assets, and character tracking.

## Requirements

- Python 3.10+
- PyYAML

## Installation

```bash
cd starforged_oracles
pip install -r requirements.txt
```

## Launch

```bash
python src/starforged_app.py
```

## Features

### Character tab
- Create, switch, and delete characters with persistent JSON storage
- **Sheet sub-tab** — name, game system, five stats (Edge/Heart/Iron/Shadow/Wits) each with a Roll button, condition meters (Health/Spirit/Supply), Momentum track (−6 to +10) with canvas visualization and color coding (red ≤ 0, vivid green at max)
- **Assets sub-tab** — searchable asset library, dark card UI with ability checkboxes, inline Remove button; per-character asset lists
- **Progress sub-tab** — three XP legacy tracks (Quests/Bonds/Discovery) with canvas 10-box tracks and tick/box buttons; unlimited named progress tracks with difficulty rank and milestone controls, displayed alphabetically
- Autosave with 250 ms debounce; last-used character auto-loads on startup

### Moves tab
- Browse all Starforged and Sundered Isles moves
- Filter by game system and category; live search by name or category
- Full move text with colour-coded outcomes (strong hit / weak hit / miss)
- **Stat roll bar** — for `action_roll` moves, shows a button for each relevant stat (e.g., +IRON (3)) drawn from the active character; rolls d6 + stat vs 2d10 and displays the outcome inline with colour coding
- d100 roll button for moves with oracle tables

### Oracles tab
- Browse ~200+ oracle tables across Starforged and Sundered Isles (18 topic files + custom oracles)
- Live search by table or category name
- **Roll d100** button — rolls and highlights the matching result in the table
- Tables with weighted options (no min/max range) are displayed as lists

### Dice tab
- Manual action roll: enter any stat bonus, roll d6 + bonus vs 2d10
- Full roll breakdown with colour-coded outcome

### Bundles tab
- Pre-configured multi-roll bundles for common oracle combinations (settlement, island, character, etc.)
- Region-sensitive bundles use default region settings automatically

### Settings tab
- Choose default regions for games with regional oracle variants
- Bundle-level region changes persist back to saved settings

## Data Source

All game data is sourced from the [rsek/datasworn](https://github.com/rsek/datasworn) repository, which provides official Ironsworn content under the [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) licence.

> Ironsworn: Starforged and Ironsworn: Sundered Isles are by Shawn Tomkin.
