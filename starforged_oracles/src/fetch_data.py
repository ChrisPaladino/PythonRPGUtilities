"""fetch_data.py – Download Starforged / Sundered Isles data files from GitHub.

Run once before launching starforged_app.py:
    python src/fetch_data.py

Files are saved to the data/ directory relative to the project root.
Requires an internet connection.
"""
from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path

BASE_RAW = "https://raw.githubusercontent.com/rsek/datasworn/main/source_data"
BASE_SF = f"{BASE_RAW}/starforged"
BASE_SI = f"{BASE_RAW}/sundered_isles"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SI_ORACLES_DIR = DATA_DIR / "si_oracles"
SF_ASSETS_DIR = DATA_DIR / "sf_assets"
SI_ASSETS_DIR = DATA_DIR / "si_assets"

# ---------------------------------------------------------------------------
# Files to download
# ---------------------------------------------------------------------------

SF_FILES: list[tuple[str, str]] = [
    (f"{BASE_SF}/moves.yaml", "starforged_moves.yaml"),
]

SI_MOVE_FILES: list[tuple[str, str]] = [
    (f"{BASE_SI}/moves/session.yaml", "si_session_moves.yaml"),
]

SF_ASSET_FILES: list[str] = [
    "command_vehicle.yaml",
    "companion.yaml",
    "deed.yaml",
    "module.yaml",
    "path.yaml",
    "support_vehicle.yaml",
]

SI_ASSET_FILES: list[str] = [
    "companion.yaml",
    "deed.yaml",
    "module.yaml",
    "path.yaml",
    "vehicle.yaml",
]

SI_ORACLE_FILES: list[str] = [
    "core.yaml",
    "characters.yaml",
    "character_creation.yaml",
    "factions.yaml",
    "seafaring.yaml",
    "sailing_ships.yaml",
    "islands.yaml",
    "settlements.yaml",
    "encounters.yaml",
    "overland.yaml",
    "caves.yaml",
    "ruins.yaml",
    "shipwrecks.yaml",
    "misc.yaml",
    "weather.yaml",
    "treasures.yaml",
    "plunder.yaml",
    "other.yaml",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _download(url: str, dest: Path) -> bool:
    print(f"  {dest.name:<40} ", end="", flush=True)
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:  # noqa: S310
            dest.write_bytes(resp.read())
        print("OK")
        return True
    except urllib.error.URLError as exc:
        print(f"FAILED  ({exc})")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SI_ORACLES_DIR.mkdir(parents=True, exist_ok=True)
    SF_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    SI_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    failed: list[str] = []

    print("Downloading Starforged move data…")
    for url, filename in SF_FILES:
        if not _download(url, DATA_DIR / filename):
            failed.append(filename)

    print("\nDownloading Sundered Isles session moves…")
    for url, filename in SI_MOVE_FILES:
        if not _download(url, DATA_DIR / filename):
            failed.append(filename)

    print("\nDownloading Starforged asset data…")
    for fname in SF_ASSET_FILES:
        url = f"{BASE_SF}/assets/{fname}"
        if not _download(url, SF_ASSETS_DIR / fname):
            failed.append(fname)

    print("\nDownloading Sundered Isles asset data…")
    for fname in SI_ASSET_FILES:
        url = f"{BASE_SI}/assets/{fname}"
        if not _download(url, SI_ASSETS_DIR / fname):
            failed.append(fname)

    print("\nDownloading Sundered Isles oracle tables…")
    for fname in SI_ORACLE_FILES:
        url = f"{BASE_SI}/oracles/{fname}"
        if not _download(url, SI_ORACLES_DIR / fname):
            failed.append(fname)

    print()
    if failed:
        print(f"WARNING: {len(failed)} file(s) could not be downloaded:")
        for f in failed:
            print(f"  • {f}")
        print("Re-run fetch_data.py when connectivity is restored.")
    else:
        print("All files downloaded successfully.")

    print("\nTo launch the app:")
    print("  python src/starforged_app.py")


if __name__ == "__main__":
    main()
