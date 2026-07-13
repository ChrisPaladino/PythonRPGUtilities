from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ker Nethalas Manager")
        self.resize(1200, 760)

        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)

        header = QGroupBox("Session")
        header_layout = QGridLayout(header)
        header_layout.addWidget(QLabel("Roll mode:"), 0, 0)

        self.roll_mode = QComboBox()
        self.roll_mode.addItems(["automatic", "manual"])
        self.roll_mode.setCurrentText("automatic")
        header_layout.addWidget(self.roll_mode, 0, 1)

        header_layout.addWidget(QPushButton("New"), 0, 2)
        header_layout.addWidget(QPushButton("Load"), 0, 3)
        header_layout.addWidget(QPushButton("Save"), 0, 4)
        header_layout.addWidget(QPushButton("Undo"), 0, 5)
        layout.addWidget(header)

        body = QGridLayout()
        layout.addLayout(body)

        resources = QGroupBox("Character")
        resources_layout = QVBoxLayout(resources)
        for line in [
            "Health: 15 / 15",
            "Toughness: 29 / 33",
            "Aether: 12 / 14 (2 sustained)",
            "Sanity: 11 / 12",
            "Exhaustion: 1",
            "Tension: d6",
            "Torch rooms: 9",
        ]:
            resources_layout.addWidget(QLabel(line))
        body.addWidget(resources, 0, 0)

        room = QGroupBox("Current Room")
        room_layout = QVBoxLayout(room)
        room_layout.addWidget(QLabel("Guard Room doorway"))
        room_layout.addWidget(QLabel("Encounter state: active"))
        body.addWidget(room, 0, 1)

        actions = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions)
        actions_layout.addWidget(QPushButton("Attack"))
        actions_layout.addWidget(QPushButton("Use Ability"))
        actions_layout.addWidget(QPushButton("Search"))
        actions_layout.addWidget(QPushButton("End Turn"))
        body.addWidget(actions, 0, 2)

        combatants = QGroupBox("Combatants")
        combatants_layout = QVBoxLayout(combatants)
        cards = QListWidget()
        cards.addItems([
            "Seraphine - HP 15, Toughness 29",
            "Skeleton - HP 4",
            "Skeletal Horror A - HP 7",
            "Skeletal Horror B - HP 5",
        ])
        combatants_layout.addWidget(cards)
        body.addWidget(combatants, 1, 0, 1, 3)

        log = QGroupBox("Roll and Calculation Log")
        log_layout = QVBoxLayout(log)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlainText(
            "Ready.\n"
            "Example: Perception 50 + Quick 10 -> target 60, roll 38 -> success."
        )
        log_layout.addWidget(self.log_text)
        layout.addWidget(log)

        self.statusBar().showMessage("MVP shell ready")

        for widget in self.findChildren(QLabel):
            widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
