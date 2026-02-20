# Action Story Trademark Manager

A Python-based Tkinter GUI application for managing and browsing trademarks from the Action Story tabletop role-playing game system. This tool helps players and game masters quickly search, filter, and view character trademarks including backgrounds, careers, and other character options.

## Features

- **Search Functionality**: Real-time search across all trademark fields (name, source, type, description, traits, flaws, gear, and advantages)
- **Organized Display**: Trademarks are automatically sorted by source, type, and name for easy browsing
- **Detailed Information**: View complete trademark details including:
  - Name, source, and type
  - Description
  - Traits list
  - Flaws list
  - Gear list
  - Advantages with descriptions
- **Data Refresh**: Reload JSON data without restarting the application (F5 or Refresh button)
- **Unicode Support**: Proper handling of special characters and Unicode text normalization
- **Keyboard Shortcuts**: 
  - F5: Refresh data
  - Ctrl+F: Focus search box
- **Resizable Interface**: Adjustable paned window for customizing view areas

## Requirements

- Python 3.7 or higher
- Tkinter (usually included with Python; install `python3-tk` on Linux if needed)
- JSON data file (`trademarks.json`) in the `data/` directory

## Installation

1. **Clone or Download the Repository**:
   ```bash
   git clone https://github.com/ChrisPaladino/PythonRPGUtilities
   cd "Action Story Trademark Manager"
   ```

2. **Ensure Python is Installed**: 
   Verify Python 3 is installed:
   ```bash
   python3 --version
   ```
   Install Python if needed from https://www.python.org/downloads

3. **Install Tkinter (if not included)**: 
   On Linux, you may need:
   ```bash
   sudo apt-get install python3-tk  # Debian/Ubuntu
   sudo yum install python3-tkinter  # CentOS/RHEL
   ```

4. **Verify JSON Data File**:
   - Ensure the `data/trademarks.json` file exists and is properly formatted
   - The file should contain a JSON object with a "trademarks" array

## Usage

1. **Launch the Application**:
   ```bash
   python3 src/ActionStoryTrademarkManager.py
   ```

2. **Browse Trademarks**:
   - The main window displays a list of all trademarks sorted by source, type, and name
   - Click on any trademark in the list to view its full details in the bottom panel

3. **Search**:
   - Type in the search box to filter trademarks in real-time
   - Search works across all fields: name, source, type, description, traits, flaws, gear, and advantages
   - Clear the search box to show all trademarks again

4. **Refresh Data**:
   - Click the "Refresh" button or press F5 to reload the JSON data
   - Useful if you've updated the trademarks.json file while the app is running

## JSON Data Structure

The `trademarks.json` file should follow this structure:

```json
{
    "trademarks": [
        {
            "name": "Trademark Name",
            "source": "Source Book",
            "type": "Background/Career/etc",
            "description": "Description text",
            "traits": ["Trait 1", "Trait 2"],
            "flaws": ["Flaw 1", "Flaw 2"],
            "gear": ["Gear Item 1", "Gear Item 2"],
            "advantages": [
                {
                    "name": "Advantage Name",
                    "description": "Advantage description"
                }
            ]
        }
    ]
}
```

### Required Fields
- `name`: String - The trademark's name
- `source`: String - The source book or material
- `type`: String - The category (Background, Career, etc.)
- `description`: String - Full description text

### Optional Fields (will default to empty if missing)
- `traits`: Array of strings - Character traits
- `flaws`: Array of strings - Character flaws
- `gear`: Array of strings - Starting equipment
- `advantages`: Array of objects - Special abilities or bonuses

## Directory Structure

```
Action Story Trademark Manager/
├── src/
│   └── ActionStoryTrademarkManager.py  # Main application file
├── data/
│   └── trademarks.json                 # Trademark database
└── docs/
    └── readme.md                       # This file
```

## Features in Detail

### Data Validation
- Automatically validates and normalizes all trademark entries on load
- Ensures all required fields are present with correct data types
- Normalizes Unicode characters to prevent display issues
- Gracefully handles malformed or missing data

### Sorting and Organization
- Trademarks are pre-sorted and cached for performance
- Display format: "Source: Type: Name" for easy scanning
- Alphabetical sorting within each category

### Error Handling
- Displays user-friendly error messages for file and JSON issues
- Continues operation even if individual trademarks have problems
- Logs warnings to stderr for invalid entries

## Keyboard Shortcuts

- **F5**: Refresh data from JSON file
- **Ctrl+F**: Focus the search box
- **Up/Down Arrow**: Navigate trademark list (when focused)
- **Enter**: Select highlighted trademark (when list is focused)

## Notes

- The application uses relative paths, so it can be run from any directory
- The trademark list is cached for performance - use Refresh to reload changes
- Search is case-insensitive and searches all text fields
- Unicode normalization ensures proper display of special characters
- The window is resizable, and you can adjust the paned divider position

## Future Improvements

- Export filtered results to text or PDF
- Add filtering by source or type
- Implement favorites or bookmarks
- Add printing support
- Include dice rolling for random trademark selection
- Support for multiple JSON files or custom data sources

## License

This project is open-source under the MIT License. Feel free to modify and distribute as needed.

## Contact

For issues or suggestions, please open an issue on the repository or contact the maintainer.
