"""
Character view — Tab 2: browse and edit protagonists.
"""
import uuid
import customtkinter as ctk
from pta_manager.models.protagonist import Protagonist
from pta_manager.models.trait import Trait
from pta_manager.ui.app_state import AppState


class CharacterView(ctk.CTkFrame):
    """Character creation, selection, and editing view."""

    def __init__(self, parent, state: AppState, on_change=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._state = state
        self._on_change = on_change or (lambda: None)
        self._selected_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self._build()
        self.refresh()

    def _build(self):
        ctk.CTkLabel(self, text="Characters", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=8, pady=8, sticky="w"
        )

        self._list_frame = ctk.CTkFrame(self)
        self._list_frame.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=(0, 8))
        self._list_frame.grid_columnconfigure(0, weight=1)
        self._list_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self._list_frame, text="Protagonists", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=8, pady=(8, 4), sticky="w"
        )

        self._list_buttons = ctk.CTkScrollableFrame(self._list_frame)
        self._list_buttons.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._list_buttons.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(self._list_frame, text="New Character", command=self._new_character).grid(
            row=2, column=0, sticky="ew", padx=8, pady=(0, 8)
        )

        self._entry_frame = ctk.CTkFrame(self)
        self._entry_frame.grid(row=1, column=1, sticky="nsew", padx=(4, 8), pady=(0, 8))
        self._entry_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self._entry_frame, text="Character Details", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=8, pady=(8, 6), sticky="w"
        )

        ctk.CTkLabel(self._entry_frame, text="Name").grid(row=1, column=0, padx=8, pady=4, sticky="w")
        self._name_entry = ctk.CTkEntry(self._entry_frame, placeholder_text="Name")
        self._name_entry.grid(row=1, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(self._entry_frame, text="Issue").grid(row=2, column=0, padx=8, pady=4, sticky="w")
        self._issue_entry = ctk.CTkEntry(self._entry_frame, placeholder_text="Issue")
        self._issue_entry.grid(row=2, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(self._entry_frame, text="Impulse").grid(row=3, column=0, padx=8, pady=4, sticky="w")
        self._impulse_entry = ctk.CTkEntry(self._entry_frame, placeholder_text="Impulse")
        self._impulse_entry.grid(row=3, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(self._entry_frame, text="SP Track (5 scenes)").grid(row=4, column=0, padx=8, pady=4, sticky="w")
        self._sp_track_entry = ctk.CTkEntry(self._entry_frame, placeholder_text="1,2,3,2,1")
        self._sp_track_entry.grid(row=4, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(self._entry_frame, text="Trait 1 (Edge)").grid(row=5, column=0, padx=8, pady=4, sticky="w")
        self._trait1_entry = ctk.CTkEntry(self._entry_frame, placeholder_text="Trait name")
        self._trait1_entry.grid(row=5, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(self._entry_frame, text="Trait 2 (Edge)").grid(row=6, column=0, padx=8, pady=4, sticky="w")
        self._trait2_entry = ctk.CTkEntry(self._entry_frame, placeholder_text="Trait name")
        self._trait2_entry.grid(row=6, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(self._entry_frame, text="Trait 3 (Connection)").grid(row=7, column=0, padx=8, pady=4, sticky="w")
        self._trait3_entry = ctk.CTkEntry(self._entry_frame, placeholder_text="Trait name")
        self._trait3_entry.grid(row=7, column=1, padx=8, pady=4, sticky="ew")

        button_row = ctk.CTkFrame(self._entry_frame, fg_color="transparent")
        button_row.grid(row=8, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 8))
        button_row.grid_columnconfigure(0, weight=1)
        button_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(button_row, text="Save Character", command=self._save_character).grid(
            row=0, column=0, padx=(0, 4), sticky="ew"
        )
        ctk.CTkButton(button_row, text="Delete Character", command=self._delete_character).grid(
            row=0, column=1, padx=(4, 0), sticky="ew"
        )

        self._new_character()

    def _parse_sp_track(self) -> list[int]:
        raw = self._sp_track_entry.get().strip()
        if not raw:
            return [1, 2, 3, 2, 1]
        values = [segment.strip() for segment in raw.split(",") if segment.strip()]
        if len(values) != 5:
            return [1, 2, 3, 2, 1]
        parsed = []
        for value in values:
            try:
                parsed.append(max(1, min(3, int(value))))
            except ValueError:
                return [1, 2, 3, 2, 1]
        return parsed

    def _new_character(self):
        self._selected_id = None
        self._name_entry.delete(0, "end")
        self._issue_entry.delete(0, "end")
        self._impulse_entry.delete(0, "end")
        self._sp_track_entry.delete(0, "end")
        self._sp_track_entry.insert(0, "1,2,3,2,1")
        self._trait1_entry.delete(0, "end")
        self._trait2_entry.delete(0, "end")
        self._trait3_entry.delete(0, "end")
        self._trait1_entry.insert(0, "Edge 1")
        self._trait2_entry.insert(0, "Edge 2")
        self._trait3_entry.insert(0, "Connection")

    def _save_character(self):
        name = self._name_entry.get().strip()
        issue = self._issue_entry.get().strip()
        impulse = self._impulse_entry.get().strip()
        sp_track = self._parse_sp_track()
        t1 = self._trait1_entry.get().strip()
        t2 = self._trait2_entry.get().strip()
        t3 = self._trait3_entry.get().strip()

        if not name:
            return

        traits = [
            Trait(name=t1 or "Edge 1", type="edge"),
            Trait(name=t2 or "Edge 2", type="edge"),
            Trait(name=t3 or "Connection", type="connection"),
        ]

        protagonist = next((p for p in self._state.protagonists if p.id == self._selected_id), None)
        if protagonist is None:
            protagonist = Protagonist(
                id=str(uuid.uuid4()),
                name=name,
                issue=issue,
                impulse=impulse,
                screen_presence=sp_track[0],
                screen_presence_track=sp_track,
                traits=traits,
            )
            self._state.protagonists.append(protagonist)
            self._selected_id = protagonist.id
        else:
            protagonist.name = name
            protagonist.issue = issue
            protagonist.impulse = impulse
            protagonist.screen_presence_track = sp_track
            protagonist.screen_presence = sp_track[0]
            protagonist.traits = traits

        self.refresh()
        self._on_change()

    def _select_character(self, protagonist_id: str):
        protagonist = next((p for p in self._state.protagonists if p.id == protagonist_id), None)
        if protagonist is None:
            return
        self._selected_id = protagonist.id
        self._name_entry.delete(0, "end")
        self._name_entry.insert(0, protagonist.name)
        self._issue_entry.delete(0, "end")
        self._issue_entry.insert(0, protagonist.issue)
        self._impulse_entry.delete(0, "end")
        self._impulse_entry.insert(0, protagonist.impulse)
        self._sp_track_entry.delete(0, "end")
        self._sp_track_entry.insert(0, ",".join(str(v) for v in protagonist.screen_presence_track[:5]))

        traits = protagonist.traits + [Trait(name="", type="edge")] * (3 - len(protagonist.traits))
        self._trait1_entry.delete(0, "end")
        self._trait1_entry.insert(0, traits[0].name)
        self._trait2_entry.delete(0, "end")
        self._trait2_entry.insert(0, traits[1].name)
        self._trait3_entry.delete(0, "end")
        self._trait3_entry.insert(0, traits[2].name)

        self.refresh()

    def _delete_character(self):
        if self._selected_id is None:
            return
        index = next((i for i, p in enumerate(self._state.protagonists) if p.id == self._selected_id), None)
        if index is None:
            return
        del self._state.protagonists[index]
        self._new_character()
        self.refresh()
        self._on_change()

    def refresh(self):
        for widget in self._list_buttons.winfo_children():
            widget.destroy()

        if not self._state.protagonists:
            ctk.CTkLabel(self._list_buttons, text="No characters yet.").grid(
                row=0, column=0, padx=6, pady=6, sticky="w"
            )
            return

        for row, protagonist in enumerate(self._state.protagonists):
            scene_num = self._state.episode_info.get("scene", 0) + 1
            sp = protagonist.get_screen_presence_for_scene(scene_num)
            label = f"{protagonist.name} | Scene SP {sp} | FM {protagonist.fan_mail}"
            is_selected = protagonist.id == self._selected_id
            ctk.CTkButton(
                self._list_buttons,
                text=label,
                anchor="w",
                fg_color=("#2f3340" if is_selected else "#22252e"),
                hover_color="#3b4050",
                command=lambda pid=protagonist.id: self._select_character(pid),
            ).grid(row=row, column=0, sticky="ew", padx=4, pady=3)
