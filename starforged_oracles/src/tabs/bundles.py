"""tabs/bundles.py – Bundles tab mixin."""
from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk
from typing import Any, TYPE_CHECKING

from styles import ACCENT, BG, BORDER, FG, HIT_MISS, PANEL_BG
from widgets import (
    make_listbox_frame, make_option_menu, make_paned, make_textbox, rebuild_option_menu,
    set_text_lines,
)

if TYPE_CHECKING:
    from starforged_app import App


class BundlesTabMixin:

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_bundles_tab(self, parent: ttk.Frame) -> None:
        paned = make_paned(parent)

        # --- Left panel ---
        left = ttk.Frame(paned, style="Panel.TFrame")
        left.rowconfigure(3, weight=1)
        left.columnconfigure(0, weight=1)
        paned.add(left, minsize=160, width=230)

        ttk.Label(left, text="Game", style="Cat.TLabel").grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 2)
        )
        all_games = sorted({b["game"] for b in self._bundles if b.get("game")})
        self._bundle_game_var = tk.StringVar(value="All")
        self._bundle_game_var.trace_add("write", lambda *_: self._refresh_bundle_list())
        make_option_menu(left, self._bundle_game_var, ["All"] + all_games).grid(
            row=1, column=0, sticky="ew", padx=8, pady=(0, 8)
        )

        ttk.Label(left, text="Bundles", style="Cat.TLabel").grid(
            row=2, column=0, sticky="w", padx=8, pady=(0, 2)
        )

        lf, self._bundle_listbox = make_listbox_frame(left)
        lf.grid(row=3, column=0, sticky="nsew", padx=4, pady=4)
        self._bundle_listbox.bind("<<ListboxSelect>>", self._on_bundle_select)

        # --- Right panel ---
        right = ttk.Frame(paned, style="Panel.TFrame")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)
        paned.add(right, minsize=200)

        title_bar = ttk.Frame(right, style="Panel.TFrame")
        title_bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(10, 2))
        self._bundle_title_var = tk.StringVar(value="Select a bundle →")
        ttk.Label(title_bar, textvariable=self._bundle_title_var, style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        roll_bar = ttk.Frame(right, style="Panel.TFrame")
        roll_bar.grid(row=1, column=0, sticky="ew", padx=6, pady=(2, 4))

        ttk.Button(
            roll_bar, text="Roll All", style="Accent.TButton",
            command=self._roll_bundle,
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        _CURSE_DIM = "#4a4a5a"
        self._bundle_cursed_var = tk.BooleanVar(value=False)
        self._bundle_cursed_chk = tk.Checkbutton(
            roll_bar, text="☠ Cursed Die",
            variable=self._bundle_cursed_var,
            bg=PANEL_BG, fg=_CURSE_DIM, selectcolor=PANEL_BG,
            activebackground=PANEL_BG, activeforeground=_CURSE_DIM,
            disabledforeground=_CURSE_DIM,
            font=("Segoe UI", 9), relief="flat", bd=0, highlightthickness=0,
            state="disabled",
        )
        self._bundle_cursed_chk.grid(row=0, column=1, sticky="w", padx=(0, 6))

        self._bundle_cursed_die_var = tk.StringVar(value="d10")
        self._bundle_cursed_die_om = tk.OptionMenu(roll_bar, self._bundle_cursed_die_var, "d10", "d12", "d20")
        self._bundle_cursed_die_om.config(bg=PANEL_BG, fg=_CURSE_DIM, activebackground=PANEL_BG, activeforeground=_CURSE_DIM,
                      highlightthickness=0, relief="flat", width=4, state="disabled")
        self._bundle_cursed_die_om["menu"].config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG)
        self._bundle_cursed_die_om.grid(row=0, column=2, sticky="w")

        # Region selector — shown only for bundles whose game has regional tables
        region_frame = ttk.Frame(roll_bar, style="Panel.TFrame")
        region_frame.grid(row=0, column=3, sticky="w", padx=(16, 0))
        ttk.Label(region_frame, text="Region:", style="Cat.TLabel").pack(side="left", padx=(0, 4))
        self._bundle_region_var = tk.StringVar(value="")
        self._bundle_region_var.trace_add("write", self._on_region_change)
        self._bundle_region_om = make_option_menu(region_frame, self._bundle_region_var, ["—"], width=12)
        self._bundle_region_om.pack(side="left")
        self._bundle_region_frame = region_frame
        self._bundle_region_frame.grid_remove()

        self._bundle_text = make_textbox(right)
        self._bundle_text.grid(row=2, column=0, sticky="nsew", padx=4, pady=(0, 4))

        self._current_bundle: dict[str, Any] | None = None
        self._bundles_visible: list[dict[str, Any]] = []
        self._refresh_bundle_list()

    # ------------------------------------------------------------------
    # Curse UI state
    # ------------------------------------------------------------------

    def _update_bundle_curse_ui(self) -> None:
        _CURSE_DIM = "#4a4a5a"
        bundle = self._current_bundle
        has_curse = bool(
            bundle and any(item.get("cursed_oracle_id") for item in bundle.get("rolls", []))
        )
        if has_curse:
            self._bundle_cursed_var.set(True)
            self._bundle_cursed_chk.config(
                state="normal", fg=HIT_MISS, activeforeground=HIT_MISS,
            )
            self._bundle_cursed_die_om.config(
                state="normal", fg=HIT_MISS, activeforeground=HIT_MISS,
            )
        else:
            self._bundle_cursed_var.set(False)
            self._bundle_cursed_chk.config(
                state="disabled", fg=_CURSE_DIM, activeforeground=_CURSE_DIM,
            )
            self._bundle_cursed_die_om.config(
                state="disabled", fg=_CURSE_DIM, activeforeground=_CURSE_DIM,
            )

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _refresh_bundle_list(self) -> None:
        game_filter = self._bundle_game_var.get() or "All"
        self._bundles_visible = [
            b for b in self._bundles
            if game_filter == "All" or b.get("game") == game_filter
        ]
        self._bundle_listbox.delete(0, tk.END)
        for b in self._bundles_visible:
            game_tag = f"[{self._short_source(b.get('game', ''))}]  " if b.get("game") else ""
            self._bundle_listbox.insert(tk.END, game_tag + b.get("name", ""))

    # ------------------------------------------------------------------
    # Selection & preview
    # ------------------------------------------------------------------

    def _on_bundle_select(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        selection = self._bundle_listbox.curselection()
        if not selection:
            return
        self._current_bundle = self._bundles_visible[selection[0]]
        bundle = self._current_bundle
        if bundle is None:
            return
        self._update_bundle_curse_ui()
        self._update_bundle_region_ui()
        self._bundle_title_var.set(bundle.get("name", ""))
        lines: list[tuple[str, str]] = [
            ("cat", f"{bundle.get('game', '')}  —  {len(bundle.get('rolls', []))} roll steps"),
            ("body", ""),
        ]
        for item in bundle.get("rolls", []):
            label = item.get("label", "?")
            extras = []
            if item.get("count", 1) > 1:
                extras.append(f"×{item['count']}")
            if item.get("cursed_oracle_id"):
                extras.append("☠")
            if item.get("cascade_from"):
                extras.append(f"→ based on {item['cascade_from']}")
            suffix = "  " + "  ".join(extras) if extras else ""
            lines.append(("bold", f"  {label}{suffix}"))
            if item.get("note"):
                lines.append(("cat", f"    ↳ {item['note']}"))
        set_text_lines(self._bundle_text, lines)

    # ------------------------------------------------------------------
    # Region UI state
    # ------------------------------------------------------------------

    def _update_bundle_region_ui(self) -> None:
        bundle = self._current_bundle
        if bundle is None:
            self._bundle_region_frame.grid_remove()
            return
        game = bundle.get("game", "")
        regions: list[str] = self._game_regions.get(game, [])
        has_regions = bool(regions) and any(
            item.get("region_map") for item in bundle.get("rolls", [])
        )
        if has_regions:
            current = self._settings.get("regions", {}).get(game, regions[0])
            rebuild_option_menu(self._bundle_region_om, self._bundle_region_var, regions)
            self._bundle_region_var.set(current if current in regions else regions[0])
            self._bundle_region_frame.grid()
        else:
            self._bundle_region_frame.grid_remove()

    def _on_region_change(self, *_: Any) -> None:
        bundle = self._current_bundle
        if bundle is None:
            return
        game = bundle.get("game", "")
        region = self._bundle_region_var.get()
        if not game or not region:
            return
        self._set_region_setting(game, region)

    # ------------------------------------------------------------------
    # Rolling
    # ------------------------------------------------------------------

    def _roll_bundle(self) -> None:
        if self._current_bundle is None:
            return

        use_cursed = self._bundle_cursed_var.get()
        die_str = self._bundle_cursed_die_var.get()
        die_sides = int(die_str[1:])

        lines: list[tuple[str, str]] = [
            ("cat", self._current_bundle.get("name", "") + "  —  " + self._current_bundle.get("game", "")),
            ("body", ""),
        ]
        label_results: dict[str, str] = {}

        for item in self._current_bundle.get("rolls", []):
            label = item.get("label", "?")
            count = item.get("count", 1)
            note = item.get("note", "")

            # Resolve oracle (region map, direct, or cascade)
            oracle_id = item.get("oracle_id", "")
            region_label = ""
            if item.get("region_map"):
                region = self._bundle_region_var.get()
                oracle_id = (item.get("region_map") or {}).get(region, "")
                region_label = f" ({region})"
                if not oracle_id:
                    lines += [
                        ("bold", f"  {label}"),
                        ("miss", f"    [No region oracle for {region!r}]"),
                        ("body", ""),
                    ]
                    continue
            elif item.get("cascade_from"):
                source_text = label_results.get(item["cascade_from"], "")
                cascade_map: dict[str, str] = item.get("cascade_map") or {}
                oracle_id = cascade_map.get(source_text, "")
                if not oracle_id:
                    for key, val in cascade_map.items():
                        if source_text.startswith(key):
                            oracle_id = val
                            break
                if not oracle_id:
                    lines += [
                        ("bold", f"  {label}"),
                        ("miss", f"    [No cascade match for {item['cascade_from']}={source_text!r}]"),
                        ("body", ""),
                    ]
                    continue

            oracle = self._oracle_by_id.get(oracle_id)
            if oracle is None:
                lines += [
                    ("bold", f"  {label}"),
                    ("miss", f"    [Oracle not found: {oracle_id}]"),
                    ("body", ""),
                ]
                continue

            cursed_oracle_id = item.get("cursed_oracle_id", "")

            for roll_num in range(count):
                roll = random.randint(1, 100)
                roll_label = label if count == 1 else f"{label} #{roll_num + 1}"

                cursed = False
                cursed_suffix = ""
                if use_cursed and cursed_oracle_id:
                    cursed_roll = random.randint(1, die_sides)
                    cursed = cursed_roll == die_sides
                    cursed_suffix = f"  ☠{die_str}:{cursed_roll}" + ("→CURSED" if cursed else "")

                active_oracle = oracle
                if cursed:
                    co = self._oracle_by_id.get(cursed_oracle_id)
                    if co:
                        active_oracle = co

                result_text = next(
                    (row["text"] for row in active_oracle.get("rows", [])
                     if row.get("min") is not None and row["min"] <= roll <= row["max"]),
                    ""
                )

                if roll_num == 0:
                    label_results[label] = result_text

                if cursed:
                    lines.append(("miss", f"  {roll_label}{region_label}  [{roll}]{cursed_suffix}"))
                    lines.append(("strong", "      \u2620 " + result_text.replace("\n", "\n        ")))
                else:
                    lines.append(("bold", f"  {roll_label}{region_label}  [{roll}]"))
                    lines.append(("body", "    " + result_text.replace("\n", "\n    ")))

            if note:
                lines.append(("cat", f"    ↳ {note}"))
            lines.append(("body", ""))

        set_text_lines(self._bundle_text, lines)
