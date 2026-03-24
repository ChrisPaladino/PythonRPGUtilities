"""loader.py – YAML loading and data extraction for the Starforged reference app."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:
    raise SystemExit("PyYAML is not installed.  Run:  pip install pyyaml")

# ---------------------------------------------------------------------------
# Paths  –  work both in development and when frozen by PyInstaller
# ---------------------------------------------------------------------------

import sys

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

# Maps YAML top-level _id values to friendly game names.
SOURCE_LABELS: dict[str, str] = {
    "starforged": "Starforged",
    "sundered_isles": "Sundered Isles",
    "classic": "Ironsworn",
    "delve": "Ironsworn: Delve",
}

# ---------------------------------------------------------------------------
# Markup helpers
# ---------------------------------------------------------------------------

_BOLD_RE = re.compile(r"__(.+?)__")
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_TABLE_RE = re.compile(r"\{\{table:[^}]+\}\}")


def strip_markup(text: str) -> str:
    """Convert light Markdown/Datasworn markup to plain text."""
    text = _BOLD_RE.sub(r"\1", text)
    text = _LINK_RE.sub(r"\1", text)
    text = _TABLE_RE.sub("[see table below]", text)
    return text


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def _sanitise_yaml(text: str) -> str:
    """Fix known quirks in Datasworn YAML that trip up PyYAML's safe loader."""
    def _fix_name(m: re.Match[str]) -> str:
        sigil = m.group(1)
        name = re.sub(r"[^A-Za-z0-9_]", "_", m.group(2))
        return sigil + name

    text = re.sub(r"([&*])([A-Za-z0-9_][A-Za-z0-9_.:]*)", _fix_name, text)

    anchor_counts: dict[str, int] = {}
    anchor_canonical: dict[str, str] = {}

    def _rewrite_anchor(m: re.Match[str]) -> str:
        name = m.group(1)
        anchor_counts[name] = anchor_counts.get(name, 0) + 1
        new_name = f"{name}_{anchor_counts[name]}" if anchor_counts[name] > 1 else name
        if name not in anchor_canonical:
            anchor_canonical[name] = new_name
        return f"&{new_name}"

    text = re.sub(r"&([A-Za-z0-9_]+)", _rewrite_anchor, text)

    def _rewrite_alias(m: re.Match[str]) -> str:
        name = m.group(1)
        canonical = anchor_canonical.get(name)
        if canonical is None:
            return "null"
        return f"*{canonical}"

    text = re.sub(r"\*([A-Za-z0-9_]+)", _rewrite_alias, text)

    sanitised_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip(" ")
        indent = line[: len(line) - len(stripped)]
        sanitised_lines.append(indent + stripped.replace("\t", " "))
    return "".join(sanitised_lines)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(
            f"Cannot open data file {path.name}.\n"
            "Run  python src/fetch_data.py  first."
        ) from exc
    return yaml.safe_load(_sanitise_yaml(raw)) or {}


def _source_name(data: dict[str, Any], fallback: str) -> str:
    return SOURCE_LABELS.get(data.get("_id", ""), fallback)


# ---------------------------------------------------------------------------
# Move extraction
# ---------------------------------------------------------------------------

def extract_moves(data: dict[str, Any], fallback_label: str) -> list[dict[str, Any]]:
    """Return a flat list of move dicts from a loaded YAML document."""
    source_name = _source_name(data, fallback_label)
    moves: list[dict[str, Any]] = []
    for cat_key, cat in (data.get("moves") or {}).items():
        if not isinstance(cat, dict):
            continue
        cat_name: str = cat.get("name", cat_key)
        for move_key, move in (cat.get("contents") or {}).items():
            if not isinstance(move, dict):
                continue
            moves.append(
                {
                    "source": source_name,
                    "category": cat_name,
                    "key": move_key,
                    "name": move.get("name", move_key),
                    "trigger": strip_markup(
                        (move.get("trigger") or {}).get("text", "")
                    ),
                    "text": strip_markup(move.get("text", "")),
                    "outcomes": {
                        k: strip_markup(v.get("text", "") if isinstance(v, dict) else v)
                        for k, v in (move.get("outcomes") or {}).items()
                    },
                    "roll_type": move.get("roll_type", "no_roll"),
                    "tables": [
                        {
                            "name": tbl.get("name", ""),
                            "rows": [
                                {
                                    "min": row.get("min"),
                                    "max": row.get("max"),
                                    "text": strip_markup(row.get("text", "")),
                                }
                                for row in (tbl.get("rows") or [])
                                if isinstance(row, dict)
                            ],
                        }
                        for tbl in (move.get("tables") or [])
                        if isinstance(tbl, dict)
                    ],
                }
            )
    return moves


# ---------------------------------------------------------------------------
# Oracle extraction
# ---------------------------------------------------------------------------

def _extract_oracle_table(
    oracle: dict[str, Any],
    category: str,
    source_label: str,
    oracle_id: str = "",
) -> dict[str, Any] | None:
    rows = oracle.get("rows")
    if not rows:
        return None
    parsed: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        text = strip_markup(row.get("text") or "")
        text2 = strip_markup(row.get("text2") or "")
        display_text = f"{text}: {text2}" if text and text2 else text or text2
        parsed.append({"min": row.get("min"), "max": row.get("max"), "text": display_text})
    if not parsed:
        return None
    cursed_ref = ""
    for _game, tag_data in (oracle.get("tags") or {}).items():
        if isinstance(tag_data, dict) and "cursed_version" in tag_data:
            cursed_ref = tag_data["cursed_version"]
            break
    return {
        "source": source_label,
        "category": category,
        "name": oracle.get("name", ""),
        "oracle_id": oracle_id,
        "cursed_version": cursed_ref,
        "rows": parsed,
    }


def _walk_oracle_collection(
    node: dict[str, Any],
    category: str,
    source_label: str,
    out: list[dict[str, Any]],
    id_prefix: str = "",
) -> None:
    for section_key in ("contents", "collections"):
        section: dict[str, Any] = node.get(section_key) or {}
        for key, child in section.items():
            if not isinstance(child, dict):
                continue
            child_id = f"{id_prefix}/{key}" if id_prefix else key
            child_type = child.get("type", "")
            if child_type == "oracle_rollable":
                tbl = _extract_oracle_table(child, category, source_label, oracle_id=child_id)
                if tbl:
                    out.append(tbl)
            elif child_type == "oracle_collection":
                child_cat = child.get("name", category)
                _walk_oracle_collection(child, child_cat, source_label, out, id_prefix=child_id)
            else:
                if "rows" in child:
                    tbl = _extract_oracle_table(child, category, source_label, oracle_id=child_id)
                    if tbl:
                        out.append(tbl)
                if "contents" in child or "collections" in child:
                    child_cat = child.get("name", category)
                    _walk_oracle_collection(child, child_cat, source_label, out, id_prefix=child_id)


def extract_oracles(data: dict[str, Any], fallback_label: str) -> list[dict[str, Any]]:
    """Return a flat list of oracle tables from a loaded YAML document."""
    source_name = _source_name(data, fallback_label)
    tables: list[dict[str, Any]] = []
    top_id = data.get("_id", "")
    for cat_key, cat in (data.get("oracles") or {}).items():
        if not isinstance(cat, dict):
            continue
        cat_name = cat.get("name", cat_key)
        id_prefix = f"{top_id}/oracles/{cat_key}" if top_id else cat_key
        _walk_oracle_collection(cat, cat_name, source_name, tables, id_prefix=id_prefix)
    return tables


# ---------------------------------------------------------------------------
# Asset extraction
# ---------------------------------------------------------------------------

def extract_assets(data: dict[str, Any], fallback_label: str) -> list[dict[str, Any]]:
    """Return a flat list of asset dicts from a loaded YAML document."""
    source_name = _source_name(data, fallback_label)
    assets: list[dict[str, Any]] = []
    for coll_key, coll in (data.get("assets") or {}).items():
        if not isinstance(coll, dict):
            continue
        coll_raw_name = coll.get("name", coll_key)
        coll_cat = re.sub(r"\s+Assets?\s*$", "", coll_raw_name, flags=re.IGNORECASE).strip()
        for _asset_key, asset in (coll.get("contents") or {}).items():
            if not isinstance(asset, dict):
                continue
            category = asset.get("category") or coll_cat
            abilities = [
                strip_markup(ab.get("text", ""))
                for ab in (asset.get("abilities") or [])
                if isinstance(ab, dict) and ab.get("text")
            ]
            assets.append(
                {
                    "source": source_name,
                    "category": category,
                    "name": asset.get("name", _asset_key),
                    "requirement": strip_markup(asset.get("requirement") or ""),
                    "abilities": abilities,
                }
            )
    return assets


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
    if BUNDLES_YAML.exists():
        bundles = load_yaml(BUNDLES_YAML).get("bundles") or []

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
    }
