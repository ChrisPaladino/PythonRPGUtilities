"""
Main window — root CTk window with top menu and switchable views.
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import customtkinter as ctk
from pta_manager.ui.app_state import AppState
from pta_manager.ui.table_view import TableView
from pta_manager.ui.character_view import CharacterView
from pta_manager.services.persistence_service import (
    SAVE_DIR,
    save_game_to_path,
    load_game_from_path,
    delete_game_by_path,
    serialize_state,
    deserialize_state,
)


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Primetime Adventures Manager")
        self.geometry("1100x720")
        self.minsize(800, 560)

        self._state = AppState()
        self._mode_var = tk.StringVar(value="DICE_MODE")
        self._build()
        self._apply_initial_episode_budget()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        menubar = tk.Menu(self)
        self.configure(menu=menubar)

        episode_menu = tk.Menu(menubar, tearoff=False)
        episode_menu.add_command(label="New Episode", command=self._new_episode)
        episode_menu.add_command(label="New Game", command=self._new_game)
        episode_menu.add_separator()
        episode_menu.add_command(label="Save Episode", command=self._save_game)
        episode_menu.add_command(label="Load Episode", command=self._load_game)
        episode_menu.add_command(label="Delete Episode", command=self._delete_game)
        menubar.add_cascade(label="Episode", menu=episode_menu)

        settings_menu = tk.Menu(menubar, tearoff=False)
        mode_menu = tk.Menu(settings_menu, tearoff=False)
        mode_menu.add_radiobutton(
            label="Dice Mode",
            variable=self._mode_var,
            value="DICE_MODE",
            command=lambda: self._on_mode_change("DICE_MODE"),
        )
        mode_menu.add_radiobutton(
            label="Card Mode",
            variable=self._mode_var,
            value="CARD_MODE",
            command=lambda: self._on_mode_change("CARD_MODE"),
        )
        settings_menu.add_cascade(label="Resolution Mode", menu=mode_menu)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        self._top_controls = ctk.CTkFrame(self, height=42)
        self._top_controls.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 0))
        self._top_controls.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self._top_controls, text="View", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=(8, 6), pady=6, sticky="w"
        )
        self._view_switcher = ctk.CTkSegmentedButton(
            self._top_controls,
            values=["Table", "Characters"],
            command=self._show_view,
        )
        self._view_switcher.grid(row=0, column=1, padx=0, pady=6, sticky="w")
        self._view_switcher.set("Table")

        self._content = ctk.CTkFrame(self)
        self._content.grid(row=1, column=0, sticky="nsew", padx=4, pady=(4, 4))
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

        self._table_view = TableView(self._content, state=self._state)
        self._table_view.grid(row=0, column=0, sticky="nsew")

        self._character_view = CharacterView(
            self._content,
            state=self._state,
            on_change=self._on_characters_changed,
        )
        self._character_view.grid(row=0, column=0, sticky="nsew")

        self._show_view("Table")

    def _on_mode_change(self, value: str):
        self._state.mode = value
        self._table_view.refresh()

    def _show_view(self, value: str):
        if value == "Characters":
            self._character_view.tkraise()
            self._character_view.refresh()
        else:
            self._table_view.tkraise()
            self._table_view.refresh()

    def _apply_initial_episode_budget(self):
        if self._state.scenes:
            return
        self._state.producer_budget = len(self._state.protagonists)

    def _on_characters_changed(self):
        # Budget scales with protagonist count at the start of an episode.
        if not self._state.scenes:
            self._state.producer_budget = len(self._state.protagonists)
        self._table_view.refresh()
        self._character_view.refresh()

    def _new_episode(self):
        self._state.scenes = []
        self._state.current_scene_id = ""
        self._state.episode_info = {"scene": 0}
        self._state.deck.shuffle()
        for protagonist in self._state.protagonists:
            protagonist.fan_mail = 0
        self._state.producer_budget = len(self._state.protagonists)
        self._table_view.refresh()
        self._character_view.refresh()
        messagebox.showinfo("New Episode", "Started a new episode using current cast.")

    def _new_game(self):
        self._state = AppState()
        self._mode_var.set("DICE_MODE")
        self._state.mode = "DICE_MODE"
        self._table_view._state = self._state
        self._character_view._state = self._state
        self._apply_initial_episode_budget()
        self._table_view.refresh()
        self._character_view.refresh()
        messagebox.showinfo("New Game", "Started a new game with an empty cast.")

    def _save_game(self):
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        initial_name = self._state.save_name or "episode_1"
        selected_path = filedialog.asksaveasfilename(
            title="Save Episode",
            initialdir=str(SAVE_DIR),
            initialfile=f"{initial_name}.json",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if not selected_path:
            return

        data = serialize_state(
            protagonists=self._state.protagonists,
            producer_budget=self._state.producer_budget,
            scenes=self._state.scenes,
            current_scene_id=self._state.current_scene_id,
            episode_info=self._state.episode_info,
            mode=self._state.mode,
        )
        save_game_to_path(selected_path, data)
        self._state.save_name = Path(selected_path).stem
        messagebox.showinfo("Episode Saved", f"Saved to:\n{selected_path}")

    def _load_game(self):
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        selected_path = filedialog.askopenfilename(
            title="Load Episode",
            initialdir=str(SAVE_DIR),
            filetypes=[("JSON files", "*.json")],
        )
        if not selected_path:
            return

        data = load_game_from_path(selected_path)
        restored = deserialize_state(data)
        self._state.protagonists = restored["protagonists"]
        self._state.producer_budget = restored["producer_budget"]
        self._state.scenes = restored["scenes"]
        self._state.current_scene_id = restored["current_scene"]
        self._state.episode_info = restored["episode_info"]
        self._state.mode = restored["mode"]
        self._state.save_name = Path(selected_path).stem
        self._mode_var.set(self._state.mode)
        self._table_view.refresh()
        self._character_view.refresh()
        messagebox.showinfo("Episode Loaded", f"Loaded:\n{selected_path}")

    def _delete_game(self):
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        selected_path = filedialog.askopenfilename(
            title="Delete Episode File",
            initialdir=str(SAVE_DIR),
            filetypes=[("JSON files", "*.json")],
        )
        if not selected_path:
            return

        confirmed = messagebox.askyesno(
            "Delete Episode",
            f"Delete this file?\n{selected_path}",
        )
        if not confirmed:
            return

        delete_game_by_path(selected_path)
        messagebox.showinfo("Episode Deleted", "Episode file deleted.")
