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
from loader import load_all_data
from styles import BG, configure_styles
from tabs.assets import AssetsTabMixin
from tabs.bundles import BundlesTabMixin
from tabs.moves import MovesTabMixin
from tabs.oracles import OraclesTabMixin


class App(MovesTabMixin, OraclesTabMixin, AssetsTabMixin, BundlesTabMixin, tk.Tk):

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

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=6, pady=6)

        for label, builder in (
            ("  Moves  ",   self._build_moves_tab),
            ("  Oracles  ", self._build_oracles_tab),
            ("  Assets  ",  self._build_assets_tab),
            ("  Bundles  ", self._build_bundles_tab),
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
