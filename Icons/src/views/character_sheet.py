"""Character sheet display and edit panel."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
)
from PySide6.QtCore import Qt

from models.character import Character, Power
from data.tables import ATTRIBUTES


class CharacterSheetWidget(QWidget):
    """Tabbed character sheet for viewing and editing a Character."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.character: Character | None = None
        self._init_ui()

    def _init_ui(self):
        """Build the tabbed interface."""
        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Create tabs
        self.tab_overview = OverviewTab()
        self.tab_attributes = AttributesTab()
        self.tab_powers = PowersTab()
        self.tab_specialties = SpecialtiesTab()
        self.tab_notes = NotesTab()

        self.tabs.addTab(self.tab_overview, "Overview")
        self.tabs.addTab(self.tab_attributes, "Attributes")
        self.tabs.addTab(self.tab_powers, "Powers")
        self.tabs.addTab(self.tab_specialties, "Specialties")
        self.tabs.addTab(self.tab_notes, "Notes")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def load_character(self, char: Character) -> None:
        """Load a character into the sheet for display/editing."""
        self.character = char
        self.tab_overview.load_character(char)
        self.tab_attributes.load_character(char)
        self.tab_powers.load_character(char)
        self.tab_specialties.load_character(char)
        self.tab_notes.load_character(char)

    def get_character(self) -> Character:
        """Extract edited character data and return."""
        if self.character is None:
            return Character()

        self.tab_overview.save_to_character(self.character)
        self.tab_attributes.save_to_character(self.character)
        self.tab_powers.save_to_character(self.character)
        self.tab_specialties.save_to_character(self.character)
        self.tab_notes.save_to_character(self.character)

        return self.character


# ---------------------------------------------------------------------------
# Individual Tabs
# ---------------------------------------------------------------------------


class OverviewTab(QWidget):
    """Name, civilian identity, origin, qualities."""

    def __init__(self):
        super().__init__()
        self.char: Character | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        # Name
        layout.addWidget(QLabel("Hero Name:"))
        self.edit_name = QLineEdit()
        layout.addWidget(self.edit_name)

        # Civilian Identity
        layout.addWidget(QLabel("Civilian Identity:"))
        self.edit_identity = QLineEdit()
        layout.addWidget(self.edit_identity)

        # Origin
        layout.addWidget(QLabel("Origin:"))
        self.label_origin = QLabel()
        layout.addWidget(self.label_origin)

        # Qualities
        layout.addWidget(QLabel("Qualities (3):"))
        self.edit_quality1 = QLineEdit()
        self.edit_quality2 = QLineEdit()
        self.edit_quality3 = QLineEdit()
        layout.addWidget(self.edit_quality1)
        layout.addWidget(self.edit_quality2)
        layout.addWidget(self.edit_quality3)

        # Description
        layout.addWidget(QLabel("Description:"))
        self.edit_description = QTextEdit()
        layout.addWidget(self.edit_description)

        layout.addStretch()
        self.setLayout(layout)

    def load_character(self, char: Character):
        self.char = char
        self.edit_name.setText(char.name)
        self.edit_identity.setText(char.civilian_identity)
        self.label_origin.setText(char.origin or "(not set)")
        self.edit_quality1.setText(char.qualities[0] if len(char.qualities) > 0 else "")
        self.edit_quality2.setText(char.qualities[1] if len(char.qualities) > 1 else "")
        self.edit_quality3.setText(char.qualities[2] if len(char.qualities) > 2 else "")
        self.edit_description.setText(char.description)

    def save_to_character(self, char: Character):
        char.name = self.edit_name.text()
        char.civilian_identity = self.edit_identity.text()
        char.qualities = [
            self.edit_quality1.text(),
            self.edit_quality2.text(),
            self.edit_quality3.text(),
        ]
        char.description = self.edit_description.toPlainText()


class AttributesTab(QWidget):
    """Six ability spinboxes, with Stamina and Determination display."""

    def __init__(self):
        super().__init__()
        self.char: Character | None = None
        self.spinboxes: dict[str, QSpinBox] = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        # Spinboxes for each attribute
        for attr in ATTRIBUTES:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{attr}:"))
            sb = QSpinBox()
            sb.setMinimum(1)
            sb.setMaximum(10)
            self.spinboxes[attr] = sb
            row.addWidget(sb)
            row.addStretch()
            layout.addLayout(row)

        layout.addWidget(QLabel("---"))

        # Derived stats (read-only)
        self.label_stamina = QLabel()
        layout.addWidget(self.label_stamina)

        self.label_determination = QLabel()
        layout.addWidget(self.label_determination)

        layout.addStretch()
        self.setLayout(layout)

    def load_character(self, char: Character):
        self.char = char
        for attr, sb in self.spinboxes.items():
            sb.setValue(char.attributes.get(attr, 1))
        self._update_derived()

    def save_to_character(self, char: Character):
        for attr, sb in self.spinboxes.items():
            char.attributes[attr] = sb.value()

    def _update_derived(self):
        if self.char is None:
            return
        self.label_stamina.setText(f"Stamina: {self.char.stamina}")
        self.label_determination.setText(f"Determination: {self.char.determination}")


class PowersTab(QWidget):
    """Table of powers with Add/Remove buttons."""

    def __init__(self):
        super().__init__()
        self.char: Character | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Type", "Name", "Level", "Extras", "Limits"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Power")
        btn_remove = QPushButton("Remove Selected")
        btn_add.clicked.connect(self._add_power)
        btn_remove.clicked.connect(self._remove_power)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_character(self, char: Character):
        self.char = char
        self.table.setRowCount(len(char.powers))
        for i, power in enumerate(char.powers):
            self.table.setItem(i, 0, QTableWidgetItem(power.type))
            self.table.setItem(i, 1, QTableWidgetItem(power.name))
            self.table.setItem(i, 2, QTableWidgetItem(str(power.level)))
            self.table.setItem(i, 3, QTableWidgetItem(", ".join(power.extras)))
            self.table.setItem(i, 4, QTableWidgetItem(", ".join(power.limits)))

    def save_to_character(self, char: Character):
        powers = []
        for row in range(self.table.rowCount()):
            power = Power(
                type=self.table.item(row, 0).text() if self.table.item(row, 0) else "",
                name=self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                level=int(self.table.item(row, 2).text() or "1") if self.table.item(row, 2) else 1,
                extras=[x.strip() for x in (self.table.item(row, 3).text() or "").split(",") if x.strip()],
                limits=[x.strip() for x in (self.table.item(row, 4).text() or "").split(",") if x.strip()],
            )
            powers.append(power)
        char.powers = powers

    def _add_power(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col in range(5):
            self.table.setItem(row, col, QTableWidgetItem(""))

    def _remove_power(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)


class SpecialtiesTab(QWidget):
    """List of specialties with Add/Remove buttons."""

    def __init__(self):
        super().__init__()
        self.char: Character | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        self.list_widget = QTableWidget()
        self.list_widget.setColumnCount(1)
        self.list_widget.setHorizontalHeaderLabels(["Specialty"])
        self.list_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Specialty")
        btn_remove = QPushButton("Remove Selected")
        btn_add.clicked.connect(self._add_specialty)
        btn_remove.clicked.connect(self._remove_specialty)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_character(self, char: Character):
        self.char = char
        self.list_widget.setRowCount(len(char.specialties))
        for i, spec in enumerate(char.specialties):
            self.list_widget.setItem(i, 0, QTableWidgetItem(spec))

    def save_to_character(self, char: Character):
        specialties = []
        for row in range(self.list_widget.rowCount()):
            item = self.list_widget.item(row, 0)
            if item:
                specialties.append(item.text())
        char.specialties = specialties

    def _add_specialty(self):
        row = self.list_widget.rowCount()
        self.list_widget.insertRow(row)
        self.list_widget.setItem(row, 0, QTableWidgetItem(""))

    def _remove_specialty(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            self.list_widget.removeRow(row)


class NotesTab(QWidget):
    """Background / notes."""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Background:"))
        self.edit_background = QTextEdit()
        layout.addWidget(self.edit_background)
        self.setLayout(layout)

    def load_character(self, char: Character):
        self.edit_background.setText(char.background)

    def save_to_character(self, char: Character):
        char.background = self.edit_background.toPlainText()
