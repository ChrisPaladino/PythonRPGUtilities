# One Page Solo Engine (OPSE)

A Python-based Tkinter GUI application implementing the One Page Solo Engine system for solo tabletop role-playing. This tool provides a comprehensive suite of oracles, generators, and game tools to support solo RPG play using a card-based or dice-based resolution system.

## Overview

The One Page Solo Engine is a GM emulator system that uses a standard 52-card deck (plus 2 jokers) or dice to generate narrative prompts, resolve yes/no questions, and create unexpected story elements. This application provides an easy-to-use interface with all the core OPSE tools and tables.

## Features

### Core Oracle Systems

- **Oracle (Card Interpretation)**: Draw cards to interpret action focus, detail focus, and topic focus based on suit (domain) and rank
- **Yes/No Oracle**: Resolve binary questions with likelihood modifiers and "but/and" results
- **Random Event Generator**: Generate unexpected story complications with subject and action elements

### Scene Management

- **Set the Scene**: Roll for altered scenes and scene complications to begin each scene
- **Pacing Moves**: Generate mid-scene story beats to maintain narrative momentum
- **Failure Moves**: Determine consequences when player actions fail

### Character & Story Generators

- **NPC Generator**: Create non-player characters with identity, goals, and notable features
- **Plot Hook Generator**: Generate complete adventure hooks with objectives, adversaries, and rewards

### Specialized Tools

- **Dungeon Crawler**: Generate dungeon rooms with location type, encounters, objects, and exits
- **Hex Crawler**: Generate wilderness hexes with terrain, contents, features, and events
- **Generic Tables**: Quick access to howor quality interpretations for any oracle result

### Deck Management

- **Card Drawing**: Draw from a standard 54-card deck (52 cards + 2 jokers)
- **Automatic Reshuffle**: When a joker is drawn, discard pile automatically shuffles back in
- **Manual Controls**: Shuffle discards or reset the full deck at any time

### Dice Tools

- **Multiple Dice Types**: Roll d4, d6, 2d6, or d12
- **Coin Flip**: Simple heads/tails resolution
- **Card-to-Dice Conversion**: Optional rules for using cards as dice substitutes

## Requirements

- Python 3.10 or higher
- Tkinter (usually included with Python; install `python3-tk` on Linux if needed)

## Installation

1. **Clone or Download the Repository**:

   ```bash
   git clone https://github.com/ChrisPaladino/PythonRPGUtilities
   cd one_page_solo_engine
   ```

2. **Ensure Python is Installed**:
   Verify Python 3 is installed:

   ```bash
   python3 --version
   ```

   Install Python if needed from <https://www.python.org/downloads>

3. **Install Tkinter (if not included)**:
   On Linux, you may need:

   ```bash
   sudo apt-get install python3-tk  # Debian/Ubuntu
   sudo yum install python3-tkinter  # CentOS/RHEL
   ```

## Usage

1. **Launch the Application**:

   ```bash
   python3 src/opse_app.py
   ```

2. **Interface Layout**:

   - **Top Row (5 tabs)**: Oracle, Set Scene, GM Moves, Random Event, NPC Generator
   - **Bottom Row (5 tabs)**: Plot Hook, Generic, Dungeon, Hex, Tools
   - **Right Panel**: Scrolling log of all results

3. **Basic Workflow**:

   - **Start a Scene**: Use "Set the Scene" tab to see if anything unexpected happens
   - **Ask Questions**: Use "Oracle" tab to interpret card draws or "Yes/No" for binary questions
   - **Generate Content**: Use NPC, Plot Hook, or location generators as needed
   - **Handle Complications**: Use "Random Event" or "GM Moves" when the story needs a twist

## Card Interpretation System

### Suits and Domains

- **♣ Clubs**: Physical (appearance, existence)
- **♦ Diamonds**: Technical (mental, operation)
- **♠ Spades**: Mystical (meaning, capability)
- **♥ Hearts**: Social (personal, connection)

### Action Focus (by Rank)

- **2**: Seek | **3**: Oppose | **4**: Communicate
- **5**: Move | **6**: Harm | **7**: Create
- **8**: Reveal | **9**: Command | **10**: Take
- **J**: Protect | **Q**: Assist | **K**: Transform
- **A**: Deceive

### Detail Focus (by Rank)

- **2**: Small | **3**: Large | **4**: Old
- **5**: New | **6**: Mundane | **7**: Simple
- **8**: Complex | **9**: Unsavory | **10**: Specialized
- **J**: Unexpected | **Q**: Exotic | **K**: Dignified
- **A**: Unique

### Topic Focus (by Rank)

- **2**: Current Need | **3**: Allies | **4**: Community
- **5**: History | **6**: Future Plans | **7**: Enemies
- **8**: Knowledge | **9**: Rumors | **10**: A Plot Arc
- **J**: Recent Events | **Q**: Equipment | **K**: A Faction
- **A**: The PCs

### Special: Jokers

When a joker is drawn:

- The discard pile automatically shuffles back into the deck
- A **Random Event** is triggered
- The log displays which color joker was drawn

## Yes/No Oracle

Ask any yes/no question and select a likelihood:

- **Likely**: Higher chance of "yes"
- **Even**: 50/50 chance
- **Unlikely**: Lower chance of "yes"

Results include:

- Basic: Yes or No
- Modified: "Yes, but..." or "No, and..."
- Exceptional: "Yes, and..." or "No, but..."

Based on 2d6 roll with modifiers.

## Scene Management Details

### Set the Scene

Before starting a new scene, roll to check if:

1. The scene is **Altered** (different than expected)
2. A **Scene Complication** occurs immediately

### Pacing Moves (d6)

Use during scenes to maintain momentum:

1. Foreshadow Trouble
2. Reveal a New Detail
3. An NPC Takes Action
4. Advance a Threat
5. Advance a Plot
6. Add a Random Event

### Failure Moves (d6)

When player actions fail:

1. Cause Harm
2. Put Someone in a Spot
3. Offer a Choice
4. Advance a Threat
5. Reveal an Unwelcome Truth
6. Foreshadow Trouble

## Random Event Generator

Generates unexpected story complications by drawing two cards:

- **First Card**: Subject (what the event is about)
- **Second Card**: Action (what happens)

Interpret using Action, Detail, and Topic focus tables.

## NPC Generator

Draws cards to create:

- **Identity**: Social role/occupation (Outlaw, Merchant, Leader, etc.)
- **Goal**: What they want (Obtain, Protect, Avenge, etc.)
- **Feature**: Notable characteristic (d6 roll)

## Plot Hook Generator

Creates complete adventure seeds with:

- **Objective** (d6): Eliminate threat, learn truth, recover item, escort, restore, or save
- **Adversaries** (d6): Organization, outlaws, guardians, inhabitants, horde, or villain
- **Rewards** (d6): Money, knowledge, support, plot advancement, or magical item

## Location Generators

### Dungeon Crawler

For each room, generates:

- **Location Type**: Purpose of the area
- **Encounter**: Empty, hostile, obstacle, or unique NPC
- **Object**: Mundane, interesting, useful, valuable, or rare
- **Exits**: Dead end, 1 exit, or 2 exits

### Hex Crawler

For wilderness exploration:

- **Terrain**: Same, common, uncommon, or rare
- **Contents**: Usually empty, occasionally has a feature
- **Feature**: Structure, hazard, settlement, natural wonder, new region, or dungeon entrance
- **Event**: Usually none, sometimes triggers random event

## Generic Tables

Quick reference for interpreting oracle results:

### How (Quality) - d6

1. Surprisingly lacking
2. Less than expected
3. About average
4. About average
5. More than expected
6. Extraordinary

## Tools Tab

Convenient access to:

- **Deck Controls**: Draw card, shuffle discards, reset full deck
- **Dice Rollers**: d4, d6, 2d6, d12, coin flip
- **Log Controls**: Clear the output log

## Directory Structure

```text
one_page_solo_engine/
├── src/
│   └── opse_app.py    # Main application file
└── docs/
    └── readme.md      # This file
```

## Tips for Use

1. **Starting a Session**:

   - Begin with "Set the Scene" to establish context
   - Use the Oracle tab to answer situational questions
   - Draw cards when you need inspiration

2. **Handling Uncertainty**:

   - Use Yes/No oracle for binary questions
   - Use Generic tables for "how much" or "how well" questions
   - Trust your interpretation of card draws

3. **Maintaining Pace**:

   - Roll Pacing Moves periodically to keep story moving
   - Use Random Events when things feel stale
   - Apply Failure Moves when actions don't succeed

4. **Building Content**:

   - NPC generator for on-the-fly characters
   - Plot Hook generator for new adventure ideas
   - Location generators for exploration scenarios

## Keyboard Navigation

- **Tab**: Move between controls
- **Enter**: Activate focused button
- **Arrow Keys**: Navigate dropdown menus
- **Mouse Wheel**: Scroll log output

## System Reference

This application implements v1.6 of the One Page Solo Engine system. For complete rules and guidance on interpreting oracle results, consult the official OPSE documentation.

### Core Mechanics

- **Card Draws**: Primary oracle resolution method
- **Dice Alternatives**: All tables can be accessed via dice if preferred
- **Joker Rule**: Automatic shuffle + random event on joker draw
- **Multiple Interpretations**: Combine Action/Detail/Topic focus for rich results

### Design Philosophy

The OPSE system emphasizes:

- Quick resolution without complex mechanics
- Multiple interpretation layers for depth
- Flexible tools for various play styles
- Support for both tactical and narrative play

## Customization

The application stores all tables as dictionaries in the source code. You can easily modify:

- Card interpretation tables (ACTION_FOCUS, DETAIL_FOCUS, TOPIC_FOCUS)
- Scene tables (SCENE_COMPLICATION, ALTERED_SCENE, PACING_MOVES)
- Generator tables (NPC_IDENTITY, PLOT_OBJECTIVE, etc.)
- Location tables (DUNGEON_*, HEX_*)

Simply edit the relevant dictionary in `opse_app.py` and restart the application.

## Future Enhancements

Potential improvements:

- Save/load game log to file
- Export results to text or markdown
- Custom table editor
- Multiple oracle deck support
- Sound effects for card draws
- Themeable UI

## License

This project is open-source under the MIT License. Feel free to modify and distribute as needed.

## Credits

This application implements the One Page Solo Engine system. OPSE is designed for solo play and GM emulation in tabletop role-playing games.

## Contact

For issues or suggestions, please open an issue on the repository or contact the maintainer.
