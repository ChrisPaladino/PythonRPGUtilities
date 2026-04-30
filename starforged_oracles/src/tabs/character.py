"""tabs/character.py - Character tab mixin."""
from __future__ import annotations

import copy
import random
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, TYPE_CHECKING
from uuid import uuid4

from loader import save_characters, save_settings
from styles import ACCENT2, BORDER, FG, PANEL_BG
from widgets import make_listbox_frame, make_option_menu

if TYPE_CHECKING:
    from starforged_app import App


class CharacterTabMixin:

    _DIFFICULTIES = ["Troublesome", "Dangerous", "Formidable", "Extreme", "Epic"]
    _DIFFICULTY_MILESTONE_TICKS = {
        "Troublesome": 12,
        "Dangerous": 8,
        "Formidable": 4,
        "Extreme": 2,
        "Epic": 1,
    }

    if TYPE_CHECKING:
        _characters: list[dict[str, Any]]
        _settings: dict[str, Any]

        def _short_source(self, source: str) -> str: ...

    _TRACK_FONT = ("Consolas", 9)

    def _build_character_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        self._character_id: str | None = None
        self._character_selected_index: int | None = None
        self._character_picker_values: list[str] = []
        self._character_autosave_after_id: str | None = None
        self._suspend_character_autosave = False

        self._char_name_var = tk.StringVar(value="")
        self._char_game_value = "Starforged"
        self._char_stat_vars = {
            "edge": tk.IntVar(value=1),
            "heart": tk.IntVar(value=1),
            "iron": tk.IntVar(value=1),
            "shadow": tk.IntVar(value=1),
            "wits": tk.IntVar(value=1),
        }
        self._char_condition_vars = {
            "health": tk.IntVar(value=5),
            "spirit": tk.IntVar(value=5),
            "supply": tk.IntVar(value=5),
            "momentum": tk.IntVar(value=2),
            "max_momentum": tk.IntVar(value=10),
            "momentum_reset": tk.IntVar(value=2),
        }
        self._char_xp_vars = {
            "quests": tk.IntVar(value=0),
            "bonds": tk.IntVar(value=0),
            "discoveries": tk.IntVar(value=0),
        }
        self._xp_display_vars = {
            "quests": tk.StringVar(value=""),
            "bonds": tk.StringVar(value=""),
            "discoveries": tk.StringVar(value=""),
        }

        self._asset_lookup: dict[str, dict[str, Any]] = {}
        self._asset_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
        self._all_asset_labels = self._build_asset_labels()
        self._asset_filtered_labels: list[str] = list(self._all_asset_labels)
        self._char_assets_selected: list[dict[str, Any]] = []

        self._char_progress_tracks: list[dict[str, Any]] = []
        self._char_track_name_var = tk.StringVar(value="")
        self._char_track_diff_var = tk.StringVar(value=self._DIFFICULTIES[0])
        self._momentum_track_var = tk.StringVar(value="")

        header = ttk.Frame(parent, style="Panel.TFrame", padding=8)
        header.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 4))
        header.columnconfigure(3, weight=1)

        self._character_title_var = tk.StringVar(value="Character")
        ttk.Label(header, textvariable=self._character_title_var, style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )

        ttk.Label(header, text="Character", style="Cat.TLabel").grid(
            row=0, column=1, sticky="w", padx=(0, 6)
        )
        self._character_picker_var = tk.StringVar(value="")
        self._character_picker = ttk.Combobox(
            header,
            textvariable=self._character_picker_var,
            state="readonly",
            width=34,
        )
        self._character_picker.grid(row=0, column=2, sticky="w", padx=(0, 8))
        self._character_picker.bind("<<ComboboxSelected>>", self._on_character_picker_select)

        actions_menu_btn = ttk.Menubutton(header, text="Character Menu")
        actions_menu_btn.grid(row=0, column=4, sticky="e")
        self._character_menu = tk.Menu(actions_menu_btn, tearoff=0)
        self._character_menu.add_command(label="New Character", command=self._new_character)
        self._character_menu.add_separator()
        self._character_menu.add_command(label="Delete Character", command=self._delete_selected_character)
        actions_menu_btn.configure(menu=self._character_menu)

        body = ttk.Notebook(parent)
        body.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))

        sheet_tab = ttk.Frame(body)
        assets_tab = ttk.Frame(body)
        progress_tab = ttk.Frame(body)
        body.add(sheet_tab, text="  Sheet  ")
        body.add(assets_tab, text="  Assets  ")
        body.add(progress_tab, text="  Progress  ")

        self._build_sheet_subtab(sheet_tab)
        self._build_assets_subtab(assets_tab)
        self._build_progress_subtab(progress_tab)

        self._configure_character_autosave()

        self._refresh_character_picker()
        self._load_initial_character()

    def _build_sheet_subtab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)

        panel = ttk.Frame(parent, style="Panel.TFrame", padding=10)
        panel.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        for col in range(6):
            panel.columnconfigure(col, weight=1)

        ttk.Label(panel, text="Name", style="Cat.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 2)
        )
        ttk.Entry(panel, textvariable=self._char_name_var).grid(
            row=1, column=0, columnspan=4, sticky="ew", padx=(0, 8), pady=(0, 8)
        )

        ttk.Label(panel, text="Stats", style="Cat.TLabel").grid(
            row=2, column=0, sticky="w", pady=(0, 2)
        )

        stat_row = 3
        for col, (name, var) in enumerate(self._char_stat_vars.items()):
            ttk.Label(panel, text=name.title()).grid(row=stat_row, column=col, sticky="w")
            tk.Spinbox(
                panel,
                from_=0,
                to=5,
                width=4,
                textvariable=var,
                justify="center",
            ).grid(row=stat_row + 1, column=col, sticky="w", padx=(0, 4), pady=(0, 8))
            ttk.Button(
                panel,
                text="Roll",
                command=lambda n=name, v=var: self._roll_with_bonus(n.title(), int(v.get())),
            ).grid(row=stat_row + 1, column=col, sticky="e", padx=(0, 8), pady=(0, 8))

        ttk.Label(panel, text="Condition", style="Cat.TLabel").grid(
            row=5, column=0, columnspan=6, sticky="w", pady=(0, 2)
        )
        self._add_meter_with_roll(panel, "Health", self._char_condition_vars["health"], 6, 0, 5)
        self._add_meter_with_roll(panel, "Spirit", self._char_condition_vars["spirit"], 6, 1, 5)
        self._add_meter_with_roll(panel, "Supply", self._char_condition_vars["supply"], 6, 2, 5)

        ttk.Label(panel, text="Momentum", style="Cat.TLabel").grid(
            row=8, column=0, columnspan=6, sticky="w", pady=(6, 2)
        )
        ttk.Label(panel, text="Momentum").grid(row=9, column=0, sticky="w")
        tk.Spinbox(
            panel,
            from_=-6,
            to=10,
            width=5,
            textvariable=self._char_condition_vars["momentum"],
            justify="center",
        ).grid(row=10, column=0, sticky="w", padx=(0, 8), pady=(0, 8))

        ttk.Label(panel, text="Momentum Reset").grid(row=9, column=1, sticky="w")
        tk.Spinbox(
            panel,
            from_=-6,
            to=10,
            width=5,
            textvariable=self._char_condition_vars["momentum_reset"],
            justify="center",
        ).grid(row=10, column=1, sticky="w", padx=(0, 8), pady=(0, 8))

        tk.Label(
            panel,
            textvariable=self._momentum_track_var,
            bg=PANEL_BG,
            fg=FG,
            anchor="w",
            font=self._TRACK_FONT,
            justify="left",
        ).grid(row=10, column=2, columnspan=4, sticky="w", padx=(0, 8), pady=(0, 8))
        self._char_condition_vars["momentum"].trace_add("write", lambda *_: self._refresh_momentum_display())
        self._refresh_momentum_display()

    def _build_assets_subtab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        tools = ttk.Frame(parent, style="Panel.TFrame", padding=8)
        tools.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 2))
        tools.columnconfigure(1, weight=1)

        ttk.Label(tools, text="Assets", style="Cat.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 8))
        assets_menu_btn = ttk.Menubutton(tools, text="Asset Menu")
        assets_menu_btn.grid(row=0, column=2, sticky="e")
        assets_menu = tk.Menu(assets_menu_btn, tearoff=0)
        assets_menu.add_command(label="Add Asset...", command=self._open_asset_library_dialog)
        assets_menu.add_command(label="Clear All Assets", command=self._clear_all_assets)
        assets_menu_btn.configure(menu=assets_menu)

        cards_wrap = ttk.Frame(parent, style="Panel.TFrame", padding=8)
        cards_wrap.grid(row=1, column=0, sticky="nsew", padx=4, pady=(2, 4))
        cards_wrap.columnconfigure(0, weight=1)
        cards_wrap.rowconfigure(0, weight=1)

        self._asset_cards_canvas = tk.Canvas(
            cards_wrap,
            highlightthickness=1,
            highlightbackground=BORDER,
            bg=PANEL_BG,
            bd=0,
        )
        self._asset_cards_canvas.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(cards_wrap, orient="vertical", command=self._asset_cards_canvas.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self._asset_cards_canvas.configure(yscrollcommand=scroll.set)

        self._asset_cards_inner = ttk.Frame(self._asset_cards_canvas, style="Panel.TFrame")
        self._asset_cards_canvas.create_window((0, 0), window=self._asset_cards_inner, anchor="nw")
        self._asset_cards_inner.bind(
            "<Configure>",
            lambda _e: self._asset_cards_canvas.configure(scrollregion=self._asset_cards_canvas.bbox("all")),
        )

        self._render_asset_cards()

    def _build_progress_subtab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        panel = ttk.Frame(parent, style="Panel.TFrame", padding=10)
        panel.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        panel.columnconfigure(1, weight=1)
        panel.rowconfigure(7, weight=1)

        ttk.Label(panel, text="XP Tracks", style="Cat.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )
        self._build_xp_row(panel, "Quests", "quests", 1)
        self._build_xp_row(panel, "Bonds", "bonds", 2)
        self._build_xp_row(panel, "Discovery", "discoveries", 3)

        ttk.Separator(panel, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=8
        )

        ttk.Label(panel, text="Progress Tracks", style="Cat.TLabel").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )

        editor = ttk.Frame(panel, style="Panel.TFrame")
        editor.grid(row=6, column=0, columnspan=2, sticky="ew")
        editor.columnconfigure(0, weight=1)

        ttk.Entry(editor, textvariable=self._char_track_name_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 6), pady=(0, 4)
        )
        make_option_menu(editor, self._char_track_diff_var, self._DIFFICULTIES, width=14).grid(
            row=0, column=1, sticky="w", padx=(0, 6), pady=(0, 4)
        )
        ttk.Button(editor, text="Add Track", command=self._add_progress_track).grid(
            row=0, column=2, sticky="ew", padx=2
        )

        tracks_wrap = ttk.Frame(panel, style="Panel.TFrame")
        tracks_wrap.grid(row=7, column=0, columnspan=2, sticky="nsew", pady=(6, 0))
        tracks_wrap.columnconfigure(0, weight=1)
        tracks_wrap.rowconfigure(0, weight=1)

        self._progress_canvas = tk.Canvas(
            tracks_wrap,
            highlightthickness=1,
            highlightbackground=BORDER,
            bg=PANEL_BG,
            bd=0,
        )
        self._progress_canvas.grid(row=0, column=0, sticky="nsew")
        p_scroll = ttk.Scrollbar(tracks_wrap, orient="vertical", command=self._progress_canvas.yview)
        p_scroll.grid(row=0, column=1, sticky="ns")
        self._progress_canvas.configure(yscrollcommand=p_scroll.set)

        self._progress_rows = ttk.Frame(self._progress_canvas, style="Panel.TFrame")
        self._progress_canvas.create_window((0, 0), window=self._progress_rows, anchor="nw")
        self._progress_rows.bind(
            "<Configure>",
            lambda _e: self._progress_canvas.configure(scrollregion=self._progress_canvas.bbox("all")),
        )

        self._refresh_xp_display()
        self._refresh_progress_tracks_rows()

    def _build_xp_row(self, parent: ttk.Frame, label: str, key: str, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=2)

        row_wrap = ttk.Frame(parent, style="Panel.TFrame")
        row_wrap.grid(row=row, column=1, sticky="ew", pady=2)
        row_wrap.columnconfigure(0, weight=1)

        tk.Label(
            row_wrap,
            textvariable=self._xp_display_vars[key],
            bg=PANEL_BG,
            fg=FG,
            anchor="w",
            justify="left",
            font=self._TRACK_FONT,
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Button(row_wrap, text="-1 Tick", command=lambda k=key: self._adjust_xp(k, -1)).grid(row=0, column=1, padx=1)
        ttk.Button(row_wrap, text="+1 Tick", command=lambda k=key: self._adjust_xp(k, 1)).grid(row=0, column=2, padx=1)
        ttk.Button(row_wrap, text="-1 Box", command=lambda k=key: self._adjust_xp(k, -4)).grid(row=0, column=3, padx=1)
        ttk.Button(row_wrap, text="+1 Box", command=lambda k=key: self._adjust_xp(k, 4)).grid(row=0, column=4, padx=1)

    def _add_meter_with_roll(
        self,
        parent: ttk.Frame,
        label: str,
        var: tk.IntVar,
        row: int,
        column: int,
        max_value: int,
        min_value: int = 0,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w")
        tk.Spinbox(
            parent,
            from_=min_value,
            to=max_value,
            width=5,
            textvariable=var,
            justify="center",
        ).grid(row=row + 1, column=column, sticky="w", padx=(0, 4), pady=(0, 8))
        ttk.Button(
            parent,
            text="Roll",
            command=lambda lbl=label, v=var: self._roll_with_bonus(lbl, int(v.get())),
        ).grid(row=row + 1, column=column, sticky="e", padx=(0, 8), pady=(0, 8))

    def _add_meter_spin(
        self,
        parent: ttk.Frame,
        label: str,
        var: tk.IntVar,
        row: int,
        column: int,
        max_value: int,
        min_value: int = 0,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w")
        tk.Spinbox(
            parent,
            from_=min_value,
            to=max_value,
            width=5,
            textvariable=var,
            justify="center",
        ).grid(row=row + 1, column=column, sticky="w", padx=(0, 8), pady=(0, 8))

    def _build_asset_labels(self) -> list[str]:
        self._asset_lookup = {}
        self._asset_by_key = {}
        labels = []
        all_assets = (
            getattr(self, "_sf_assets", [])
            + getattr(self, "_si_assets", [])
            + getattr(self, "_is_assets", [])
        )
        for asset in sorted(all_assets, key=lambda a: (a["source"], a["category"], a["name"])):
            label = f"[{self._short_source(asset['source'])}] {asset['category']} - {asset['name']}"
            labels.append(label)
            payload = {
                "source": asset["source"],
                "category": asset["category"],
                "name": asset["name"],
                "abilities": list(asset.get("abilities", []))[:3],
            }
            self._asset_lookup[label] = payload
            self._asset_by_key[(payload["source"], payload["category"], payload["name"])] = payload
        return labels

    def _refresh_asset_search_list(self, query_text: str = "") -> None:
        query = query_text.strip().lower()
        if not query:
            filtered = list(self._all_asset_labels)
        else:
            filtered = []
            for label in self._all_asset_labels:
                entry = self._asset_lookup.get(label, {})
                haystack = " ".join(
                    [
                        label.lower(),
                        str(entry.get("name", "")).lower(),
                        str(entry.get("category", "")).lower(),
                        str(entry.get("source", "")).lower(),
                    ]
                )
                if query in haystack:
                    filtered.append(label)

        self._asset_filtered_labels = filtered

    def _configure_character_autosave(self) -> None:
        for var in [self._char_name_var, *self._char_stat_vars.values(), *self._char_condition_vars.values(), *self._char_xp_vars.values()]:
            var.trace_add("write", lambda *_: self._queue_character_autosave())

    def _queue_character_autosave(self) -> None:
        if self._suspend_character_autosave:
            return
        if self._character_autosave_after_id is not None:
            self.after_cancel(self._character_autosave_after_id)
        self._character_autosave_after_id = self.after(250, self._autosave_character)

    def _autosave_character(self) -> None:
        self._character_autosave_after_id = None
        self._save_character_from_form(update_title=True)

    def _open_asset_library_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Add Asset")
        dialog.geometry("620x420")
        dialog.configure(bg=PANEL_BG)
        dialog.transient(self)
        dialog.grab_set()

        frame = ttk.Frame(dialog, style="Panel.TFrame", padding=10)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        ttk.Label(frame, text="Search Assets", style="Cat.TLabel").grid(row=0, column=0, sticky="w")
        search_var = tk.StringVar(value="")
        entry = ttk.Entry(frame, textvariable=search_var)
        entry.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        lf_assets, search_listbox = make_listbox_frame(frame)
        lf_assets.grid(row=2, column=0, sticky="nsew", pady=(0, 6))

        def repopulate() -> None:
            self._refresh_asset_search_list(search_var.get())
            search_listbox.delete(0, tk.END)
            for label in self._asset_filtered_labels:
                search_listbox.insert(tk.END, label)

        def add_selected() -> None:
            selection = search_listbox.curselection()
            if not selection:
                messagebox.showinfo("Assets", "Select an asset to add.", parent=dialog)
                return
            self._add_asset_by_label(self._asset_filtered_labels[selection[0]], parent_dialog=dialog)

        search_var.trace_add("write", lambda *_: repopulate())
        repopulate()

        btns = ttk.Frame(frame, style="Panel.TFrame")
        btns.grid(row=3, column=0, sticky="e")
        ttk.Button(btns, text="Add", style="Accent.TButton", command=add_selected).grid(row=0, column=0, padx=2)
        ttk.Button(btns, text="Close", command=dialog.destroy).grid(row=0, column=1, padx=2)
        entry.focus_set()

    def _add_asset_by_label(self, label: str, parent_dialog: tk.Misc | None = None) -> None:
        if not label:
            return
        if len(self._char_assets_selected) >= 3:
            messagebox.showinfo(
                "Assets",
                "A character can currently hold up to 3 assets.",
                parent=parent_dialog,
            )
            return
        asset = self._asset_lookup.get(label)
        if not asset:
            return

        existing_keys = {
            (a.get("source", ""), a.get("category", ""), a.get("name", ""))
            for a in self._char_assets_selected
        }
        key = (asset["source"], asset["category"], asset["name"])
        if key in existing_keys:
            messagebox.showinfo("Assets", "That asset is already on this character.", parent=parent_dialog)
            return

        self._char_assets_selected.append(
            {
                "source": asset["source"],
                "category": asset["category"],
                "name": asset["name"],
                "abilities_used": [False, False, False],
            }
        )
        self._render_asset_cards()
        self._queue_character_autosave()

    def _clear_all_assets(self) -> None:
        if not self._char_assets_selected:
            return
        if not messagebox.askyesno("Assets", "Remove all assets from this character?"):
            return
        self._char_assets_selected = []
        self._render_asset_cards()
        self._queue_character_autosave()

    def _render_asset_cards(self) -> None:
        if not hasattr(self, "_asset_cards_inner"):
            return

        for child in self._asset_cards_inner.winfo_children():
            child.destroy()

        if not self._char_assets_selected:
            ttk.Label(
                self._asset_cards_inner,
                text="No assets selected. Search and add an asset to create a card.",
                style="Body.TLabel",
                wraplength=520,
                justify="left",
            ).grid(row=0, column=0, sticky="w", padx=2, pady=2)
            return

        for idx, asset in enumerate(self._char_assets_selected):
            title = f"{asset.get('name', 'Asset')}  -  {asset.get('category', '')}"
            card = tk.Frame(
                self._asset_cards_inner,
                bg=PANEL_BG,
                highlightthickness=1,
                highlightbackground=BORDER,
                padx=8,
                pady=8,
            )
            card.grid(row=idx, column=0, sticky="ew", padx=2, pady=4)
            card.columnconfigure(0, weight=1)

            tk.Label(
                card,
                text=title,
                bg=PANEL_BG,
                fg=ACCENT2,
                anchor="w",
                font=("Segoe UI", 10, "bold"),
            ).grid(row=0, column=0, sticky="w", pady=(0, 2))

            tk.Label(
                card,
                text=asset.get("source", ""),
                bg=PANEL_BG,
                fg=FG,
                anchor="w",
                font=("Segoe UI", 9, "italic"),
            ).grid(
                row=1, column=0, sticky="w", pady=(0, 6)
            )

            key = (asset.get("source", ""), asset.get("category", ""), asset.get("name", ""))
            source_asset = self._asset_by_key.get(key, {})
            abilities = list(source_asset.get("abilities", []))[:3]
            current_used = list(asset.get("abilities_used", [False, False, False]))[:3]
            while len(current_used) < 3:
                current_used.append(False)
            asset["abilities_used"] = current_used

            wraplength = max(280, self._asset_cards_canvas.winfo_width() - 120)

            for ability_idx in range(3):
                ability_text = abilities[ability_idx] if ability_idx < len(abilities) else "(No ability text)"
                var = tk.BooleanVar(value=bool(current_used[ability_idx]))
                ability_row = tk.Frame(card, bg=PANEL_BG)
                ability_row.grid(row=ability_idx + 2, column=0, sticky="ew", pady=2)
                ability_row.grid_columnconfigure(2, weight=1)

                cb = tk.Checkbutton(
                    ability_row,
                    variable=var,
                    bg=PANEL_BG,
                    fg=FG,
                    activebackground=PANEL_BG,
                    activeforeground=FG,
                    selectcolor=PANEL_BG,
                    anchor="w",
                    justify="left",
                    command=lambda aidx=idx, bidx=ability_idx, v=var: self._set_asset_ability_used(aidx, bidx, v.get()),
                )
                cb.grid(row=0, column=0, sticky="nw", padx=(0, 4))
                tk.Label(
                    ability_row,
                    text=f"Ability {ability_idx + 1}",
                    bg=PANEL_BG,
                    fg=ACCENT2,
                    anchor="nw",
                    justify="left",
                    font=("Segoe UI", 9, "bold"),
                ).grid(row=0, column=1, sticky="nw", padx=(0, 8))
                tk.Label(
                    ability_row,
                    text=ability_text,
                    bg=PANEL_BG,
                    fg=FG,
                    anchor="nw",
                    justify="left",
                    wraplength=wraplength,
                ).grid(row=0, column=2, sticky="nw")

            ttk.Button(card, text="Remove", command=lambda aidx=idx: self._remove_asset(aidx)).grid(
                row=5, column=0, sticky="e", pady=(6, 0)
            )

    def _set_asset_ability_used(self, asset_idx: int, ability_idx: int, value: bool) -> None:
        if asset_idx >= len(self._char_assets_selected):
            return
        used = self._char_assets_selected[asset_idx].setdefault("abilities_used", [False, False, False])
        while len(used) < 3:
            used.append(False)
        used[ability_idx] = bool(value)
        self._queue_character_autosave()

    def _remove_asset(self, idx: int) -> None:
        if idx < 0 or idx >= len(self._char_assets_selected):
            return
        del self._char_assets_selected[idx]
        self._render_asset_cards()
        self._queue_character_autosave()

    def _refresh_xp_display(self) -> None:
        for key, var in self._char_xp_vars.items():
            ticks = max(0, min(40, int(var.get())))
            var.set(ticks)
            self._xp_display_vars[key].set(f"{self._render_tick_track(ticks)}  ({ticks}/40 ticks)")

    def _adjust_xp(self, key: str, delta_ticks: int) -> None:
        if key not in self._char_xp_vars:
            return
        current = int(self._char_xp_vars[key].get())
        self._char_xp_vars[key].set(max(0, min(40, current + delta_ticks)))
        self._refresh_xp_display()

    @staticmethod
    def _render_tick_track(ticks: int) -> str:
        box_states = ["[....]", "[#...]", "[##..]", "[###.]", "[####]"]
        out: list[str] = []
        clamped = max(0, min(40, ticks))
        for box_idx in range(10):
            box_ticks = max(0, min(4, clamped - (box_idx * 4)))
            out.append(box_states[box_ticks])
        return " ".join(out)

    def _render_progress_track_summary(self, ticks: int) -> str:
        visible = self._render_tick_track(min(40, ticks))
        if ticks <= 40:
            return f"{visible} ({ticks}t)"
        overflow = ticks - 40
        return f"{visible} +{overflow}t"

    def _difficulty_milestone_ticks(self, difficulty: str) -> int:
        return self._DIFFICULTY_MILESTONE_TICKS.get(difficulty, 4)

    def _refresh_momentum_display(self) -> None:
        momentum = int(self._char_condition_vars["momentum"].get())
        momentum = max(-6, min(10, momentum))
        positions = list(range(-6, 11))
        cells: list[str] = []
        for pos in positions:
            if pos == momentum:
                cell = "[#]"
            else:
                cell = "[ ]"
            cells.append(cell)
        self._momentum_track_var.set(f"{momentum:+d}  {' '.join(cells)}")

    def _roll_action_vs_challenge(self, bonus: int) -> dict[str, Any]:
        action_die = random.randint(1, 6)
        challenge_1 = random.randint(1, 10)
        challenge_2 = random.randint(1, 10)
        score = min(10, action_die + bonus)
        beats_1 = score > challenge_1
        beats_2 = score > challenge_2
        is_match = challenge_1 == challenge_2

        if beats_1 and beats_2 and is_match:
            outcome = "Strong Hit with Match"
        elif beats_1 and beats_2:
            outcome = "Strong Hit"
        elif beats_1 or beats_2:
            outcome = "Weak Hit"
        else:
            outcome = "Miss"

        return {
            "action_die": action_die,
            "bonus": bonus,
            "score": score,
            "challenge_1": challenge_1,
            "challenge_2": challenge_2,
            "is_match": is_match,
            "outcome": outcome,
        }

    def _roll_with_bonus(self, label: str, bonus: int) -> None:
        result = self._roll_action_vs_challenge(bonus)
        dialog = tk.Toplevel(self)
        dialog.title("Action Roll")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=PANEL_BG)

        panel = ttk.Frame(dialog, style="Panel.TFrame", padding=12)
        panel.pack(fill="both", expand=True)
        panel.columnconfigure(0, weight=1)

        ttk.Label(panel, text=f"{label} Roll", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        tk.Label(
            panel,
            text=(
                f"Action die: {result['action_die']}\n"
                f"Bonus: {bonus:+d}\n"
                f"Action score: {result['score']}\n"
                f"Challenge dice: {result['challenge_1']} and {result['challenge_2']}\n"
                f"Match: {'Yes' if result['is_match'] else 'No'}"
            ),
            bg=PANEL_BG,
            fg=FG,
            justify="left",
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(8, 10))
        ttk.Label(panel, text=result["outcome"], style="Title.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Button(panel, text="Close", command=dialog.destroy).grid(row=3, column=0, sticky="e", pady=(12, 0))

    def _refresh_character_picker(self) -> None:
        self._character_picker_values = []
        for idx, character in enumerate(self._characters):
            name = character.get("name", "Unnamed")
            self._character_picker_values.append(f"{idx + 1}. {name}")
        self._character_picker["values"] = self._character_picker_values

    def _load_initial_character(self) -> None:
        if not self._characters:
            self._new_character()
            return

        last_id = self._settings.get("character", {}).get("last_id", "")
        idx = 0
        if last_id:
            for i, character in enumerate(self._characters):
                if character.get("id") == last_id:
                    idx = i
                    break

        self._load_character_by_index(idx)

    def _set_last_character_id(self, char_id: str) -> None:
        character_settings = self._settings.setdefault("character", {})
        if character_settings.get("last_id") == char_id:
            return
        character_settings["last_id"] = char_id
        save_settings(self._settings)

    def _clear_last_character_id_if_matches(self, char_id: str) -> None:
        character_settings = self._settings.setdefault("character", {})
        if character_settings.get("last_id") != char_id:
            return
        character_settings["last_id"] = ""
        save_settings(self._settings)

    def _load_character_by_index(self, idx: int) -> None:
        if idx < 0 or idx >= len(self._characters):
            return
        self._character_selected_index = idx
        character = copy.deepcopy(self._characters[idx])
        self._populate_character_form(character)
        picker_text = self._character_picker_values[idx] if idx < len(self._character_picker_values) else ""
        self._character_picker_var.set(picker_text)
        display_name = character.get("name") or "Unnamed"
        self._character_title_var.set(f"Character: {display_name}")
        if self._character_id:
            self._set_last_character_id(self._character_id)

    def _default_character(self) -> dict[str, Any]:
        return {
            "id": str(uuid4()),
            "name": "",
            "game": "Starforged",
            "stats": {
                "edge": 1,
                "heart": 1,
                "iron": 1,
                "shadow": 1,
                "wits": 1,
            },
            "condition": {
                "health": 5,
                "spirit": 5,
                "supply": 5,
                "momentum": 2,
                "max_momentum": 10,
                "momentum_reset": 2,
            },
            "xp_tracks": {
                "quests": 0,
                "bonds": 0,
                "discoveries": 0,
            },
            "assets": [],
            "progress_tracks": [],
        }

    def _new_character(self) -> None:
        self._character_selected_index = None
        self._populate_character_form(self._default_character())
        self._character_picker_var.set("")
        self._character_title_var.set("Character: New")

    def _on_character_picker_select(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        value = self._character_picker_var.get()
        if value not in self._character_picker_values:
            return
        self._load_character_by_index(self._character_picker_values.index(value))

    def _populate_character_form(self, character: dict[str, Any]) -> None:
        self._suspend_character_autosave = True
        self._character_id = character.get("id") or str(uuid4())
        self._char_name_var.set(character.get("name", ""))
        self._char_game_value = str(character.get("game", "Starforged"))

        stats = character.get("stats", {})
        for key, var in self._char_stat_vars.items():
            var.set(int(stats.get(key, 1)))

        condition = character.get("condition", {})
        for key, var in self._char_condition_vars.items():
            var.set(int(condition.get(key, var.get())))
        self._refresh_momentum_display()

        xp_tracks = character.get("xp_tracks", {})
        for key, var in self._char_xp_vars.items():
            var.set(int(xp_tracks.get(key, 0)))
        self._refresh_xp_display()

        self._char_assets_selected = []
        for asset in character.get("assets", []):
            if not isinstance(asset, dict):
                continue
            normalized = {
                "source": str(asset.get("source", "")),
                "category": str(asset.get("category", "")),
                "name": str(asset.get("name", "")),
                "abilities_used": [bool(x) for x in list(asset.get("abilities_used", [False, False, False]))[:3]],
            }
            while len(normalized["abilities_used"]) < 3:
                normalized["abilities_used"].append(False)
            self._char_assets_selected.append(normalized)
        self._render_asset_cards()

        self._char_progress_tracks = [
            {
                "name": str(track.get("name", "")),
                "difficulty": str(track.get("difficulty", self._DIFFICULTIES[0])),
                "ticks": max(0, int(track.get("ticks", 0))),
            }
            for track in character.get("progress_tracks", [])
            if isinstance(track, dict)
        ]
        self._refresh_progress_tracks_rows()
        self._char_track_name_var.set("")
        self._char_track_diff_var.set(self._DIFFICULTIES[0])
        self._char_condition_vars["max_momentum"].set(10)
        self._suspend_character_autosave = False

    def _character_from_form(self) -> dict[str, Any]:
        name = self._char_name_var.get().strip() or "Unnamed"
        assets: list[dict[str, Any]] = []
        for asset in self._char_assets_selected:
            assets.append(
                {
                    "source": str(asset.get("source", "")),
                    "category": str(asset.get("category", "")),
                    "name": str(asset.get("name", "")),
                    "abilities_used": [bool(x) for x in list(asset.get("abilities_used", [False, False, False]))[:3]],
                }
            )
        return {
            "id": self._character_id or str(uuid4()),
            "name": name,
            "game": self._char_game_value,
            "stats": {k: int(v.get()) for k, v in self._char_stat_vars.items()},
            "condition": {k: int(v.get()) for k, v in self._char_condition_vars.items()},
            "xp_tracks": {k: int(v.get()) for k, v in self._char_xp_vars.items()},
            "assets": assets,
            "progress_tracks": copy.deepcopy(self._char_progress_tracks),
        }

    def _save_character_from_form(self, *, update_title: bool = True) -> None:
        character = self._character_from_form()
        if self._character_selected_index is None:
            self._characters.append(character)
            self._character_selected_index = len(self._characters) - 1
        else:
            self._characters[self._character_selected_index] = character
        save_characters(self._characters)

        self._refresh_character_picker()
        idx = self._character_selected_index if self._character_selected_index is not None else 0
        if idx < len(self._character_picker_values):
            self._character_picker_var.set(self._character_picker_values[idx])
        if update_title:
            self._character_title_var.set(f"Character: {character['name']}")
        self._set_last_character_id(character["id"])

    def _delete_selected_character(self) -> None:
        if self._character_selected_index is None:
            messagebox.showinfo("Delete character", "Select a character to delete.")
            return
        idx = self._character_selected_index
        character = self._characters[idx]
        name = character.get("name", "Unnamed")
        if not messagebox.askyesno("Delete character", f"Delete {name}?"):
            return

        char_id = str(character.get("id", ""))
        del self._characters[idx]
        save_characters(self._characters)
        if char_id:
            self._clear_last_character_id_if_matches(char_id)

        self._refresh_character_picker()
        if self._characters:
            next_idx = min(idx, len(self._characters) - 1)
            self._load_character_by_index(next_idx)
        else:
            self._new_character()

    def _refresh_progress_tracks_rows(self) -> None:
        if not hasattr(self, "_progress_rows"):
            return
        for child in self._progress_rows.winfo_children():
            child.destroy()

        if not self._char_progress_tracks:
            ttk.Label(
                self._progress_rows,
                text="No progress tracks yet. Add one above.",
                style="Body.TLabel",
            ).grid(row=0, column=0, sticky="w", padx=2, pady=2)
            return

        for idx, track in enumerate(self._char_progress_tracks):
            rowf = ttk.Frame(self._progress_rows, style="Panel.TFrame", padding=(2, 2))
            rowf.grid(row=idx, column=0, sticky="ew", pady=2)
            rowf.columnconfigure(1, weight=1)

            name = str(track.get("name", "Unnamed"))
            difficulty = str(track.get("difficulty", self._DIFFICULTIES[0]))
            ticks = int(track.get("ticks", 0))

            ttk.Label(rowf, text=f"{name} [{difficulty}]", style="Cat.TLabel").grid(
                row=0, column=0, sticky="w", padx=(0, 8)
            )
            tk.Label(
                rowf,
                text=self._render_progress_track_summary(ticks),
                bg=PANEL_BG,
                fg=FG,
                anchor="w",
                justify="left",
                font=self._TRACK_FONT,
            ).grid(row=0, column=1, sticky="w", padx=(0, 8))
            ttk.Button(rowf, text="- Milestone", command=lambda i=idx: self._adjust_progress_row_milestone(i, -1)).grid(
                row=0, column=2, padx=1
            )
            ttk.Button(rowf, text="+ Milestone", command=lambda i=idx: self._adjust_progress_row_milestone(i, 1)).grid(
                row=0, column=3, padx=1
            )
            ttk.Button(rowf, text="Delete", command=lambda i=idx: self._delete_progress_track_row(i)).grid(
                row=0, column=4, padx=1
            )

    def _add_progress_track(self) -> None:
        name = self._char_track_name_var.get().strip()
        if not name:
            messagebox.showinfo("Progress track", "Enter a track name first.")
            return
        self._char_progress_tracks.append(
            {
                "name": name,
                "difficulty": self._char_track_diff_var.get(),
                "ticks": 0,
            }
        )
        self._char_track_name_var.set("")
        self._refresh_progress_tracks_rows()
        self._queue_character_autosave()

    def _adjust_progress_row_milestone(self, idx: int, delta: int) -> None:
        if idx < 0 or idx >= len(self._char_progress_tracks):
            return
        track = self._char_progress_tracks[idx]
        difficulty = str(track.get("difficulty", self._DIFFICULTIES[0]))
        step = self._difficulty_milestone_ticks(difficulty)
        current = int(track.get("ticks", 0))
        milestones = max(0, current // step)
        milestones = max(0, milestones + delta)
        track["ticks"] = milestones * step
        self._refresh_progress_tracks_rows()
        self._queue_character_autosave()

    def _delete_progress_track_row(self, idx: int) -> None:
        if idx < 0 or idx >= len(self._char_progress_tracks):
            return
        del self._char_progress_tracks[idx]
        self._refresh_progress_tracks_rows()
        self._queue_character_autosave()
