"""loader.py – YAML loading for the Starforged reference app.

Data format (simple YAML):
  Oracles:  source, oracles[]{category, name, id, cursed_version?, rows[]{min, max, text}}
  Assets:   source, assets[]{category, name, requirement?, abilities[]}
  Moves:    source, categories[]{name, moves[]{name, roll_type, trigger, text, outcomes?, tables?}}
  Bundles:  unchanged (bundles.yaml)
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import sys

try:
    import yaml
except ModuleNotFoundError:
    raise SystemExit("PyYAML is not installed.  Run:  pip install pyyaml")

# ---------------------------------------------------------------------------
# Paths  –  work both in development and when frozen by PyInstaller
# ---------------------------------------------------------------------------

if getattr(sys, "frozen", False):
    _BASE_DIR = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    _BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = _BASE_DIR / "data"
SF_MOVES_YAML = DATA_DIR / "starforged_moves.yaml"
SI_MOVES_YAML = DATA_DIR / "sundered_isles_moves.yaml"
SF_ORACLES_DIR = DATA_DIR / "sf_oracles"
SI_ORACLES_DIR = DATA_DIR / "si_oracles"
CUSTOM_ORACLES_DIR = DATA_DIR / "custom_oracles"
IS_ORACLES_DIR = DATA_DIR / "is_oracles"
SF_ASSETS_DIR = DATA_DIR / "sf_assets"
SI_ASSETS_DIR = DATA_DIR / "si_assets"
IS_ASSETS_DIR = DATA_DIR / "is_assets"
BUNDLES_YAML = DATA_DIR / "bundles.yaml"
SETTINGS_JSON = DATA_DIR / "user_settings.json"

# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def load_yaml(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Cannot open data file {path.name}.") from exc
    return yaml.safe_load(raw) or {}


# ---------------------------------------------------------------------------
# Oracle extraction
# ---------------------------------------------------------------------------

def extract_oracles(data: dict[str, Any], fallback_label: str) -> list[dict[str, Any]]:
    """Return a flat list of oracle tables from a simple-format YAML document."""
    source = data.get("source", fallback_label)
    out: list[dict[str, Any]] = []
    for entry in data.get("oracles", []):
        if not isinstance(entry, dict) or not entry.get("rows"):
            continue
        out.append({
            "source": source,
            "category": entry.get("category", ""),
            "name": entry.get("name", ""),
            "oracle_id": entry.get("id", ""),
            "cursed_version": entry.get("cursed_version", ""),
            "rows": [
                {"min": r.get("min"), "max": r.get("max"), "text": r.get("text", "")}
                for r in entry["rows"]
                if isinstance(r, dict)
            ],
        })
    return out


# ---------------------------------------------------------------------------
# Asset extraction
# ---------------------------------------------------------------------------

def extract_assets(data: dict[str, Any], fallback_label: str) -> list[dict[str, Any]]:
    """Return a flat list of asset dicts from a simple-format YAML document."""
    source = data.get("source", fallback_label)
    out: list[dict[str, Any]] = []
    for entry in data.get("assets", []):
        if not isinstance(entry, dict):
            continue
        out.append({
            "source": source,
            "category": entry.get("category", ""),
            "name": entry.get("name", ""),
            "requirement": entry.get("requirement", ""),
            "abilities": [str(a) for a in entry.get("abilities", [])],
        })
    return out


# ---------------------------------------------------------------------------
# Move extraction
# ---------------------------------------------------------------------------

def extract_moves(data: dict[str, Any], fallback_label: str) -> list[dict[str, Any]]:
    """Return a flat list of move dicts from a simple-format YAML document."""
    source = data.get("source", fallback_label)
    out: list[dict[str, Any]] = []
    for cat in data.get("categories", []):
        if not isinstance(cat, dict):
            continue
        cat_name = cat.get("name", "")
        for move in cat.get("moves", []):
            if not isinstance(move, dict):
                continue
            out.append({
                "source": source,
                "category": cat_name,
                "name": move.get("name", ""),
                "roll_type": move.get("roll_type", "no_roll"),
                "trigger": move.get("trigger", ""),
                "text": move.get("text", ""),
                "outcomes": move.get("outcomes") or {},
                "tables": move.get("tables") or [],
            })
    return out


# ---------------------------------------------------------------------------
# User settings  (persisted to data/user_settings.json)
# ---------------------------------------------------------------------------

_DEFAULT_SETTINGS: dict[str, Any] = {
    "regions": {
        "Sundered Isles": "Margins",
        "Starforged": "Terminus",
    },
}


def load_settings() -> dict[str, Any]:
    """Load user_settings.json, merging missing keys from defaults."""
    defaults = copy.deepcopy(_DEFAULT_SETTINGS)
    if not SETTINGS_JSON.exists():
        return defaults
    try:
        data: dict[str, Any] = json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
            elif isinstance(v, dict):
                for sk, sv in v.items():
                    data[k].setdefault(sk, sv)
        return data
    except Exception:
        return defaults


def save_settings(settings: dict[str, Any]) -> None:
    """Persist settings to user_settings.json."""
    SETTINGS_JSON.write_text(json.dumps(settings, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Top-level load function used by App._load_data
# ---------------------------------------------------------------------------

def load_all_data() -> dict[str, Any]:
    """Load every data file and return a dict of all game data."""
    sf_moves = extract_moves(load_yaml(SF_MOVES_YAML), "Starforged")
    si_moves = extract_moves(load_yaml(SI_MOVES_YAML), "Sundered Isles")

    si_oracles: list[dict[str, Any]] = []
    for d in (SI_ORACLES_DIR, CUSTOM_ORACLES_DIR):
        if d.is_dir():
            for f in sorted(d.glob("*.yaml")):
                si_oracles.extend(extract_oracles(load_yaml(f), "Sundered Isles"))

    sf_oracles: list[dict[str, Any]] = []
    if SF_ORACLES_DIR.is_dir():
        for f in sorted(SF_ORACLES_DIR.glob("*.yaml")):
            sf_oracles.extend(extract_oracles(load_yaml(f), "Starforged"))

    is_oracles: list[dict[str, Any]] = []
    if IS_ORACLES_DIR.is_dir():
        for f in sorted(IS_ORACLES_DIR.glob("*.yaml")):
            is_oracles.extend(extract_oracles(load_yaml(f), "Ironsworn"))

    sf_assets: list[dict[str, Any]] = []
    if SF_ASSETS_DIR.is_dir():
        for f in sorted(SF_ASSETS_DIR.glob("*.yaml")):
            sf_assets.extend(extract_assets(load_yaml(f), "Starforged"))

    si_assets: list[dict[str, Any]] = []
    if SI_ASSETS_DIR.is_dir():
        for f in sorted(SI_ASSETS_DIR.glob("*.yaml")):
            si_assets.extend(extract_assets(load_yaml(f), "Sundered Isles"))

    is_assets: list[dict[str, Any]] = []
    if IS_ASSETS_DIR.is_dir():
        for f in sorted(IS_ASSETS_DIR.glob("*.yaml")):
            is_assets.extend(extract_assets(load_yaml(f), "Ironsworn"))

    all_oracles = sf_oracles + si_oracles + is_oracles
    oracle_by_id: dict[str, dict[str, Any]] = {
        o["oracle_id"]: o for o in all_oracles if o.get("oracle_id")
    }

    bundles: list[dict[str, Any]] = []
    game_regions: dict[str, list[str]] = {}
    if BUNDLES_YAML.exists():
        bundles_data = load_yaml(BUNDLES_YAML)
        bundles = bundles_data.get("bundles") or []
        game_regions = bundles_data.get("game_regions") or {}

    settings = load_settings()

    return {
        "sf_moves": sf_moves,
        "si_moves": si_moves,
        "sf_oracles": sf_oracles,
        "si_oracles": si_oracles,
        "is_oracles": is_oracles,
        "sf_assets": sf_assets,
        "si_assets": si_assets,
        "is_assets": is_assets,
        "oracle_by_id": oracle_by_id,
        "bundles": bundles,
        "game_regions": game_regions,
        "settings": settings,
    }
