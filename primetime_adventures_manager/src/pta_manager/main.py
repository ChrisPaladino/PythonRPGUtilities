"""
Entry point for Primetime Adventures Manager.
"""
import customtkinter as ctk
from pta_manager.ui.main_window import MainWindow


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
