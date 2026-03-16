# ConCat Markdown

A simple Python script to concatenate all Markdown (`.md`) files from an Obsidian vault (or any folder) into a single Markdown file, preserving folder-based ordering and adding page breaks for easy PDF export.

## Purpose

This tool was built to suit my personal Obsidian workflow, where I organize notes in numerically prefixed folders (e.g., `1-Sessions`, `2-PCs`, `3-NPCs`, `8-Locations`). It combines all `.md` files into one large file, using filenames as headers, while respecting the natural folder hierarchy—perfect for exporting to PDF or archiving.

## Features

- **Folder-Based Sorting**: Files are appended in the order of their folder structure (e.g., `1-Sessions/Session 001.md` before `2-PCs/Uthgar.md`).
- **Contextual Headers**: Creates headers with folder context (e.g., `1-Sessions - Session 001`) when files are in subdirectories, or just the filename for root-level files. Underscores in filenames are replaced with spaces for readability.
- **Page Breaks**: Inserts `<div style="page-break-after: always;"></div>` between files for PDF compatibility (works with tools like Pandoc).
- **GUI Selection**: Uses Tkinter to let you pick the source folder and output file via a file dialog.
- **Obsidian-Friendly**: Ignores hidden or special folders (e.g., `.obsidian`, `_trash`) and files (e.g., `.hidden.md`, `_notes.md`) that start with a period (`.`) or underscore (`_`).

## Example

Given this folder structure:
vault/
├── 1-Sessions/
│   └── Session 001.md
├── 2-PCs/
│   └── Uthgar.md
├── 3-NPCs/
│   └── Elaris.md
├── 8-Locations/
│   └── Blackthorn.md
├── .obsidian/
│   └── config
├── _trash/
│   └── old_note.md
└── .hidden.md

The output file (`unified_notes.md`) will include only the non-hidden, non-underscored `.md` files:

```markdown
# 1-Sessions - Session 001
[content from Session 001.md]
<div style="page-break-after: always;"></div>

# 2-PCs - Uthgar
[content from Uthgar.md]
<div style="page-break-after: always;"></div>

# 3-NPCs - Elaris
[content from Elaris.md]
<div style="page-break-after: always;"></div>

# 8-Locations - Blackthorn
[content from Blackthorn.md]
```

Files like .hidden.md and folders like .obsidian or _trash (and their contents) are skipped.

## Requirements

- Python 3.10+
- Tkinter (usually included with Python)

## Usage

Clone or download this repository.
Run the script:
Select your Obsidian vault folder (or any folder with .md files) in the dialog.
Choose where to save the unified Markdown file (defaults to unified_notes.md).
Check the console for confirmation or error messages.

## Installation

- No special installation needed—just ensure Python is installed on your system:
- Verify Python and Tkinter

```bash
python --version
python -m tkinter
```

Then run the script directly.

## Notes

- Sorting: Relies on alphanumeric folder/file naming (e.g., 1-Sessions before 2-PCs). Adjust your folder names for desired order.
- Page Breaks: The HTML `<div>` works with some PDF converters (e.g., Pandoc). For other tools, you might need to tweak the separator.
- Error Handling: Skips problematic files (e.g., permission issues) and logs errors to the console.
- Ignored Files/Folders: Folders and files starting with `.` or `_` (e.g., `.obsidian`, `_trash`, `.hidden.md`, `_notes.md`) are automatically skipped to avoid processing hidden or temporary content.

## Contributing

Feel free to fork this repo and submit pull requests if you’d like to adapt it for your own workflow! Suggestions for improvements are welcome.
