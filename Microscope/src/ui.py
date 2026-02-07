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
        self.root.title("Microscope Solo Play")
        self.root.geometry("1400x900")
        
        self.game_state = GameState()
        self.selected_period_id: Optional[UUID] = None
        self.selected_event_id: Optional[UUID] = None
        
        self._setup_ui()
        self._update_display()
    
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
        
        # Phase indicator
        phase_frame = ttk.LabelFrame(left_panel, text="Current Phase", padding=10)
        phase_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.phase_label = ttk.Label(phase_frame, text="Setup: Big Picture", font=("Arial", 12, "bold"))
        self.phase_label.pack()
        
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
        
        # Control buttons
        control_frame = ttk.Frame(left_panel)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Create Period", command=self._create_period_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Create Event", command=self._create_event_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Create Scene", command=self._create_scene_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Complete Phase", command=self._complete_phase).pack(side=tk.LEFT, padx=2)
        
        # === RIGHT PANEL ===
        
        # Instructions panel
        instructions_frame = ttk.LabelFrame(right_panel, text="Instructions", padding=10)
        instructions_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.instructions_text = scrolledtext.ScrolledText(instructions_frame, wrap=tk.WORD, height=10, width=40)
        self.instructions_text.pack(fill=tk.BOTH, expand=True)
        
        # Detail inspector
        detail_frame = ttk.LabelFrame(right_panel, text="Details", padding=10)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.detail_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, height=15, width=40)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # Palette display
        palette_frame = ttk.LabelFrame(right_panel, text="Palette", padding=10)
        palette_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.palette_text = scrolledtext.ScrolledText(palette_frame, wrap=tk.WORD, height=10, width=40)
        self.palette_text.pack(fill=tk.BOTH, expand=True)
    
    def _update_display(self):
        """Update all display elements"""
        # Update phase label
        self.phase_label.config(text=self.game_state.current_phase.value)
        
        # Update focus label
        if self.game_state.current_focus:
            self.focus_label.config(text=self.game_state.current_focus.description)
        else:
            self.focus_label.config(text="No Focus")
        
        # Update instructions
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
        dialog.title("Enter Big Picture")
        dialog.geometry("500x300")
        
        ttk.Label(dialog, text="Describe your history in 1-2 sentences:",
                 font=("Arial", 11)).pack(padx=10,pady=10)
        
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, height=8)
        text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        def submit():
            big_picture = text_widget.get(1.0, tk.END).strip()
            if big_picture:
                if self.game_state.set_big_picture(big_picture):
                    self._update_display()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to set Big Picture")
            else:
                messagebox.showwarning("Warning", "Big Picture cannot be empty")
        
        ttk.Button(dialog, text="Submit", command=submit).pack(pady=10)
    
    def _create_period_dialog(self):
        """Dialog to create a new Period"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Period")
        dialog.geometry("450x400")
        
        # Title
        ttk.Label(dialog, text="Title:").pack(padx=10, pady=5)
        title_entry = ttk.Entry(dialog, width=50)
        title_entry.pack(padx=10, pady=5)
        
        # Description
        ttk.Label(dialog, text="Description:").pack(padx=10, pady=5)
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
            
            # Check if this is bookend creation
            if self.game_state.current_phase == GamePhase.SETUP_BOOKENDS:
                has_start = self.game_state.history.start_period_id is not None
                has_end = self.game_state.history.end_period_id is not None
                
                if not has_start:
                    is_start = messagebox.askyesno("Bookend", "Is this the START period?")
                    self.game_state.create_bookend_period(title, description, tone, is_start)
                elif not has_end:
                    is_start = False
                    self.game_state.create_bookend_period(title, description, tone, is_start)
                else:
                    messagebox.showinfo("Info", "Both bookends already created")
                    dialog.destroy()
                    return
            else:
                # Regular period creation - Insert after selected period or at start
                insert_after_idx = 0
                if self.selected_period_id:
                    periods = self.game_state.history.periods
                    for i, p in enumerate(periods):
                        if p.id == self.selected_period_id:
                            insert_after_idx = i
                            break
                
                period_id = self.game_state.create_period(title, description, tone, insert_after_idx)
                if not period_id:
                    messagebox.showerror("Error", "Failed to create period")
                    return
            
            self._update_display()
            dialog.destroy()
        
        ttk.Button(dialog, text="Create", command=submit).pack(pady=10)
    
    def _create_event_dialog(self):
        """Dialog to create a new Event"""
        if not self.selected_period_id and self.game_state.history.periods:
            messagebox.showinfo("Info", "Please select a Period first")
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
        if not self.selected_event_id and self.game_state.current_phase != GamePhase.PLAY_MAKE_HISTORY:
            messagebox.showinfo("Info", "Please select an Event first")
            return
        
        # Find an event
        event_id = self.selected_event_id
        if not event_id:
            # Try to find any event
            for period in self.game_state.history.periods:
                if period.events:
                    event_id = period.events[0].id
                    break
        
        if not event_id:
            messagebox.showerror("Error", "No events available. Create an Event first.")
            return
        
        SceneWizard(self.root, self.game_state, event_id, self._update_display)
    
    def _declare_focus(self):
        """Dialog to declare a Focus"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Declare Focus")
        dialog.geometry("500x250")
        
        ttk.Label(dialog, text="Enter your Focus for this round:",
                 font=("Arial", 11)).pack(padx=10, pady=10)
        
        ttk.Label(dialog, text="(A theme, question, or element to explore)").pack(padx=10)
        
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, height=6)
        text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        def submit():
            focus = text_widget.get(1.0, tk.END).strip()
            if focus:
                if self.game_state.declare_focus(focus):
                    self._update_display()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to declare Focus")
            else:
                messagebox.showwarning("Warning", "Focus cannot be empty")
        
        ttk.Button(dialog, text="Declare", command=submit).pack(pady=10)
    
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
        self.dialog.geometry("600x500")
        
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
        ttk.Label(self.dialog, text="Step 1: State the Question",
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Label(self.dialog, text="What question will this scene answer?").pack(pady=5)
        
        question_text = scrolledtext.ScrolledText(self.dialog, wrap=tk.WORD, height=6)
        question_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        def next_step():
            question = question_text.get(1.0, tk.END).strip()
            if question:
                self.scene.question = question
                self.step = 2
                self._show_step()
            else:
                messagebox.showwarning("Warning", "Question required")
        
        ttk.Button(self.dialog, text="Next", command=next_step).pack(pady=10)
    
    def _step_set_stage(self):
        """Step 2: Set the Stage"""
        ttk.Label(self.dialog, text="Step 2: Set the Stage",
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Label(self.dialog, text="Describe the setting:").pack(pady=5)
        
        stage_text = scrolledtext.ScrolledText(self.dialog, wrap=tk.WORD, height=6)
        stage_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Dictated option
        is_dictated_var = tk.BooleanVar()
        ttk.Checkbutton(self.dialog, text="Dictated Scene (narrated, not played)",
                       variable=is_dictated_var).pack(pady=5)
        
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
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Back", command=prev_step).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Next", command=next_step).pack(side=tk.LEFT, padx=5)
    
    def _step_characters(self):
        """Step 3: Choose Characters"""
        ttk.Label(self.dialog, text="Step 3: Choose Characters",
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        ttk.Label(self.dialog, text="Add characters to this scene:").pack(pady=5)
        
        # Character list
        char_frame = ttk.Frame(self.dialog)
        char_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        char_listbox = tk.Listbox(char_frame, height=8)
        char_listbox.pack(fill=tk.BOTH, expand=True)
        
        for char in self.characters:
            char_listbox.insert(tk.END, char.name)
        
        # Add character
        add_frame = ttk.Frame(self.dialog)
        add_frame.pack(fill=tk.X, padx=10)
        
        ttk.Label(add_frame, text="Name:").pack(side=tk.LEFT)
        name_entry = ttk.Entry(add_frame, width=30)
        name_entry.pack(side=tk.LEFT, padx=5)
        
        def add_char():
            name = name_entry.get().strip()
            if name:
                char = Character(name=name)
                self.characters.append(char)
                char_listbox.insert(tk.END, name)
                name_entry.delete(0, tk.END)
        
        ttk.Button(add_frame, text="Add", command=add_char).pack(side=tk.LEFT)
        
        def next_step():
            self.scene.characters = self.characters
            self.step = 4
            self._show_step()
        
        def prev_step():
            self.step = 2
            self._show_step()
        
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Back", command=prev_step).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Next", command=next_step).pack(side=tk.LEFT, padx=5)
    
    def _step_play(self):
        """Step 4: Play/Narrate Scene"""
        ttk.Label(self.dialog, text="Step 4: Play the Scene",
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        if self.scene.is_dictated:
            ttk.Label(self.dialog, text="Narrate what happens:").pack(pady=5)
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
