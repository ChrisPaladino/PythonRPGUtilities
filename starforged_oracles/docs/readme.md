# Starforged / Sundered Isles Reference

A Tkinter GUI reference tool for *Ironsworn: Starforged* and *Ironsworn: Sundered Isles* moves and oracle tables.

## Requirements

- Python 3.10+
- PyYAML

## Installation

```bash
cd starforged_oracles
pip install -r requirements.txt
```

## Setup — Download Data

Game data is fetched directly from the [Datasworn repository](https://github.com/rsek/datasworn) (CC-BY-4.0).  
Run this **once** before launching the app:

```bash
python src/fetch_data.py
```

Files are saved to the `data/` directory.

## Launch

```bash
python src/starforged_app.py
```

## Features

- **Moves tab** — Browse all 56 Starforged moves (12 categories)
  - Filter by category (Adventure, Combat, Quest, etc.)
  - Live search by move name or category
  - Full move text with colour-coded outcomes (strong hit / weak hit / miss)
- **Oracles tab** — Browse ~200 Sundered Isles oracle tables (18 topic files)
  - Live search by table or category name
  - **Roll d100** button — rolls and highlights the matching result in the table
  - Tables with weighted options (no min/max range) are displayed as lists

## Data Source

All game data is sourced from the [rsek/datasworn](https://github.com/rsek/datasworn) repository, which provides official Ironsworn content under the [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) licence.

> Ironsworn: Starforged and Ironsworn: Sundered Isles are by Shawn Tomkin.
