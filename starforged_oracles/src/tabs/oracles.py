"""tabs/oracles.py – Oracles tab mixin."""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk
from typing import Any, TYPE_CHECKING

from styles import ACCENT, BG, BORDER, FG, HIT_MISS, PANEL_BG, SEL_BG
from widgets import (
    make_listbox_frame, make_option_menu, make_paned, make_search_entry,
    make_textbox, rebuild_option_menu, set_text_lines,
)

if TYPE_CHECKING:
    from starforged_app import App


class OraclesTabMixin:

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_oracles_tab(self: "App", parent: ttk.Frame) -> None:
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
            {o["source"] for o in self._sf_oracles + self._si_oracles + self._is_oracles}
        )
        self._oracle_game_var = tk.StringVar(value="All")
        self._oracle_game_var.trace_add("write", lambda *_: self._on_oracle_game_change())
        make_option_menu(left, self._oracle_game_var, ["All"] + all_sources).grid(
            row=1, column=0, sticky="ew", padx=8, pady=(0, 4)
        )

        ttk.Label(left, text="Category", style="Cat.TLabel").grid(
            row=2, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        all_cats = sorted(
            {o["category"] for o in self._sf_oracles + self._si_oracles + self._is_oracles}
        )
        self._oracle_selected_cat = "All"
        self._oracle_cat_var = tk.StringVar(value="All")
        self._oracle_cat_var.trace_add("write", lambda *_: self._on_oracle_cat_change())
        self._oracle_cat_om = make_option_menu(left, self._oracle_cat_var, ["All"] + all_cats)
        self._oracle_cat_om.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 4))

        ttk.Label(left, text="Search", style="Cat.TLabel").grid(
            row=4, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        self._oracle_search_var = tk.StringVar()
        self._oracle_search_var.trace_add("write", lambda *_: self._refresh_oracle_list())
        make_search_entry(left, self._oracle_search_var).grid(
            row=4, column=0, sticky="ew", padx=8, pady=(0, 4)
        )

        lf, self._oracle_listbox = make_listbox_frame(left)
        lf.grid(row=5, column=0, sticky="nsew", padx=4, pady=4)
        self._oracle_listbox.bind("<<ListboxSelect>>", self._on_oracle_select)

        # --- Right panel ---
        right = ttk.Frame(paned, style="Panel.TFrame")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)
        paned.add(right, minsize=200)

        self._oracle_title_var = tk.StringVar(value="Select an oracle →")
        ttk.Label(right, textvariable=self._oracle_title_var, style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 2)
        )

        roll_bar = ttk.Frame(right, style="Panel.TFrame")
        roll_bar.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 4))
        self._roll_result_var = tk.StringVar(value="")
        ttk.Button(
            roll_bar, text="Roll d100", style="Accent.TButton",
            command=self._roll_oracle,
        ).pack(side="left", padx=(0, 8))

        self._cursed_enabled_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            roll_bar, text="☠ Cursed Die",
            variable=self._cursed_enabled_var,
            bg=PANEL_BG, fg=HIT_MISS, selectcolor=PANEL_BG,
            activebackground=PANEL_BG, activeforeground=HIT_MISS,
            font=("Segoe UI", 9), relief="flat", bd=0, highlightthickness=0,
        ).pack(side="left", padx=(0, 4))

        self._cursed_die_var = tk.StringVar(value="d10")
        cursed_die_om = tk.OptionMenu(roll_bar, self._cursed_die_var, "d10", "d12", "d20")
        cursed_die_om.config(
            bg=PANEL_BG, fg=HIT_MISS, activebackground=SEL_BG, activeforeground=HIT_MISS,
            highlightthickness=0, relief="flat", width=3,
        )
        cursed_die_om["menu"].config(bg=PANEL_BG, fg=HIT_MISS, activebackground=SEL_BG, activeforeground=HIT_MISS)
        cursed_die_om.pack(side="left", padx=(0, 12))

        ttk.Label(roll_bar, textvariable=self._roll_result_var, style="Title.TLabel").pack(
            side="left"
        )

        self._oracle_text = make_textbox(right)
        self._oracle_text.grid(row=2, column=0, sticky="nsew", padx=6, pady=4)

        self._oracles_visible: list[dict[str, Any]] = []
        self._current_oracle: dict[str, Any] | None = None
        self._refresh_oracle_list()

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _on_oracle_game_change(self: "App") -> None:
        game_filter = self._oracle_game_var.get() or "All"
        all_oracles = self._sf_oracles + self._si_oracles + self._is_oracles
        if game_filter == "All":
            cats = sorted({o["category"] for o in all_oracles})
        else:
            cats = sorted({o["category"] for o in all_oracles if o["source"] == game_filter})
        rebuild_option_menu(self._oracle_cat_om, self._oracle_cat_var, ["All"] + cats)
        if self._oracle_selected_cat not in cats:
            self._oracle_selected_cat = "All"
            self._oracle_cat_var.set("All")
        self._refresh_oracle_list()

    def _on_oracle_cat_change(self: "App") -> None:
        self._oracle_selected_cat = self._oracle_cat_var.get()
        self._refresh_oracle_list()

    def _refresh_oracle_list(self: "App") -> None:
        game_filter = self._oracle_game_var.get() or "All"
        cat_filter = self._oracle_selected_cat
        query = self._oracle_search_var.get().strip().lower()
        all_oracles = self._sf_oracles + self._si_oracles + self._is_oracles
        filtered = [
            o for o in all_oracles
            if (game_filter == "All" or o["source"] == game_filter)
            and (cat_filter == "All" or o["category"] == cat_filter)
            and (not query
                 or query in o["name"].lower()
                 or query in o["category"].lower()
                 or query in o["source"].lower())
        ]
        filtered.sort(key=lambda o: (o["source"], o["category"], o["name"]))
        self._oracles_visible = filtered
        self._oracle_listbox.delete(0, tk.END)
        for o in filtered:
            label = f"[{self._short_source(o['source'])}]  {o['category']} › {o['name']}"
            self._oracle_listbox.insert(tk.END, label)

    # ------------------------------------------------------------------
    # Selection & display
    # ------------------------------------------------------------------

    def _on_oracle_select(self: "App", _event: tk.Event) -> None:  # type: ignore[type-arg]
        selection = self._oracle_listbox.curselection()
        if not selection:
            return
        oracle = self._oracles_visible[selection[0]]
        self._current_oracle = oracle
        self._roll_result_var.set("")
        self._display_oracle(oracle)

    def _display_oracle(
        self: "App",
        oracle: dict[str, Any],
        highlight_roll: int | None = None,
        cursed: bool = False,
    ) -> None:
        name = ("☠  " + oracle["name"]) if cursed else oracle["name"]
        self._oracle_title_var.set(f"{name}  —  {oracle['category']}")
        src_label = oracle["source"] + "  ·  " + oracle["category"]
        if cursed:
            src_label += "  [☠ CURSED]"
        lines: list[tuple[str, str]] = [("miss" if cursed else "cat", src_label), ("body", "")]
        for row in oracle.get("rows", []):
            rmin, rmax, text = row.get("min"), row.get("max"), row.get("text", "")
            if rmin is None or rmax is None:
                range_str = "    –   "
            elif rmin != rmax:
                range_str = f"{rmin:>3}–{rmax:<3}"
            else:
                range_str = f"{rmin:>3}      "
            tag = "body"
            if highlight_roll is not None and rmin is not None and rmax is not None:
                if rmin <= highlight_roll <= rmax:
                    tag = "strong"
            lines.append((tag, f"  {range_str}  {text}"))
        set_text_lines(self._oracle_text, lines)

    def _roll_oracle(self: "App") -> None:
        if self._current_oracle is None:
            return
        roll = random.randint(1, 100)
        cursed = False
        cursed_roll_str = ""
        if self._cursed_enabled_var.get() and self._current_oracle.get("cursed_version"):
            die_str = self._cursed_die_var.get()
            die_sides = int(die_str[1:])
            cursed_roll = random.randint(1, die_sides)
            cursed = cursed_roll == die_sides
            cursed_roll_str = f"  |  ☠ {die_str}: {cursed_roll}{'  → CURSED!' if cursed else ''}"
        display_oracle = self._current_oracle
        if cursed:
            co = self._oracle_by_id.get(self._current_oracle["cursed_version"])
            if co:
                display_oracle = co
        matching = next(
            (row["text"] for row in display_oracle.get("rows", [])
             if row.get("min") is not None and row["min"] <= roll <= row["max"]),
            ""
        )
        self._roll_result_var.set(f"Rolled {roll}  →  {matching}{cursed_roll_str}")
        self._display_oracle(display_oracle, highlight_roll=roll, cursed=cursed)
