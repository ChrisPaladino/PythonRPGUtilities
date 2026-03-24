"""widgets.py – Shared widget helpers used by all tab mixins."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from styles import (
    ACCENT, ACCENT2, BG, BORDER, FG, HIT_MISS, HIT_STRONG, HIT_WEAK, PANEL_BG,
)


def make_paned(parent: ttk.Frame) -> tk.PanedWindow:
    """Create and pack a standard horizontal PanedWindow."""
    paned = tk.PanedWindow(
        parent, orient="horizontal",
        bg=BORDER, sashrelief="flat", sashwidth=5, bd=0, handlesize=0,
    )
    paned.pack(fill="both", expand=True)
    return paned


def make_left_panel(paned: tk.PanedWindow, list_row: int = 5) -> ttk.Frame:
    """Add and return the standard left filter panel."""
    left = ttk.Frame(paned, style="Panel.TFrame")
    left.rowconfigure(list_row, weight=1)
    left.columnconfigure(0, weight=1)
    paned.add(left, minsize=160, width=230)
    return left


def make_right_panel(paned: tk.PanedWindow, text_row: int = 1) -> ttk.Frame:
    """Add and return the standard right detail panel."""
    right = ttk.Frame(paned, style="Panel.TFrame")
    right.rowconfigure(text_row, weight=1)
    right.columnconfigure(0, weight=1)
    paned.add(right, minsize=200)
    return right


def make_option_menu(
    parent: tk.Widget,
    var: tk.StringVar,
    values: list[str],
    *,
    width: int = 20,
) -> tk.OptionMenu:
    """Create a styled OptionMenu and return it (not yet gridded)."""
    om = tk.OptionMenu(parent, var, *values)
    om.config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG,
              highlightthickness=0, relief="flat", anchor="w", width=width)
    om["menu"].config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG)
    return om


def make_search_entry(parent: tk.Widget, var: tk.StringVar) -> tk.Entry:
    """Create a styled Search entry and return it (not yet gridded)."""
    return tk.Entry(
        parent,
        textvariable=var,
        bg=PANEL_BG, fg=FG,
        insertbackground=FG,
        relief="flat",
        highlightthickness=1,
        highlightcolor=ACCENT,
        highlightbackground=BORDER,
    )


def make_listbox_frame(parent: tk.Widget) -> tuple[ttk.Frame, tk.Listbox]:
    """Create a scrollable Listbox inside a Frame; return (frame, listbox)."""
    lf = ttk.Frame(parent, style="Panel.TFrame")
    lf.rowconfigure(0, weight=1)
    lf.columnconfigure(0, weight=1)
    lb = tk.Listbox(
        lf,
        bg=PANEL_BG, fg=FG,
        selectbackground=ACCENT, selectforeground=BG,
        activestyle="none", relief="flat", borderwidth=0,
        highlightthickness=0, font=("Segoe UI", 9),
    )
    lb.grid(row=0, column=0, sticky="nsew")
    sb = ttk.Scrollbar(lf, command=lb.yview)
    sb.grid(row=0, column=1, sticky="ns")
    lb.configure(yscrollcommand=sb.set)
    return lf, lb


def make_textbox(parent: tk.Widget) -> tk.Text:
    """Create a styled read-only Text widget with a scrollbar; return the Text."""
    frame = ttk.Frame(parent, style="Panel.TFrame")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    txt = tk.Text(
        frame,
        bg=PANEL_BG, fg=FG,
        insertbackground=FG,
        relief="flat", borderwidth=0, highlightthickness=0,
        wrap="word", font=("Segoe UI", 10),
        padx=8, pady=8,
        state="disabled", cursor="arrow",
    )
    txt.grid(row=0, column=0, sticky="nsew")
    sb = ttk.Scrollbar(frame, command=txt.yview)
    sb.grid(row=0, column=1, sticky="ns")
    txt.configure(yscrollcommand=sb.set)

    txt.tag_configure("bold",   font=("Segoe UI", 10, "bold"), foreground=ACCENT)
    txt.tag_configure("cat",    font=("Segoe UI", 9, "italic"), foreground=ACCENT2)
    txt.tag_configure("strong", foreground=HIT_STRONG, font=("Segoe UI", 10, "bold"))
    txt.tag_configure("weak",   foreground=HIT_WEAK,   font=("Segoe UI", 10, "bold"))
    txt.tag_configure("miss",   foreground=HIT_MISS,   font=("Segoe UI", 10, "bold"))
    txt.tag_configure("body",   foreground=FG,          font=("Segoe UI", 10))

    txt._container_frame = frame  # type: ignore[attr-defined]
    return txt


def set_text_lines(txt: tk.Text, lines: list[tuple[str, str]]) -> None:
    """Replace the contents of a Text widget with tagged lines."""
    txt.configure(state="normal")
    txt.delete("1.0", tk.END)
    for tag, text in lines:
        txt.insert(tk.END, text + "\n", tag)
    txt.configure(state="disabled")
    txt.see("1.0")


def rebuild_option_menu(
    om: tk.OptionMenu, var: tk.StringVar, values: list[str]
) -> None:
    """Replace all entries in an existing OptionMenu."""
    menu = om["menu"]
    menu.delete(0, "end")
    for val in values:
        menu.add_command(label=val, command=lambda v=val: var.set(v))


# ---------------------------------------------------------------------------
# Monkey-patch tk.Text.grid so it targets the container frame instead
# ---------------------------------------------------------------------------

_orig_grid = tk.Text.grid


def _patched_grid(self: tk.Text, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
    frame = getattr(self, "_container_frame", None)
    if frame is not None:
        frame.grid(*args, **kwargs)
    else:
        _orig_grid(self, *args, **kwargs)


tk.Text.grid = _patched_grid  # type: ignore[method-assign]
