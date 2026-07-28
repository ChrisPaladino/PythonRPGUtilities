"""File I/O for character saving and loading."""

from __future__ import annotations

import json
from pathlib import Path

from models.character import Character, Power


def save_character(hero: Character, file_path: str | Path) -> None:
    """Save a character to a JSON file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "name": hero.name,
        "civilian_identity": hero.civilian_identity,
        "origin": hero.origin,
        "attributes": hero.attributes,
        "powers": [
            {
                "type": p.type,
                "name": p.name,
                "level": p.level,
                "extras": p.extras,
                "limits": p.limits,
                "device": p.device,
            }
            for p in hero.powers
        ],
        "specialties": hero.specialties,
        "qualities": hero.qualities,
        "description": hero.description,
        "background": hero.background,
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_character(file_path: str | Path) -> Character:
    """Load a character from a JSON file."""
    file_path = Path(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    hero = Character(
        name=data.get("name", ""),
        civilian_identity=data.get("civilian_identity", ""),
        origin=data.get("origin", ""),
        attributes=data.get("attributes", {}),
        powers=[
            Power(
                type=p.get("type", ""),
                name=p.get("name", ""),
                level=p.get("level", 1),
                extras=p.get("extras", []),
                limits=p.get("limits", []),
                device=p.get("device", False),
            )
            for p in data.get("powers", [])
        ],
        specialties=data.get("specialties", []),
        qualities=data.get("qualities", ["", "", ""]),
        description=data.get("description", ""),
        background=data.get("background", ""),
        file_path=str(file_path),
    )

    return hero
