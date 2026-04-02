"""tabs/assets.py – Assets tab mixin."""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, TYPE_CHECKING

from styles import ACCENT, BG, BORDER, FG, PANEL_BG
from widgets import (
    make_listbox_frame, make_option_menu, make_paned, make_search_entry,
    make_textbox, rebuild_option_menu, set_text_lines,
)

if TYPE_CHECKING:
    from starforged_app import App


class AssetsTabMixin:

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_assets_tab(self, parent: ttk.Frame) -> None:
        paned = make_paned(parent)

        # --- Left panel ---
        left = ttk.Frame(paned, style="Panel.TFrame")
        left.rowconfigure(5, weight=1)
        left.columnconfigure(0, weight=1)
        paned.add(left, minsize=160, width=230)

        ttk.Label(left, text="Game", style="Cat.TLabel").grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 2)
        )
        all_sources = sorted(
            {a["source"] for a in getattr(self, '_sf_assets', []) + getattr(self, '_si_assets', []) + getattr(self, '_is_assets', [])}
        )
        self._asset_game_var = tk.StringVar(value="All")
        self._asset_game_var.trace_add("write", lambda *_: self._on_asset_game_change())
        make_option_menu(left, self._asset_game_var, ["All"] + all_sources).grid(
            row=1, column=0, sticky="ew", padx=8, pady=(0, 4)
        )

        ttk.Label(left, text="Category", style="Cat.TLabel").grid(
            row=2, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        all_cats = sorted(
            {a["category"] for a in getattr(self, '_sf_assets', []) + getattr(self, '_si_assets', []) + getattr(self, '_is_assets', [])}
        )
        self._asset_selected_cat = "All"
        self._asset_cat_var = tk.StringVar(value="All")
        self._asset_cat_var.trace_add("write", lambda *_: self._on_asset_cat_change())
        self._asset_cat_om = make_option_menu(left, self._asset_cat_var, ["All"] + all_cats)
        self._asset_cat_om.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 4))

        ttk.Label(left, text="Search", style="Cat.TLabel").grid(
            row=4, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        self._asset_search_var = tk.StringVar()
        self._asset_search_var.trace_add("write", lambda *_: self._refresh_asset_list())
        make_search_entry(left, self._asset_search_var).grid(
            row=4, column=0, sticky="ew", padx=8, pady=(0, 4)
        )

        lf, self._asset_listbox = make_listbox_frame(left)
        lf.grid(row=5, column=0, sticky="nsew", padx=4, pady=4)
        self._asset_listbox.bind("<<ListboxSelect>>", self._on_asset_select)

        # --- Right panel ---
        right = ttk.Frame(paned, style="Panel.TFrame")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        paned.add(right, minsize=200)

        title_bar = ttk.Frame(right, style="Panel.TFrame")
        title_bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(10, 2))
        title_bar.columnconfigure(1, weight=1)

        ttk.Button(
            title_bar, text="Random", style="Accent.TButton",
            command=self._pick_random_asset,
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._asset_title_var = tk.StringVar(value="Select an asset →")
        ttk.Label(title_bar, textvariable=self._asset_title_var, style="Title.TLabel").grid(
            row=0, column=1, sticky="w"
        )

        self._asset_text = make_textbox(right)
        self._asset_text.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)

        self._assets_visible: list[dict[str, Any]] = []
        self._refresh_asset_category_options()
        self._refresh_asset_list()

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _on_asset_game_change(self) -> None:
        self._refresh_asset_category_options()
        self._refresh_asset_list()

    def _on_asset_cat_change(self) -> None:
        self._asset_selected_cat = self._asset_cat_var.get()
        self._refresh_asset_list()

    def _refresh_asset_category_options(self) -> None:
        game_filter = self._asset_game_var.get()
        all_assets = getattr(self, '_sf_assets', []) + getattr(self, '_si_assets', []) + getattr(self, '_is_assets', [])
        if game_filter == "All":
            cats = sorted({a["category"] for a in all_assets})
        else:
            cats = sorted({a["category"] for a in all_assets if a["source"] == game_filter})
        valid = ["All"] + cats
        rebuild_option_menu(self._asset_cat_om, self._asset_cat_var, valid)
        if self._asset_selected_cat not in valid:
            self._asset_selected_cat = "All"
            self._asset_cat_var.set("All")

    def _refresh_asset_list(self) -> None:
        game_filter = self._asset_game_var.get()
        cat_filter = self._asset_selected_cat
        query = self._asset_search_var.get().strip().lower()
        all_assets = getattr(self, '_sf_assets', []) + getattr(self, '_si_assets', []) + getattr(self, '_is_assets', [])
        filtered = [
            a for a in all_assets
            if (game_filter == "All" or a["source"] == game_filter)
            and (cat_filter == "All" or a["category"] == cat_filter)
            and (not query or query in a["name"].lower() or query in a["category"].lower())
        ]
        filtered.sort(key=lambda a: (a["source"], a["category"], a["name"]))
        self._assets_visible = filtered
        self._asset_listbox.delete(0, tk.END)
        short_source = getattr(self, '_short_source', lambda s: s)
        for a in filtered:
            label = f"[{short_source(a['source'])}]  {a['category']} › {a['name']}"
            self._asset_listbox.insert(tk.END, label)

    # ------------------------------------------------------------------
    # Selection & display
    # ------------------------------------------------------------------

    def _pick_random_asset(self) -> None:
        if not self._assets_visible:
            messagebox.showinfo("No assets", "No assets match the current filters.")
            return
        idx = random.randrange(len(self._assets_visible))
        self._asset_listbox.selection_clear(0, tk.END)
        self._asset_listbox.selection_set(idx)
        self._asset_listbox.activate(idx)
        self._asset_listbox.see(idx)
        self._display_asset(self._assets_visible[idx])

    def _on_asset_select(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        selection = self._asset_listbox.curselection()
        if not selection:
            return
        self._display_asset(self._assets_visible[selection[0]])

    def _display_asset(self, asset: dict[str, Any]) -> None:
        self._asset_title_var.set(f"{asset['name']}  —  {asset['category']}")
        lines: list[tuple[str, str]] = [
            ("cat", f"{asset['source']}  ·  {asset['category']}"),
            ("body", ""),
        ]
        if asset["requirement"]:
            lines.append(("bold", f"Requirement:  {asset['requirement']}"))
            lines.append(("body", ""))
        for i, ability_text in enumerate(asset["abilities"], 1):
            lines.append(("bold", f"Ability {i}"))
            lines.append(("body", ability_text))
            lines.append(("body", ""))
        set_text_lines(self._asset_text, lines)
