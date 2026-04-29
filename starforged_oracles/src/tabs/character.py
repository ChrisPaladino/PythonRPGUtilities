"""tabs/character.py - Character tab mixin."""
from __future__ import annotations

import copy
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, TYPE_CHECKING
from uuid import uuid4

from loader import save_characters
from widgets import make_listbox_frame, make_option_menu, make_paned

if TYPE_CHECKING:
	from starforged_app import App


class CharacterTabMixin:

	_DIFFICULTIES = ["Troublesome", "Dangerous", "Formidable", "Extreme", "Epic"]

	if TYPE_CHECKING:
		_characters: list[dict[str, Any]]

		def _short_source(self, source: str) -> str: ...

	def _build_character_tab(self, parent: ttk.Frame) -> None:
		paned = make_paned(parent)

		# --- Left panel: character list and CRUD ---
		left = ttk.Frame(paned, style="Panel.TFrame")
		left.rowconfigure(2, weight=1)
		left.columnconfigure(0, weight=1)
		paned.add(left, minsize=220, width=260)

		ttk.Label(left, text="Characters", style="Title.TLabel").grid(
			row=0, column=0, sticky="w", padx=8, pady=(10, 6)
		)

		lf, self._character_listbox = make_listbox_frame(left)
		lf.grid(row=2, column=0, sticky="nsew", padx=6, pady=4)
		self._character_listbox.bind("<<ListboxSelect>>", self._on_character_select)

		char_buttons = ttk.Frame(left, style="Panel.TFrame")
		char_buttons.grid(row=3, column=0, sticky="ew", padx=6, pady=(2, 8))
		char_buttons.columnconfigure((0, 1, 2), weight=1)

		ttk.Button(char_buttons, text="New", command=self._new_character).grid(
			row=0, column=0, sticky="ew", padx=(0, 4)
		)
		ttk.Button(
			char_buttons,
			text="Save",
			style="Accent.TButton",
			command=self._save_character_from_form,
		).grid(row=0, column=1, sticky="ew", padx=2)
		ttk.Button(char_buttons, text="Delete", command=self._delete_selected_character).grid(
			row=0, column=2, sticky="ew", padx=(4, 0)
		)

		# --- Right panel: character editor ---
		right = ttk.Frame(paned, style="Panel.TFrame")
		right.columnconfigure(0, weight=1)
		paned.add(right, minsize=380)

		self._character_title_var = tk.StringVar(value="Character Sheet")
		ttk.Label(right, textvariable=self._character_title_var, style="Title.TLabel").grid(
			row=0, column=0, sticky="w", padx=10, pady=(10, 6)
		)

		form = ttk.Frame(right, style="Panel.TFrame")
		form.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
		for col in range(6):
			form.columnconfigure(col, weight=1)

		self._character_id: str | None = None
		self._character_selected_index: int | None = None

		self._char_name_var = tk.StringVar(value="")
		self._char_game_var = tk.StringVar(value="Starforged")
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

		ttk.Label(form, text="Name", style="Cat.TLabel").grid(
			row=0, column=0, sticky="w", padx=(0, 6), pady=(0, 2)
		)
		ttk.Entry(form, textvariable=self._char_name_var).grid(
			row=1, column=0, columnspan=3, sticky="ew", padx=(0, 8), pady=(0, 8)
		)

		ttk.Label(form, text="Game", style="Cat.TLabel").grid(
			row=0, column=3, sticky="w", padx=(0, 6), pady=(0, 2)
		)
		self._char_game_om = make_option_menu(
			form,
			self._char_game_var,
			["Starforged", "Sundered Isles", "Ironsworn"],
			width=16,
		)
		self._char_game_om.grid(row=1, column=3, columnspan=3, sticky="w", pady=(0, 8))

		ttk.Label(form, text="Stats", style="Cat.TLabel").grid(
			row=2, column=0, sticky="w", pady=(0, 2)
		)
		stat_row = 3
		stat_col = 0
		for name, var in self._char_stat_vars.items():
			ttk.Label(form, text=name.title()).grid(row=stat_row, column=stat_col, sticky="w")
			tk.Spinbox(
				form,
				from_=0,
				to=5,
				width=4,
				textvariable=var,
				justify="center",
			).grid(row=stat_row + 1, column=stat_col, sticky="w", padx=(0, 8), pady=(0, 8))
			stat_col += 1

		ttk.Label(form, text="Condition and Momentum", style="Cat.TLabel").grid(
			row=5, column=0, columnspan=6, sticky="w", pady=(0, 2)
		)
		self._add_meter_spin(form, "Health", self._char_condition_vars["health"], 6, 0, 5)
		self._add_meter_spin(form, "Spirit", self._char_condition_vars["spirit"], 6, 1, 5)
		self._add_meter_spin(form, "Supply", self._char_condition_vars["supply"], 6, 2, 5)
		self._add_meter_spin(form, "Momentum", self._char_condition_vars["momentum"], 6, 3, 10, -6)
		self._add_meter_spin(form, "Max Momentum", self._char_condition_vars["max_momentum"], 6, 4, 10)
		self._add_meter_spin(form, "Momentum Reset", self._char_condition_vars["momentum_reset"], 6, 5, 10, -6)

		ttk.Label(form, text="XP Tracks (ticks)", style="Cat.TLabel").grid(
			row=8, column=0, columnspan=6, sticky="w", pady=(0, 2)
		)
		self._add_meter_spin(form, "Quests", self._char_xp_vars["quests"], 9, 0, 40)
		self._add_meter_spin(form, "Bonds", self._char_xp_vars["bonds"], 9, 1, 40)
		self._add_meter_spin(form, "Discovery", self._char_xp_vars["discoveries"], 9, 2, 40)

		ttk.Label(form, text="Asset Slots", style="Cat.TLabel").grid(
			row=11, column=0, columnspan=6, sticky="w", pady=(0, 2)
		)
		self._asset_lookup: dict[str, dict[str, str]] = {}
		self._all_asset_labels = self._build_asset_labels()
		self._char_asset_vars = [tk.StringVar(value="(none)") for _ in range(3)]
		self._char_asset_search_vars = [tk.StringVar(value="") for _ in range(3)]
		self._char_asset_combos: list[ttk.Combobox] = []
		for i, asset_var in enumerate(self._char_asset_vars):
			asset_row = 12 + i
			ttk.Label(form, text=f"Asset {i + 1}").grid(row=asset_row, column=0, sticky="w")
			ttk.Entry(form, textvariable=self._char_asset_search_vars[i]).grid(
				row=asset_row, column=1, columnspan=2, sticky="ew", padx=(0, 6), pady=(0, 4)
			)
			combo = ttk.Combobox(
				form,
				textvariable=asset_var,
				values=self._all_asset_labels,
				state="normal",
				width=36,
			)
			combo.grid(row=asset_row, column=3, columnspan=3, sticky="ew", pady=(0, 4))
			self._char_asset_combos.append(combo)

			self._char_asset_search_vars[i].trace_add(
				"write",
				lambda *_args, idx=i: self._filter_asset_options(idx),
			)
			combo.bind("<KeyRelease>", lambda _event, idx=i: self._sync_asset_search_from_combo(idx))
			combo.bind("<<ComboboxSelected>>", lambda _event, idx=i: self._sync_asset_search_from_combo(idx))

		ttk.Separator(form, orient="horizontal").grid(
			row=15, column=0, columnspan=6, sticky="ew", pady=8
		)

		ttk.Label(form, text="Progress Tracks", style="Cat.TLabel").grid(
			row=16, column=0, columnspan=6, sticky="w", pady=(0, 2)
		)
		track_frame = ttk.Frame(form, style="Panel.TFrame")
		track_frame.grid(row=17, column=0, columnspan=6, sticky="nsew")
		track_frame.columnconfigure(0, weight=1)

		self._char_progress_tracks: list[dict[str, Any]] = []
		self._char_track_name_var = tk.StringVar(value="")
		self._char_track_diff_var = tk.StringVar(value=self._DIFFICULTIES[0])
		self._char_track_ticks_var = tk.IntVar(value=0)

		ttk.Entry(track_frame, textvariable=self._char_track_name_var).grid(
			row=0, column=0, sticky="ew", padx=(0, 6), pady=(0, 4)
		)
		make_option_menu(track_frame, self._char_track_diff_var, self._DIFFICULTIES, width=14).grid(
			row=0, column=1, sticky="w", padx=(0, 6), pady=(0, 4)
		)
		tk.Spinbox(
			track_frame,
			from_=0,
			to=400,
			width=6,
			textvariable=self._char_track_ticks_var,
			justify="center",
		).grid(row=0, column=2, sticky="w", padx=(0, 6), pady=(0, 4))

		lf_tracks, self._char_tracks_listbox = make_listbox_frame(track_frame)
		lf_tracks.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(0, 4))
		self._char_tracks_listbox.bind("<<ListboxSelect>>", self._on_progress_track_select)

		track_btns = ttk.Frame(track_frame, style="Panel.TFrame")
		track_btns.grid(row=2, column=0, columnspan=3, sticky="ew")
		for i in range(7):
			track_btns.columnconfigure(i, weight=1)
		ttk.Button(track_btns, text="Add", command=self._add_progress_track).grid(row=0, column=0, sticky="ew", padx=(0, 4))
		ttk.Button(track_btns, text="Update", command=self._update_progress_track).grid(row=0, column=1, sticky="ew", padx=2)
		ttk.Button(track_btns, text="Delete", command=self._delete_progress_track).grid(row=0, column=2, sticky="ew", padx=2)
		ttk.Button(track_btns, text="+1", command=lambda: self._adjust_progress_track(1)).grid(row=0, column=3, sticky="ew", padx=2)
		ttk.Button(track_btns, text="+4", command=lambda: self._adjust_progress_track(4)).grid(row=0, column=4, sticky="ew", padx=2)
		ttk.Button(track_btns, text="-1", command=lambda: self._adjust_progress_track(-1)).grid(row=0, column=5, sticky="ew", padx=2)
		ttk.Button(track_btns, text="-4", command=lambda: self._adjust_progress_track(-4)).grid(row=0, column=6, sticky="ew", padx=(2, 0))

		self._refresh_character_list()
		self._new_character()

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
		labels = ["(none)"]
		all_assets = (
			getattr(self, "_sf_assets", [])
			+ getattr(self, "_si_assets", [])
			+ getattr(self, "_is_assets", [])
		)
		for asset in sorted(all_assets, key=lambda a: (a["source"], a["category"], a["name"])):
			label = f"[{self._short_source(asset['source'])}] {asset['category']} - {asset['name']}"
			labels.append(label)
			self._asset_lookup[label] = {
				"source": asset["source"],
				"category": asset["category"],
				"name": asset["name"],
			}
		return labels

	def _sync_asset_search_from_combo(self, idx: int) -> None:
		if idx >= len(self._char_asset_vars) or idx >= len(self._char_asset_search_vars):
			return
		selected = self._char_asset_vars[idx].get()
		if selected in self._asset_lookup:
			name = self._asset_lookup[selected].get("name", "")
			if self._char_asset_search_vars[idx].get() != name:
				self._char_asset_search_vars[idx].set(name)

	def _filter_asset_options(self, idx: int) -> None:
		if idx >= len(self._char_asset_combos) or idx >= len(self._char_asset_search_vars):
			return
		query = self._char_asset_search_vars[idx].get().strip().lower()
		if not query:
			filtered = self._all_asset_labels
		else:
			filtered = [self._all_asset_labels[0]]
			for label in self._all_asset_labels[1:]:
				entry = self._asset_lookup.get(label, {})
				haystack = " ".join([
					label.lower(),
					str(entry.get("name", "")).lower(),
					str(entry.get("category", "")).lower(),
					str(entry.get("source", "")).lower(),
				])
				if query in haystack:
					filtered.append(label)

		current_value = self._char_asset_vars[idx].get()
		self._char_asset_combos[idx]["values"] = filtered
		if current_value and current_value not in filtered:
			self._char_asset_vars[idx].set("(none)")

	def _refresh_character_list(self) -> None:
		self._character_listbox.delete(0, tk.END)
		for character in self._characters:
			name = character.get("name", "Unnamed")
			game = character.get("game", "")
			self._character_listbox.insert(tk.END, f"{name} ({game})")

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
		self._character_title_var.set("New Character")
		self._character_listbox.selection_clear(0, tk.END)

	def _on_character_select(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
		selection = self._character_listbox.curselection()
		if not selection:
			return
		idx = selection[0]
		self._character_selected_index = idx
		char = copy.deepcopy(self._characters[idx])
		self._populate_character_form(char)
		display_name = char.get("name") or "Unnamed"
		self._character_title_var.set(f"Editing: {display_name}")

	def _populate_character_form(self, character: dict[str, Any]) -> None:
		self._character_id = character.get("id") or str(uuid4())
		self._char_name_var.set(character.get("name", ""))
		self._char_game_var.set(character.get("game", "Starforged"))

		stats = character.get("stats", {})
		for key, var in self._char_stat_vars.items():
			var.set(int(stats.get(key, 1)))

		condition = character.get("condition", {})
		for key, var in self._char_condition_vars.items():
			var.set(int(condition.get(key, var.get())))

		xp_tracks = character.get("xp_tracks", {})
		for key, var in self._char_xp_vars.items():
			var.set(int(xp_tracks.get(key, 0)))

		for asset_var in self._char_asset_vars:
			asset_var.set("(none)")
		for search_var in self._char_asset_search_vars:
			search_var.set("")
		for combo in self._char_asset_combos:
			combo["values"] = self._all_asset_labels
		for i, asset in enumerate(character.get("assets", [])[:3]):
			label = self._asset_label_from_asset(asset)
			self._char_asset_vars[i].set(label)
			if label in self._asset_lookup:
				self._char_asset_search_vars[i].set(self._asset_lookup[label].get("name", ""))

		self._char_progress_tracks = [
			{
				"name": str(track.get("name", "")),
				"difficulty": str(track.get("difficulty", self._DIFFICULTIES[0])),
				"ticks": max(0, int(track.get("ticks", 0))),
			}
			for track in character.get("progress_tracks", [])
			if isinstance(track, dict)
		]
		self._refresh_progress_tracks_list()
		self._char_track_name_var.set("")
		self._char_track_diff_var.set(self._DIFFICULTIES[0])
		self._char_track_ticks_var.set(0)

	def _asset_label_from_asset(self, asset: dict[str, Any]) -> str:
		source = asset.get("source", "")
		category = asset.get("category", "")
		name = asset.get("name", "")
		label = f"[{self._short_source(source)}] {category} - {name}"
		if label in self._asset_lookup:
			return label
		return "(none)"

	def _character_from_form(self) -> dict[str, Any]:
		name = self._char_name_var.get().strip() or "Unnamed"
		assets: list[dict[str, str]] = []
		for asset_var in self._char_asset_vars:
			label = asset_var.get()
			if label and label != "(none)" and label in self._asset_lookup:
				assets.append(dict(self._asset_lookup[label]))
		return {
			"id": self._character_id or str(uuid4()),
			"name": name,
			"game": self._char_game_var.get(),
			"stats": {k: int(v.get()) for k, v in self._char_stat_vars.items()},
			"condition": {k: int(v.get()) for k, v in self._char_condition_vars.items()},
			"xp_tracks": {k: int(v.get()) for k, v in self._char_xp_vars.items()},
			"assets": assets,
			"progress_tracks": copy.deepcopy(self._char_progress_tracks),
		}

	def _save_character_from_form(self) -> None:
		character = self._character_from_form()
		if self._character_selected_index is None:
			self._characters.append(character)
			self._character_selected_index = len(self._characters) - 1
		else:
			self._characters[self._character_selected_index] = character
		save_characters(self._characters)
		self._refresh_character_list()
		idx = self._character_selected_index
		if idx is not None:
			self._character_listbox.selection_set(idx)
			self._character_listbox.activate(idx)
			self._character_listbox.see(idx)
		self._character_title_var.set(f"Saved: {character['name']}")

	def _delete_selected_character(self) -> None:
		selection = self._character_listbox.curselection()
		if not selection:
			messagebox.showinfo("Delete character", "Select a character to delete.")
			return
		idx = selection[0]
		character = self._characters[idx]
		name = character.get("name", "Unnamed")
		if not messagebox.askyesno("Delete character", f"Delete {name}?"):
			return
		del self._characters[idx]
		save_characters(self._characters)
		self._refresh_character_list()
		self._new_character()

	def _refresh_progress_tracks_list(self) -> None:
		self._char_tracks_listbox.delete(0, tk.END)
		for track in self._char_progress_tracks:
			name = track.get("name", "Unnamed")
			difficulty = track.get("difficulty", self._DIFFICULTIES[0])
			ticks = int(track.get("ticks", 0))
			boxes = ticks / 4.0
			self._char_tracks_listbox.insert(
				tk.END,
				f"{name} [{difficulty}] - {ticks} ticks ({boxes:.2f} boxes)",
			)

	def _on_progress_track_select(self, _event: tk.Event | None) -> None:  # type: ignore[type-arg]
		selection = self._char_tracks_listbox.curselection()
		if not selection:
			return
		track = self._char_progress_tracks[selection[0]]
		self._char_track_name_var.set(track.get("name", ""))
		diff = track.get("difficulty", self._DIFFICULTIES[0])
		self._char_track_diff_var.set(diff if diff in self._DIFFICULTIES else self._DIFFICULTIES[0])
		self._char_track_ticks_var.set(int(track.get("ticks", 0)))

	def _add_progress_track(self) -> None:
		name = self._char_track_name_var.get().strip()
		if not name:
			messagebox.showinfo("Progress track", "Enter a track name first.")
			return
		self._char_progress_tracks.append(
			{
				"name": name,
				"difficulty": self._char_track_diff_var.get(),
				"ticks": max(0, int(self._char_track_ticks_var.get())),
			}
		)
		self._refresh_progress_tracks_list()

	def _update_progress_track(self) -> None:
		selection = self._char_tracks_listbox.curselection()
		if not selection:
			messagebox.showinfo("Progress track", "Select a track to update.")
			return
		idx = selection[0]
		name = self._char_track_name_var.get().strip()
		if not name:
			messagebox.showinfo("Progress track", "Enter a track name.")
			return
		self._char_progress_tracks[idx] = {
			"name": name,
			"difficulty": self._char_track_diff_var.get(),
			"ticks": max(0, int(self._char_track_ticks_var.get())),
		}
		self._refresh_progress_tracks_list()
		self._char_tracks_listbox.selection_set(idx)

	def _delete_progress_track(self) -> None:
		selection = self._char_tracks_listbox.curselection()
		if not selection:
			messagebox.showinfo("Progress track", "Select a track to delete.")
			return
		idx = selection[0]
		del self._char_progress_tracks[idx]
		self._refresh_progress_tracks_list()

	def _adjust_progress_track(self, delta_ticks: int) -> None:
		selection = self._char_tracks_listbox.curselection()
		if not selection:
			messagebox.showinfo("Progress track", "Select a track first.")
			return
		idx = selection[0]
		current = int(self._char_progress_tracks[idx].get("ticks", 0))
		self._char_progress_tracks[idx]["ticks"] = max(0, current + delta_ticks)
		self._refresh_progress_tracks_list()
		self._char_tracks_listbox.selection_set(idx)
		self._on_progress_track_select(None)
