"""
Producer panel — displays and controls the Producer's budget and spend.
"""
import customtkinter as ctk
from pta_manager.ui.app_state import AppState


class ProducerPanel(ctk.CTkFrame):
    def __init__(self, parent, state: AppState, on_change, **kwargs):
        super().__init__(parent, **kwargs)
        self._state = state
        self._on_change = on_change
        self._budget_spend = ctk.IntVar(value=0)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Producer", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, columnspan=3, padx=8, pady=(8, 4), sticky="w"
        )

        ctk.CTkLabel(self, text="Budget:").grid(row=1, column=0, padx=8, sticky="w")
        self._budget_label = ctk.CTkLabel(self, text=str(self._state.producer_budget))
        self._budget_label.grid(row=1, column=1, padx=4)

        ctk.CTkButton(self, text="+", width=28, command=self._add_budget).grid(row=1, column=2, padx=4)
        ctk.CTkButton(self, text="-", width=28, command=self._remove_budget).grid(row=1, column=3, padx=(0, 8))

        ctk.CTkLabel(self, text="Spend this scene:").grid(row=2, column=0, padx=8, sticky="w", pady=(8, 0))
        self._spend_label = ctk.CTkLabel(self, text="0")
        self._spend_label.grid(row=2, column=1, padx=4)

        ctk.CTkButton(self, text="+", width=28, command=self._add_spend).grid(row=2, column=2, padx=4)
        ctk.CTkButton(self, text="-", width=28, command=self._remove_spend).grid(row=2, column=3, padx=(0, 8))

    def _add_budget(self):
        self._state.producer_budget += 1
        self.refresh()
        self._on_change()

    def _remove_budget(self):
        if self._state.producer_budget > 0:
            self._state.producer_budget -= 1
        self.refresh()
        self._on_change()

    def _add_spend(self):
        current = self._budget_spend.get()
        if current < min(5, self._state.producer_budget):
            self._budget_spend.set(current + 1)
            self._spend_label.configure(text=str(self._budget_spend.get()))

    def _remove_spend(self):
        current = self._budget_spend.get()
        if current > 0:
            self._budget_spend.set(current - 1)
            self._spend_label.configure(text=str(self._budget_spend.get()))

    def get_spend(self) -> int:
        return self._budget_spend.get()

    def reset_spend(self):
        self._budget_spend.set(0)
        self._spend_label.configure(text="0")

    def refresh(self):
        self._budget_label.configure(text=str(self._state.producer_budget))
