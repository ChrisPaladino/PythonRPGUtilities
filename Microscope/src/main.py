"""
Microscope Solo Play - Main Entry Point

A desktop application for playing the tabletop RPG Microscope in solo mode.
Based on the game by Ben Robbins.

This application enforces rules, tracks state, and guides the player through
the structured creative process of building a history from the outside-in.
"""

from ui import MicroscopeApp


def main():
    """Main entry point for the Microscope Solo Play application"""
    app = MicroscopeApp()
    app.run()


if __name__ == "__main__":
    main()
