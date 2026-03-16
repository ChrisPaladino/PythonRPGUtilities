# Python RPG Utilities

A collection of Python-based tools and utilities for tabletop role-playing games (TTRPGs). This workspace contains five distinct applications designed to assist game masters and players with various aspects of RPG gameplay, from character management to oracle generation and document compilation.

## Projects Overview

### 1. Action Story Trademark Manager

A Tkinter GUI application for managing and browsing character trademarks from the Action Story tabletop RPG system.

**Features:**

- Real-time search across all trademark fields
- Organized display sorted by source, type, and name
- Detailed view of traits, flaws, gear, and advantages
- Data refresh without restarting
- Unicode support with proper text normalization

**Location:** `action_story_trademark_manager/`  
**Documentation:** [readme.md](action_story_trademark_manager/docs/readme.md)

### 2. ConCat Markdown

A Python script to concatenate all Markdown files from an Obsidian vault (or any folder) into a single Markdown file for easy PDF export.

**Features:**

- Folder-based sorting with natural hierarchy
- Contextual headers with directory names
- Page breaks for PDF compatibility
- Ignores hidden and special files/folders (.obsidian, _trash, etc.)
- GUI folder and file selection

**Location:** `concat_markdown/`  
**Documentation:** [readme.md](concat_markdown/docs/readme.md)

### 3. LitM Oracles

A Tkinter GUI application for rolling oracles to support *Legends in the Mist* tabletop RPG campaigns.

**Features:**

- Interpretive Oracle with d66 rolls
- Yes/No Oracle with power modifiers
- Conflict Oracle for narrative challenges
- Profile Builder for enemies and challenges
- Challenge Action Oracle for threats
- Consequence Oracle for failed actions
- Revelations Oracle for story-driven revelations

**Location:** `litm_oracles/`  
**Documentation:** [readme.md](litm_oracles/docs/readme.md)

### 4. One Page Solo Engine (OPSE)

A comprehensive Tkinter GUI implementing the One Page Solo Engine system for solo tabletop RPG play.

**Features:**

- Card-based oracle system with full deck management
- Yes/No oracle with likelihood modifiers
- Scene management (altered scenes, complications)
- Random event generator
- NPC and plot hook generators
- Dungeon and hex crawling tools
- Pacing and failure move tables
- Multiple dice rollers

**Location:** `one_page_solo_engine/`  
**Documentation:** [readme.md](one_page_solo_engine/docs/readme.md)

### 5. RPG Generator

A versatile TTRPG helper application providing dice rolling, oracles, NPC generation, and campaign management tools.

**Features:**

- Dice rolling with action/danger dice and mastery rerolls
- Fate checks with chaos factor and likelihood scales
- NPC generation with detailed characteristics
- Action oracle for narrative prompts
- Theme-based plot point generation
- Character and thread management
- Campaign save/load functionality
- NPC interaction system

**Location:** `rpg_generator/`  
**Documentation:** [readme.md](rpg_generator/docs/readme.md)

## Requirements

All projects require:

- **Python 3.10 or higher**
- **Tkinter** (usually included with Python; on Linux: `sudo apt-get install python3-tk`)

Some projects also require JSON data files which are included in their respective folders.

## Quick Start

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/ChrisPaladino/PythonRPGUtilities
   cd PythonRPGUtilities
   ```

2. **Choose a Tool**:
   Navigate to any project folder and run its main script. For example:

   ```bash
   # Action Story Trademark Manager
   python3 action_story_trademark_manager/src/action_story_trademark_manager.py
   
   # ConCat Markdown
   python3 concat_markdown/src/combine_markdown.py
   
   # LitM Oracles
   python3 litm_oracles/src/litm_oracles.py
   
   # One Page Solo Engine
   python3 one_page_solo_engine/src/opse_app.py
   
   # RPG Generator
   python3 rpg_generator/src/rpg_generator.py
   ```

3. **Read Documentation**:
   Each project has detailed documentation in its `docs/readme.md` file with specific usage instructions and features.

## Project Structure

PythonRPGUtilities/
├── action_story_trademark_manager/
│   ├── src/                    # Python source code
│   ├── data/                   # JSON trademark database
│   └── docs/                   # Documentation
├── concat_markdown/
│   ├── src/                    # Python source code
│   └── docs/                   # Documentation
├── litm_oracles/
│   ├── src/                    # Python source code
│   ├── data/                   # Oracle JSON files
│   └── docs/                   # Documentation
├── one_page_solo_engine/
│   ├── src/                    # Python source code
│   └── docs/                   # Documentation
├── rpg_generator/
│   ├── src/                    # Python source code
│   ├── data/                   # Campaign and oracle data
│   └── docs/                   # Documentation
└── PythonRPGUtilities.code-workspace

## Use Cases

### For Game Masters

- **RPG Generator**: Manage campaigns, generate NPCs, create plot points
- **LitM Oracles**: Roll oracles for *Legends in the Mist* sessions
- **One Page Solo Engine**: Use oracle tools for improvisation and solo play
- **Action Story Trademark Manager**: Quick reference for Action Story game system

### For Solo Players

- **One Page Solo Engine**: Complete solo play toolset with GM emulation
- **RPG Generator**: Fate checks, oracles, and random generators
- **LitM Oracles**: Story generation for *Legends in the Mist* campaigns

### For Content Creators

- **ConCat Markdown**: Compile Obsidian vaults or markdown notes into single PDFs
- **Action Story Trademark Manager**: Organize and reference game system content

### For Developers

- All tools are open-source and can be customized or extended
- JSON-based data files for easy content modification
- Tkinter GUI examples for Python RPG tool development

## Technology Stack

- **Language**: Python 3.10+
- **GUI Framework**: Tkinter
- **Data Format**: JSON
- **Platform**: Cross-platform (Windows, macOS, Linux)

## Features Common to All Tools

- Clean, user-friendly Tkinter GUIs
- Keyboard shortcuts and navigation
- Error handling with graceful degradation
- JSON-based data storage
- Cross-platform compatibility
- No external dependencies beyond Python standard library

## Contributing

Contributions are welcome! Each tool is independently maintainable, so you can:

- Fork the repository
- Create a feature branch for a specific tool
- Submit pull requests with improvements
- Report issues or suggest features

## License

This project is open-source under the MIT License. Feel free to modify and distribute as needed.

## Future Enhancements

Potential improvements across the workspace:

- Additional oracle systems and generators
- More game system support (e.g., other RPG systems)
- Export functionality (PDF, HTML, CSV)
- Save/load state across sessions
- Theme customization
- Mobile/web versions

## Contact

For issues, suggestions, or questions:

- Open an issue on GitHub
- Contact the maintainer

## Acknowledgments

These tools were created to support various tabletop RPG systems and solo play methodologies:

- **Action Story**: Character trademark system
- **Legends in the Mist**: Oracle-based gameplay
- **One Page Solo Engine (OPSE)**: Card-based GM emulation
- **Mythic GME**: Fate chart inspiration (RPG Generator)

---

Last Updated: February 19, 2026
