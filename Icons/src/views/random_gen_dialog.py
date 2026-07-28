"""Random generation wizard dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)
from PySide6.QtCore import Qt

from models.character import Character
from models.generator import generate_random_hero


class RandomGenDialog(QDialog):
    """Modal dialog for rolling a random hero."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.character: Character | None = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Generate Random Hero")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Rolling a random hero..."))

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        layout.addWidget(self.text_output)

        btn_layout = QHBoxLayout()
        btn_roll = QPushButton("Roll Hero")
        btn_accept = QPushButton("Accept")
        btn_cancel = QPushButton("Cancel")
        btn_roll.clicked.connect(self._roll)
        btn_accept.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_roll)
        btn_layout.addWidget(btn_accept)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _roll(self):
        """Generate a new random hero and display."""
        self.character = generate_random_hero()
        self._display_hero()

    def _display_hero(self):
        """Show the current character's stats."""
        if self.character is None:
            return

        text = f"""
Hero Name: {self.character.display_name}
Origin: {self.character.origin}

Attributes:
  Prowess:      {self.character.attributes.get("Prowess", 1)}
  Coordination: {self.character.attributes.get("Coordination", 1)}
  Strength:     {self.character.attributes.get("Strength", 1)}
  Intellect:    {self.character.attributes.get("Intellect", 1)}
  Awareness:    {self.character.attributes.get("Awareness", 1)}
  Willpower:    {self.character.attributes.get("Willpower", 1)}

Stamina: {self.character.stamina}
Determination: {self.character.determination}

Powers ({len(self.character.powers)}):
"""
        for p in self.character.powers:
            text += f"  - {p.name} ({p.type}) Level {p.level}\n"

        text += f"\nSpecialties ({len(self.character.specialties)}):\n"
        for s in self.character.specialties:
            text += f"  - {s}\n"

        self.text_output.setText(text)

    def get_character(self) -> Character | None:
        """Return the generated character (if accepted)."""
        return self.character
