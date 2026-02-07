"""
Main Tkinter UI for Microscope Solo Play
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Optional, Callable
from uuid import UUID
import os

from game_state import GameState
from models import Period, Event, Scene, Character
from constants import Tone, GamePhase, LIGHT_COLOR, DARK_COLOR, NEUTRAL_COLOR, FOCUS_COLOR, LEGACY_COLOR
from persistence import PersistenceManager


class MicroscopeApp:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Microscope Solo Play - Tutorial Mode")
        self.root.geometry("1400x900")
        
        self.game_state = GameState()
        self.selected_period_id: Optional[UUID] = None
        self.selected_event_id: Optional[UUID] = None
        self.tutorial_mode = True  # Always in tutorial mode
        
        self._setup_ui()
        self._update_display()
        
        # Show welcome screen
        self.root.after(100, self._show_welcome)
    
    def _setup_ui(self):
        """Setup main UI layout"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Game", command=self._new_game)
        file_menu.add_command(label="Save Game", command=self._save_game)
        file_menu.add_command(label="Load Game", command=self._load_game)
        file_menu.add_separator()
        file_menu.add_command(label="Export to Markdown", command=self._export_markdown)
        file_menu.add_command(label="Export to Text", command=self._export_text)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel: Timeline and Controls
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=3)
        
        # Right panel: Detail Inspector and Instructions
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        
        # === LEFT PANEL ===
        
        # Phase indicator with step counter
        phase_frame = ttk.LabelFrame(left_panel, text="📍 Where You Are", padding=10)
        phase_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.phase_label = ttk.Label(phase_frame, text="Setup: Big Picture", font=("Arial", 14, "bold"), foreground="#2E86AB")
        self.phase_label.pack()
        
        self.step_label = ttk.Label(phase_frame, text="Step 1 of 8", font=("Arial", 10))
        self.step_label.pack(pady=5)
        
        # Current Focus display
        self.focus_frame = ttk.LabelFrame(left_panel, text="Current Focus", padding=10)
        self.focus_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.focus_label = ttk.Label(self.focus_frame, text="No Focus", wraplength=800)
        self.focus_label.pack()
        
        # Timeline canvas
        timeline_frame = ttk.LabelFrame(left_panel, text="Timeline", padding=5)
        timeline_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollable canvas
        self.canvas = tk.Canvas(timeline_frame, bg="white")
        scrollbar_y = ttk.Scrollbar(timeline_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(timeline_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Control buttons - now context-aware
        control_frame = ttk.Frame(left_panel)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Primary action button (changes based on phase)
        self.primary_button = ttk.Button(control_frame, text="Let's Begin!", 
                                        command=self._primary_action, style="Primary.TButton")
        self.primary_button.pack(fill=tk.X, padx=5, pady=5)
        
        # Secondary action buttons
        self.secondary_frame = ttk.Frame(control_frame)
        self.secondary_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Help button
        ttk.Button(control_frame, text="❓ What Do I Do Now?", 
                  command=self._show_help).pack(fill=tk.X, padx=5, pady=5)
        
        # === RIGHT PANEL ===
        
        # Instructions panel - enhanced for tutorial
        instructions_frame = ttk.LabelFrame(right_panel, text="📖 Step-by-Step Guide", padding=10)
        instructions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.instructions_text = scrolledtext.ScrolledText(
            instructions_frame, wrap=tk.WORD, height=10, width=40,
            font=("Arial", 10), bg="#FFFEF7"
        )
        self.instructions_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for formatting
        self.instructions_text.tag_configure("title", font=("Arial", 12, "bold"), foreground="#2E86AB")
        self.instructions_text.tag_configure("step", font=("Arial", 10, "bold"), foreground="#A23B72")
        self.instructions_text.tag_configure("example", font=("Arial", 9, "italic"), foreground="#555555")
        self.instructions_text.tag_configure("tip", font=("Arial", 9), foreground="#0D7377", background="#E8F5E9")
        self.instructions_text.pack(fill=tk.BOTH, expand=True)
        
        # Detail inspector
        detail_frame = ttk.LabelFrame(right_panel, text="Details", padding=10)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.detail_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, height=15, width=40)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # Palette display
        palette_frame = ttk.LabelFrame(right_panel, text="Palette", padding=10)
        palette_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        step counter
        step_info = self._get_step_info()
        self.step_label.config(text=step_info)
        
        # Update focus label
        if self.game_state.current_focus:
            self.focus_label.config(text=self.game_state.current_focus.description)
        else:
            self.focus_label.config(text="No Focus")
        
        # Update instructions with tutorial content
        self._update_tutorial_instructions()
        
        # Update palette
        self._update_palette_display()
        
        # Update timeline
        self._draw_timeline()
        
        # Update context-aware buttons
        self._update_action_buttonsns
        self.instructions_text.delete(1.0, tk.END)
        instructions = self.game_state.get_phase_instructions()
        self.instructions_text.insert(1.0, instructions)
        
        # Update palette
        self._update_palette_display()
        
        # Update timeline
        self._draw_timeline()
    
    def _update_palette_display(self):
        """Update the palette display"""
        self.palette_text.delete(1.0, tk.END)
        palette = self.game_state.history.palette
        
        if palette.yes_items:
            self.palette_text.insert(tk.END, "YES:\n", "header")
            for item in palette.yes_items:
                self.palette_text.insert(tk.END, f"  • {item}\n")
            self.palette_text.insert(tk.END, "\n")
        
        if palette.no_items:
            self.palette_text.insert(tk.END, "NO:\n", "header")
            for item in palette.no_items:
                self.palette_text.insert(tk.END, f"  • {item}\n")
        
        self.palette_text.tag_configure("header", font=("Arial", 10, "bold"))
    
    # === Tutorial Support Methods ===
    
    def _show_welcome(self):
        """Show welcome tutorial dialog"""
        welcome = tk.Toplevel(self.root)
        welcome.title("Welcome to Microscope!")
        welcome.geometry("700x600")
        welcome.transient(self.root)
        welcome.grab_set()
        
        # Header
        header = ttk.Label(welcome, text="🎮 Welcome to Microscope Solo Play!", 
                          font=("Arial", 16, "bold"))
        header.pack(pady=20)
        
        # Content
        content = scrolledtext.ScrolledText(welcome, wrap=tk.WORD, font=("Arial", 11), 
                                           bg="#FFFEF7", padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        content.insert(tk.END, "What is Microscope?\n", "title")
        content.insert(tk.END, 
            "Microscope is a game about building epic histories. You'll create a timeline "
            "spanning centuries or millennia, from the outside-in—starting big, then zooming "
            "into specific moments.\n\n")
        
        content.insert(tk.END, "How This Works:\n", "title")
        content.insert(tk.END,
            "This app will guide you step-by-step through the game. You'll:\n\n"
            "1️⃣  Describe your Big Picture (the whole history)\n"
            "2️⃣  Create the Start and End periods\n"
            "3️⃣  Build a Palette (what must/cannot exist)\n"
            "4️⃣  Add initial Periods and Events\n"
            "5️⃣  Play rounds with Focus and exploration\n\n")
        
        content.insert(tk.END, "Important:\n", "title")
        content.insert(tk.END,
            "• This app doesn't create content—YOU do all the creative work\n"
            "• The app enforces rules and guides you through the structure\n"
            "• Take your time and be creative!\n"
            "• You can save and come back anytime\n\n")
        
        content.insert(tk.END, "Ready?\n", "title")
        content.insert(tk.END,
            "Click 'Start Your History' to begin the tutorial walkthrough. "
            "Each step will have detailed instructions and examples.\n\n")
        
        content.tag_configure("title", font=("Arial", 12, "bold"), foreground="#2E86AB")
        content.config(state=tk.DISABLED)
        
        # Button
        btn_frame = ttk.Frame(welcome)
        btn_frame.pack(pady=20)
        
        def start():
            welcome.destroy()
            self._enter_big_picture()
        
        ttk.Button(btn_frame, text="🚀 Start Your History!", 
                  command=start, style="Primary.TButton").pack(pady=10)
        
        # Configure button style
        style = ttk.Style()
        style.configure("Primary.TButton", font=("Arial", 11, "bold"))
    
    def _get_step_info(self) -> str:
        """Get current step number and total"""
        phase_steps = {
            GamePhase.SETUP_BIG_PICTURE: "Step 1 of 8: Big Picture",
            GamePhase.SETUP_BOOKENDS: "Step 2 of 8: Bookend Periods",
            GamePhase.SETUP_PALETTE: "Step 3 of 8: Palette",
            GamePhase.SETUP_FIRST_PASS: "Step 4 of 8: First Pass",
            GamePhase.PLAY_DECLARE_FOCUS: "Playing: Declare Focus",
            GamePhase.PLAY_MAKE_HISTORY: "Playing: Make History",
            GamePhase.PLAY_CREATE_LEGACY: "Playing: Legacy",
            GamePhase.PLAY_EXPLORE_LEGACY: "Playing: Explore Legacy",
        }
        return phase_steps.get(self.game_state.current_phase, "Playing")
    
    def _update_tutorial_instructions(self):
        """Update instructions with detailed tutorial content"""
        self.instructions_text.config(state=tk.NORMAL)
        self.instructions_text.delete(1.0, tk.END)
        
        phase = self.game_state.current_phase
        
        if phase == GamePhase.SETUP_BIG_PICTURE:
            self.instructions_text.insert(tk.END, "📝 The Big Picture\n\n", "title")
            self.instructions_text.insert(tk.END, "What to do:\n", "step")
            self.instructions_text.insert(tk.END,
                "Describe your entire history in 1-2 sentences. This is the grand scope—"
                "think thousands of years, rise and fall of civilizations, epic journeys.\n\n")
            
            self.instructions_text.insert(tk.END, "💡 Examples:\n", "step")
            self.instructions_text.insert(tk.END,
                "• \"The rise and fall of the Galactic Empire, from first contact to the final diaspora.\"\n"
                "• \"A kingdom's struggle against an ancient curse that spans centuries.\"\n"
                "• \"Humanity's expansion into the solar system and the conflicts that followed.\"\n\n",
                "example")
            
            self.instructions_text.insert(tk.END, "💡 Tip: ", "tip")
            self.instructions_text.insert(tk.END,
                "Keep it broad! You'll fill in the details later. This is just the scope.\n\n", "tip")
        
        elif phase == GamePhase.SETUP_BOOKENDS:
            self.instructions_text.insert(tk.END, "📅 Bookend Periods\n\n", "title")
            self.instructions_text.insert(tk.END, "What to do:\n", "step")
            self.instructions_text.insert(tk.END,
                f"Create TWO Periods that bookend your history:\n"
                f"{'✅ START period created' if self.game_state.history.start_period_id else '⬜ START period (the beginning)'}\n"
                f"{'✅ END period created' if self.game_state.history.end_period_id else '⬜ END period (how it ends)'}\n\n")
            
            self.instructions_text.insert(tk.END, "What's a Period?\n", "step")
            self.instructions_text.insert(tk.END,
                "A Period is a large chunk of time—decades, centuries, or more. "
                "It has a title, description, and tone (Light or Dark).\n\n")
            
            self.instructions_text.insert(tk.END, "💡 Example START:\n", "step")
            self.instructions_text.insert(tk.END,
                "Title: First Contact\n"
                "Description: Humanity discovers ancient alien ruins on Mars\n"
                "Tone: Light (hopeful, exciting)\n\n", "example")
            
            self.instructions_text.insert(tk.END, "💡 Example END:\n", "step")
            self.instructions_text.insert(tk.END,
                "Title: The Long Silence\n"
                "Description: The last transmission fades as colonies go dark\n"
                "Tone: Dark (ominous, sad)\n\n", "example")
            
            self.instructions_text.insert(tk.END, "💡 Tip: ", "tip")
            self.instructions_text.insert(tk.END,
                "Make them contrast! A light beginning and dark end (or vice versa) creates interesting tension.\n\n", "tip")
        
        elif phase == GamePhase.SETUP_PALETTE:
            self.instructions_text.insert(tk.END, "🎨 The Palette\n\n", "title")
            self.instructions_text.insert(tk.END, "What to do:\n", "step")
            self.instructions_text.insert(tk.END,
                "Add items to two lists:\n"
                "• YES list: Things that MUST exist in your history\n"
                "• NO list: Things that CANNOT exist\n\n")
            
            self.instructions_text.insert(tk.END, "Why?\n", "step")
            self.instructions_text.insert(tk.END,
                "The Palette constrains creativity in interesting ways. "
                "It prevents contradictions and sparks ideas.\n\n")
            
            self.instructions_text.insert(tk.END, "💡 Examples:\n", "step")
            self.instructions_text.insert(tk.END,
                "YES:\n"
                "• Advanced AI\n"
                "• Interstellar travel\n"
                "• Ancient mysteries\n\n"
                "NO:\n"
                "• Faster-than-light communication\n"
                "• Time travel\n"
                "• Benevolent aliens\n\n", "example")
            
            self.instructions_text.insert(tk.END, "💡 Tip: ", "tip")
            self.instructions_text.insert(tk.END,
                "Add 3-5 items to each list. Don't overthink it—you can always work around them creatively!\n\n", "tip")
        
        elif phase == GamePhase.SETUP_FIRST_PASS:
            self.instructions_text.insert(tk.END, "🌍 First Pass\n\n", "title")
            self.instructions_text.insert(tk.END, "What to do:\n", "step")
            self.instructions_text.insert(tk.END,
                "Add some Periods and Events to flesh out your timeline. "
                "Think of this as sketching the outline of your history.\n\n")
            
            self.instructions_text.insert(tk.END, "You can create:\n", "step")
            self.instructions_text.insert(tk.END,
                "• PERIODS: Large time spans between your bookends\n"
                "• EVENTS: Specific things that happen within Periods\n\n")
            
            self.instructions_text.insert(tk.END, "You CANNOT create:\n", "step")
            self.instructions_text.insert(tk.END, "• Scenes (those come later during play)\n\n")
            
            self.instructions_text.insert(tk.END, "💡 Tip: ", "tip")
            self.instructions_text.insert(tk.END,
                "Add 2-3 Periods and maybe 1-2 Events per Period. Don't fill everything in—leave gaps to explore later!\n\n", "tip")
            
            self.instructions_text.insert(tk.END, "When done:\n", "step")
            self.instructions_text.insert(tk.END,
                "Click 'Complete First Pass' to begin the main game!\n\n")
        
        elif phase == GamePhase.PLAY_DECLARE_FOCUS:
            self.instructions_text.insert(tk.END, "🎯 Declare a Focus\n\n", "title")
            self.instructions_text.insert(tk.END, "What to do:\n", "step")
            self.instructions_text.insert(tk.END,
                "Choose something to explore in this round. It could be:\n"
                "• A theme (\"war and peace\")\n"
                "• A question (\"What caused the Great Silence?\")\n"
                "• An element (\"The fate of Earth\")\n\n")
            
            self.instructions_text.insert(tk.END, "Why?\n", "step")
            self.instructions_text.insert(tk.END,
                "Everything you create this round should relate to your Focus. "
                "It gives direction to your exploration.\n\n")
            
            self.instructions_text.insert(tk.END, "💡 Examples:\n", "step")
            self.instructions_text.insert(tk.END,
                "• \"The war between Mars and the Belt\"\n"
                "• \"How did AI become sentient?\"\n"
                "• \"The mysterious Precursors\"\n\n", "example")
            
            self.instructions_text.insert(tk.END, "💡 Tip: ", "tip")
            self.instructions_text.insert(tk.END,
                "Pick something that genuinely interests you right now!\n\n", "tip")
        
        elif phase == GamePhase.PLAY_MAKE_HISTORY:
            self.instructions_text.insert(tk.END, "⚡ Make History\n\n", "title")
            self.instructions_text.insert(tk.END, "What to do:\n", "step")
            self.instructions_text.insert(tk.END,
                f"Create content related to your Focus:\n"
                f"📍 \"{self.game_state.current_focus.description if self.game_state.current_focus else 'Your Focus'}\"\n\n")
            
            self.instructions_text.insert(tk.END, "You can create:\n", "step")
            self.instructions_text.insert(tk.END,
                "• PERIOD: Click to select where to insert, then create\n"
                "• EVENT: Click a Period, then create Event inside it\n"
                "• SCENE: Click an Event, then create a Scene to explore in detail\n\n")
            
            self.instructions_text.insert(tk.END, "Scenes are special:\n", "step")
            self.instructions_text.insert(tk.END,
                "Scenes are where you zoom WAY in. You'll:\n"
                "1. Ask a question\n"
                "2. Set up the situation\n"
                "3. Add characters\n"
                "4. Play it out\n"
                "5. Answer the question\n\n")
            
            self.instructions_text.insert(tk.END, "💡 Tip: ", "tip")
            self.instructions_text.insert(tk.END,
                "Create 2-4 items this round. When you're done exploring your Focus, click 'Complete Focus'.\n\n", "tip")
        
        elif phase == GamePhase.PLAY_CREATE_LEGACY:
            self.instructions_text.insert(tk.END, "⭐ Create a Legacy\n\n", "title")
            self.instructions_text.insert(tk.END, "What to do:\n", "step")
            self.instructions_text.insert(tk.END,
                "Look at what you just created. Did something important emerge? "
                "Something worth revisiting later?\n\n")
            
            self.instructions_text.insert(tk.END, "If yes:\n", "step")
            self.instructions_text.insert(tk.END,
                "Create a Legacy! It's like bookmarking something for later exploration.\n\n")
            
            self.instructions_text.insert(tk.END, "If no:\n", "step")
            self.instructions_text.insert(tk.END, "Click 'Skip' to move to the next Focus.\n\n")
            
            self.instructions_text.insert(tk.END, "💡 Tip: ", "tip")
            self.instructions_text.insert(tk.END,
                "Don't force it! Legacies should feel natural and interesting.\n\n", "tip")
        
        elif phase == GamePhase.PLAY_EXPLORE_LEGACY:
            self.instructions_text.insert(tk.END, "🔍 Explore Legacy\n\n", "title")
            self.instructions_text.insert(tk.END, "What to do:\n", "step")
            self.instructions_text.insert(tk.END,
                "Create ONE Event or dictated Scene related to your Legacy. "
                "This is a quick exploration before moving on.\n\n")
            
            self.instructions_text.insert(tk.END, "Then:\n", "step")
            self.instructions_text.insert(tk.END,
                "Click 'Complete Legacy Exploration' to start a new Focus!\n\n")
        
        self.instructions_text.config(state=tk.DISABLED)
    
    def _update_action_buttons(self):
        """Update context-aware action buttons"""
        # Clear secondary buttons
        for widget in self.secondary_frame.winfo_children():
            widget.destroy()
        
        phase = self.game_state.current_phase
        
        # Update primary button
        if phase == GamePhase.SETUP_BIG_PICTURE:
            self.primary_button.config(text="📝 Enter Big Picture", command=self._enter_big_picture)
        
        elif phase == GamePhase.SETUP_BOOKENDS:
            if not self.game_state.history.start_period_id:
                self.primary_button.config(text="📅 Create START Period", command=self._create_period_dialog)
            elif not self.game_state.history.end_period_id:
                self.primary_button.config(text="📅 Create END Period", command=self._create_period_dialog)
            else:
                self.primary_button.config(text="✅ Continue to Palette", command=self._advance_after_bookends)
        
        elif phase == GamePhase.SETUP_PALETTE:
            self.primary_button.config(text="🎨 Add to Palette", command=self._complete_palette)
        
        elif phase == GamePhase.SETUP_FIRST_PASS:
            self.primary_button.config(text="✅ Complete First Pass & Start Playing!", command=self._complete_first_pass_confirm)
            ttk.Button(self.secondary_frame, text="➕ Add Period", 
                      command=self._create_period_dialog).pack(fill=tk.X, pady=2)
            ttk.Button(self.secondary_frame, text="➕ Add Event", 
                      command=self._create_event_dialog).pack(fill=tk.X, pady=2)
        
        elif phase == GamePhase.PLAY_DECLARE_FOCUS:
            self.primary_button.config(text="🎯 Declare Focus", command=self._declare_focus)
        
        elif phase == GamePhase.PLAY_MAKE_HISTORY:
            self.primary_button.config(text="✅ Complete Focus", command=self._complete_focus)
            ttk.Button(self.secondary_frame, text="➕ Create Period", 
                      command=self._create_period_dialog).pack(fill=tk.X, pady=2)
            ttk.Button(self.secondary_frame, text="➕ Create Event", 
                      command=self._create_event_dialog).pack(fill=tk.X, pady=2)
            ttk.Button(self.secondary_frame, text="🎬 Create Scene", 
                      command=self._create_scene_dialog).pack(fill=tk.X, pady=2)
        
        elif phase == GamePhase.PLAY_CREATE_LEGACY:
            self.primary_button.config(text="⭐ Create Legacy", command=self._create_legacy)
            ttk.Button(self.secondary_frame, text="⏭️ Skip Legacy", 
                      command=self._skip_legacy).pack(fill=tk.X, pady=2)
        
        elif phase == GamePhase.PLAY_EXPLORE_LEGACY:
            self.primary_button.config(text="✅ Finish Exploring Legacy", 
                                      command=self._finish_legacy_exploration)
            ttk.Button(self.secondary_frame, text="➕ Add Event", 
                      command=self._create_event_dialog).pack(fill=tk.X, pady=2)
            ttk.Button(self.secondary_frame, text="🎬 Add Scene", 
                      command=self._create_scene_dialog).pack(fill=tk.X, pady=2)
    
    def _primary_action(self):
        """Primary action based on current phase"""
        phase = self.game_state.current_phase
        
        if phase == GamePhase.SETUP_BIG_PICTURE:
            self._enter_big_picture()
        elif phase == GamePhase.SETUP_BOOKENDS:
            self._create_period_dialog()
        elif phase == GamePhase.SETUP_PALETTE:
            self._complete_palette()
        elif phase == GamePhase.SETUP_FIRST_PASS:
            self._complete_first_pass_confirm()
        elif phase == GamePhase.PLAY_DECLARE_FOCUS:
            self._declare_focus()
        elif phase == GamePhase.PLAY_MAKE_HISTORY:
            self._complete_focus()
        elif phase == GamePhase.PLAY_CREATE_LEGACY:
            self._create_legacy()
        elif phase == GamePhase.PLAY_EXPLORE_LEGACY:
            self._finish_legacy_exploration()
    
    def _show_help(self):
        """Show context-sensitive help"""
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("What Do I Do Now?")
        help_dialog.geometry("600x500")
        help_dialog.transient(self.root)
        
        help_text = scrolledtext.ScrolledText(help_dialog, wrap=tk.WORD, font=("Arial", 11),
                                             bg="#FFFEF7", padx=20, pady=20)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        phase = self.game_state.current_phase
        
        help_text.insert(tk.END, f"{self.game_state.current_phase.value}\n\n", "title")
        help_text.insert(tk.END, self.game_state.get_phase_instructions() + "\n\n")
        
        help_text.insert(tk.END, "Available Actions:\n", "title")
        for action in self.game_state.get_available_actions():
            help_text.insert(tk.END, f"  • {action}\n")
        
        help_text.tag_configure("title", font=("Arial", 13, "bold"), foreground="#2E86AB")
        help_text.config(state=tk.DISABLED)
        
        ttk.Button(help_dialog, text="Got It!", command=help_dialog.destroy).pack(pady=10)
    
    def _advance_after_bookends(self):
        """Advance to palette after bookends are complete"""
        self.game_state.current_phase = GamePhase.SETUP_PALETTE
        self._update_display()
    
    def _complete_first_pass_confirm(self):
        """Confirm completion of first pass"""
        if len(self.game_state.history.periods) < 3:
            if not messagebox.askyesno("Complete First Pass?",
                "You only have a few Periods. Are you sure you want to continue?\n\n"
                "(It's okay to add more now, or you can add them later during play)"):
                return
        
        self.game_state.complete_first_pass()
        self._update_display()
        messagebox.showinfo("Setup Complete!", 
            "Great! Setup is done.\n\n"
            "Now begins the main game: you'll declare a Focus, explore it, "
            "and create Legacies. Let's start!")
    
    def _skip_legacy(self):
        """Skip legacy creation"""
        if self.game_state.skip_legacy_creation():
            self._update_display()
    
    def _finish_legacy_exploration(self):
        """Finish exploring legacy"""
        if self.game_state.complete_legacy_exploration():
            self._update_display()
            messagebox.showinfo("Round Complete!",
                "Great work! Now start a new round with a fresh Focus.")

    
    def _draw_timeline(self):
        """Draw the timeline on canvas"""
        self.canvas.delete("all")
        
        x_offset = 20
        y_offset = 20
        period_width = 200
        period_spacing = 50
        
        for i, period in enumerate(self.game_state.history.periods):
            # Draw period card
            x = x_offset + i * (period_width + period_spacing)
            y = y_offset
            
            color = LIGHT_COLOR if period.tone == Tone.LIGHT else DARK_COLOR
            
            # Period rectangle
            period_rect = self.canvas.create_rectangle(
                x, y, x + period_width, y + 100,
                fill=color, outline="black", width=2
            )
            
            # Period title
            self.canvas.create_text(
                x + period_width // 2, y + 20,
                text=period.title, font=("Arial", 11, "bold"),
                width=period_width - 10
            )
            
            # Period description
            self.canvas.create_text(
                x + period_width // 2, y + 60,
                text=period.description[:50] + "..." if len(period.description) > 50 else period.description,
                font=("Arial", 9), width=period_width - 10
            )
            
            # Bind click event
            self.canvas.tag_bind(period_rect, "<Button-1>",
                               lambda e, pid=period.id: self._select_period(pid))
            
            # Draw events under period
            event_y = y + 120
            for j, event in enumerate(period.events):
                event_color = LIGHT_COLOR if event.tone == Tone.LIGHT else DARK_COLOR
                
                event_rect = self.canvas.create_rectangle(
                    x + 10, event_y, x + period_width - 10, event_y + 80,
                    fill=event_color, outline="gray", width=1
                )
                
                self.canvas.create_text(
                    x + period_width // 2, event_y + 15,
                    text=event.title, font=("Arial", 10, "bold"),
                    width=period_width - 30
                )
                
                self.canvas.create_text(
                    x + period_width // 2, event_y + 45,
                    text=event.description[:40] + "..." if len(event.description) > 40 else event.description,
                    font=("Arial", 8), width=period_width - 30
                )
                
                # Scene count indicator
                if event.scenes:
                    self.canvas.create_text(
                        x + period_width - 20, event_y + 70,
                        text=f"🎬{len(event.scenes)}", font=("Arial", 8)
                    )
                
                self.canvas.tag_bind(event_rect, "<Button-1>",
                                   lambda e, eid=event.id: self._select_event(eid))
                
                event_y += 90
        
        # Update scroll region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def _select_period(self, period_id: UUID):
        """Select a period and show details"""
        self.selected_period_id = period_id
        self.selected_event_id = None
        
        period = self.game_state.history.get_period(period_id)
        if period:
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, f"PERIOD: {period.title}\n\n", "header")
            self.detail_text.insert(tk.END, f"Tone: {period.tone.value}\n")
            self.detail_text.insert(tk.END, f"\n{period.description}\n")
            self.detail_text.insert(tk.END, f"\nEvents: {len(period.events)}")
            
            self.detail_text.tag_configure("header", font=("Arial", 12, "bold"))
    
    def _select_event(self, event_id: UUID):
        """Select an event and show details"""
        self.selected_event_id = event_id
        
        event = self.game_state.history.get_event(event_id)
        if event:
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, f"EVENT: {event.title}\n\n", "header")
            self.detail_text.insert(tk.END, f"Tone: {event.tone.value}\n")
            self.detail_text.insert(tk.END, f"\n{event.description}\n")
            self.detail_text.insert(tk.END, f"\nScenes: {len(event.scenes)}\n")
            
            if event.scenes:
                self.detail_text.insert(tk.END, "\n--- Scenes ---\n", "subheader")
                for scene in event.scenes:
                    scene_type = "Dictated" if scene.is_dictated else "Played"
                    self.detail_text.insert(tk.END, f"\n[{scene_type}] {scene.question}\n")
                    if scene.answer:
                        self.detail_text.insert(tk.END, f"Answer: {scene.answer}\n")
            
            self.detail_text.tag_configure("header", font=("Arial", 12, "bold"))
            self.detail_text.tag_configure("subheader", font=("Arial", 10, "bold"))
    
    # === Action Methods ===
    
    def _new_game(self):
        """Start a new game"""
        if messagebox.askyesno("New Game", "Start a new game? Current progress will be lost."):
            self.game_state = GameState()
            self._update_display()
    
    def _save_game(self):
        """Save current game"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            if PersistenceManager.save_game(self.game_state, filepath):
                messagebox.showinfo("Save Game", "Game saved successfully!")
            else:
                messagebox.showerror("Save Game", "Failed to save game.")
    
    def _load_game(self):
        """Load a saved game"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            state = PersistenceManager.load_game(filepath)
            if state:
                self.game_state = state
                self._update_display()
                messagebox.showinfo("Load Game", "Game loaded successfully!")
            else:
                messagebox.showerror("Load Game", "Failed to load game.")
    
    def _export_markdown(self):
        """Export to markdown"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if filepath:
            if PersistenceManager.export_to_markdown(self.game_state, filepath):
                messagebox.showinfo("Export", "Exported to Markdown successfully!")
            else:
                messagebox.showerror("Export", "Failed to export.")
    
    def _export_text(self):
        """Export to plain text"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            if PersistenceManager.export_to_text(self.game_state, filepath):
                messagebox.showinfo("Export", "Exported to Text successfully!")
            else:
                messagebox.showerror("Export", "Failed to export.")
    
    def _complete_phase(self):
        """Complete the current phase"""
        phase = self.game_state.current_phase
        
        if phase == GamePhase.SETUP_BIG_PICTURE:
            self._enter_big_picture()
        elif phase == GamePhase.SETUP_BOOKENDS:
            messagebox.showinfo("Bookends", "Please create both Start and End periods using 'Create Period' button.")
        elif phase == GamePhase.SETUP_PALETTE:
            self._complete_palette()
        elif phase == GamePhase.SETUP_FIRST_PASS:
            self.game_state.complete_first_pass()
            self._update_display()
            messagebox.showinfo("First Pass Complete", "Beginning main play phase!")
        elif phase == GamePhase.PLAY_DECLARE_FOCUS:
            self._declare_focus()
        elif phase == GamePhase.PLAY_MAKE_HISTORY:
            self._complete_focus()
        elif phase == GamePhase.PLAY_CREATE_LEGACY:
            self._create_legacy()
        elif phase == GamePhase.PLAY_EXPLORE_LEGACY:
            messagebox.showinfo("Explore Legacy", "Create an Event or dictated Scene related to the current Legacy.")
    
    def _enter_big_picture(self):
        """Dialog to enter Big Picture"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Step 1: The Big Picture")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="📝 Describe Your Entire History", 
                 font=("Arial", 14, "bold")).pack(padx=10, pady=15)
        
        # Instructions
        inst_frame = ttk.Frame(dialog)
        inst_frame.pack(padx=20, pady=10, fill=tk.X)
        
        ttk.Label(inst_frame, text="In 1-2 sentences, describe the WHOLE scope of your history:",
                 wraplength=550).pack(anchor="w", pady=5)
        
        ttk.Label(inst_frame, text="Think BIG: centuries, millennia, empires, civilizations",
                 font=("Arial", 9, "italic"), foreground="#666").pack(anchor="w")
        
        # Examples
        ex_frame = ttk.LabelFrame(dialog, text="💡 Examples", padding=10)
        ex_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        examples = [
            "The rise and fall of the Martian Empire, from first colonists to the last transmission.",
            "A thousand-year curse placed on a kingdom and the heroes who tried to break it.",
            "Humanity's expansion into the stars and the war that nearly destroyed us.",
        ]
        
        for ex in examples:
            ttk.Label(ex_frame, text=f"• {ex}", wraplength=520, 
                     font=("Arial", 9)).pack(anchor="w", pady=3)
        
        # Input
        ttk.Label(dialog, text="Your Big Picture:", font=("Arial", 10, "bold")).pack(padx=20, pady=(10,5))
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, height=4, font=("Arial", 11))
        text_widget.pack(padx=20, pady=5, fill=tk.BOTH)
        text_widget.focus()
        
        def submit():
            big_picture = text_widget.get(1.0, tk.END).strip()
            if big_picture:
                if self.game_state.set_big_picture(big_picture):
                    self._update_display()
                    dialog.destroy()
                    messagebox.showinfo("Great!", 
                        "Your Big Picture is set!\n\n"
                        "Next: Create the START and END periods that bookend your history.")
                else:
                    messagebox.showerror("Error", "Failed to set Big Picture")
            else:
                messagebox.showwarning("Oops!", "Please enter your Big Picture before continuing.")
        
        ttk.Button(dialog, text="✅ Continue", command=submit, 
                  style="Primary.TButton").pack(pady=15)
    
    def _create_period_dialog(self):
        """Dialog to create a new Period"""
        dialog = tk.Toplevel(self.root)
        
        is_bookend = self.game_state.current_phase == GamePhase.SETUP_BOOKENDS
        
        if is_bookend:
            has_start = self.game_state.history.start_period_id is not None
            has_end = self.game_state.history.end_period_id is not None
            
            if not has_start:
                dialog.title("Create START Period")
                instruction = "This is the BEGINNING of your history. What era does it start in?"
            elif not has_end:
                dialog.title("Create END Period")
                instruction = "This is the END of your history. How does it conclude?"
            else:
                messagebox.showinfo("Done!", "Both bookends are created. Click the main button to continue.")
                dialog.destroy()
                return
        else:
            dialog.title("Create a Period")
            instruction = "Periods are large chunks of time. Where does this fit in your timeline?"
        
        dialog.geometry("550x600")
        dialog.transient(self.root)
        
        ttk.Label(dialog, text=instruction, font=("Arial", 11), 
                 wraplength=500).pack(padx=15, pady=15)
        
        # Title
        ttk.Label(dialog, text="Title:", font=("Arial", 10, "bold")).pack(padx=15, pady=(10,5), anchor="w")
        ttk.Label(dialog, text="Short, evocative name", font=("Arial", 9, "italic"),
                 foreground="#666").pack(padx=15, pady=(0,5), anchor="w")
        title_entry = ttk.Entry(dialog, width=50, font=("Arial", 11))
        title_entry.pack(padx=15, pady=5)
        title_entry.focus()
        
        # Examples
        if is_bookend and not has_start:
            ttk.Label(dialog, text="Examples: First Contact, The Golden Age, Dawn of Magic",
                     font=("Arial", 9), foreground="#888").pack(padx=15, pady=2)
        elif is_bookend:
            ttk.Label(dialog, text="Examples: The Long Silence, Final Days, The Reckoning",
                     font=("Arial", 9), foreground="#888").pack(padx=15, pady=2)
        
        # Description
        ttk.Label(dialog, text="Description:", font=("Arial", 10, "bold")).pack(padx=15, pady=(15,5), anchor="w")
        ttk.Label(dialog, text="What happens during this period?", font=("Arial", 9, "italic"),
                 foreground="#666").pack(padx=15, pady=(0,5), anchor="w")
        desc_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, height=6, font=("Arial", 10))
        desc_text.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)
        
        # Tone
        ttk.Label(dialog, text="Tone:", font=("Arial", 10, "bold")).pack(padx=15, pady=(10,5), anchor="w")
        
        tone_frame = ttk.Frame(dialog)
        tone_frame.pack(padx=15, pady=5)
        
        tone_var = tk.StringVar(value="Light")
        
        light_rb = ttk.Radiobutton(tone_frame, text="☀️ Light (hopeful, peaceful, positive)", 
                                   variable=tone_var, value="Light")
        light_rb.pack(anchor="w", pady=2)
        
        dark_rb = ttk.Radiobutton(tone_frame, text="🌑 Dark (ominous, tragic, negative)", 
                                 variable=tone_var, value="Dark")
        dark_rb.pack(anchor="w", pady=2)
        
        def submit():Select a Period", 
                "First, click on a Period in the timeline to select it.\n\n"
                "Events happen INSIDE Periods, so you need to choose which Period this Event belongs to.")
            return
        
        period_id = self.selected_period_id or (
            self.game_state.history.periods[0].id if self.game_state.history.periods else None
        )
        
        if not period_id:
            messagebox.showerror("No Periods", 
                "You need to create at least one Period before you can add Events!")
            return
        
        period = self.game_state.history.get_period(period_id)
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Create an Event")
        dialog.geometry("550x600")
        dialog.transient(self.root)
        
        ttk.Label(dialog, text=f"Creating Event in: {period.title}", 
                 font=("Arial", 12, "bold"), foreground="#2E86AB").pack(padx=15, pady=15)
        
        ttk.Label(dialog, text="Events are specific things that happen. They have visible outcomes.",
                 wraplength=500).pack(padx=15, pady=(0,15))
        
        # Title
        ttk.Label(dialog, text="Title:", font=("Arial", 10, "bold")).pack(padx=15, pady=(10,5), anchor="w")
        ttk.Label(dialog, text="What happens?", font=("Arial", 9, "italic"),
                 foreground="#666").pack(padx=15, pady=(0,5), anchor="w")
        title_entry = ttk.Entry(dialog, width=50, font=("Arial", 11))
        title_entry.pack(padx=15, pady=5)
        title_entry.focus()
        
        ttk.Label(dialog, text="Examples: The Treaty is Signed, First AI Awakens, Battle of Europa",
                 font=("Arial", 9), foreground="#888").pack(padx=15, pady=2)
        
        # Description
        ttk.Label(dialog, text="Description:", font=("Arial", 10, "bold")).pack(padx=15, pady=(15,5), anchor="w")
        ttk.Label(dialog, text="What's the outcome? What changes?", font=("Arial", 9, "italic"),
                 foreground="#666").pack(padx=15, pady=(0,5), anchor="w")
        desc_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, height=6, font=("Arial", 10))
        desc_text.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)
        
        # Tone
        ttk.Label(dialog, text="Tone:", font=("Arial", 10, "bold")).pack(padx=15, pady=(10,5), anchor="w")
        
        tone_frame = ttk.Frame(dialog)
        tone_frame.pack(padx=15, pady=5)
        
        tone_var = tk.StringVar(value="Light")
        ttk.Radiobutton(tone_frame, text="☀️ Light", variable=tone_var, value="Light").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(tone_frame, text="🌑 Dark", variable=tone_var, value="Dark").pack(side=tk.LEFT, padx=10)
        
        def submit():
            title = title_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            tone = Tone.LIGHT if tone_var.get() == "Light" else Tone.DARK
            
            if not title or not description:
                messagebox.showwarning("Missing Info", "Please fill in both title and description!")
                return
            
            event_id = self.game_state.create_event(title, description, tone, period_id)
            if event_id:
                self._update_display()
                dialog.destroy()
                messagebox.showinfo("Event Created!", 
                    "Your Event has been added to the timeline!\n\n"
                    "You can now create Scenes inside this Event to explore it in detail.")
            else:
                messagebox.showerror("Error", "Failed to create event")
        
        ttk.Button(dialog, text="✅ Create Event", command=submit, 
                  style="Primary.TButton").pack(pady=15)
            return
        
        period_id = self.selected_period_id or (
            self.game_state.history.periods[0].id if self.game_state.history.periods else None
        )
        
        if not period_id:
            messagebox.showerror("Error", "No periods available")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Event")
        dialog.geometry("450x400")
        
        # Title
        ttk.Label(dialog, text="Title:").pack(padx=10, pady=5)
        title_entry = ttk.Entry(dialog, width=50)
        title_entry.pack(padx=10, pady=5)
        
        # Description
        ttk.Label(dialog, text="Description (must show visible outcome):").pack(padx=10, pady=5)
        desc_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, height=6)
        desc_text.pack(padx=10, pady=5)
        
        # Tone
        ttk.Label(dialog, text="Tone:").pack(padx=10, pady=5)
        tone_var = tk.StringVar(value="Light")
        ttk.Radiobutton(dialog, text="Light", variable=tone_var, value="Light").pack()
        ttk.Radiobutton(dialog, text="Dark", variable=tone_var, value="Dark").pack()
        
        def submit():
            title = title_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            tone = Tone.LIGHT if tone_var.get() == "Light" else Tone.DARK
            
            if not title or not description:
                messagebox.showwarning("Warning", "Title and description required")
                return
            
            event_id = self.game_state.create_event(title, description, tone, period_id)
            if event_id:
                self._update_display()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to create event")
        
        ttk.Button(dialog, text="Create", command=submit).pack(pady=10)
    
    def _create_scene_dialog(self):
        """Open Scene creation wizard"""
        if self.game_state.current_phase not in [GamePhase.PLAY_MAKE_HISTORY, GamePhase.PLAY_EXPLORE_LEGACY]:
            messagebox.showinfo("Not Yet", 
                "You can create Scenes during the main play phase.\n\n"
                "Complete the setup first!")
            return
        
        if not self.selected_event_id:
            # Try to find any event
            event_id = None
            for period in self.game_state.history.periods:
                if period.events:
                    event_id = period.events[0].id
                    break
            
            if not event_id:
                messagebox.showinfo("Create an Event First",
                    "Scenes happen INSIDE Events.\n\n"
                    "First, click on a Period and create an Event. "
                    "Then you can create Scenes inside that Event.")
                return
            else:
                messagebox.showinfo("Select an Event",
                    "Click on an Event in the timeline first.\n\n"
                    "Scenes happen inside Events, so you need to choose which Event this Scene explores.")
                return
        
        event_id = self.selected_event_id
        SceneWizard(self.root, self.game_state, event_id, self._update_display)
    
    def _declare_focus(self):
        """Dialog to declare a Focus"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Declare Your Focus")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="🎯 What Will You Explore This Round?", 
                 font=("Arial", 14, "bold")).pack(padx=15, pady=15)
        
        ttk.Label(dialog, text="Your Focus is a theme, question, or element to explore.",
                 wraplength=550).pack(padx=15, pady=(0,10))
        
        # Examples
        ex_frame = ttk.LabelFrame(dialog, text="💡 Examples of Good Foci", padding=15)
        ex_frame.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)
        
        examples = [
            ("Theme", "The cost of war on ordinary people"),
            ("Question", "What caused the AI rebellion?"),
            ("Element", "The fate of the Mars colonies"),
            ("Character/Group", "The mysterious Precursors"),
            ("Event", "The consequences of first contact"),
        ]
        
        for category, example in examples:
            frame = ttk.Frame(ex_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=f"{category}:", font=("Arial", 9, "bold"), 
                     width=15).pack(side=tk.LEFT)
            ttk.Label(frame, text=example, font=("Arial", 9)).pack(side=tk.LEFT)
        
        # Input
        ttk.Label(dialog, text="Your Focus:", font=("Arial", 10, "bold")).pack(padx=20, pady=(15,5), anchor="w")
        ttk.Label(dialog, text="Everything you create this round should relate to this",
                 font=("Arial", 9, "italic"), foreground="#666").pack(padx=20, pady=(0,5), anchor="w")
        
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, height=3, font=("Arial", 11))
        text_widget.pack(padx=20, pady=5, fill=tk.X)
        text_widget.focus()
        
        def submit():
            focus = text_widget.get(1.0, tk.END).strip()
            if focus:
                if self.game_state.declare_focus(focus):
                    self._update_display()
                    dialog.destroy()
                    messagebox.showinfo("Focus Declared!",
                        f"Your Focus: {focus}\n\n"
                        "Now create Periods, Events, or Scenes related to this Focus. "
                        "When you're done exploring, click 'Complete Focus'.")
                else:
                    messagebox.showerror("Error", "Failed to declare Focus")
            else:
                messagebox.showwarning("Missing Focus", "Please enter a Focus to explore!")
        
        ttk.Button(dialog, text="✅ Start Exploring", command=submit, 
                  style="Primary.TButton").pack(pady=15)
    
    def _complete_focus(self):
        """Complete current Focus and move to Legacy"""
        if self.game_state.complete_focus():
            self._update_display()
            messagebox.showinfo("Focus Complete", "Create a Legacy from your exploration, or skip to next Focus.")
        else:
            messagebox.showerror("Error", "Cannot complete Focus")
    
    def _create_legacy(self):
        """Dialog to create a Legacy"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Legacy")
        dialog.geometry("500x300")
        
        ttk.Label(dialog, text="Create a Legacy from your exploration:",
                 font=("Arial", 11)).pack(padx=10, pady=10)
        
        ttk.Label(dialog, text="Description:").pack(padx=10, pady=5)
        desc_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, height=6)
        desc_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        ttk.Label(dialog, text="(Will use currently selected Period/Event)").pack(padx=10)
        
        def submit():
            description = desc_text.get(1.0, tk.END).strip()
            if description:
                origin_id = self.selected_event_id or self.selected_period_id
                if not origin_id and self.game_state.history.periods:
                    origin_id = self.game_state.history.periods[0].id
                
                if origin_id:
                    if self.game_state.create_legacy(description, origin_id):
                        self._update_display()
                        dialog.destroy()
                        messagebox.showinfo("Legacy Created", "Now explore this Legacy by creating related content.")
                    else:
                        messagebox.showerror("Error", "Failed to create Legacy")
                else:
                    messagebox.showerror("Error", "No origin element selected")
            else:
                messagebox.showwarning("Warning", "Description required")
        
        def skip():
            if self.game_state.skip_legacy_creation():
                self._update_display()
                dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Create Legacy", command=submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Skip", command=skip).pack(side=tk.LEFT, padx=5)
    
    def _complete_palette(self):
        """Dialog to add items to palette"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Build Palette")
        dialog.geometry("600x500")
        
        ttk.Label(dialog, text="Add items to Yes/No lists", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Yes frame
        yes_frame = ttk.LabelFrame(dialog, text="YES (Must Exist)", padding=10)
        yes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        yes_entry = ttk.Entry(yes_frame, width=50)
        yes_entry.pack(pady=5)
        
        yes_listbox = tk.Listbox(yes_frame, height=6)
        yes_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        def add_yes():
            item = yes_entry.get().strip()
            if item:
                self.game_state.add_to_palette(item, True)
                yes_listbox.insert(tk.END, item)
                yes_entry.delete(0, tk.END)
                self._update_palette_display()
        
        ttk.Button(yes_frame, text="Add to Yes", command=add_yes).pack()
        
        # No frame
        no_frame = ttk.LabelFrame(dialog, text="NO (Cannot Exist)", padding=10)
        no_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        no_entry = ttk.Entry(no_frame, width=50)
        no_entry.pack(pady=5)
        
        no_listbox = tk.Listbox(no_frame, height=6)
        no_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        def add_no():
            item = no_entry.get().strip()
            if item:
                self.game_state.add_to_palette(item, False)
                no_listbox.insert(tk.END, item)
                no_entry.delete(0, tk.END)
                self._update_palette_display()
        
        ttk.Button(no_frame, text="Add to No", command=add_no).pack()
        
        # Load existing items
        for item in self.game_state.history.palette.yes_items:
            yes_listbox.insert(tk.END, item)
        for item in self.game_state.history.palette.no_items:
            no_listbox.insert(tk.END, item)
        
        def complete():
            if self.game_state.complete_palette():
                self._update_display()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to complete palette")
        
        ttk.Button(dialog, text="Complete Palette", command=complete).pack(pady=10)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


class SceneWizard:
    """Wizard for creating Scenes step-by-step"""
    
    def __init__(self, parent, game_state: GameState, event_id: UUID, callback: Callable):
        self.game_state = game_state
        self.event_id = event_id
        self.callback = callback
        self.characters = []
        
        self.scene = Scene()
        self.scene.event_id = event_id
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create Scene")
        self.dialog.geometry("600x550")
        self.dialog.transient(parent)
        
        self.step = 1
        self._show_step()
    
    def _show_step(self):
        """Show current step of wizard"""
        # Clear dialog
        for widget in self.dialog.winfo_children():
            widget.destroy()
        
        if self.step == 1:
            self._step_question()
        elif self.step == 2:
            self._step_set_stage()
        elif self.step == 3:
            self._step_characters()
        elif self.step == 4:
            self._step_play()
        elif self.step == 5:
            self._step_answer()
    
    def _step_question(self):
        """Step 1: State the Question"""
        ttk.Label(self.dialog, text="🎬 Creating a Scene (Step 1 of 5)",
                 font=("Arial", 14, "bold")).pack(pady=15)
        
        ttk.Label(self.dialog, text="Step 1: State the Question",
                 font=("Arial", 12, "bold"), foreground="#2E86AB").pack(pady=10)
        
        info_frame = ttk.Frame(self.dialog)
        info_frame.pack(padx=20, pady=10, fill=tk.X)
        
        ttk.Label(info_frame, text="Scenes answer questions. What do you want to know?",
                 wraplength=550).pack(anchor="w", pady=5)
        
        ttk.Label(info_frame, text="💡 Examples:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,5))
        examples = [
            "How did the peace treaty fall apart?",
            "What did the AI say when it first awoke?",
            "Who sabotaged the colony ship?",
        ]
        for ex in examples:
            ttk.Label(info_frame, text=f"  • {ex}", font=("Arial", 9)).pack(anchor="w", pady=2)
        
        ttk.Label(self.dialog, text="Your Question:", font=("Arial", 10, "bold")).pack(padx=20, pady=(15,5), anchor="w")
        question_text = scrolledtext.ScrolledText(self.dialog, wrap=tk.WORD, height=4, font=("Arial", 11))
        question_text.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        question_text.focus()
        
        def next_step():
            question = question_text.get(1.0, tk.END).strip()
            if question:
                self.scene.question = question
                self.step = 2
                self._show_step()
            else:
                messagebox.showwarning("Missing Question", "Please enter a question for this Scene!")
        
        ttk.Button(self.dialog, text="Next ➡️", command=next_step, 
                  style="Primary.TButton").pack(pady=15)
    
    def _step_set_stage(self):
        """Step 2: Set the Stage"""
        ttk.Label(self.dialog, text="🎬 Creating a Scene (Step 2 of 5)",
                 font=("Arial", 14, "bold")).pack(pady=15)
        
        ttk.Label(self.dialog, text="Step 2: Set the Stage",
                 font=("Arial", 12, "bold"), foreground="#2E86AB").pack(pady=10)
        
        ttk.Label(self.dialog, text="Where and when does this Scene take place?",
                 wraplength=550).pack(padx=20, pady=10)
        
        ttk.Label(self.dialog, text="Setting Description:", font=("Arial", 10, "bold")).pack(padx=20, pady=(10,5), anchor="w")
        stage_text = scrolledtext.ScrolledText(self.dialog, wrap=tk.WORD, height=5, font=("Arial", 10))
        stage_text.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        stage_text.focus()
        
        # Dictated option
        dict_frame = ttk.LabelFrame(self.dialog, text="Scene Type", padding=10)
        dict_frame.pack(padx=20, pady=15, fill=tk.X)
        
        is_dictated_var = tk.BooleanVar()
        
        ttk.Radiobutton(dict_frame, text="🎭 Played Scene (I'll roleplay it out)", 
                       variable=is_dictated_var, value=False).pack(anchor="w", pady=3)
        ttk.Radiobutton(dict_frame, text="📖 Dictated Scene (I'll just describe what happens)", 
                       variable=is_dictated_var, value=True).pack(anchor="w", pady=3)
        
        def next_step():
            stage = stage_text.get(1.0, tk.END).strip()
            self.scene.stage_description = stage
            self.scene.is_dictated = is_dictated_var.get()
            self.step = 3
            self._show_step()
        
        def prev_step():
            self.step = 1
            self._show_step()
        
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="⬅️ Back", command=prev_step).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Next ➡️", command=next_step, 
                  style="Primary.TButton").pack(side=tk.LEFT, padx=5)
    
    def _step_characters(self):
                 font=("Arial", 12, "bold"), foreground="#2E86AB").pack(pady=10)
        
        ttk.Label(self.dialog, text="Who appears in this Scene? (Optional but recommended)",
                 wraplength=550).pack(padx=20, pady=10)
        
        # Character list
        list_frame = ttk.LabelFrame(self.dialog, text="Characters in Scene", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        char_listbox = tk.Listbox(list_frame, height=6, font=("Arial", 10))
        char_listbox.pack(fill=tk.BOTH, expand=True)
        
        for char in self.characters:
            char_listbox.insert(tk.END, char.name)
        
        # Add character
        add_frame = ttk.LabelFrame(self.dialog, text="Add a Character", padding=10)
        add_frame.pack(fill=tk.X, padx=20, pady=10)
        
        name_frame = ttk.Frame(add_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="Name:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0,10))
        name_entry = ttk.Entry(name_frame, width=30, font=("Arial", 10))
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        
        def add_char():
            name = name_entry.get().strip()
            if name:
                char = Character(name=name)
                self.characters.append(char)
                char_listbox.insert(tk.END, name)
                name_entry.delete(0, tk.END)
        
        ttk.Button(name_frame, text="➕ Add", command=add_char).pack(side=tk.LEFT)
        
        ttk.Label(add_frame, text="💡 Tip: Add 1-3 characters. You can create new ones or reuse existing ones.",
                 font=("Arial", 9), foreground="#666", wraplength=500).pack(pady=5)
        
        def next_step():
            self.scene.characters = self.characters
            self.step = 4
            self._show_step()
        
        def prev_step():
            self.step = 2
            self._show_step()
        
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="⬅️ Back", command=prev_step).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Next ➡️", command=next_step, 
                  style="Primary.TButton"scene:").pack(pady=5)
        
        # Character list
        char_frame = ttk.Frame(self.d🎬 Creating a Scene (Step 4 of 5)",
                 font=("Arial", 14, "bold")).pack(pady=15)
        
        ttk.Label(self.dialog, text="Step 4: Play It Out",
                 font=("Arial", 12, "bold"), foreground="#2E86AB").pack(pady=10)
        
        if self.scene.is_dictated:
            ttk.Label(self.dialog, text="This is a DICTATED scene. Describe what happens:",
                     wraplength=550).pack(padx=20, pady=10)
        else:
            ttk.Label(self.dialog, text="This is a PLAYED scene. Roleplay the characters and take notes:",
                     wraplength=550).pack(padx=20, pady=10)
        
        ttk.Label(self.dialog, text="Your Notes (Optional):", font=("Arial", 10, "bold")).pack(padx=20, pady=(10,5), anchor="w")
        ttk.Label(self.dialog, text="Record dialogue, actions, or just jot down what happens",
                 font=("Arial", 9, "italic"), foreground="#666").pack(padx=20, pady=(0,5), anchor="w")
        
        notes_text = scrolledtext.ScrolledText(self.dialog, wrap=tk.WORD, height=8, font=("Arial", 10))
        notes_text.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        notes_text.focus()
        
        ttk.Label(self.dialog, text="💡 Take your time! This is where the magic happens.",
                 font=("Arial", 9), foreground="#0D7377", background="#E8F5E9",
                 wraplength=550).pack(padx=20, pady=10, fill=tk.X)
        
        def next_step():
            # Notes are optional - just move on
            self.step = 5🎬 Creating a Scene (Step 5 of 5)",
                 font=("Arial", 14, "bold")).pack(pady=15)
        
        ttk.Label(self.dialog, text="Step 5: Answer the Question",
                 font=("Arial", 12, "bold"), foreground="#2E86AB").pack(pady=10)
        
        q_frame = ttk.LabelFrame(self.dialog, text="The Question", padding=15)
        q_frame.pack(padx=20, pady=15, fill=tk.X)
        
        ttk.Label(q_frame, text=self.scene.question, wraplength=520, 
                 font=("Arial", 11, "italic"), foreground="#555").pack()
        
        ttk.Label(self.dialog, text="Based on what happened in the Scene, what's the answer?",
                 wraplength=550).pack(padx=20, pady=10)
        
        ttk.Label(self.dialog, text="Your Answer:", font=("Arial", 10, "bold")).pack(padx=20, pady=(10,5), anchor="w")
        answer_text = scrolledtext.ScrolledText(self.dialog, wrap=tk.WORD, height=5, font=("Arial", 11))
        answer_text.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        answer_text.focus()
        
        ttk.Label(self.dialog, text="💡 The answer should come from what you played/narrated. Be specific!",
                 font=("Arial", 9), foreground="#0D7377", background="#E8F5E9",
                 wraplength=550).pack(padx=20, pady=10, fill=tk.X)
        
        def complete():
            answer = answer_text.get(1.0, tk.END).strip()
            if answer:
                self.scene.answer = answer
                self.scene.is_complete = True
                
                # Create the scene
                scene_id = self.game_state.create_scene(self.scene, self.event_id)
                if scene_id:
                    self.callback()
                    self.dialog.destroy()
                    messagebox.showinfo("Scene Complete! 🎬",
                        "Your Scene has been added to the timeline!\n\n"
                        "You just zoomed WAY into a specific moment in history. "
                        "That's the magic of Microscope!")
                else:
                    messagebox.showerror("Error", "Failed to create scene")
            else:
                messagebox.showwarning("Missing Answer", 
                    "You must answer the question to complete the Scene!")
        
        def prev_step():
            self.step = 4
            self._show_step()
        
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="⬅️ Back", command=prev_step).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✅ Complete Scene", command=complete, 
                  style="Primary.TButton"(pady=5)
        else:
            ttk.Label(self.dialog, text="Play out the scene (take notes if desired):").pack(pady=5)
        
        notes_text = scrolledtext.ScrolledText(self.dialog, wrap=tk.WORD, height=10)
        notes_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        def next_step():
            # Notes are optional
            self.step = 5
            self._show_step()
        
        def prev_step():
            self.step = 3
            self._show_step()
        
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Back", command=prev_step).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Next", command=next_step).pack(side=tk.LEFT, padx=5)
    
    def _step_answer(self):
        """Step 5: Answer the Question"""
        ttk.Label(self.dialog, text="Step 5: Answer the Question",
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Label(self.dialog, text=f"Question: {self.scene.question}",
                 wraplength=550, font=("Arial", 10, "italic")).pack(pady=10)
        
        ttk.Label(self.dialog, text="Answer:").pack(pady=5)
        
        answer_text = scrolledtext.ScrolledText(self.dialog, wrap=tk.WORD, height=6)
        answer_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        def complete():
            answer = answer_text.get(1.0, tk.END).strip()
            if answer:
                self.scene.answer = answer
                self.scene.is_complete = True
                
                # Create the scene
                scene_id = self.game_state.create_scene(self.scene, self.event_id)
                if scene_id:
                    self.callback()
                    self.dialog.destroy()
                    messagebox.showinfo("Scene Created", "Scene successfully created!")
                else:
                    messagebox.showerror("Error", "Failed to create scene")
            else:
                messagebox.showwarning("Warning", "Answer required")
        
        def prev_step():
            self.step = 4
            self._show_step()
        
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Back", command=prev_step).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Complete Scene", command=complete).pack(side=tk.LEFT, padx=5)


if __name__ == "__main__":
    app = MicroscopeApp()
    app.run()
