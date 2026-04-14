"""tabs/settings.py - Settings tab mixin."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from widgets import make_option_menu

if TYPE_CHECKING:
    from starforged_app import App


class SettingsTabMixin:

    def _build_settings_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        panel = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        panel.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        panel.columnconfigure(1, weight=1)

        ttk.Label(panel, text="Oracle Defaults", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )
        ttk.Label(
            panel,
            text=(
                "Choose the default region for games with regional oracle variants. "
                "Bundles use these values automatically, and the bundle-level region picker "
                "updates the same setting."
            ),
            wraplength=520,
            justify="left",
            style="Body.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 14))

        self._settings_region_vars: dict[str, tk.StringVar] = {}

        row = 2
        for game in sorted(self._game_regions):
            regions = self._game_regions.get(game, [])
            if not regions:
                continue

            current = self._settings.get("regions", {}).get(game, regions[0])
            var = tk.StringVar(value=current if current in regions else regions[0])
            var.trace_add(
                "write",
                lambda *_args, game=game, var=var: self._set_region_setting(game, var.get()),
            )
            self._settings_region_vars[game] = var

            ttk.Label(panel, text=f"{game} Region", style="Cat.TLabel").grid(
                row=row, column=0, sticky="w", padx=(0, 12), pady=4
            )
            make_option_menu(panel, var, regions, width=16).grid(
                row=row, column=1, sticky="w", pady=4
            )
            row += 1