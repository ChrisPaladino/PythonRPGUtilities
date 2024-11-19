##### ConCat Markdown
Fairly specific to how I set up my Obsidian folders, this will allow me to combine all the various files into one large file to then export to PDF

---

##### RPG_Generator
A series of oracles, tables and generators from several sources smashed together - including Adventure Creatior, Mything Game Emulator, and a variety of Oracles

---

#### HexFlowers
## Project Overview
The Hexflower Map Generator is a Python application designed to assist tabletop RPG players by generating random events using hexflower maps. The application will feature a graphical user interface (GUI) built with Tkinter, allowing users to visualize weather and terrain hexmaps.

## Functional Requirements
### 1. User Interface
- **Main Window**: The application will have a main window displaying two hexflower maps: one for weather and one for terrain.
- **Hexflower Maps**:
  - **Weather Hexmap**: A hexflower map representing different weather conditions based on the selected season.
  - **Terrain Hexmap**: A hexflower map representing various terrain types.
- **Dropdown Menu**: A dropdown menu will allow users to select the current season (Spring, Summer, Autumn, Winter), which will update the weather hexmap accordingly.
- **Highlighting Current Hex**: The currently active hex will be visually highlighted to indicate the current position.
- **Manual Cell Setting**: Users will have the option to manually set or modify the contents of a hex cell.

### 2. Hexflower Structure
- **Hexflower Layout**: The hexflower will consist of 19 hexes arranged as follows:
  - 1 center hex.
  - 6 surrounding hexes (first ring).
  - 12 outer hexes (second ring).
  - These 19 hexes are also layed out in 5 columns (3 tall, 4 tall, 5 tall, 4 tall and 3 tall)
- **Hex Size**: Each hex will have a defined size (e.g., 30 pixels).

### 3. Random Event Generation
- **Dice Rolling Mechanism**: The application will include a button to roll 2d6, determining movement across the hexflower.
- **Movement Directions**: The application will interpret the rolled value to move in one of six directions:
  - 12: North
  - 2, 3: Upper Right
  - 4, 5: Lower Right
  - 6, 7: South
  - 8, 9: Lower Left
  - 10, 11: Upper Left
- **Edge of the Map**: If you are in an edge hex, and your roll takes you off the map, you should "wrap around", staying in the same vertical column (if a 12, 6 or 7 are rolled), or diagonal column. Example: If you are on the top-most hex, and you roll a 12 (North), you would end up in the bottom-most hex.

### 4. Output
- **Display Results**: After rolling the dice, the application will display the rolled value and the corresponding movement direction.
- **Event Generation**: Based on the current hex position, the application will generate and display a random event or condition relevant to the selected hex.

### 5. Technical Requirements
- **Programming Language**: Python 3.x
- **Libraries**: Tkinter for GUI, random for event generation.
- **Platform**: The application should be compatible with major operating systems (Windows, macOS, Linux).

## Non-Functional Requirements
- **Usability**: The interface should be intuitive and easy to navigate for users of all experience levels.
- **Performance**: The application should respond quickly to user inputs, such as rolling dice and updating hex maps.
- **Maintainability**: The code should be well-documented and structured to facilitate future updates and enhancements.

## Conclusion
This document outlines the functional requirements for the Hexflower Map Generator. The goal is to create an engaging and useful tool for tabletop RPG players, enhancing their gameplay experience through random event generation and visual representation of hexflower maps.