"""
Persistence service — save/load/delete episode JSON files.
"""
import json
import os
from pathlib import Path

from pta_manager.models.protagonist import Protagonist
from pta_manager.models.scene import Scene

SAVE_DIR = Path.home() / ".pta_manager" / "saves"


def _ensure_save_dir():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)


def list_saves() -> list[str]:
    _ensure_save_dir()
    return [f.stem for f in SAVE_DIR.glob("*.json")]


def save_game(name: str, state: dict):
    _ensure_save_dir()
    path = SAVE_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def load_game(name: str) -> dict:
    path = SAVE_DIR / f"{name}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_game(name: str):
    path = SAVE_DIR / f"{name}.json"
    if path.exists():
        path.unlink()


def serialize_state(
    protagonists: list[Protagonist],
    producer_budget: int,
    scenes: list[Scene],
    current_scene_id: str,
    episode_info: dict,
    mode: str = "DICE_MODE",
) -> dict:
    return {
        "protagonists": [p.to_dict() for p in protagonists],
        "producer": {"budget": producer_budget},
        "scenes": [s.to_dict() for s in scenes],
        "current_scene": current_scene_id,
        "episode_info": episode_info,
        "mode": mode,
    }


def deserialize_state(data: dict) -> dict:
    return {
        "protagonists": [Protagonist.from_dict(p) for p in data.get("protagonists", [])],
        "producer_budget": data.get("producer", {}).get("budget", 0),
        "scenes": [Scene.from_dict(s) for s in data.get("scenes", [])],
        "current_scene": data.get("current_scene", ""),
        "episode_info": data.get("episode_info", {}),
        "mode": data.get("mode", "DICE_MODE"),
    }
