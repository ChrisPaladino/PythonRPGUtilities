"""
Table view — Tab 1: main play view.

Layout (grid):
  Row 0 — episode/act/scene info bar (full width)
  Row 1 — left: protagonists list | center: scene panel | right: producer panel
  Row 2 — results log (full width)
"""
import customtkinter as ctk
from pta_manager.ui.app_state import AppState
from pta_manager.ui.scene_panel import ScenePanel
from pta_manager.ui.producer_panel import ProducerPanel


class TableView(ctk.CTkFrame):
    def __init__(self, parent, state: AppState, **kwargs):
        super().__init__(parent, **kwargs)
        self._state = state
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()
        self.refresh()

    def _build(self):
        # --- Row 0: episode bar ---
        self._episode_bar = ctk.CTkFrame(self, height=36)
        self._episode_bar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=4, pady=(4, 0))
        self._episode_bar.grid_columnconfigure(0, weight=1)
        self._episode_label = ctk.CTkLabel(self._episode_bar, text="Episode Info")
        self._episode_label.grid(row=0, column=0, padx=8, pady=6, sticky="w")

        # --- Row 1 left: protagonists ---
        self._protagonist_frame = ctk.CTkScrollableFrame(self, width=180)
        self._protagonist_frame.grid(row=1, column=0, sticky="nsew", padx=(4, 2), pady=4)
        self._protagonist_frame.grid_columnconfigure(0, weight=1)
        self._protagonists_header = ctk.CTkLabel(
            self._protagonist_frame,
            text="Protagonists",
            font=ctk.CTkFont(weight="bold"),
        )
        self._protagonists_header.grid(row=0, column=0, sticky="w", padx=4, pady=(4, 2))

        # --- Row 1 center: scene panel ---
        self._scene_panel = ScenePanel(
            self,
            state=self._state,
            on_resolve=self._on_resolve,
            get_producer_spend=self._get_producer_spend,
            on_state_change=self._refresh,
        )
        self._scene_panel.grid(row=1, column=1, sticky="nsew", padx=2, pady=4)

        # --- Row 1 right: producer panel ---
        self._producer_panel = ProducerPanel(self, state=self._state, on_change=self._refresh)
        self._producer_panel.grid(row=1, column=2, sticky="nsew", padx=(2, 4), pady=4)

        # --- Row 2: results log ---
        self._results_log = ctk.CTkTextbox(self, height=120, state="disabled")
        self._results_log.grid(row=2, column=0, columnspan=3, sticky="ew", padx=4, pady=(0, 4))

    def _on_resolve(self, result_text: str = ""):
        self._results_log.configure(state="normal")
        self._results_log.insert("end", result_text + "\n")
        self._results_log.see("end")
        self._results_log.configure(state="disabled")

    def _get_producer_spend(self) -> int:
        return self._producer_panel.get_spend()

    def _refresh(self):
        self._scene_panel.refresh()
        self._producer_panel.refresh()
        self._update_episode_bar()

    def refresh(self):
        self._refresh()
        self._rebuild_protagonists()

    def _rebuild_protagonists(self):
        for widget in self._protagonist_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(
            self._protagonist_frame,
            text="Protagonists",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=4, pady=(4, 2))
        scene_number = self._state.episode_info.get("scene", 0) + 1
        for idx, p in enumerate(self._state.protagonists, start=1):
            scene_sp = p.get_screen_presence_for_scene(scene_number)
            ctk.CTkLabel(
                self._protagonist_frame,
                text=f"{p.name}  SP:{scene_sp}  FM:{p.fan_mail}",
            ).grid(row=idx, column=0, sticky="w", padx=4, pady=1)

    def _update_episode_bar(self):
        scene_number = self._state.episode_info.get("scene", 0)
        mode = self._state.mode
        cards_left = self._state.deck.remaining
        self._episode_label.configure(
            text=f"Scene #{scene_number} | Mode: {mode} | Budget: {self._state.producer_budget} | Deck: {cards_left}"
        )
