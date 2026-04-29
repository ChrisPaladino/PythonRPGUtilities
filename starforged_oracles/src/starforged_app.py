"""starforged_app.py - Starforged / Sundered Isles reference GUI.

Requires Python 3.10+, Tkinter (stdlib), and PyYAML.
Data must be downloaded first:
    python src/fetch_data.py

Usage:
    python src/starforged_app.py
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

import widgets  # applies the tk.Text.grid monkey-patch on import
from loader import load_all_data, save_settings
from styles import BG, configure_styles
from tabs.assets import AssetsTabMixin
from tabs.bundles import BundlesTabMixin
from tabs.character import CharacterTabMixin
from tabs.dice import DiceTabMixin
from tabs.moves import MovesTabMixin
from tabs.oracles import OraclesTabMixin
from tabs.settings import SettingsTabMixin

class App(
    CharacterTabMixin,
    DiceTabMixin,
    MovesTabMixin,
    OraclesTabMixin,
    AssetsTabMixin,
    BundlesTabMixin,
    SettingsTabMixin,
    tk.Tk,
):

    def __init__(self) -> None:
        super().__init__()
        self.title("Starforged / Sundered Isles Reference")
        self.geometry("800x600")
        self.minsize(780, 560)
        self.configure(bg=BG)
        configure_styles(self)
        self._load_data()
        self._build_ui()

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    def _load_data(self) -> None:
        data = load_all_data()
        self._sf_moves: list[dict[str, Any]] = data["sf_moves"]
        self._si_moves: list[dict[str, Any]] = data["si_moves"]
        self._sf_oracles: list[dict[str, Any]] = data["sf_oracles"]
        self._si_oracles: list[dict[str, Any]] = data["si_oracles"]
        self._is_oracles: list[dict[str, Any]] = data["is_oracles"]
        self._sf_assets: list[dict[str, Any]] = data["sf_assets"]
        self._si_assets: list[dict[str, Any]] = data["si_assets"]
        self._is_assets: list[dict[str, Any]] = data["is_assets"]
        self._oracle_by_id: dict[str, dict[str, Any]] = data["oracle_by_id"]
        self._bundles: list[dict[str, Any]] = data["bundles"]
        self._game_regions: dict[str, list[str]] = data["game_regions"]
        self._settings: dict[str, Any] = data["settings"]
        self._characters: list[dict[str, Any]] = data["characters"]

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=6, pady=6)

        for label, builder in (
            ("  Character  ", self._build_character_tab),
            ("  Roller  ", self._build_dice_tab),
            ("  Moves  ",   self._build_moves_tab),
            ("  Oracles  ", self._build_oracles_tab),
            ("  Bundles  ", self._build_bundles_tab),
            ("  Assets  ",  self._build_assets_tab),
            ("  Settings  ", self._build_settings_tab),
        ):
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=label)
            builder(tab)

    # ------------------------------------------------------------------
    # Shared helpers (used by all tab mixins via self)
    # ------------------------------------------------------------------

    @staticmethod
    def _short_source(source: str) -> str:
        return {"Starforged": "SF", "Sundered Isles": "SI", "Ironsworn": "IS"}.get(
            source, source
        )

    def _make_textbox(self, parent: tk.Widget) -> tk.Text:
        return widgets.make_textbox(parent)

    def _set_text_lines(self, txt: tk.Text, lines: list[tuple[str, str]]) -> None:
        widgets.set_text_lines(txt, lines)

    def _set_region_setting(self, game: str, region: str) -> None:
        if not game or not region:
            return
        regions = self._game_regions.get(game, [])
        if regions and region not in regions:
            return

        current = self._settings.setdefault("regions", {}).get(game)
        if current != region:
            self._settings["regions"][game] = region
            save_settings(self._settings)

        settings_region_vars = getattr(self, "_settings_region_vars", {})
        settings_var = settings_region_vars.get(game)
        if settings_var is not None and settings_var.get() != region:
            settings_var.set(region)

        current_bundle = getattr(self, "_current_bundle", None)
        bundle_region_var = getattr(self, "_bundle_region_var", None)
        if (
            current_bundle
            and bundle_region_var is not None
            and current_bundle.get("game") == game
            and bundle_region_var.get() != region
        ):
            bundle_region_var.set(region)

    @staticmethod
    def _rebuild_option_menu(
        om: tk.OptionMenu, var: tk.StringVar, values: list[str]
    ) -> None:
        widgets.rebuild_option_menu(om, var, values)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
