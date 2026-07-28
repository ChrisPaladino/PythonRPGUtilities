"""Main application window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt

from models.character import Character
from views.character_sheet import CharacterSheetWidget
from views.random_gen_wizard import RandomGenWizard
from utils.file_io import save_character, load_character


class MainWindow(QMainWindow):
    """Main application window with character roster and sheet."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Icons TTRPG Character Manager")
        self.setGeometry(100, 100, 1200, 700)

        self.characters: list[Character] = []
        self.current_character: Character | None = None
        self.character_dir = Path.home() / "Documents" / "Icons Characters"

        self._init_ui()

    def _init_ui(self):
        """Build the main window layout."""
        central = QWidget()
        main_layout = QHBoxLayout()

        # Left panel: roster
        left_panel = self._build_roster_panel()
        main_layout.addLayout(left_panel, 1)

        # Right panel: character sheet
        self.sheet_widget = CharacterSheetWidget()
        main_layout.addWidget(self.sheet_widget, 3)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self._load_roster()

    def _build_roster_panel(self) -> QVBoxLayout:
        """Build the left roster panel."""
        layout = QVBoxLayout()

        # Character list
        self.list_characters = QListWidget()
        self.list_characters.itemSelectionChanged.connect(self._on_character_selected)
        layout.addWidget(self.list_characters)

        # Buttons
        btn_new = QPushButton("New Random")
        btn_new.clicked.connect(self._new_random_character)
        layout.addWidget(btn_new)

        btn_open = QPushButton("Open File...")
        btn_open.clicked.connect(self._open_character)
        layout.addWidget(btn_open)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self._save_character)
        layout.addWidget(btn_save)

        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self._delete_character)
        layout.addWidget(btn_delete)

        btn_open_folder = QPushButton("Open Characters Folder")
        btn_open_folder.clicked.connect(self._open_characters_folder)
        layout.addWidget(btn_open_folder)

        return layout

    def _load_roster(self):
        """Load all characters from the character directory."""
        self.character_dir.mkdir(parents=True, exist_ok=True)
        self.characters = []
        self.list_characters.clear()

        for json_file in self.character_dir.glob("*.json"):
            try:
                char = load_character(json_file)
                self.characters.append(char)
                self.list_characters.addItem(char.display_name)
            except Exception as e:
                print(f"Failed to load {json_file}: {e}")

    def _on_character_selected(self):
        """Handle character selection from the roster."""
        index = self.list_characters.currentRow()
        if index >= 0 and index < len(self.characters):
            self.current_character = self.characters[index]
            self.sheet_widget.load_character(self.current_character)

    def _new_random_character(self):
        """Launch the random generation wizard."""
        wizard = RandomGenWizard(self)
        if wizard.exec() == QDialog.Accepted:
            char = wizard.get_character()
            if char:
                self.characters.append(char)
                self.current_character = char
                self.sheet_widget.load_character(char)
                # Add to list
                self.list_characters.addItem(char.display_name)
                self.list_characters.setCurrentRow(len(self.characters) - 1)

    def _save_character(self):
        """Save the current character to a JSON file."""
        if self.current_character is None:
            QMessageBox.warning(self, "No Character", "No character selected to save.")
            return

        # Update from sheet
        self.current_character = self.sheet_widget.get_character()

        # Get a filename
        name = self.current_character.display_name.replace(" ", "_").replace("/", "-")
        file_path = self.character_dir / f"{name}.json"

        try:
            save_character(self.current_character, file_path)
            self.current_character.file_path = str(file_path)
            QMessageBox.information(self, "Saved", f"Character saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save character: {e}")

    def _open_character(self):
        """Open a character file via file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Character",
            str(self.character_dir),
            "JSON Files (*.json)",
        )
        if file_path:
            try:
                char = load_character(file_path)
                # Check if already in roster
                if char not in self.characters:
                    self.characters.append(char)
                    self.list_characters.addItem(char.display_name)
                self.current_character = char
                self.sheet_widget.load_character(char)
                idx = self.characters.index(char)
                self.list_characters.setCurrentRow(idx)
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Failed to load character: {e}")

    def _delete_character(self):
        """Delete the current character from the roster."""
        index = self.list_characters.currentRow()
        if index < 0:
            QMessageBox.warning(self, "No Selection", "No character selected.")
            return

        reply = QMessageBox.question(
            self,
            "Delete Character",
            f"Delete {self.characters[index].display_name}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            char = self.characters.pop(index)
            self.list_characters.takeItem(index)
            self.current_character = None
            self.sheet_widget.load_character(Character())
            # Delete the file too
            if char.file_path and Path(char.file_path).exists():
                Path(char.file_path).unlink()

    def _open_characters_folder(self):
        """Open the characters folder in the file explorer."""
        import os
        import sys
        if sys.platform == "win32":
            os.startfile(self.character_dir)
        elif sys.platform == "darwin":
            os.system(f"open '{self.character_dir}'")
        else:
            os.system(f"xdg-open '{self.character_dir}'")
