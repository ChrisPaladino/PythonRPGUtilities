"""Random generation wizard - auto-rolls everything, user reviews and optionally tweaks."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QStackedWidget,
    QComboBox,
    QMessageBox,
    QWidget,
)

from models.character import Character
from models.interactive_generator import InteractiveGenerator
from data.tables import ATTRIBUTES, MENTAL_ATTRIBUTES, ORIGIN_DESCRIPTIONS


class RandomGenWizard(QDialog):
    """
    Streamlined 4-step wizard.
    Each step auto-rolls on arrival. User can re-roll or adjust, then move on.

    Steps:
        1. Origin      - auto-rolled, can re-roll or override via dropdown
        2. Attributes  - auto-rolled (retries silently if <20), optional swap/re-assign
        3. Powers      - auto-rolled, can re-roll
        4. Specialties - auto-rolled, can re-roll
        5. Summary     - accept or start over
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Random Hero")
        self.resize(680, 520)

        self.generator = InteractiveGenerator()
        self.character: Character | None = None
        self._origin_modifiers_applied = False

        self._build_ui()
        self._go_to_origin()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.stacked = QStackedWidget()
        layout.addWidget(self.stacked)

        self.page_origin      = self._make_origin_page()
        self.page_attributes  = self._make_attributes_page()
        self.page_powers      = self._make_powers_page()
        self.page_specialties = self._make_specialties_page()
        self.page_summary     = self._make_summary_page()

        for page in (self.page_origin, self.page_attributes, self.page_powers,
                     self.page_specialties, self.page_summary):
            self.stacked.addWidget(page)

        nav = QHBoxLayout()
        self.btn_back   = QPushButton("<- Back")
        self.btn_next   = QPushButton("Next ->")
        self.btn_cancel = QPushButton("Cancel")
        self.btn_back.clicked.connect(self._go_back)
        self.btn_next.clicked.connect(self._go_next)
        self.btn_cancel.clicked.connect(self.reject)
        nav.addWidget(self.btn_back)
        nav.addWidget(self.btn_next)
        nav.addStretch()
        nav.addWidget(self.btn_cancel)
        layout.addLayout(nav)

    # -------------------------------------------------------------------
    # Page builders
    # -------------------------------------------------------------------

    def _make_origin_page(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.addWidget(QLabel("<b>Step 1 of 4: Origin</b>"))

        self.lbl_origin_result = QLabel()
        self.lbl_origin_result.setStyleSheet("font-size: 14pt; font-weight: bold;")
        v.addWidget(self.lbl_origin_result)

        self.lbl_origin_desc = QLabel()
        self.lbl_origin_desc.setWordWrap(True)
        v.addWidget(self.lbl_origin_desc)

        v.addSpacing(10)
        v.addWidget(QLabel("Override (optional):"))
        self.combo_origin_override = QComboBox()
        self.combo_origin_override.addItem("-- keep rolled origin --", None)
        for origin in ORIGIN_DESCRIPTIONS:
            self.combo_origin_override.addItem(origin, origin)
        self.combo_origin_override.currentIndexChanged.connect(self._on_origin_override)
        v.addWidget(self.combo_origin_override)

        btn_reroll = QPushButton("Re-roll Origin")
        btn_reroll.clicked.connect(self._roll_origin)
        v.addWidget(btn_reroll)
        v.addStretch()
        return w

    def _make_attributes_page(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.addWidget(QLabel("<b>Step 2 of 4: Attributes</b>"))
        v.addWidget(QLabel("(Totals below 20 are automatically re-rolled. Origin modifier applied on Next.)"))

        self.text_attrs = QTextEdit()
        self.text_attrs.setReadOnly(True)
        self.text_attrs.setMaximumHeight(180)
        v.addWidget(self.text_attrs)

        self.lbl_attr_total = QLabel()
        v.addWidget(self.lbl_attr_total)

        btn_row = QHBoxLayout()
        btn_reroll = QPushButton("Re-roll Attributes")
        btn_swap   = QPushButton("Swap Two...")
        btn_cust   = QPushButton("Re-assign Values...")
        btn_reroll.clicked.connect(self._roll_attributes)
        btn_swap.clicked.connect(self._swap_attributes)
        btn_cust.clicked.connect(self._reassign_attributes)
        btn_row.addWidget(btn_reroll)
        btn_row.addWidget(btn_swap)
        btn_row.addWidget(btn_cust)
        v.addLayout(btn_row)
        v.addStretch()
        return w

    def _make_powers_page(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.addWidget(QLabel("<b>Step 3 of 4: Powers</b>"))
        self.text_powers = QTextEdit()
        self.text_powers.setReadOnly(True)
        v.addWidget(self.text_powers)
        btn = QPushButton("Re-roll Powers")
        btn.clicked.connect(self._roll_powers)
        v.addWidget(btn)
        v.addStretch()
        return w

    def _make_specialties_page(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.addWidget(QLabel("<b>Step 4 of 4: Specialties</b>"))
        self.text_specs = QTextEdit()
        self.text_specs.setReadOnly(True)
        v.addWidget(self.text_specs)
        btn = QPushButton("Re-roll Specialties")
        btn.clicked.connect(self._roll_specialties)
        v.addWidget(btn)
        v.addStretch()
        return w

    def _make_summary_page(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.addWidget(QLabel("<b>Summary</b>"))
        self.text_summary = QTextEdit()
        self.text_summary.setReadOnly(True)
        v.addWidget(self.text_summary)
        btn_row = QHBoxLayout()
        btn_start_over = QPushButton("Start Over")
        btn_accept     = QPushButton("Accept Hero")
        btn_start_over.clicked.connect(self._start_over)
        btn_accept.clicked.connect(self._accept)
        btn_row.addWidget(btn_start_over)
        btn_row.addStretch()
        btn_row.addWidget(btn_accept)
        v.addLayout(btn_row)
        return w

    # -------------------------------------------------------------------
    # Roll helpers
    # -------------------------------------------------------------------

    def _roll_origin(self):
        from data.tables import ORIGIN_TABLE
        from models.roller import roll_2d6
        r = roll_2d6()
        origin = ORIGIN_TABLE[r]
        self.generator.choose_origin(origin)
        self._origin_modifiers_applied = False
        self.combo_origin_override.blockSignals(True)
        self.combo_origin_override.setCurrentIndex(0)
        self.combo_origin_override.blockSignals(False)
        self.lbl_origin_result.setText(f"Rolled {r}  ->  {origin}")
        self.lbl_origin_desc.setText(ORIGIN_DESCRIPTIONS.get(origin, ""))

    def _on_origin_override(self, index: int):
        if index <= 0:
            return
        origin = self.combo_origin_override.currentData()
        if origin:
            self.generator.choose_origin(origin)
            self._origin_modifiers_applied = False
            self.lbl_origin_result.setText(f"Override  ->  {origin}")
            self.lbl_origin_desc.setText(ORIGIN_DESCRIPTIONS.get(origin, ""))

    def _roll_attributes(self):
        while True:
            self.generator.roll_attributes()
            if sum(self.generator.state.attribute_rolls.values()) >= 20:
                break
        self.generator.state.attributes_final = self.generator.state.attribute_rolls.copy()
        self._origin_modifiers_applied = False
        self._refresh_attr_display()

    def _refresh_attr_display(self):
        lines = [f"  {a}:  {self.generator.state.attributes_final[a]}" for a in ATTRIBUTES]
        self.text_attrs.setText("\n".join(lines))
        total = sum(self.generator.state.attributes_final.values())
        stamina = (self.generator.state.attributes_final.get("Strength", 1)
                   + self.generator.state.attributes_final.get("Willpower", 1))
        self.lbl_attr_total.setText(f"Total: {total}    Stamina (preview): {stamina}")

    def _apply_origin_modifiers_once(self):
        if not self._origin_modifiers_applied:
            self.generator.apply_origin_modifier_attributes()
            self._origin_modifiers_applied = True

    def _roll_powers(self):
        self.generator.state.powers = []
        self.generator.roll_powers()
        self._refresh_powers_display()

    def _refresh_powers_display(self):
        r = self.generator.state.num_powers_roll
        n = self.generator.state.num_powers
        lines = [f"Rolled {r}  ->  {n} power(s):\n"]
        for p in self.generator.state.powers:
            tag = "  [Device]" if p.device else ""
            lines.append(f"  * {p.name}  ({p.type})  Level {p.level}{tag}")
        self.text_powers.setText("\n".join(lines))

    def _roll_specialties(self):
        self.generator.state.specialties = []
        self.generator.roll_specialties()
        self._refresh_specs_display()

    def _refresh_specs_display(self):
        r = self.generator.state.num_specialties_roll
        n = self.generator.state.num_specialties
        word = "specialty" if n == 1 else "specialties"
        lines = [f"Rolled {r}  ->  {n} {word}:\n"]
        for s in self.generator.state.specialties:
            lines.append(f"  * {s}")
        self.text_specs.setText("\n".join(lines))

    # -------------------------------------------------------------------
    # Attribute tweaks (optional buttons on attributes page)
    # -------------------------------------------------------------------

    def _swap_attributes(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Swap Two Attributes")
        v = QVBoxLayout(dlg)
        v.addWidget(QLabel("First attribute:"))
        c1 = QComboBox(); c1.addItems(ATTRIBUTES); v.addWidget(c1)
        v.addWidget(QLabel("Second attribute:"))
        c2 = QComboBox(); c2.addItems(ATTRIBUTES); c2.setCurrentIndex(1); v.addWidget(c2)

        def ok():
            a1, a2 = c1.currentText(), c2.currentText()
            if a1 == a2:
                QMessageBox.warning(dlg, "Invalid", "Choose two different attributes.")
                return
            self.generator.assign_attributes_swap(a1, a2)
            self._origin_modifiers_applied = False
            self._refresh_attr_display()
            dlg.accept()

        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(QPushButton("OK", clicked=ok))
        v.addLayout(h)
        dlg.exec()

    def _reassign_attributes(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Re-assign Attribute Values")
        v = QVBoxLayout(dlg)
        rolls_sorted = sorted(self.generator.state.attribute_rolls.values(), reverse=True)
        v.addWidget(QLabel(f"Rolled values: {rolls_sorted}"))
        v.addWidget(QLabel("Assign a value to each attribute:"))

        combos = []
        for attr in ATTRIBUTES:
            h = QHBoxLayout()
            h.addWidget(QLabel(f"{attr}:"))
            c = QComboBox()
            for j, val in enumerate(rolls_sorted):
                c.addItem(f"{val}  (roll #{j+1})", val)
            h.addWidget(c)
            v.addLayout(h)
            combos.append((attr, c))

        def ok():
            vals = [c.currentData() for _, c in combos]
            self.generator.assign_attributes_ala_carte(vals)
            self._origin_modifiers_applied = False
            self._refresh_attr_display()
            dlg.accept()

        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(QPushButton("OK", clicked=ok))
        v.addLayout(h)
        dlg.exec()

    # -------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------

    def _go_to_origin(self):
        self._roll_origin()
        self.stacked.setCurrentWidget(self.page_origin)
        self.btn_back.setEnabled(False)
        self.btn_next.setEnabled(True)
        self.btn_next.show()
        self.btn_next.setText("Next ->")

    def _go_to_attributes(self):
        self._roll_attributes()
        self.stacked.setCurrentWidget(self.page_attributes)
        self.btn_back.setEnabled(True)
        self.btn_next.setText("Next ->")

    def _go_to_powers(self):
        self._apply_origin_modifiers_once()
        self._roll_powers()
        self.stacked.setCurrentWidget(self.page_powers)
        self.btn_back.setEnabled(True)
        self.btn_next.setText("Next ->")

    def _go_to_specialties(self):
        self._roll_specialties()
        self.stacked.setCurrentWidget(self.page_specialties)
        self.btn_back.setEnabled(True)
        self.btn_next.setText("Review Summary ->")

    def _go_to_summary(self):
        char = self.generator.state.to_character()
        self.character = char

        attrs  = "\n".join(f"  {a}: {v}" for a, v in char.attributes.items())
        powers = "\n".join(f"  * {p.name} ({p.type}) Lvl {p.level}" for p in char.powers)
        specs  = "\n".join(f"  * {s}" for s in char.specialties)

        self.text_summary.setText(
            f"Origin: {char.origin}\n\n"
            f"Attributes:\n{attrs}\n\n"
            f"Stamina: {char.stamina}    Determination: {char.determination}\n\n"
            f"Powers ({len(char.powers)}):\n{powers}\n\n"
            f"Specialties ({len(char.specialties)}):\n{specs}\n\n"
            f"Fill in name, qualities, and background in the character sheet."
        )
        self.stacked.setCurrentWidget(self.page_summary)
        self.btn_back.setEnabled(True)
        self.btn_next.setEnabled(False)
        self.btn_next.hide()

    def _go_back(self):
        cur = self.stacked.currentWidget()
        if cur == self.page_attributes:
            self._go_to_origin()
        elif cur == self.page_powers:
            self._origin_modifiers_applied = False
            self.stacked.setCurrentWidget(self.page_attributes)
        elif cur == self.page_specialties:
            self.stacked.setCurrentWidget(self.page_powers)
        elif cur == self.page_summary:
            self.btn_next.setEnabled(True)
            self.btn_next.show()
            self.stacked.setCurrentWidget(self.page_specialties)

    def _go_next(self):
        cur = self.stacked.currentWidget()
        if cur == self.page_origin:
            self._go_to_attributes()
        elif cur == self.page_attributes:
            self._go_to_powers()
        elif cur == self.page_powers:
            self._go_to_specialties()
        elif cur == self.page_specialties:
            self._go_to_summary()

    def _start_over(self):
        self.generator = InteractiveGenerator()
        self._origin_modifiers_applied = False
        self.character = None
        self._go_to_origin()

    def _accept(self):
        self.accept()

    def get_character(self) -> Character | None:
        return self.character