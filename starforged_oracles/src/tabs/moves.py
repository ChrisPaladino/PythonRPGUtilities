"""tabs/moves.py – Moves tab mixin."""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk
from typing import Any, TYPE_CHECKING

from styles import ACCENT, ACCENT2, BG, BORDER, FG, PANEL_BG
from widgets import (
    make_listbox_frame, make_option_menu, make_paned, make_search_entry,
    make_textbox, rebuild_option_menu, set_text_lines,
)

if TYPE_CHECKING:
    from starforged_app import App


class MovesTabMixin:

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_moves_tab(self, parent: ttk.Frame) -> None:
        paned = make_paned(parent)

        # --- Left panel ---
        left = ttk.Frame(paned, style="Panel.TFrame")
        left.rowconfigure(5, weight=1)
        left.columnconfigure(0, weight=1)
        paned.add(left, minsize=160, width=230)

        ttk.Label(left, text="Game", style="Cat.TLabel").grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 2)
        )
        all_move_sources = sorted({m["source"] for m in self._sf_moves + self._si_moves})
        self._move_game_var = tk.StringVar(value="All")
        self._move_game_var.trace_add("write", lambda *_: self._on_move_game_change())
        move_game_om = make_option_menu(left, self._move_game_var, ["All"] + all_move_sources)
        move_game_om.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))

        ttk.Label(left, text="Category", style="Cat.TLabel").grid(
            row=2, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        self._move_selected_cat = "All"
        all_move_cats = sorted({m["category"] for m in self._sf_moves + self._si_moves})
        self._move_cat_var = tk.StringVar(value="All")
        self._move_cat_var.trace_add("write", lambda *_: self._on_move_cat_change())
        self._move_cat_om = make_option_menu(left, self._move_cat_var, ["All"] + all_move_cats)
        self._move_cat_om.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 4))

        ttk.Label(left, text="Search", style="Cat.TLabel").grid(
            row=4, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        self._move_search_var = tk.StringVar()
        self._move_search_var.trace_add("write", lambda *_: self._refresh_move_list())
        make_search_entry(left, self._move_search_var).grid(
            row=4, column=0, sticky="ew", padx=8, pady=(0, 4)
        )

        lf, self._move_listbox = make_listbox_frame(left)
        lf.grid(row=5, column=0, sticky="nsew", padx=4, pady=4)
        self._move_listbox.bind("<<ListboxSelect>>", self._on_move_select)

        # --- Right panel ---
        right = ttk.Frame(paned, style="Panel.TFrame")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)
        paned.add(right, minsize=200)

        self._move_title_var = tk.StringVar(value="Select a move →")
        ttk.Label(right, textvariable=self._move_title_var, style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 2)
        )

        move_roll_bar = ttk.Frame(right, style="Panel.TFrame")
        move_roll_bar.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 4))
        self._move_roll_result_var = tk.StringVar(value="")
        ttk.Button(
            move_roll_bar, text="Roll d100", style="Accent.TButton",
            command=self._roll_move_table,
        ).pack(side="left", padx=(0, 8))
        ttk.Label(
            move_roll_bar, textvariable=self._move_roll_result_var, style="Title.TLabel"
        ).pack(side="left")
        move_roll_bar.grid_remove()
        self._move_roll_bar = move_roll_bar

        self._move_text = make_textbox(right)
        self._move_text.grid(row=2, column=0, sticky="nsew", padx=6, pady=4)

        self._moves_visible: list[dict[str, Any]] = []
        self._current_move: dict[str, Any] | None = None
        self._refresh_move_list()

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _on_move_game_change(self) -> None:
        game_filter = self._move_game_var.get()
        all_moves = self._sf_moves + self._si_moves
        if game_filter == "All":
            cats = sorted({m["category"] for m in all_moves})
        else:
            cats = sorted({m["category"] for m in all_moves if m["source"] == game_filter})
        rebuild_option_menu(self._move_cat_om, self._move_cat_var, ["All"] + cats)
        if self._move_selected_cat not in cats:
            self._move_selected_cat = "All"
            self._move_cat_var.set("All")
        self._refresh_move_list()

    def _on_move_cat_change(self) -> None:
        self._move_selected_cat = self._move_cat_var.get()
        self._refresh_move_list()

    def _refresh_move_list(self) -> None:
        game_filter = self._move_game_var.get()
        cat_filter = self._move_selected_cat
        query = self._move_search_var.get().strip().lower()
        all_moves = self._sf_moves + self._si_moves
        filtered = [
            m for m in all_moves
            if (game_filter == "All" or m["source"] == game_filter)
            and (cat_filter == "All" or m["category"] == cat_filter)
            and (not query or query in m["name"].lower() or query in m["category"].lower())
        ]
        filtered.sort(key=lambda m: (m["source"], m["category"], m["name"]))
        self._moves_visible = filtered
        self._move_listbox.delete(0, tk.END)
        for m in filtered:
            if game_filter == "All":
                label = f"[{self._short_source(m['source'])}]  {m['category']} › {m['name']}"
            else:
                label = f"{m['category']} › {m['name']}"
            self._move_listbox.insert(tk.END, label)

    # ------------------------------------------------------------------
    # Selection & display
    # ------------------------------------------------------------------

    def _on_move_select(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        selection = self._move_listbox.curselection()
        if not selection:
            return
        move = self._moves_visible[selection[0]]
        self._move_roll_result_var.set("")
        self._display_move(move)

    def _display_move(
        self, move: dict[str, Any], highlight_roll: int | None = None
    ) -> None:
        self._current_move = move
        tables = move.get("tables", [])
        if tables:
            self._move_roll_bar.grid()
        else:
            self._move_roll_bar.grid_remove()

        self._move_title_var.set(f"{move['name']}  —  {move['category']}")
        lines: list[tuple[str, str]] = []
        lines.append(("cat", f"{move['source']}  ·  {move['category']}"))
        lines.append(("body", ""))

        if move["trigger"]:
            lines.append(("bold", "Trigger:"))
            lines.append(("body", move["trigger"]))
            lines.append(("body", ""))

        if move["text"]:
            lines.append(("bold", "Move text:"))
            lines.append(("body", move["text"]))

        if move["outcomes"]:
            lines.append(("body", ""))
            lines.append(("bold", "Outcomes:"))
            for outcome_key, outcome_txt in move["outcomes"].items():
                tag = {"strong_hit": "strong", "weak_hit": "weak", "miss": "miss"}.get(
                    outcome_key, "body"
                )
                lines.append((tag, f"  {outcome_key.replace('_', ' ').title()}"))
                lines.append(("body", f"    {outcome_txt}"))
                lines.append(("body", ""))

        for i, tbl in enumerate(tables):
            lines.append(("body", ""))
            lines.append(("bold", tbl["name"] + ":"))
            lines.append(("body", ""))
            for row in tbl.get("rows", []):
                rmin, rmax, text = row.get("min"), row.get("max"), row.get("text", "")
                if rmin is None or rmax is None:
                    range_str = "    –   "
                elif rmin == rmax:
                    range_str = f"{rmin:>3}      "
                else:
                    range_str = f"{rmin:>3}–{rmax:<3}"
                tag = "body"
                if i == 0 and highlight_roll is not None and rmin is not None and rmax is not None:
                    if rmin <= highlight_roll <= rmax:
                        tag = "strong"
                lines.append((tag, f"  {range_str}  {text}"))

        set_text_lines(self._move_text, lines)

    def _roll_move_table(self) -> None:
        if self._current_move is None:
            return
        tables = self._current_move.get("tables", [])
        if not tables:
            return
        tbl = tables[0]
        roll = random.randint(1, 100)
        matching = next(
            (row["text"] for row in tbl.get("rows", [])
             if row.get("min") is not None and row["min"] <= roll <= row["max"]),
            ""
        )
        self._move_roll_result_var.set(f"Rolled {roll}  \u2192  {matching}")
        self._display_move(self._current_move, highlight_roll=roll)
