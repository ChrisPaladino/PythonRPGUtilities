"""
Persistence layer for Microscope Solo Play
Handles save/load and export functionality
"""
import json
from pathlib import Path
from typing import Optional
from game_state import GameState
from models import History, Period, Event


class PersistenceManager:
    """Handles saving and loading game state"""
    
    @staticmethod
    def save_game(game_state: GameState, filepath: str) -> bool:
        """Save game state to JSON file"""
        try:
            data = game_state.to_dict()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    @staticmethod
    def load_game(filepath: str) -> Optional[GameState]:
        """Load game state from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return GameState.from_dict(data)
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    @staticmethod
    def export_to_markdown(game_state: GameState, filepath: str) -> bool:
        """Export history to Markdown document"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                history = game_state.history
                
                # Header
                f.write("# Microscope History\n\n")
                
                # Big Picture
                f.write("## The Big Picture\n\n")
                f.write(f"{history.big_picture}\n\n")
                
                # Palette
                f.write("## Palette\n\n")
                if history.palette.yes_items:
                    f.write("**Yes:**\n")
                    for item in history.palette.yes_items:
                        f.write(f"- {item}\n")
                    f.write("\n")
                
                if history.palette.no_items:
                    f.write("**No:**\n")
                    for item in history.palette.no_items:
                        f.write(f"- {item}\n")
                    f.write("\n")
                
                # Timeline
                f.write("## Timeline\n\n")
                for period in history.periods:
                    tone_marker = "☀️" if period.tone.value == "Light" else "🌑"
                    f.write(f"### {tone_marker} {period.title}\n\n")
                    f.write(f"*{period.description}*\n\n")
                    
                    if period.events:
                        for event in period.events:
                            event_tone = "☀️" if event.tone.value == "Light" else "🌑"
                            f.write(f"#### {event_tone} {event.title}\n\n")
                            f.write(f"{event.description}\n\n")
                            
                            if event.scenes:
                                for scene in event.scenes:
                                    scene_type = "📖 Dictated" if scene.is_dictated else "🎭 Played"
                                    f.write(f"##### {scene_type}: {scene.question}\n\n")
                                    
                                    if scene.stage_description:
                                        f.write(f"**Setting:** {scene.stage_description}\n\n")
                                    
                                    if scene.characters:
                                        f.write("**Characters:**\n")
                                        for char in scene.characters:
                                            f.write(f"- {char.name}")
                                            if char.id in scene.revealed_thoughts:
                                                f.write(f" (thinks: *{scene.revealed_thoughts[char.id]}*)")
                                            f.write("\n")
                                        f.write("\n")
                                    
                                    if scene.answer:
                                        f.write(f"**Answer:** {scene.answer}\n\n")
                
                # Foci
                if history.foci:
                    f.write("## Foci\n\n")
                    for focus in history.foci:
                        f.write(f"- {focus.description}\n")
                    f.write("\n")
                
                # Legacies
                if history.legacies:
                    f.write("## Legacies\n\n")
                    for legacy in history.legacies:
                        f.write(f"- {legacy.description}\n")
                    f.write("\n")
            
            return True
        except Exception as e:
            print(f"Error exporting to markdown: {e}")
            return False
    
    @staticmethod
    def export_to_text(game_state: GameState, filepath: str) -> bool:
        """Export history to plain text timeline"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                history = game_state.history
                
                f.write("=" * 60 + "\n")
                f.write("MICROSCOPE HISTORY\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"BIG PICTURE: {history.big_picture}\n\n")
                
                f.write("PALETTE:\n")
                if history.palette.yes_items:
                    f.write("  YES: " + ", ".join(history.palette.yes_items) + "\n")
                if history.palette.no_items:
                    f.write("  NO: " + ", ".join(history.palette.no_items) + "\n")
                f.write("\n")
                
                f.write("TIMELINE:\n")
                f.write("-" * 60 + "\n")
                
                for period in history.periods:
                    tone = "LIGHT" if period.tone.value == "Light" else "DARK"
                    f.write(f"\n[{tone}] {period.title}\n")
                    f.write(f"  {period.description}\n")
                    
                    for event in period.events:
                        event_tone = "LIGHT" if event.tone.value == "Light" else "DARK"
                        f.write(f"\n  [{event_tone}] {event.title}\n")
                        f.write(f"    {event.description}\n")
                        
                        for scene in event.scenes:
                            scene_type = "DICTATED" if scene.is_dictated else "PLAYED"
                            f.write(f"\n    [{scene_type}] {scene.question}\n")
                            if scene.answer:
                                f.write(f"      Answer: {scene.answer}\n")
                
                f.write("\n" + "=" * 60 + "\n")
            
            return True
        except Exception as e:
            print(f"Error exporting to text: {e}")
            return False
