# Code Review Findings

## RPG_Generator/logic.py
- `generate_npc_age`, `generate_npc`, `generate_name`, and `generate_themes` are defined twice. The second block (lines ~253-297) overrides the earlier implementations, so callers silently get the later behavior (e.g., `generate_name` returns concatenated names without spaces instead of the space-separated version defined earlier). This shadowing makes maintenance harder and changes output without warning. 【F:RPG_Generator/logic.py†L63-L94】【F:RPG_Generator/logic.py†L253-L297】

## LitM Oracles/main.py
- The module performs five JSON reads at import time without any error handling. Missing or malformed data files will crash the program before the UI appears, and importing the module in another script will try to open files immediately. Wrapping these loads or deferring them to runtime would improve resiliency. 【F:LitM Oracles/main.py†L7-L24】
- In `show_conflict`, the text widget is cleared twice in succession (`result_textbox.delete` is called on consecutive lines), which is redundant and suggests copy/paste noise. 【F:LitM Oracles/main.py†L186-L200】
- The Tkinter window is constructed and started at the top level, so simply importing `main.py` launches the GUI and blocks. This makes the module unusable as a library and complicates testing. Guarding the startup logic with `if __name__ == "__main__":` would avoid these side effects. 【F:LitM Oracles/main.py†L471-L504】

## Action Story Trademark Manager/ActionStoryTrademarkManager.py
- The module changes the process working directory on import (`os.chdir(script_dir)`). That side effect can break relative paths for any caller that imports this file instead of running it as a script. Using absolute paths without mutating global state would be safer. 【F:Action Story Trademark Manager/ActionStoryTrademarkManager.py†L7-L10】
- `view_trademark_details` splits the listbox entry on `":"` and assumes exactly three parts, so any trademark fields containing a colon will raise a `ValueError` and break selection. This parsing approach is brittle and should be replaced with an ID lookup or a more robust delimiter strategy. 【F:Action Story Trademark Manager/ActionStoryTrademarkManager.py†L132-L146】

## General
- Several GUI modules (e.g., `Paragraph Count/CountParagraphs.py`, `LitM Oracles/main.py`) do not validate external dependencies at startup (Tkinter data files, `pyttsx3` voices, etc.), so runtime failures will surface as stack traces rather than user-friendly errors. Consider defensive checks for required resources before constructing the UI. 【F:Paragraph Count/CountParagraphs.py†L1-L82】【F:LitM Oracles/main.py†L7-L24】
