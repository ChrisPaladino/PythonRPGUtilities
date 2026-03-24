"""Launch starforged_app without a console window.

On Windows, .pyw files are automatically run with pythonw.exe (no console).
Double-click this file, or run:  pythonw run.pyw
"""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
runpy.run_module("starforged_app", run_name="__main__")
