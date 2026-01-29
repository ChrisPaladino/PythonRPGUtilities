# RPG Generator

RPG Generator is a Python-based tabletop role-playing game (TTRPG) helper application designed to assist game masters and players by providing tools for rolling dice, generating oracles, managing characters and threads, and creating narrative elements like NPCs and plot points. Built with Tkinter for a user-friendly GUI, it supports solo and group play by offering features like fate checks, action oracles, and theme-based plot generation.

## Features

- **Dice Rolling**: Roll action and danger dice with customizable counts (0–10 each), with results like Success, Partial Success, Failure, or Botch, including boon calculations.
- **Fate Checks**: Use a chaos factor (1–9) and likelihood scale (Certain to Impossible) to resolve yes/no questions, with outcomes including Exceptional Yes/No and Random Events.
- **NPC Generation**: Create detailed NPCs with names, ages, sexes, motivations, and characteristics drawn from JSON data.
- **Action Oracle**: Generate random action prompts for narrative inspiration (e.g., "Investigate Mystery").
- **Theme and Plot Points**: Generate story themes (Action, Mystery, Personal, Social, Tension) with associated plot points, weighted by user-defined order.
- **NPC Interactions**: Roll for NPC mood, bearing, and focus based on relationship and demeanor for dynamic roleplay.
- **Character and Thread Management**: Add, update, delete, and randomly select characters and threads, stored in JSON files for campaign persistence.
- **Campaign Save/Load**: Save and load campaign data (characters, threads) to/from JSON files for continuity.

## Requirements

- Python 3.6 or higher
- Tkinter (usually included with Python; install `python3-tk` on Linux if needed)
- JSON files (`action_oracle.json`, `npc_data.json`, `plot_points.json`) in the `data/` directory

## Installation

1. **Clone or Download the Repository**:
    git clone <https://github.com/ChrisPaladino/PythonRPGUtilities>
    cd RPG_Generator
2. Ensure Python is Installed: Verify Python 3 is installed:
    python3 --version
    Install Python if needed from <https://www.python.org/downloads>
3. Install Tkinter (if not included): On Linux, you may need:
    sudo apt-get install python3-tk  # Debian/Ubuntu
    sudo yum install python3-tkinter  # CentOS/RHEL
4. Verify JSON Data Files:
    - Ensure the data/ directory contains:  
        - action_oracle.json
        - npc_data.json
        - plot_points.json
    - These files are required for NPC generation, action oracles, and plot points. Example structures are assumed (e.g., npc_data.json with names, modifiers, nouns, etc.).
5. Run the Application:
    python3 main.py

## Usage

1. Launch the Application: Run main.py to open the Tkinter GUI with three tabs: Themes, Fate & Oracles, and Characters & Threads.
2. Themes Tab:
    - Reorder themes (Action, Mystery, Personal, Social, Tension) using Move Up/Down buttons.
    - Click "Generate Themes" to produce five weighted plot points based on theme order.
    - Reset to default order with "Reset Order".
    - Output appears in a scrollable text area.
3. Fate & Oracles Tab:
    - Dice Rolling: Set action (0–10) and danger (0–10) dice counts, then click "Roll Dice" to see results (e.g., "Success with 2 BOON(s)") with a visual dice display.
    - Fate Check: Select chaos factor (1–9) and likelihood (Certain to Impossible), then click "Roll Fate" for outcomes like "Yes" or "Random Event".
    - NPC Interaction: Choose relationship (e.g., friendly, hostile) and demeanor (e.g., scheming, inquisitive), then click "Roll Interaction" for NPC behavior.
    - Action Oracle: Click "Action Oracle" for random action prompts.
    - Create NPC: Generate a detailed NPC (e.g., "NPC: Elara Voon, the female, adult (32), cunning scholar...").
    - Output appears in a scrollable text area.
4. Characters & Threads Tab:
    - Add up to 25 characters/threads (max 3 duplicates each) via text entry and "Add/Update" buttons.
    - Delete selected entries with "Delete Character/Thread".
    - Click "Choose Character" or "Choose Thread" to randomly select an entry.
    - Save or load campaign data using "Save Campaign" or "Load Campaign" (JSON files in data/lists/).
    - Output appears in a scrollable text area.
5. Campaign Management:
    - On startup, select a JSON file to load existing campaign data or start fresh.
    - Save campaigns to data/lists/ for persistence.
    - Autosave occurs after adding/updating/deleting entries if a file is loaded.

## Folder Structure

    RPG_Generator/
    ├── data_manager.py        # Handles data operations (add/remove items, save/load JSON)
    ├── main.py                # Entry point, initializes Tkinter and DataManager
    ├── logic.py               # Core logic for dice, oracles, NPC generation, and fate checks
    ├── ui.py                  # Tkinter GUI implementation
    ├── readme.md              # This file
    ├── data/                  # Data files directory
    │   ├── action_oracle.json # Action oracle data (action1, action2 lists)
    │   ├── npc_data.json      # NPC generation data (names, modifiers, nouns, etc.)
    │   ├── plot_points.json   # Plot points for themes (Action, Mystery, etc.)
    │   ├── lists/             # Campaign save/load directory
    │   │   ├── data_game1.json # Example campaign data
    │   │   ├── data_game2.json # Example campaign data

## Notes

- JSON File Dependency: The application requires action_oracle.json, npc_data.json, and plot_points.json to function fully. Missing or malformed files will cause errors (e.g., "Error loading NPC data").
- Data Limits: Characters and threads are capped at 25 entries each, with a maximum of 3 identical entries to prevent duplicates.
- Randomization: Uses Python’s random module for dice rolls, NPC generation, and selections. Results are pseudo-random.
- GUI: Tkinter provides a simple, cross-platform interface. The window is fixed at 600x700 pixels with scrollable output areas.
- Error Handling: Includes basic error handling for file operations and user input (e.g., invalid dice counts).
- Building: pyinstaller --onefile --add-data "data/lists;data/lists" --windowed main.py

## Example JSON File Structures

action_oracle.json
    {
        "action1": ["Investigate", "Confront", "Explore"],
        "action2": ["Mystery", "Danger", "Secret"]
    }

npc_data.json
    {
        "names": ["Elara", "Voon", "Tarek"],
        "modifiers": ["cunning", "brave"],
        "nouns": ["scholar", "warrior"],
        "motivationVerbs": ["seek", "protect"],
        "motivationNouns": ["truth", "honor"],
        "npcMood": { "neutral": { "01-50": "calm", "51-100": "wary" } },
        "npcBearing": { "friendly": ["openly", "warmly"] },
        "npcFocus": ["quest", "past"]
    }

plot_points.json
    {
        "Action": { "01-20": "A daring escape", "21-40": "A fierce battle" },
        "Mystery": { "01-50": "A hidden clue", "51-100": "A secret revealed" }
    }

## Future Improvements

- Add support for custom JSON file paths or templates.
- Enhance dice visuals with animations or custom graphics.
- Implement undo/redo for character/thread changes.
- Add export options for generated content (e.g., to PDF or text).
- Include settings for adjusting weights or random seed for reproducibility.

## License

This project is open-source under the MIT License. Feel free to modify and distribute as needed.

## Contact

For issues or suggestions, please open an issue on the repository or contact the maintainer.
