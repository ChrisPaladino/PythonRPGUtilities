"""
Table view — Tab 1: main play view.

Layout (grid):
  Row 0 — episode/act/scene info bar (full width)
    Row 1 — scene panel (participants left, toggles/producer spend right)
  Row 2 — results log (full width)
"""
import customtkinter as ctk
from pta_manager.ui.app_state import AppState
from pta_manager.ui.scene_panel import ScenePanel


class TableView(ctk.CTkFrame):
    def __init__(self, parent, state: AppState, **kwargs):
        super().__init__(parent, **kwargs)
        self._state = state
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build()
        self.refresh()

    def _build(self):
        # --- Row 0: scene panel (owns scene info in its label) ---
        self._scene_panel = ScenePanel(
            self,
            state=self._state,
            on_resolve=self._on_resolve,
            on_state_change=self._refresh,
        )
        self._scene_panel.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # --- Row 1: results log ---
        self._results_log = ctk.CTkTextbox(self, height=120, state="disabled")
        self._results_log.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 4))

    def _on_resolve(self, result_text: str = ""):
        self._results_log.configure(state="normal")
        self._results_log.insert("end", result_text + "\n")
        self._results_log.see("end")
        self._results_log.configure(state="disabled")

    def _refresh(self):
        self._scene_panel.refresh()

    def refresh(self):
        self._refresh()
