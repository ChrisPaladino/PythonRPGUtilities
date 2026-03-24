"""styles.py – Colour constants and ttk style configuration."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"
ACCENT2 = "#a6e3a1"
PANEL_BG = "#252535"
SEL_BG = "#313244"
BORDER = "#45475a"
HIT_STRONG = "#a6e3a1"
HIT_WEAK = "#f9e2af"
HIT_MISS = "#f38ba8"


def configure_styles(widget: tk.Tk) -> None:
    """Apply the dark theme to all ttk widgets."""
    style = ttk.Style(widget)
    style.theme_use("clam")

    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL_BG)
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("Title.TLabel", background=BG, foreground=ACCENT,
                    font=("Segoe UI", 11, "bold"))
    style.configure("Cat.TLabel", background=PANEL_BG, foreground=ACCENT2,
                    font=("Segoe UI", 9, "italic"))
    style.configure("TButton", background=PANEL_BG, foreground=FG,
                    relief="flat", padding=4)
    style.map("TButton",
              background=[("active", SEL_BG), ("pressed", BORDER)],
              foreground=[("active", ACCENT)])
    style.configure("Accent.TButton", background=ACCENT, foreground=BG,
                    font=("Segoe UI", 9, "bold"), relief="flat", padding=5)
    style.map("Accent.TButton",
              background=[("active", "#74c7ec"), ("pressed", "#89b4fa")])
    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=PANEL_BG, foreground=FG,
                    padding=(10, 4))
    style.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", BG)])
    style.configure("TCombobox", fieldbackground=PANEL_BG,
                    background=PANEL_BG, foreground=FG, selectbackground=SEL_BG)
    style.configure("TScrollbar", background=BORDER, troughcolor=PANEL_BG,
                    arrowcolor=FG)
    style.configure("TSeparator", background=BORDER)
