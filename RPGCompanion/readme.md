# RPG Dice Rolling Program Requirements

## Overview
This Python program aims to provide a minimal, discrete, and efficient tool for RPG dice rolling, catering to office workers or individuals in constrained environments. It will focus initially on dice rolling functionality for Cortex (Tales of Xadia), with Starforged support as the next priority.

## Functional Requirements

### Core Features (MVP)
1. **Dice Rolling:**
   - Support for standard RPG dice types: d4, d6, d8, d10, d12, d20, d100.
   - Allow rolling odd dice (e.g., d2, Zocchi dice) and custom input formulas.
   - Enable users to input and roll custom formulas (e.g., `3d6+2`, `4d6 drop lowest`).
   - Results should display in a scrollable text box with:
     - **Clear** button to reset the output.
     - **Copy** button to copy results to the clipboard.

2. **Graphical Interface:**
   - Minimalist design using Python's TKinter library.
   - Grid-based layout for control and scalability.
   - Buttons for each supported dice type (d4, d6, etc.), represented with clickable dice images/icons.
   - Input area for manual dice formulas.
   - Dedicated area to select the system (starting with Cortex, expandable later).

3. **System-Specific Rolls:**
   - **Priority 1**: Basic dice rolling for Cortex (e.g., click on a dice icon to roll).
   - **Priority 2**: Add action and challenge dice rolling for Starforged.

4. **Customization:**
   - Configuration through JSON files for:
     - Dice rules (e.g., exploding dice, rerolls).
     - System-specific features (e.g., Starforged results like strong/weak/miss).
   - JSON files will be manually edited in a text editor (e.g., Notepad++) initially.

### Long-Term Features (Post-MVP)
1. **Advanced Dice Mechanics:**
   - Implement advanced dice rolling (e.g., exploding dice, `4d6 drop lowest`, dice pools).
   - Add support for defining rules for Weak/Strong/Miss in PBTA or Starforged.

2. **System Expansion:**
   - Enable users to define custom game systems through JSON files.
   - Add preloaded assets and moves for Starforged and other systems.

3. **Session Tools:**
   - Note-taking and roll history.
   - Initiative tracking and campaign management.
   - Ability to save/load campaign or session states.

4. **Themes & Visual Customization:**
   - Allow users to customize the interface through JSON-based themes.
   - Provide curated or shareable themes for personalization.

5. **Character Management:**
   - Enable users to define and track character attributes, stats, and changes over time.
   - Display character information in the interface.

## Non-Functional Requirements

1. **Performance:**
   - Load within 2 seconds on standard hardware.
   - Render dice rolls and output instantly without lag.

2. **Usability:**
   - Minimalist design for discreet use.
   - No dice animations or flashy effects.
   - Results should be clear and easy to interpret.

3. **Error Handling:**
   - Basic error messages for invalid inputs or JSON configurations.
   - Handle unexpected inputs gracefully without crashing.

4. **Expandability:**
   - Modular design to support additional features or systems in future updates.

5. **Platform:**
   - Compatible with Python 3.x.
   - Use only core Python libraries where possible to reduce dependencies.

## Acceptance Criteria

1. **MVP Delivery:**
   - Users can roll standard RPG dice (d4, d6, d8, d10, d12, d20, d100) via clickable icons or manual formulas.
   - Dice results display in a scrollable, clear text box with options to clear or copy results.
   - Basic JSON configuration for adding dice types or rules.

2. **System-Specific Rolls:**
   - Cortex dice rolling fully functional.
   - Basic Starforged action and challenge dice rolling implemented.

3. **Error Handling:**
   - Program gracefully handles invalid dice inputs or malformed JSON files.
   - Errors are logged or displayed in a non-intrusive manner.

4. **UI/UX:**
   - The interface is clean, intuitive, and suitable for discreet use in an office environment.
   - Rolls and outputs are visible without unnecessary clutter.

## Future Vision
The program will evolve into a more comprehensive RPG assistant, supporting full character management, system-specific features, and customizable tools for both solo and group play. However, the focus remains on providing a robust and flexible dice roller as the core functionality.