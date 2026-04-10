"""tabs/dice.py - Action roll tab mixin."""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk
from typing import Any

from widgets import make_option_menu, make_textbox, set_text_lines


class DiceTabMixin:

    _STAT_VALUES = [str(value) for value in range(-3, 6)]

    def _build_dice_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        controls = ttk.Frame(parent, style="Panel.TFrame")
        controls.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 4))
        controls.columnconfigure(4, weight=1)

        ttk.Label(controls, text="Bonus", style="Cat.TLabel").grid(
            row=0, column=0, sticky="w", padx=(8, 4), pady=(8, 2)
        )
        self._dice_stat_value_var = tk.StringVar(value="2")
        self._dice_stat_value_om = make_option_menu(controls, self._dice_stat_value_var, self._STAT_VALUES, width=4)
        self._dice_stat_value_om.grid(row=1, column=0, sticky="w", padx=(8, 8), pady=(0, 8))

        ttk.Button(
            controls,
            text="Roll Action",
            style="Accent.TButton",
            command=self._roll_from_dice_tab,
        ).grid(row=1, column=1, sticky="w", padx=(8, 8), pady=(0, 8))

        ttk.Button(
            controls,
            text="Clear",
            command=self._reset_dice_tab,
        ).grid(row=1, column=2, sticky="w", padx=(0, 8), pady=(0, 8))

        self._dice_summary_var = tk.StringVar(value="Action roll ready")
        ttk.Label(controls, textvariable=self._dice_summary_var, style="Title.TLabel").grid(
            row=1, column=3, columnspan=2, sticky="w", padx=(8, 8), pady=(0, 8)
        )

        self._dice_text = make_textbox(parent)
        self._dice_text.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))

        self._reset_dice_tab()

    def _show_dice_placeholder(self) -> None:
        set_text_lines(
            self._dice_text,
            [
                ("cat", "Action Roll"),
                ("body", ""),
                ("body", "Choose a stat bonus and roll against two challenge dice."),
                ("body", "Future move integration can reuse the same roll method."),
            ],
        )

    def _reset_dice_tab(self) -> None:
        self._dice_summary_var.set("Action roll ready")
        self._show_dice_placeholder()

    def _roll_action_vs_challenge(self, stat_value: int) -> dict[str, Any]:
        action_die = random.randint(1, 6)
        challenge_1 = random.randint(1, 10)
        challenge_2 = random.randint(1, 10)
        score = action_die + stat_value
        beats_1 = score > challenge_1
        beats_2 = score > challenge_2
        if beats_1 and beats_2:
            outcome = "Strong Hit"
            outcome_tag = "strong"
        elif beats_1 or beats_2:
            outcome = "Weak Hit"
            outcome_tag = "weak"
        else:
            outcome = "Miss"
            outcome_tag = "miss"
        return {
            "action_die": action_die,
            "stat_value": stat_value,
            "score": score,
            "challenge_1": challenge_1,
            "challenge_2": challenge_2,
            "outcome": outcome,
            "outcome_tag": outcome_tag,
            "is_match": challenge_1 == challenge_2,
        }

    def _roll_from_dice_tab(self) -> None:
        stat_value = int(self._dice_stat_value_var.get())
        result = self._roll_action_vs_challenge(stat_value)
        match_text = "Match on the challenge dice." if result["is_match"] else "No match."
        self._dice_summary_var.set(
            f"{result['outcome']}  |  {result['score']} vs {result['challenge_1']}/{result['challenge_2']}"
        )
        score_expr = f"{result['action_die']} {stat_value:+d}" if stat_value < 0 else f"{result['action_die']} + {stat_value}"

        lines: list[tuple[str, str]] = [
            ("cat", "Action roll"),
            ("body", ""),
            ("bold", f"Action die: d6 → {result['action_die']}"),
            ("body", f"Stat bonus: {stat_value:+d}"),
            ("body", f"Action score: {score_expr} = {result['score']}"),
            ("body", ""),
            ("bold", f"Challenge dice: d10 → {result['challenge_1']} and {result['challenge_2']}"),
            (result["outcome_tag"], result["outcome"]),
            ("cat" if result["is_match"] else "body", match_text),
        ]
        set_text_lines(self._dice_text, lines)
