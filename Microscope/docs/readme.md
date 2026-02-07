# Microscope Solo Play

A desktop application for playing the tabletop RPG **Microscope** by Ben Robbins in solo mode.

## Overview

Microscope is a fractal role-playing game of epic histories. This application enables solo players to explore history construction through:

- **Outside-in timeline building**: Start with bookend periods, then add Events and Scenes
- **Non-chronological exploration**: Jump around in time, filling in the gaps
- **Structured creativity**: The app enforces game rules while you provide all the creative content
- **Focus-driven play**: Each round explores a specific theme or question
- **Legacy creation**: Build lasting elements that connect your explorations

## Features

✅ **Full Game Support**
- Complete Setup Phase (Big Picture, Bookends, Palette, First Pass)
- Play Phase with Focus/Legacy mechanics
- Scene creation wizard with step-by-step guidance
- Save/Load game state
- Export to Markdown or plain text

✅ **Visual Timeline**
- Horizontal Period layout
- Nested Events and Scenes
- Light/Dark tone indicators
- Click to view details

✅ **Rule Enforcement**
- Palette compliance checking
- Phase-appropriate actions
- Prevents invalid operations

## Installation

### Requirements
- Python 3.10 or later
- tkinter (usually included with Python)

### Running the Application

1. Navigate to the Microscope directory:
```bash
cd "c:\GitHub\PythonRPGUtilities\Microscope"
```

2. Run the application:
```bash
python src/main.py
```

Or on some systems:
```bash
python3 src/main.py
```

## How to Play

### Setup Phase

1. **Big Picture**: Describe your history in 1-2 sentences
2. **Bookend Periods**: Create the Start and End periods that frame your timeline
3. **Palette**: Add items to the Yes (must exist) and No (cannot exist) lists
4. **First Pass**: Add some initial Periods and Events to flesh out the timeline

### Play Phase

1. **Declare Focus**: Choose a theme, question, or element to explore
2. **Make History**: Create Periods, Events, or Scenes related to your Focus
   - **Periods**: Large spans of time
   - **Events**: Specific occurrences within a Period
   - **Scenes**: Detailed explorations with questions and answers
3. **Complete Focus**: When you're done exploring
4. **Create Legacy**: (Optional) Mark something important from your exploration
5. **Explore Legacy**: Create content related to your Legacy
6. Repeat with new Focus

### Creating Scenes

Scenes follow a structured wizard:
1. **Question**: What will this scene answer?
2. **Set the Stage**: Where and when does it take place?
3. **Characters**: Who's involved?
4. **Play/Dictate**: Act it out or narrate what happens
5. **Answer**: Answer the original question

## File Structure

```
Microscope/
├── docs/
│   └── readme.md          # This file
├── src/
│   ├── main.py            # Entry point
│   ├── models.py          # Data structures
│   ├── constants.py       # Enums and constants
│   ├── game_state.py      # Game logic and state management
│   ├── ui.py              # Tkinter user interface
│   └── persistence.py     # Save/load/export functionality
```

## Saving and Loading

- **Save Game**: File → Save Game (saves as JSON)
- **Load Game**: File → Load Game (restores complete state)
- **Export Markdown**: File → Export to Markdown (readable history document)
- **Export Text**: File → Export to Text (plain text timeline)

## Design Philosophy

This application follows the principle of **rule enforcement, not content generation**:

- ✅ Enforces game rules and structure
- ✅ Tracks state and constraints
- ✅ Guides with prompts and instructions
- ❌ Does NOT generate content automatically
- ❌ Does NOT use AI to create story elements
- ❌ Does NOT replace player creativity

All creative content comes from YOU, the player. The app simply provides structure and keeps you honest to the rules.

## Tips for Solo Play

1. **Be disciplined with Focus**: Each Focus should genuinely guide your choices
2. **Respect the Palette**: The constraints spark creativity
3. **Answer Scene questions honestly**: Don't pre-decide outcomes
4. **Embrace non-chronology**: Jump around to wherever interests you
5. **Let Legacies emerge**: Don't force them; create them when something feels significant

## About Microscope

Microscope is a tabletop roleplaying game by Ben Robbins, published by Lame Mage Productions.

This application is an independent digital tool for solo play and is not affiliated with or endorsed by the game's creator or publisher.

**To play, you should own a copy of the Microscope rulebook.**

Purchase the game at: http://www.lamemage.com/microscope/

## License

This application is for personal use. The Microscope game system is ©2011 Ben Robbins, all rights reserved.

## Version

**Version 1.0** - Initial release
- Complete Setup and Play phases
- Scene wizard
- Save/Load functionality  
- Markdown/Text export
- Visual timeline display

## Known Limitations

- No drag-and-drop reordering of timeline elements
- Canvas scrolling can be improved
- Scene wizard doesn't support "Reveal Thoughts" in detail
- No undo/redo functionality

## Future Enhancements (Potential)

- Better timeline visualization with zoom levels
- Drag-and-drop Period/Event reordering
- Search and filter functionality
- Timeline heatmap by tone
- Character relationship tracking
- Enhanced export formats (PDF, HTML)

## Troubleshooting

**Application won't start:**
- Ensure Python 3.10+ is installed: `python --version`
- Ensure tkinter is available: `python -m tkinter`

**Timeline not displaying:**
- Try resizing the window
- Check that you've created the bookend periods

**Can't create Scenes:**
- Ensure you've created at least one Event first
- Check that you're in the Play phase

## Support

For issues or questions about the application itself, check the code comments or modify as needed.

For questions about Microscope rules, consult the official rulebook.

---

**Enjoy building epic histories!**
