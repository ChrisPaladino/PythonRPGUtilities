"""starforged_app.py – Starforged / Sundered Isles move & oracle reference GUI.

Requires Python 3.10+, Tkinter (stdlib), and PyYAML.
Data must be downloaded first:
    python src/fetch_data.py

Usage:
    python src/starforged_app.py
"""
from __future__ import annotations

import random
import re
import sys
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox, ttk
from typing import Any

try:
    import yaml
except ModuleNotFoundError:
    raise SystemExit(
        "PyYAML is not installed.  Run:  pip install pyyaml"
    )

# ---------------------------------------------------------------------------
# Paths  –  work both in development and when frozen by PyInstaller
# ---------------------------------------------------------------------------

if getattr(sys, "frozen", False):   # running inside a PyInstaller bundle
    _BASE_DIR = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    _BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = _BASE_DIR / "data"
SF_MOVES_YAML = DATA_DIR / "starforged_moves.yaml"
SI_MOVES_YAML = DATA_DIR / "sundered_isles_moves.yaml"
SF_ORACLES_DIR = DATA_DIR / "sf_oracles"
SI_ORACLES_DIR = DATA_DIR / "si_oracles"
CUSTOM_ORACLES_DIR = DATA_DIR / "custom_oracles"
IS_ORACLES_DIR = DATA_DIR / "is_oracles"
SF_ASSETS_DIR = DATA_DIR / "sf_assets"
SI_ASSETS_DIR = DATA_DIR / "si_assets"
IS_ASSETS_DIR = DATA_DIR / "is_assets"
BUNDLES_YAML = DATA_DIR / "bundles.yaml"

# ---------------------------------------------------------------------------
# Markdown-to-plain-text helpers
# ---------------------------------------------------------------------------

_BOLD_RE = re.compile(r"__(.+?)__")
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_TABLE_RE = re.compile(r"\{\{table:[^}]+\}\}")


def strip_markup(text: str) -> str:
    """Convert light Markdown/Datasworn markup to plain text."""
    text = _BOLD_RE.sub(r"\1", text)
    text = _LINK_RE.sub(r"\1", text)
    text = _TABLE_RE.sub("[see table below]", text)
    return text


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _sanitise_yaml(text: str) -> str:
    """Fix known quirks in Datasworn YAML that trip up PyYAML's safe loader.

    1. Anchor/alias names with dots or colons – replace all invalid chars with
       underscores (handles multi-segment names like ``&i18n.result.common_noun``
       and colon-prefixed names like ``&table:Planets.Peril``).
    2. Literal tab characters inside lines – replace with a space.
    3. Duplicate anchor names – append ``_N`` to make each anchor definition
       unique; aliases are rewritten to the FIRST (earliest) definition so they
       never reference an anchor that hasn't been declared yet.
    """
    # Step 1: Normalise anchor and alias names that contain characters invalid
    # in PyYAML anchor identifiers (dots, colons, etc.).  Match the full name
    # including those characters so nothing is left dangling.
    def _fix_name(m: re.Match[str]) -> str:
        sigil = m.group(1)  # & or *
        name = re.sub(r"[^A-Za-z0-9_]", "_", m.group(2))
        return sigil + name

    text = re.sub(r"([&*])([A-Za-z0-9_][A-Za-z0-9_.:]*)", _fix_name, text)

    # Step 2: Remove duplicate anchor definitions by suffixing a counter.
    # Aliases are rewritten to point to the FIRST definition so that references
    # before the later re-definitions continue to resolve correctly.
    anchor_counts: dict[str, int] = {}
    anchor_canonical: dict[str, str] = {}  # original_name -> first rewritten name

    def _rewrite_anchor(m: re.Match[str]) -> str:
        name = m.group(1)
        anchor_counts[name] = anchor_counts.get(name, 0) + 1
        new_name = f"{name}_{anchor_counts[name]}" if anchor_counts[name] > 1 else name
        if name not in anchor_canonical:
            anchor_canonical[name] = new_name  # only record the first occurrence
        return f"&{new_name}"

    text = re.sub(r"&([A-Za-z0-9_]+)", _rewrite_anchor, text)

    # Rewrite aliases to point to the first anchor definition.
    # If an alias name was never defined in this file, replace it with null
    # rather than letting PyYAML raise a ComposerError.
    def _rewrite_alias(m: re.Match[str]) -> str:
        name = m.group(1)
        canonical = anchor_canonical.get(name)
        if canonical is None:
            return "null"
        return f"*{canonical}"

    text = re.sub(r"\*([A-Za-z0-9_]+)", _rewrite_alias, text)

    # Replace tab characters outside of leading indentation
    sanitised_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip(" ")
        indent = line[: len(line) - len(stripped)]
        sanitised_lines.append(indent + stripped.replace("\t", " "))
    return "".join(sanitised_lines)


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(
            f"Cannot open data file {path.name}.\n"
            "Run  python src/fetch_data.py  first."
        ) from exc
    return yaml.safe_load(_sanitise_yaml(raw)) or {}


def _source_name(data: dict[str, Any], fallback: str) -> str:
    """Return a friendly game name from a YAML document's top-level _id."""
    return SOURCE_LABELS.get(data.get("_id", ""), fallback)


def _extract_moves(data: dict[str, Any], fallback_label: str) -> list[dict[str, Any]]:
    """Return a flat list of move dicts from a loaded YAML document."""
    source_name = _source_name(data, fallback_label)
    moves: list[dict[str, Any]] = []
    for cat_key, cat in (data.get("moves") or {}).items():
        if not isinstance(cat, dict):
            continue
        cat_name: str = cat.get("name", cat_key)
        for move_key, move in (cat.get("contents") or {}).items():
            if not isinstance(move, dict):
                continue
            moves.append(
                {
                    "source": source_name,
                    "category": cat_name,
                    "key": move_key,
                    "name": move.get("name", move_key),
                    "trigger": strip_markup(
                        (move.get("trigger") or {}).get("text", "")
                    ),
                    "text": strip_markup(move.get("text", "")),
                    "outcomes": {
                        k: strip_markup(v.get("text", "") if isinstance(v, dict) else v)
                        for k, v in (move.get("outcomes") or {}).items()
                    },
                    "roll_type": move.get("roll_type", "no_roll"),
                    "tables": [
                        {
                            "name": tbl.get("name", ""),
                            "rows": [
                                {
                                    "min": row.get("min"),
                                    "max": row.get("max"),
                                    "text": strip_markup(row.get("text", "")),
                                }
                                for row in (tbl.get("rows") or [])
                                if isinstance(row, dict)
                            ],
                        }
                        for tbl in (move.get("tables") or [])
                        if isinstance(tbl, dict)
                    ],
                }
            )
    return moves


def _extract_oracle_table(
    oracle: dict[str, Any],
    category: str,
    source_label: str,
    oracle_id: str = "",
) -> dict[str, Any] | None:
    """Return a single oracle-table dict, or None if not a rollable table."""
    rows = oracle.get("rows")
    if not rows:
        return None
    parsed: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        text = strip_markup(row.get("text") or "")
        text2 = strip_markup(row.get("text2") or "")
        if text and text2:
            display_text = f"{text}: {text2}"
        else:
            display_text = text or text2
        parsed.append(
            {
                "min": row.get("min"),
                "max": row.get("max"),
                "text": display_text,
            }
        )
    if not parsed:
        return None
    # cursed_version is stored under tags.<game_id>.cursed_version in Datasworn
    cursed_ref = ""
    tags = oracle.get("tags") or {}
    for _game, tag_data in tags.items():
        if isinstance(tag_data, dict) and "cursed_version" in tag_data:
            cursed_ref = tag_data["cursed_version"]
            break
    return {
        "source": source_label,
        "category": category,
        "name": oracle.get("name", ""),
        "oracle_id": oracle_id,
        "cursed_version": cursed_ref,
        "rows": parsed,
    }


def _walk_oracle_collection(
    node: dict[str, Any],
    category: str,
    source_label: str,
    out: list[dict[str, Any]],
    id_prefix: str = "",
) -> None:
    # Walk both 'contents' and 'collections' (Datasworn uses both)
    for section_key in ("contents", "collections"):
        section: dict[str, Any] = node.get(section_key) or {}
        for key, child in section.items():
            if not isinstance(child, dict):
                continue
            child_id = f"{id_prefix}/{key}" if id_prefix else key
            child_type = child.get("type", "")
            if child_type == "oracle_rollable":
                tbl = _extract_oracle_table(child, category, source_label, oracle_id=child_id)
                if tbl:
                    out.append(tbl)
            elif child_type == "oracle_collection":
                child_cat = child.get("name", category)
                _walk_oracle_collection(child, child_cat, source_label, out, id_prefix=child_id)
            else:
                # Heuristic: a rows key means it's a table; contents/collections mean recurse
                if "rows" in child:
                    tbl = _extract_oracle_table(child, category, source_label, oracle_id=child_id)
                    if tbl:
                        out.append(tbl)
                if "contents" in child or "collections" in child:
                    child_cat = child.get("name", category)
                    _walk_oracle_collection(child, child_cat, source_label, out, id_prefix=child_id)


def _extract_oracles(
    data: dict[str, Any], fallback_label: str
) -> list[dict[str, Any]]:
    """Return a flat list of oracle tables from a loaded YAML document."""
    source_name = _source_name(data, fallback_label)
    tables: list[dict[str, Any]] = []
    top_id = data.get("_id", "")
    for cat_key, cat in (data.get("oracles") or {}).items():
        if not isinstance(cat, dict):
            continue
        cat_name = cat.get("name", cat_key)
        id_prefix = f"{top_id}/oracles/{cat_key}" if top_id else cat_key
        _walk_oracle_collection(cat, cat_name, source_name, tables, id_prefix=id_prefix)
    return tables


def _extract_assets(
    data: dict[str, Any], fallback_label: str
) -> list[dict[str, Any]]:
    """Return a flat list of asset dicts from a loaded YAML document."""
    source_name = _source_name(data, fallback_label)
    assets: list[dict[str, Any]] = []
    for coll_key, coll in (data.get("assets") or {}).items():
        if not isinstance(coll, dict):
            continue
        # Derive category name: use collection's 'name', strip trailing " Assets"
        coll_raw_name = coll.get("name", coll_key)
        coll_cat = re.sub(r"\s+Assets?\s*$", "", coll_raw_name, flags=re.IGNORECASE).strip()
        for _asset_key, asset in (coll.get("contents") or {}).items():
            if not isinstance(asset, dict):
                continue
            category = asset.get("category") or coll_cat
            abilities = [
                strip_markup(ab.get("text", ""))
                for ab in (asset.get("abilities") or [])
                if isinstance(ab, dict) and ab.get("text")
            ]
            assets.append(
                {
                    "source": source_name,
                    "category": category,
                    "name": asset.get("name", _asset_key),
                    "requirement": strip_markup(asset.get("requirement") or ""),
                    "abilities": abilities,
                }
            )
    return assets


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

# Maps YAML top-level _id values to friendly game names.
SOURCE_LABELS: dict[str, str] = {
    "starforged": "Starforged",
    "sundered_isles": "Sundered Isles",
    "classic": "Ironsworn",
    "delve": "Ironsworn: Delve",
}

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


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Starforged / Sundered Isles Reference")
        self.geometry("800x600")
        self.minsize(780, 560)
        self.configure(bg=BG)
        self._configure_styles()
        self._load_data()
        self._build_ui()

    # ------------------------------------------------------------------
    # Style
    # ------------------------------------------------------------------

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
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

        # Listbox colours are set via direct widget options (no ttk)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------

    def _load_data(self) -> None:
        """Load all YAML data; raise SystemExit on missing files."""
        sf_raw = _load_yaml(SF_MOVES_YAML)
        self._sf_moves = _extract_moves(sf_raw, "Starforged")

        si_session_raw = _load_yaml(SI_MOVES_YAML)
        self._si_moves = _extract_moves(si_session_raw, "Sundered Isles")

        self._si_oracles: list[dict[str, Any]] = []
        if SI_ORACLES_DIR.is_dir():
            for yaml_file in sorted(SI_ORACLES_DIR.glob("*.yaml")):
                raw = _load_yaml(yaml_file)
                self._si_oracles.extend(_extract_oracles(raw, "Sundered Isles"))
        if CUSTOM_ORACLES_DIR.is_dir():
            for yaml_file in sorted(CUSTOM_ORACLES_DIR.glob("*.yaml")):
                raw = _load_yaml(yaml_file)
                self._si_oracles.extend(_extract_oracles(raw, "Sundered Isles"))

        self._sf_oracles: list[dict[str, Any]] = []
        if SF_ORACLES_DIR.is_dir():
            for yaml_file in sorted(SF_ORACLES_DIR.glob("*.yaml")):
                raw = _load_yaml(yaml_file)
                self._sf_oracles.extend(_extract_oracles(raw, "Starforged"))

        self._is_oracles: list[dict[str, Any]] = []
        if IS_ORACLES_DIR.is_dir():
            for yaml_file in sorted(IS_ORACLES_DIR.glob("*.yaml")):
                raw = _load_yaml(yaml_file)
                self._is_oracles.extend(_extract_oracles(raw, "Ironsworn"))

        self._sf_assets: list[dict[str, Any]] = []
        if SF_ASSETS_DIR.is_dir():
            for yaml_file in sorted(SF_ASSETS_DIR.glob("*.yaml")):
                raw = _load_yaml(yaml_file)
                self._sf_assets.extend(_extract_assets(raw, "Starforged"))

        self._si_assets: list[dict[str, Any]] = []
        if SI_ASSETS_DIR.is_dir():
            for yaml_file in sorted(SI_ASSETS_DIR.glob("*.yaml")):
                raw = _load_yaml(yaml_file)
                self._si_assets.extend(_extract_assets(raw, "Sundered Isles"))

        self._is_assets: list[dict[str, Any]] = []
        if IS_ASSETS_DIR.is_dir():
            for yaml_file in sorted(IS_ASSETS_DIR.glob("*.yaml")):
                raw = _load_yaml(yaml_file)
                self._is_assets.extend(_extract_assets(raw, "Ironsworn"))

        # Build a lookup from oracle_id → oracle dict, used for cursed die resolution.
        all_oracles = self._sf_oracles + self._si_oracles + self._is_oracles
        self._oracle_by_id: dict[str, dict[str, Any]] = {
            o["oracle_id"]: o for o in all_oracles if o.get("oracle_id")
        }

        # Load oracle bundles
        self._bundles: list[dict[str, Any]] = []
        if BUNDLES_YAML.exists():
            raw_bundles = _load_yaml(BUNDLES_YAML)
            self._bundles = raw_bundles.get("bundles") or []

    # ------------------------------------------------------------------
    # UI layout
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=6, pady=6)

        # Tab 1 – Moves
        moves_tab = ttk.Frame(notebook)
        notebook.add(moves_tab, text="  Moves  ")
        self._build_moves_tab(moves_tab)

        # Tab 2 – Oracles
        oracles_tab = ttk.Frame(notebook)
        notebook.add(oracles_tab, text="  Oracles  ")
        self._build_oracles_tab(oracles_tab)

        # Tab 3 – Assets
        assets_tab = ttk.Frame(notebook)
        notebook.add(assets_tab, text="  Assets  ")
        self._build_assets_tab(assets_tab)

        # Tab 4 – Bundles
        bundles_tab = ttk.Frame(notebook)
        notebook.add(bundles_tab, text="  Bundles  ")
        self._build_bundles_tab(bundles_tab)

    @staticmethod
    def _short_source(source: str) -> str:
        return {
            "Starforged": "SF",
            "Sundered Isles": "SI",
            "Ironsworn": "IS",
        }.get(source, source)

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _rebuild_option_menu(
        om: tk.OptionMenu, var: tk.StringVar, values: list[str]
    ) -> None:
        """Replace all entries in an OptionMenu with new values."""
        menu = om["menu"]
        menu.delete(0, "end")
        for val in values:
            menu.add_command(label=val, command=lambda v=val: var.set(v))

    # ------------------------------------------------------------------
    # Moves tab
    # ------------------------------------------------------------------

    def _build_moves_tab(self, parent: ttk.Frame) -> None:
        paned = tk.PanedWindow(
            parent, orient="horizontal",
            bg=BORDER, sashrelief="flat", sashwidth=5, bd=0, handlesize=0,
        )
        paned.pack(fill="both", expand=True)

        # --- Left panel: filter + listbox ---
        left = ttk.Frame(paned, style="Panel.TFrame")
        left.rowconfigure(5, weight=1)
        left.columnconfigure(0, weight=1)
        paned.add(left, minsize=160, width=230)

        ttk.Label(left, text="Game", style="Cat.TLabel").grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 2)
        )
        all_move_sources = sorted({m["source"] for m in self._sf_moves + self._si_moves})
        self._move_game_var = tk.StringVar(value="All")
        self._move_game_var.trace_add("write", lambda *_: self._on_move_game_change())
        move_game_om = tk.OptionMenu(left, self._move_game_var, "All", *all_move_sources)
        move_game_om.config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG,
                            highlightthickness=0, relief="flat", anchor="w", width=20)
        move_game_om["menu"].config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG)
        move_game_om.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))

        ttk.Label(left, text="Category", style="Cat.TLabel").grid(
            row=2, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        self._move_selected_cat = "All"
        all_move_cats = sorted({m["category"] for m in self._sf_moves + self._si_moves})
        self._move_cat_var = tk.StringVar(value="All")
        self._move_cat_var.trace_add("write", lambda *_: self._on_move_cat_change())
        self._move_cat_om = tk.OptionMenu(left, self._move_cat_var, "All", *all_move_cats)
        self._move_cat_om.config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG,
                                 highlightthickness=0, relief="flat", anchor="w", width=20)
        self._move_cat_om["menu"].config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG)
        self._move_cat_om.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 4))

        ttk.Label(left, text="Search", style="Cat.TLabel").grid(
            row=4, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        self._move_search_var = tk.StringVar()
        self._move_search_var.trace_add("write", lambda *_: self._refresh_move_list())
        search_entry = tk.Entry(
            left,
            textvariable=self._move_search_var,
            bg=PANEL_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            highlightthickness=1,
            highlightcolor=ACCENT,
            highlightbackground=BORDER,
        )
        search_entry.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 4))

        # List
        lf = ttk.Frame(left, style="Panel.TFrame")
        lf.grid(row=5, column=0, sticky="nsew", padx=4, pady=4)
        lf.rowconfigure(0, weight=1)
        lf.columnconfigure(0, weight=1)

        self._move_listbox = tk.Listbox(
            lf,
            bg=PANEL_BG,
            fg=FG,
            selectbackground=ACCENT,
            selectforeground=BG,
            activestyle="none",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 9),
        )
        self._move_listbox.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, command=self._move_listbox.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._move_listbox.configure(yscrollcommand=sb.set)
        self._move_listbox.bind("<<ListboxSelect>>", self._on_move_select)

        # --- Right panel: detail view ---
        right = ttk.Frame(paned, style="Panel.TFrame")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)
        paned.add(right, minsize=200)

        self._move_title_var = tk.StringVar(value="Select a move →")
        ttk.Label(
            right, textvariable=self._move_title_var, style="Title.TLabel"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))

        move_roll_bar = ttk.Frame(right, style="Panel.TFrame")
        move_roll_bar.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 4))
        self._move_roll_result_var = tk.StringVar(value="")
        ttk.Button(
            move_roll_bar,
            text="Roll d100",
            style="Accent.TButton",
            command=self._roll_move_table,
        ).pack(side="left", padx=(0, 8))
        ttk.Label(
            move_roll_bar, textvariable=self._move_roll_result_var, style="Title.TLabel"
        ).pack(side="left")
        move_roll_bar.grid_remove()
        self._move_roll_bar = move_roll_bar

        self._move_text = self._make_textbox(right)
        self._move_text.grid(row=2, column=0, sticky="nsew", padx=6, pady=4)

        # Populate
        self._moves_visible: list[dict[str, Any]] = []
        self._current_move: dict[str, Any] | None = None
        self._refresh_move_list()

    def _on_move_game_change(self) -> None:
        game_filter = self._move_game_var.get()
        all_moves = self._sf_moves + self._si_moves
        if game_filter == "All":
            cats = sorted({m["category"] for m in all_moves})
        else:
            cats = sorted({m["category"] for m in all_moves if m["source"] == game_filter})
        self._rebuild_option_menu(self._move_cat_om, self._move_cat_var, ["All"] + cats)
        if self._move_selected_cat not in cats:
            self._move_selected_cat = "All"
            self._move_cat_var.set("All")
        self._refresh_move_list()

    def _on_move_cat_change(self) -> None:
        self._move_selected_cat = self._move_cat_var.get()
        self._refresh_move_list()

    def _refresh_move_list(self) -> None:
        game_filter = self._move_game_var.get()
        cat_filter = self._move_selected_cat
        query = self._move_search_var.get().strip().lower()

        all_moves = self._sf_moves + self._si_moves

        filtered: list[dict[str, Any]] = []
        for m in all_moves:
            if game_filter != "All" and m["source"] != game_filter:
                continue
            if cat_filter != "All" and m["category"] != cat_filter:
                continue
            if query and query not in m["name"].lower() and query not in m["category"].lower():
                continue
            filtered.append(m)

        filtered.sort(key=lambda m: (m["source"], m["category"], m["name"]))
        self._moves_visible = filtered
        self._move_listbox.delete(0, tk.END)
        for m in filtered:
            if game_filter == "All":
                label = f"[{self._short_source(m['source'])}]  {m['category']} › {m['name']}"
            else:
                label = f"{m['category']} › {m['name']}"
            self._move_listbox.insert(tk.END, label)

    def _on_move_select(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        selection = self._move_listbox.curselection()
        if not selection:
            return
        move = self._moves_visible[selection[0]]
        self._move_roll_result_var.set("")
        self._display_move(move)

    def _display_move(self, move: dict[str, Any], highlight_roll: int | None = None) -> None:
        self._current_move = move
        tables = move.get("tables", [])
        if tables:
            self._move_roll_bar.grid()
        else:
            self._move_roll_bar.grid_remove()

        self._move_title_var.set(f"{move['name']}  —  {move['category']}")

        lines: list[tuple[str, str]] = []

        lines.append(("cat", f"{move['source']}  ·  {move['category']}"))
        lines.append(("body", ""))
        if move["trigger"]:
            lines.append(("bold", "Trigger:"))
            lines.append(("body", move["trigger"]))
            lines.append(("body", ""))

        if move["text"]:
            lines.append(("bold", "Move text:"))
            lines.append(("body", move["text"]))

        if move["outcomes"]:
            lines.append(("body", ""))
            lines.append(("bold", "Outcomes:"))
            for outcome_key, outcome_txt in move["outcomes"].items():
                tag = {
                    "strong_hit": "strong",
                    "weak_hit": "weak",
                    "miss": "miss",
                }.get(outcome_key, "body")
                lines.append((tag, f"  {outcome_key.replace('_', ' ').title()}"))
                lines.append(("body", f"    {outcome_txt}"))
                lines.append(("body", ""))

        for i, tbl in enumerate(tables):
            lines.append(("body", ""))
            lines.append(("bold", tbl["name"] + ":"))
            lines.append(("body", ""))
            for row in tbl.get("rows", []):
                rmin = row.get("min")
                rmax = row.get("max")
                text = row.get("text", "")
                if rmin is None or rmax is None:
                    range_str = "    –   "
                elif rmin == rmax:
                    range_str = f"{rmin:>3}      "
                else:
                    range_str = f"{rmin:>3}–{rmax:<3}"
                tag = "body"
                if i == 0 and highlight_roll is not None and rmin is not None and rmax is not None:
                    if rmin <= highlight_roll <= rmax:
                        tag = "strong"
                lines.append((tag, f"  {range_str}  {text}"))

        self._set_text_lines(self._move_text, lines)

    def _roll_move_table(self) -> None:
        if self._current_move is None:
            return
        tables = self._current_move.get("tables", [])
        if not tables:
            return
        tbl = tables[0]
        roll = random.randint(1, 100)
        matching = ""
        for row in tbl.get("rows", []):
            rmin = row.get("min")
            rmax = row.get("max")
            if rmin is not None and rmax is not None and rmin <= roll <= rmax:
                matching = row.get("text", "")
                break
        self._move_roll_result_var.set(f"Rolled {roll}  \u2192  {matching}")
        self._display_move(self._current_move, highlight_roll=roll)

    # ------------------------------------------------------------------
    # Oracles tab
    # ------------------------------------------------------------------

    def _build_oracles_tab(self, parent: ttk.Frame) -> None:
        paned = tk.PanedWindow(
            parent, orient="horizontal",
            bg=BORDER, sashrelief="flat", sashwidth=5, bd=0, handlesize=0,
        )
        paned.pack(fill="both", expand=True)

        # Left panel
        left = ttk.Frame(paned, style="Panel.TFrame")
        left.rowconfigure(5, weight=1)
        left.columnconfigure(0, weight=1)
        paned.add(left, minsize=160, width=230)

        ttk.Label(left, text="Game", style="Cat.TLabel").grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 2)
        )
        all_oracle_sources = sorted(
            {o["source"] for o in self._sf_oracles + self._si_oracles + self._is_oracles}
        )
        self._oracle_game_var = tk.StringVar(value="All")
        self._oracle_game_var.trace_add("write", lambda *_: self._on_oracle_game_change())
        game_om = tk.OptionMenu(left, self._oracle_game_var, "All", *all_oracle_sources)
        game_om.config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG,
                       highlightthickness=0, relief="flat", anchor="w", width=20)
        game_om["menu"].config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG)
        game_om.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))

        ttk.Label(left, text="Category", style="Cat.TLabel").grid(
            row=2, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        all_oracle_cats = sorted(
            {o["category"] for o in self._sf_oracles + self._si_oracles + self._is_oracles}
        )
        self._oracle_selected_cat = "All"
        self._oracle_cat_var = tk.StringVar(value="All")
        self._oracle_cat_var.trace_add("write", lambda *_: self._on_oracle_cat_change())
        self._oracle_cat_om = tk.OptionMenu(left, self._oracle_cat_var, "All", *all_oracle_cats)
        self._oracle_cat_om.config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG,
                                   highlightthickness=0, relief="flat", anchor="w", width=20)
        self._oracle_cat_om["menu"].config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG)
        self._oracle_cat_om.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 4))

        ttk.Label(left, text="Search", style="Cat.TLabel").grid(
            row=4, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        self._oracle_search_var = tk.StringVar()
        self._oracle_search_var.trace_add("write", lambda *_: self._refresh_oracle_list())
        ok_entry = tk.Entry(
            left,
            textvariable=self._oracle_search_var,
            bg=PANEL_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            highlightthickness=1,
            highlightcolor=ACCENT,
            highlightbackground=BORDER,
        )
        ok_entry.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 4))

        lf = ttk.Frame(left, style="Panel.TFrame")
        lf.grid(row=5, column=0, sticky="nsew", padx=4, pady=4)
        lf.rowconfigure(0, weight=1)
        lf.columnconfigure(0, weight=1)

        self._oracle_listbox = tk.Listbox(
            lf,
            bg=PANEL_BG,
            fg=FG,
            selectbackground=ACCENT,
            selectforeground=BG,
            activestyle="none",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 9),
        )
        self._oracle_listbox.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, command=self._oracle_listbox.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._oracle_listbox.configure(yscrollcommand=sb.set)
        self._oracle_listbox.bind("<<ListboxSelect>>", self._on_oracle_select)

        # Right panel
        right = ttk.Frame(paned, style="Panel.TFrame")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)
        paned.add(right, minsize=200)

        self._oracle_title_var = tk.StringVar(value="Select an oracle →")
        ttk.Label(
            right, textvariable=self._oracle_title_var, style="Title.TLabel"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))

        roll_bar = ttk.Frame(right, style="Panel.TFrame")
        roll_bar.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 4))
        self._roll_result_var = tk.StringVar(value="")
        ttk.Button(
            roll_bar,
            text="Roll d100",
            style="Accent.TButton",
            command=self._roll_oracle,
        ).pack(side="left", padx=(0, 8))

        # Cursed Die controls
        self._cursed_enabled_var = tk.BooleanVar(value=False)
        cursed_cb = tk.Checkbutton(
            roll_bar, text="☠ Cursed Die",
            variable=self._cursed_enabled_var,
            bg=PANEL_BG, fg=HIT_MISS, selectcolor=PANEL_BG,
            activebackground=PANEL_BG, activeforeground=HIT_MISS,
            font=("Segoe UI", 9), relief="flat", bd=0,
            highlightthickness=0,
        )
        cursed_cb.pack(side="left", padx=(0, 4))

        self._cursed_die_var = tk.StringVar(value="d10")
        cursed_die_om = tk.OptionMenu(roll_bar, self._cursed_die_var, "d10", "d12", "d20")
        cursed_die_om.config(
            bg=PANEL_BG, fg=HIT_MISS, activebackground=SEL_BG, activeforeground=HIT_MISS,
            highlightthickness=0, relief="flat", width=3,
        )
        cursed_die_om["menu"].config(bg=PANEL_BG, fg=HIT_MISS, activebackground=SEL_BG, activeforeground=HIT_MISS)
        cursed_die_om.pack(side="left", padx=(0, 12))

        ttk.Label(roll_bar, textvariable=self._roll_result_var, style="Title.TLabel").pack(
            side="left"
        )

        self._oracle_text = self._make_textbox(right)
        self._oracle_text.grid(row=2, column=0, sticky="nsew", padx=6, pady=4)

        self._oracles_visible: list[dict[str, Any]] = []
        self._current_oracle: dict[str, Any] | None = None
        self._refresh_oracle_list()

    def _on_oracle_game_change(self) -> None:
        # Rebuild category list to only include categories present in the selected game,
        # then reset the category filter so we don't keep a stale selection.
        game_filter = self._oracle_game_var.get() or "All"
        all_oracles = self._sf_oracles + self._si_oracles + self._is_oracles
        if game_filter == "All":
            cats = sorted({o["category"] for o in all_oracles})
        else:
            cats = sorted({o["category"] for o in all_oracles if o["source"] == game_filter})
        self._rebuild_option_menu(self._oracle_cat_om, self._oracle_cat_var, ["All"] + cats)
        # Reset category selection only if the current choice no longer exists
        if self._oracle_selected_cat not in cats:
            self._oracle_selected_cat = "All"
            self._oracle_cat_var.set("All")
        self._refresh_oracle_list()

    def _on_oracle_cat_change(self) -> None:
        self._oracle_selected_cat = self._oracle_cat_var.get()
        self._refresh_oracle_list()

    def _refresh_oracle_list(self) -> None:
        game_filter = self._oracle_game_var.get() or "All"
        cat_filter = self._oracle_selected_cat
        query = self._oracle_search_var.get().strip().lower()

        all_oracles = self._sf_oracles + self._si_oracles + self._is_oracles
        filtered: list[dict[str, Any]] = []
        for o in all_oracles:
            if game_filter != "All" and o["source"] != game_filter:
                continue
            if cat_filter != "All" and o["category"] != cat_filter:
                continue
            if query and query not in o["name"].lower() and query not in o["category"].lower() and query not in o["source"].lower():
                continue
            filtered.append(o)

        filtered.sort(key=lambda o: (o["source"], o["category"], o["name"]))
        self._oracles_visible = filtered
        self._oracle_listbox.delete(0, tk.END)
        for o in filtered:
            label = f"[{self._short_source(o['source'])}]  {o['category']} › {o['name']}"
            self._oracle_listbox.insert(tk.END, label)

    def _on_oracle_select(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        selection = self._oracle_listbox.curselection()
        if not selection:
            return
        oracle = self._oracles_visible[selection[0]]
        self._current_oracle = oracle
        self._roll_result_var.set("")
        self._display_oracle(oracle)

    def _display_oracle(
        self,
        oracle: dict[str, Any],
        highlight_roll: int | None = None,
        cursed: bool = False,
    ) -> None:
        name = oracle["name"]
        if cursed:
            name = "☠  " + name
        self._oracle_title_var.set(f"{name}  —  {oracle['category']}")
        lines: list[tuple[str, str]] = []
        src_label = oracle["source"] + "  ·  " + oracle["category"]
        if cursed:
            src_label += "  [☠ CURSED]"
        lines.append(("miss" if cursed else "cat", src_label))
        lines.append(("body", ""))
        for row in oracle.get("rows", []):
            rmin = row.get("min")
            rmax = row.get("max")
            text = row.get("text", "")
            if rmin is None or rmax is None:
                range_str = "    –   "
            elif rmin != rmax:
                range_str = f"{rmin:>3}–{rmax:<3}"
            else:
                range_str = f"{rmin:>3}      "
            tag = "body"
            if highlight_roll is not None and rmin is not None and rmax is not None:
                if rmin <= highlight_roll <= rmax:
                    tag = "strong"
            lines.append((tag, f"  {range_str}  {text}"))
        self._set_text_lines(self._oracle_text, lines)

    def _roll_oracle(self) -> None:
        if self._current_oracle is None:
            return
        roll = random.randint(1, 100)
        # Cursed die logic
        cursed = False
        cursed_roll_str = ""
        if self._cursed_enabled_var.get() and self._current_oracle.get("cursed_version"):
            die_str = self._cursed_die_var.get()   # "d10", "d12", or "d20"
            die_sides = int(die_str[1:])
            cursed_roll = random.randint(1, die_sides)
            cursed = (cursed_roll == die_sides)
            cursed_roll_str = f"  |  ☠ {die_str}: {cursed_roll}{'  → CURSED!' if cursed else ''}"
        # Resolve which table to display/match against
        display_oracle = self._current_oracle
        if cursed:
            cursed_id = self._current_oracle["cursed_version"]
            cursed_oracle = self._oracle_by_id.get(cursed_id)
            if cursed_oracle:
                display_oracle = cursed_oracle
        matching = ""
        for row in display_oracle.get("rows", []):
            rmin = row.get("min")
            rmax = row.get("max")
            if rmin is not None and rmax is not None and rmin <= roll <= rmax:
                matching = row.get("text", "")
                break
        self._roll_result_var.set(f"Rolled {roll}  →  {matching}{cursed_roll_str}")
        self._display_oracle(display_oracle, highlight_roll=roll, cursed=cursed)

    # ------------------------------------------------------------------
    # Assets tab
    # ------------------------------------------------------------------

    def _build_assets_tab(self, parent: ttk.Frame) -> None:
        paned = tk.PanedWindow(
            parent, orient="horizontal",
            bg=BORDER, sashrelief="flat", sashwidth=5, bd=0, handlesize=0,
        )
        paned.pack(fill="both", expand=True)

        # --- Left panel: filter + listbox ---
        left = ttk.Frame(paned, style="Panel.TFrame")
        left.rowconfigure(5, weight=1)
        left.columnconfigure(0, weight=1)
        paned.add(left, minsize=160, width=230)

        ttk.Label(left, text="Game", style="Cat.TLabel").grid(
            row=0, column=0, sticky="w", padx=8, pady=(8, 2)
        )
        all_sources = sorted({a["source"] for a in self._sf_assets + self._si_assets + self._is_assets})
        self._asset_game_var = tk.StringVar(value="All")
        self._asset_game_var.trace_add("write", lambda *_: self._on_asset_game_change())
        game_om = tk.OptionMenu(left, self._asset_game_var, "All", *all_sources)
        game_om.config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG,
                       highlightthickness=0, relief="flat", anchor="w", width=20)
        game_om["menu"].config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG)
        game_om.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))

        ttk.Label(left, text="Category", style="Cat.TLabel").grid(
            row=2, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        all_cats = sorted({a["category"] for a in self._sf_assets + self._si_assets + self._is_assets})
        self._asset_selected_cat = "All"
        self._asset_cat_var = tk.StringVar(value="All")
        self._asset_cat_var.trace_add("write", lambda *_: self._on_asset_cat_change())
        self._asset_cat_om = tk.OptionMenu(left, self._asset_cat_var, "All", *all_cats)
        self._asset_cat_om.config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG,
                                  highlightthickness=0, relief="flat", anchor="w", width=20)
        self._asset_cat_om["menu"].config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG)
        self._asset_cat_om.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 4))

        ttk.Label(left, text="Search", style="Cat.TLabel").grid(
            row=4, column=0, sticky="w", padx=8, pady=(4, 2)
        )
        self._asset_search_var = tk.StringVar()
        self._asset_search_var.trace_add("write", lambda *_: self._refresh_asset_list())
        search_entry = tk.Entry(
            left,
            textvariable=self._asset_search_var,
            bg=PANEL_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            highlightthickness=1,
            highlightcolor=ACCENT,
            highlightbackground=BORDER,
        )
        search_entry.grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 4))

        lf = ttk.Frame(left, style="Panel.TFrame")
        lf.grid(row=5, column=0, sticky="nsew", padx=4, pady=4)
        lf.rowconfigure(0, weight=1)
        lf.columnconfigure(0, weight=1)

        self._asset_listbox = tk.Listbox(
            lf,
            bg=PANEL_BG,
            fg=FG,
            selectbackground=ACCENT,
            selectforeground=BG,
            activestyle="none",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 9),
        )
        self._asset_listbox.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, command=self._asset_listbox.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._asset_listbox.configure(yscrollcommand=sb.set)
        self._asset_listbox.bind("<<ListboxSelect>>", self._on_asset_select)

        # --- Right panel: detail view ---
        right = ttk.Frame(paned, style="Panel.TFrame")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        paned.add(right, minsize=200)

        title_bar = ttk.Frame(right, style="Panel.TFrame")
        title_bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(10, 2))
        title_bar.columnconfigure(1, weight=1)

        ttk.Button(
            title_bar,
            text="Random",
            style="Accent.TButton",
            command=self._pick_random_asset,
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._asset_title_var = tk.StringVar(value="Select an asset →")
        ttk.Label(
            title_bar, textvariable=self._asset_title_var, style="Title.TLabel"
        ).grid(row=0, column=1, sticky="w")

        self._asset_text = self._make_textbox(right)
        self._asset_text.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)

        self._assets_visible: list[dict[str, Any]] = []
        self._refresh_asset_category_options()
        self._refresh_asset_list()

    def _on_asset_game_change(self) -> None:
        self._refresh_asset_category_options()
        self._refresh_asset_list()

    def _on_asset_cat_change(self) -> None:
        self._asset_selected_cat = self._asset_cat_var.get()
        self._refresh_asset_list()

    def _refresh_asset_category_options(self) -> None:
        game_filter = self._asset_game_var.get()
        all_assets = self._sf_assets + self._si_assets + self._is_assets
        if game_filter == "All":
            cats = sorted({a["category"] for a in all_assets})
        else:
            cats = sorted({a["category"] for a in all_assets if a["source"] == game_filter})

        valid_values = ["All"] + cats
        self._rebuild_option_menu(self._asset_cat_om, self._asset_cat_var, valid_values)
        if self._asset_selected_cat not in valid_values:
            self._asset_selected_cat = "All"
            self._asset_cat_var.set("All")

    def _refresh_asset_list(self) -> None:
        game_filter = self._asset_game_var.get()
        cat_filter = self._asset_selected_cat
        query = self._asset_search_var.get().strip().lower()

        all_assets = self._sf_assets + self._si_assets + self._is_assets

        filtered: list[dict[str, Any]] = []
        for a in all_assets:
            if game_filter != "All" and a["source"] != game_filter:
                continue
            if cat_filter != "All" and a["category"] != cat_filter:
                continue
            if query and query not in a["name"].lower() and query not in a["category"].lower():
                continue
            filtered.append(a)

        filtered.sort(key=lambda a: (a["source"], a["category"], a["name"]))
        self._assets_visible = filtered
        self._asset_listbox.delete(0, tk.END)
        for a in filtered:
            label = f"[{self._short_source(a['source'])}]  {a['category']} › {a['name']}"
            self._asset_listbox.insert(tk.END, label)

    def _pick_random_asset(self) -> None:
        if not self._assets_visible:
            messagebox.showinfo("No assets", "No assets match the current filters.")
            return

        idx = random.randrange(len(self._assets_visible))
        self._asset_listbox.selection_clear(0, tk.END)
        self._asset_listbox.selection_set(idx)
        self._asset_listbox.activate(idx)
        self._asset_listbox.see(idx)
        self._display_asset(self._assets_visible[idx])

    def _on_asset_select(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        selection = self._asset_listbox.curselection()
        if not selection:
            return
        asset = self._assets_visible[selection[0]]
        self._display_asset(asset)

    def _display_asset(self, asset: dict[str, Any]) -> None:
        self._asset_title_var.set(f"{asset['name']}  —  {asset['category']}")

        lines: list[tuple[str, str]] = []
        lines.append(("cat", f"{asset['source']}  ·  {asset['category']}"))
        lines.append(("body", ""))

        if asset["requirement"]:
            lines.append(("bold", f"Requirement:  {asset['requirement']}"))
            lines.append(("body", ""))

        for i, ability_text in enumerate(asset["abilities"], 1):
            lines.append(("bold", f"Ability {i}"))
            lines.append(("body", ability_text))
            lines.append(("body", ""))

        self._set_text_lines(self._asset_text, lines)

    # ------------------------------------------------------------------
    # Bundles tab
    # ------------------------------------------------------------------

    def _build_bundles_tab(self, parent: ttk.Frame) -> None:
        paned = tk.PanedWindow(
            parent, orient="horizontal",
            bg=BORDER, sashrelief="flat", sashwidth=5, bd=0, handlesize=0,
        )
        paned.pack(fill="both", expand=True)

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
        game_om = tk.OptionMenu(left, self._bundle_game_var, "All", *all_games)
        game_om.config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG,
                       highlightthickness=0, relief="flat", anchor="w", width=20)
        game_om["menu"].config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG)
        game_om.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        ttk.Label(left, text="Bundles", style="Cat.TLabel").grid(
            row=2, column=0, sticky="w", padx=8, pady=(0, 2)
        )

        lf = ttk.Frame(left, style="Panel.TFrame")
        lf.grid(row=3, column=0, sticky="nsew", padx=4, pady=4)
        lf.rowconfigure(0, weight=1)
        lf.columnconfigure(0, weight=1)

        self._bundle_listbox = tk.Listbox(
            lf,
            bg=PANEL_BG, fg=FG,
            selectbackground=ACCENT, selectforeground=BG,
            activestyle="none", relief="flat", borderwidth=0,
            highlightthickness=0, font=("Segoe UI", 9),
        )
        self._bundle_listbox.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lf, command=self._bundle_listbox.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._bundle_listbox.configure(yscrollcommand=sb.set)
        self._bundle_listbox.bind("<<ListboxSelect>>", self._on_bundle_select)

        # --- Right panel ---
        right = ttk.Frame(paned, style="Panel.TFrame")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)
        paned.add(right, minsize=200)

        # Title bar
        title_bar = ttk.Frame(right, style="Panel.TFrame")
        title_bar.grid(row=0, column=0, sticky="ew", padx=6, pady=(10, 2))
        title_bar.columnconfigure(1, weight=1)

        self._bundle_title_var = tk.StringVar(value="Select a bundle →")
        ttk.Label(
            title_bar, textvariable=self._bundle_title_var, style="Title.TLabel"
        ).grid(row=0, column=0, sticky="w")

        # Roll bar
        roll_bar = ttk.Frame(right, style="Panel.TFrame")
        roll_bar.grid(row=1, column=0, sticky="ew", padx=6, pady=(2, 4))

        ttk.Button(
            roll_bar, text="Roll All", style="Accent.TButton",
            command=self._roll_bundle,
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        # Cursed die controls
        self._bundle_cursed_var = tk.BooleanVar(value=False)
        cursed_check = tk.Checkbutton(
            roll_bar, text="☠ Cursed Die",
            variable=self._bundle_cursed_var,
            bg=PANEL_BG, fg=FG, selectcolor=PANEL_BG,
            activebackground=PANEL_BG, activeforeground=ACCENT,
            font=("Segoe UI", 9), relief="flat", bd=0,
        )
        cursed_check.grid(row=0, column=1, sticky="w", padx=(0, 6))

        self._bundle_cursed_die_var = tk.StringVar(value="d10")
        die_om = tk.OptionMenu(roll_bar, self._bundle_cursed_die_var, "d10", "d12", "d20")
        die_om.config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG,
                      highlightthickness=0, relief="flat", width=4)
        die_om["menu"].config(bg=PANEL_BG, fg=FG, activebackground=ACCENT, activeforeground=BG)
        die_om.grid(row=0, column=2, sticky="w")

        # Results text
        self._bundle_text = self._make_textbox(right)
        self._bundle_text.grid(row=2, column=0, sticky="nsew", padx=4, pady=(0, 4))

        # State
        self._current_bundle: dict[str, Any] | None = None
        self._bundles_visible: list[dict[str, Any]] = []
        self._refresh_bundle_list()

    def _refresh_bundle_list(self) -> None:
        game_filter = self._bundle_game_var.get() or "All"
        filtered = [
            b for b in self._bundles
            if game_filter == "All" or b.get("game") == game_filter
        ]
        self._bundles_visible = filtered
        self._bundle_listbox.delete(0, tk.END)
        for b in filtered:
            game_tag = f"[{self._short_source(b.get('game', ''))}]  " if b.get("game") else ""
            self._bundle_listbox.insert(tk.END, game_tag + b.get("name", ""))

    def _on_bundle_select(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        selection = self._bundle_listbox.curselection()
        if not selection:
            return
        self._current_bundle = self._bundles_visible[selection[0]]
        bundle = self._current_bundle
        if bundle is None:
            return
        self._bundle_title_var.set(bundle.get("name", ""))
        lines: list[tuple[str, str]] = []
        lines.append(("cat", f"{bundle.get('game', '')}  —  {len(bundle.get('rolls', []))} roll steps"))
        lines.append(("body", ""))
        for item in bundle.get("rolls", []):
            label = item.get("label", "?")
            count = item.get("count", 1)
            cursed_id = item.get("cursed_oracle_id", "")
            cascade = item.get("cascade_from", "")
            extras = []
            if count > 1:
                extras.append(f"×{count}")
            if cursed_id:
                extras.append("☠")
            if cascade:
                extras.append(f"→ based on {cascade}")
            suffix = "  " + "  ".join(extras) if extras else ""
            lines.append(("bold", f"  {label}{suffix}"))
            if item.get("note"):
                lines.append(("cat", f"    ↳ {item['note']}"))
        self._set_text_lines(self._bundle_text, lines)

    def _roll_bundle(self) -> None:
        if self._current_bundle is None:
            return

        use_cursed = self._bundle_cursed_var.get()
        die_str = self._bundle_cursed_die_var.get()
        die_sides = int(die_str[1:])

        lines: list[tuple[str, str]] = []
        lines.append(("cat", self._current_bundle.get("name", "") + "  —  " + self._current_bundle.get("game", "")))
        lines.append(("body", ""))

        # Track label → last result text so cascade can look it up
        label_results: dict[str, str] = {}

        for item in self._current_bundle.get("rolls", []):
            label = item.get("label", "?")
            count = item.get("count", 1)
            note = item.get("note", "")

            # Resolve oracle_id: direct or cascade
            oracle_id = item.get("oracle_id", "")
            if item.get("cascade_from"):
                source_label = item["cascade_from"]
                source_text = label_results.get(source_label, "")
                cascade_map: dict[str, str] = item.get("cascade_map") or {}
                # Exact match first; fall back to prefix match for text+text2 combined rows
                oracle_id = cascade_map.get(source_text, "")
                if not oracle_id:
                    for key, val in cascade_map.items():
                        if source_text.startswith(key):
                            oracle_id = val
                            break
                if not oracle_id:
                    lines.append(("bold", f"  {label}"))
                    lines.append(("miss", f"    [No cascade match for {source_label}={source_text!r}]"))
                    lines.append(("body", ""))
                    continue

            oracle = self._oracle_by_id.get(oracle_id)
            if oracle is None:
                lines.append(("bold", f"  {label}"))
                lines.append(("miss", f"    [Oracle not found: {oracle_id}]"))
                lines.append(("body", ""))
                continue

            cursed_oracle_id = item.get("cursed_oracle_id", "")

            for roll_num in range(count):
                roll = random.randint(1, 100)
                roll_label = label if count == 1 else f"{label} #{roll_num + 1}"

                # Cursed die
                cursed = False
                cursed_suffix = ""
                if use_cursed and cursed_oracle_id:
                    cursed_roll = random.randint(1, die_sides)
                    cursed = (cursed_roll == die_sides)
                    cursed_suffix = f"  ☠{die_str}:{cursed_roll}" + ("→CURSED" if cursed else "")

                # Resolve table
                active_oracle = oracle
                if cursed:
                    co = self._oracle_by_id.get(cursed_oracle_id)
                    if co:
                        active_oracle = co

                # Find matching row
                result_text = ""
                for row in active_oracle.get("rows", []):
                    rmin = row.get("min")
                    rmax = row.get("max")
                    if rmin is not None and rmax is not None and rmin <= roll <= rmax:
                        result_text = row.get("text", "")
                        break

                # Store last result for cascade lookup (use first roll only)
                if roll_num == 0:
                    label_results[label] = result_text

                if cursed:
                    lines.append(("miss", f"  {roll_label}  [{roll}]{cursed_suffix}"))
                    lines.append(("strong", f"    ☠ {result_text}"))
                else:
                    lines.append(("bold", f"  {roll_label}  [{roll}]"))
                    lines.append(("body", f"    {result_text}"))

            if note:
                lines.append(("cat", f"    ↳ {note}"))
            lines.append(("body", ""))

        self._set_text_lines(self._bundle_text, lines)

    # ------------------------------------------------------------------
    # Shared text helpers
    # ------------------------------------------------------------------

    def _make_textbox(self, parent: tk.Widget) -> tk.Text:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        txt = tk.Text(
            frame,
            bg=PANEL_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            wrap="word",
            font=("Segoe UI", 10),
            padx=8,
            pady=8,
            state="disabled",
            cursor="arrow",
        )
        txt.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(frame, command=txt.yview)
        sb.grid(row=0, column=1, sticky="ns")
        txt.configure(yscrollcommand=sb.set)

        # Tags
        txt.tag_configure("bold", font=("Segoe UI", 10, "bold"), foreground=ACCENT)
        txt.tag_configure("cat", font=("Segoe UI", 9, "italic"), foreground=ACCENT2)
        txt.tag_configure("strong", foreground=HIT_STRONG, font=("Segoe UI", 10, "bold"))
        txt.tag_configure("weak", foreground=HIT_WEAK, font=("Segoe UI", 10, "bold"))
        txt.tag_configure("miss", foreground=HIT_MISS, font=("Segoe UI", 10, "bold"))
        txt.tag_configure("body", foreground=FG, font=("Segoe UI", 10))

        # Store the frame alongside the text widget so grid works on the frame
        txt._container_frame = frame  # type: ignore[attr-defined]
        return txt

    def _set_text_lines(
        self, txt: tk.Text, lines: list[tuple[str, str]]
    ) -> None:
        txt.configure(state="normal")
        txt.delete("1.0", tk.END)
        for tag, text in lines:
            txt.insert(tk.END, text + "\n", tag)
        txt.configure(state="disabled")
        txt.see("1.0")


# Override .grid so that calls to txt.grid(...) reach the container frame.
_orig_grid = tk.Text.grid


def _patched_grid(self: tk.Text, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
    frame = getattr(self, "_container_frame", None)
    if frame is not None:
        frame.grid(*args, **kwargs)
    else:
        _orig_grid(self, *args, **kwargs)


tk.Text.grid = _patched_grid  # type: ignore[method-assign]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
