"""
Top-level launcher. Run with: python run.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pta_manager.main import main

main()
