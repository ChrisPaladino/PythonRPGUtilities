import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog  # Added filedialog here
import time
from logic import (generate_themes, generate_npc, get_une_interaction, select_from_list,
                  generate_action_oracle, check_fate_chart, determine_result,
                  process_results, roll_dice)
from data_manager import add_to_general_data, remove_from_general_data, get_general_data, load_campaign, save_campaign
import os
import json

class RPGApp:
    # Class constants for magic numbers
    MAX_ITEMS = 25
    MAX_DUPLICATES = 3
    DICE_SIZE = 30
    MAX_DICE = 10
    
    def __init__(self, root, data_manager):
        self.root = root
        self.root.title("RPG Generator")
        self.data_manager = data_manager
        self.file_path = None
        self.relationship_var = tk.StringVar(value="neutral")
        self.demeanor_var = tk.StringVar(value="friendly")
        self.theme_order = ["Action", "Mystery", "Personal", "Social", "Tension"]  # Default theme order
        self.themes_listbox = None

        # Initialize variables for Rolling with Mastery feature
        self.action_dice_values = []
        self.danger_dice_values = []
        self.action_dice_tags = []
        self.mastery_used = False
        self.mastery_die_index = None # Track which die was rerolled with mastery
        self.mastery_is_action = None
        self.mastery_die_value = None  # Track the value of the rerolled die

        self.root.geometry("600x700")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.themes_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.themes_tab, text="Themes")
        self.setup_themes_tab()

        self.fate_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.fate_tab, text="Fate & Oracles")
        self.setup_fate_tab()

        self.chars_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chars_tab, text="Characters & Threads")
        self.setup_chars_tab()

        self.status_label = tk.Label(self.root, text="", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=5)

        self.file_path = self.prompt_initial_file()
        if self.file_path and self.data_manager.load_from_file(self.file_path):
            self.update_status(f"Data loaded from {self.file_path}")
            # Populate listboxes immediately after loading data
            self.update_listbox(self.chars_listbox, 'characters')
            self.update_listbox(self.threads_listbox, 'threads')
        else:
            self.update_status("No file selected. Starting with empty lists.")
            # Populate empty listboxes if no file loaded
            self.update_listbox(self.chars_listbox, 'characters')
            self.update_listbox(self.threads_listbox, 'threads')
        self.update_all_lists()

    def update_status(self, message):
        self.status_label.config(text=message)

    def get_config_path(self):
        """Get the path to the config file that stores the last loaded file."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, "..", "data", "app_config.json")

    def save_last_file_path(self, file_path):
        """Save the last loaded file path to config."""
        try:
            config_path = self.get_config_path()
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump({"last_file": file_path}, f)
        except Exception as e:
            print(f"Could not save config: {e}")

    def load_last_file_path(self):
        """Load the last loaded file path from config."""
        try:
            config_path = self.get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get("last_file")
        except Exception as e:
            print(f"Could not load config: {e}")
        return None

    def prompt_initial_file(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        lists_dir = os.path.join(script_dir, "..", "data", "lists")
        os.makedirs(lists_dir, exist_ok=True)
        
        # Try to load the last file automatically
        last_file = self.load_last_file_path()
        if last_file and os.path.exists(last_file):
            # Automatically load the last file without prompting
            self.save_last_file_path(last_file)  # Refresh the config
            return last_file
        
        # If no last file or it doesn't exist, prompt the user
        file_path = filedialog.askopenfilename(
            title="Select default JSON file",
            initialdir=lists_dir,
            filetypes=[("JSON files", "*.json")]
        )
        
        # Save the selected file for next time
        if file_path:
            self.save_last_file_path(file_path)
        
        return file_path

    def update_all_lists(self):
        """Update the themes listbox with the current theme order."""
        self.themes_listbox.delete(0, tk.END)
        for theme in self.theme_order:
            self.themes_listbox.insert(tk.END, theme)

    def move_theme_up(self):
        """Move the selected theme up in the list."""
        try:
            selection = self.themes_listbox.curselection()
            if not selection or selection[0] == 0:
                return
            index = selection[0]
            self.theme_order[index], self.theme_order[index - 1] = self.theme_order[index - 1], self.theme_order[index]
            self.update_all_lists()
            self.themes_listbox.selection_clear(0, tk.END)
            self.themes_listbox.selection_set(index - 1)
            self.themes_listbox.see(index - 1)
        except:
            messagebox.showwarning("Warning", "Please select a theme to move.")

    def move_theme_down(self):
        """Move the selected theme down in the list."""
        try:
            selection = self.themes_listbox.curselection()
            if not selection or selection[0] == len(self.theme_order) - 1:
                return
            index = selection[0]
            self.theme_order[index], self.theme_order[index + 1] = self.theme_order[index + 1], self.theme_order[index]
            self.update_all_lists()
            self.themes_listbox.selection_clear(0, tk.END)
            self.themes_listbox.selection_set(index + 1)
            self.themes_listbox.see(index + 1)
        except:
            messagebox.showwarning("Warning", "Please select a theme to move.")

    def reset_theme_order(self):
        """Reset the theme order to the default (Action, Mystery, Personal, Social, Tension)."""
        self.theme_order = ["Action", "Mystery", "Personal", "Social", "Tension"]
        self.update_all_lists()

    def setup_themes_tab(self):
        control_frame = tk.Frame(self.themes_tab)
        control_frame.pack(pady=10, padx=10, fill="x")

        # Reordering controls and listbox
        reorder_frame = tk.Frame(control_frame)
        reorder_frame.pack(fill="x", pady=5)

        self.themes_listbox = tk.Listbox(reorder_frame, height=5, selectmode=tk.SINGLE)
        self.themes_listbox.pack(side=tk.LEFT, padx=5, fill="y")
        self.update_all_lists()  # Initialize with default order

        # Reordering buttons
        button_frame = tk.Frame(reorder_frame)
        button_frame.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Move Up", command=self.move_theme_up).pack(pady=2)
        ttk.Button(button_frame, text="Move Down", command=self.move_theme_down).pack(pady=2)
        ttk.Button(button_frame, text="Reset Order", command=self.reset_theme_order).pack(pady=2)

        # Action buttons
        action_frame = tk.Frame(control_frame)
        action_frame.pack(fill="x", pady=5)
        tk.Button(action_frame, text="Generate Themes", command=self.btn_generate_themes).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Clear Output", command=lambda: self.themes_output.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)

        # Output area
        self.themes_output = scrolledtext.ScrolledText(self.themes_tab, wrap=tk.WORD, height=20, width=70)
        self.themes_output.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_fate_tab(self):
        control_frame = tk.Frame(self.fate_tab)
        control_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(control_frame, text="Action Dice:").grid(row=0, column=0, padx=5, pady=5)
        self.action_dice_entry = ttk.Entry(control_frame, width=4)
        self.action_dice_entry.insert(0, "1")
        self.action_dice_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="+", width=2, command=lambda: self.adjust_dice(self.action_dice_entry, 1)).grid(row=0, column=2, padx=2)
        ttk.Button(control_frame, text="-", width=2, command=lambda: self.adjust_dice(self.action_dice_entry, -1)).grid(row=0, column=3, padx=2)

        tk.Label(control_frame, text="Danger Dice:").grid(row=1, column=0, padx=5, pady=5)
        self.danger_dice_entry = ttk.Entry(control_frame, width=4)
        self.danger_dice_entry.insert(0, "0")
        self.danger_dice_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="+", width=2, command=lambda: self.adjust_dice(self.danger_dice_entry, 1)).grid(row=1, column=2, padx=2)
        ttk.Button(control_frame, text="-", width=2, command=lambda: self.adjust_dice(self.danger_dice_entry, -1)).grid(row=1, column=3, padx=2)

        ttk.Button(control_frame, text="Roll Dice", command=self.roll_and_process).grid(row=0, column=4, padx=10, pady=5)
        ttk.Button(control_frame, text="Clear Dice", command=self.clear_dice).grid(row=1, column=4, padx=10, pady=5)

        self.dice_result_label = tk.Label(self.fate_tab, text="", font=("Helvetica", 12, "bold"))
        self.dice_result_label.pack(pady=5)

        self.dice_canvas = tk.Canvas(self.fate_tab, height=0)
        self.dice_canvas.pack(fill="x", padx=10, pady=5)

        fate_frame = tk.LabelFrame(self.fate_tab, text="Fate Check")
        fate_frame.pack(pady=5, padx=10, fill="x")

        tk.Label(fate_frame, text="Chaos Factor:").grid(row=0, column=0, padx=5, pady=5)
        self.chaos_factor_var = tk.StringVar(value="5")
        ttk.Combobox(fate_frame, textvariable=self.chaos_factor_var, values=[str(i) for i in range(1, 10)], state="readonly", width=4).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(fate_frame, text="Likelihood:").grid(row=0, column=2, padx=5, pady=5)
        self.likelihood_var = tk.StringVar(value="50/50")
        ttk.Combobox(fate_frame, textvariable=self.likelihood_var, values=["Certain", "Nearly Certain", "Very Likely", "Likely", "50/50", "Unlikely", "Very Unlikely", "Nearly Impossible", "Impossible"], state="readonly").grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(fate_frame, text="Roll Fate", command=self.btn_roll_fate).grid(row=0, column=4, padx=10, pady=5)

        interaction_frame = tk.LabelFrame(self.fate_tab, text="NPC Interaction")
        interaction_frame.pack(pady=5, padx=10, fill="x")

        ttk.Combobox(interaction_frame, textvariable=self.relationship_var, state='readonly', 
                     values=["loved", "friendly", "peaceful", "neutral", "distrustful", "hostile", "hated"]).grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(interaction_frame, textvariable=self.demeanor_var, state='readonly', 
                     values=["scheming", "insane", "friendly", "hostile", "inquisitive", "knowing", "mysterious", "prejudiced"]).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(interaction_frame, text="Roll Interaction", command=self.btn_roll_interaction).grid(row=0, column=2, padx=10, pady=5)

        other_frame = tk.Frame(self.fate_tab)
        other_frame.pack(pady=5, padx=10, fill="x")
        tk.Button(other_frame, text="Action Oracle", command=self.btn_action_oracle).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(other_frame, text="Create NPC", command=self.btn_create_npc).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(other_frame, text="Clear Output", command=lambda: self.fate_output.delete(1.0, tk.END)).grid(row=0, column=2, padx=5, pady=5)

        self.fate_output = scrolledtext.ScrolledText(self.fate_tab, wrap=tk.WORD, height=15, width=70)
        self.fate_output.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_chars_tab(self):
        """Setup the Characters & Threads tab with characters and threads sections."""
        main_frame = tk.Frame(self.chars_tab)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Setup Characters and Threads sections side by side
        self._setup_characters_section(main_frame)
        self._setup_threads_section(main_frame)
        
        # Setup buttons and output area
        self._setup_chars_controls(main_frame)
        self._setup_chars_output(main_frame)
        self._setup_campaign_buttons(main_frame)

        # Populate listboxes
        self.update_listbox(self.chars_listbox, 'characters')
        self.update_listbox(self.threads_listbox, 'threads')

    def _setup_characters_section(self, parent_frame):
        """Setup the Characters section with entry, buttons, and listbox."""
        chars_frame = tk.LabelFrame(parent_frame, text="Characters")
        chars_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)
        chars_frame.grid_columnconfigure(0, weight=1)
        chars_frame.grid_rowconfigure(2, weight=1)

        self.char_entry = tk.Entry(chars_frame, width=30, state='normal')
        self.char_entry.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

        tk.Button(chars_frame, text="Add/Update Character", 
                  command=lambda: self.add_update_entry('characters', self.char_entry, self.chars_listbox)
                  ).grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        tk.Button(chars_frame, text="Delete Character", 
                  command=lambda: self.delete_entry('characters', self.chars_listbox)
                  ).grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        self.chars_listbox = tk.Listbox(chars_frame, selectmode=tk.SINGLE)
        self.chars_listbox.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=2)
        self.chars_listbox.bind('<<ListboxSelect>>', lambda event: self.on_listbox_select(event, self.char_entry))

    def _setup_threads_section(self, parent_frame):
        """Setup the Threads section with entry, buttons, and listbox."""
        threads_frame = tk.LabelFrame(parent_frame, text="Threads")
        threads_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)
        threads_frame.grid_columnconfigure(0, weight=1)
        threads_frame.grid_rowconfigure(2, weight=1)

        self.thread_entry = tk.Entry(threads_frame, width=30, state='normal')
        self.thread_entry.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

        tk.Button(threads_frame, text="Add/Update Thread", 
                  command=lambda: self.add_update_entry('threads', self.thread_entry, self.threads_listbox)
                  ).grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        tk.Button(threads_frame, text="Delete Thread", 
                  command=lambda: self.delete_entry('threads', self.threads_listbox)
                  ).grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        self.threads_listbox = tk.Listbox(threads_frame, selectmode=tk.SINGLE)
        self.threads_listbox.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=2)
        self.threads_listbox.bind('<<ListboxSelect>>', lambda event: self.on_listbox_select(event, self.thread_entry))

    def _setup_chars_controls(self, parent_frame):
        """Setup control buttons for character and thread selection."""
        control_frame = tk.Frame(parent_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        tk.Button(control_frame, text="Choose Character", command=self.btn_choose_character
                  ).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="Choose Thread", command=self.btn_choose_thread
                  ).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(control_frame, text="Clear Output", command=lambda: self.chars_output.delete(1.0, tk.END)
                  ).grid(row=0, column=2, padx=5, pady=5)

    def _setup_chars_output(self, parent_frame):
        """Setup the output area for character and thread selections."""
        self.chars_output = scrolledtext.ScrolledText(parent_frame, wrap=tk.WORD, height=10, width=70)
        self.chars_output.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

    def _setup_campaign_buttons(self, parent_frame):
        """Setup load/save campaign buttons."""
        button_frame = tk.Frame(parent_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
        tk.Button(button_frame, text="Load Campaign", command=self.load_campaign
                  ).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(button_frame, text="Save Campaign", command=self.save_campaign
                  ).grid(row=0, column=1, padx=5, pady=5)

    # Dice Methods
    def adjust_dice(self, entry, delta):
        try:
            current_value = int(entry.get())
        except ValueError:
            current_value = 0
        new_value = max(0, min(10, current_value + delta))
        entry.delete(0, tk.END)
        entry.insert(0, str(new_value))

    def on_die_click(self, die_index, is_action):
        if self.mastery_used:
            self.update_status("Mastery already used, cannot reroll again")
            return

        if is_action:
            die_value = self.action_dice_values[die_index]
        else:
            die_value = self.danger_dice_values[die_index]

        # Set mastery flag immediately to prevent race condition from rapid clicks
        self.mastery_used = True
        
        # Disable all click bindings immediately
        for tag in self.action_dice_tags:
            self.dice_canvas.tag_unbind(tag, '<Button-1>')

        confirm = messagebox.askyesno(
            "Roll with Mastery",
            f"Roll with Mastery for {'Action' if is_action else 'Danger'} die with value {die_value}?"
        )
        if not confirm:
            self.update_status("Mastery reroll cancelled by user")
            # Re-enable click bindings if user cancels
            self.mastery_used = False
            for i, tag in enumerate(self.action_dice_tags):
                self.dice_canvas.tag_bind(tag, '<Button-1>', lambda event, idx=i, is_act=True: self.on_die_click(idx, is_act))
            return

        # Track *which die and type* was rerolled!
        self.mastery_die_index = die_index
        self.mastery_is_action = is_action

        # Reroll it
        if is_action:
            self.action_dice_values[die_index] = roll_dice(1)[0]
            self.mastery_die_value = self.action_dice_values[die_index]
        else:
            self.danger_dice_values[die_index] = roll_dice(1)[0]
            self.mastery_die_value = self.danger_dice_values[die_index]

        self.mastery_used = True

        # Rerun dice logic
        action_dice_sorted, danger_dice_sorted, cancelled_dice, remaining_action_dice = process_results(
            self.action_dice_values.copy(), self.danger_dice_values.copy()
        )

        remaining_danger_dice = self.danger_dice_values.copy()
        for action_die in self.action_dice_values:
            if action_die in remaining_danger_dice:
                remaining_danger_dice.remove(action_die)

        pressure_increase = remaining_danger_dice.count(6)
        result = determine_result(remaining_action_dice)
        if pressure_increase > 0:
            result = f"{result}; Pressure +{pressure_increase}"

        self.dice_result_label.config(text=result)

        self.dice_canvas.delete("all")
        x, y = 10, 10
        y = self.draw_dice(action_dice_sorted, x, y, 30, "Action Dice", cancelled_dice, remaining_action_dice, True)
        y = self.draw_dice(danger_dice_sorted, x, y, 30, "Danger Dice", cancelled_dice, [], False)
        self.dice_canvas.config(height=y)
        self.dice_canvas.update()

        self.fate_output.insert(tk.END, f"Mastery Reroll Result: {result}\n")
        if pressure_increase > 0:
            self.fate_output.insert(tk.END, f"Pressure: +{pressure_increase}\n")
        self.fate_output.insert(tk.END, "\n")
        self.fate_output.see(tk.END)


    def clear_dice(self):
        """Clear dice display and reset all dice-related state."""
        self.action_dice_entry.delete(0, tk.END)
        self.action_dice_entry.insert(0, "1")
        self.danger_dice_entry.delete(0, tk.END)
        self.danger_dice_entry.insert(0, "0")
        self.dice_result_label.config(text="")
        
        # Explicitly unbind all canvas tags before deletion
        for tag in self.action_dice_tags:
            self.dice_canvas.tag_unbind(tag, '<Button-1>')
        
        # Clear canvas and reset height
        self.dice_canvas.delete("all")
        self.dice_canvas.config(height=0)

        # Reset Rolling with Mastery state
        self.action_dice_values = []
        self.danger_dice_values = []
        self.action_dice_tags = []
        self.mastery_used = False
        self.mastery_die_value = None
        self.mastery_die_index = None
        self.mastery_is_action = None

    def _determine_die_color(self, die, i, is_action, cancelled_count, highest_remaining_die, remaining_dice):
        """Determine die background and text color based on its status.
        
        Args:
            die: The die value
            i: Die index in the list
            is_action: Whether this is an action die
            cancelled_count: Dict tracking cancelled dice
            highest_remaining_die: Highest die value that remains
            remaining_dice: List of remaining dice
            
        Returns:
            Tuple of (rect_color, text_color)
        """
        rect_color = "grey"
        text_color = "black"

        # Set background color based on die status
        if die in cancelled_count and cancelled_count[die] > 0:
            rect_color = "#D32F2F"
            text_color = "white"
            cancelled_count[die] -= 1
        elif is_action and die == highest_remaining_die and die in remaining_dice:
            rect_color = "#388E3C"
            text_color = "white"

        # BLUE for the rerolled die (mastery)
        if (
            self.mastery_used
            and self.mastery_die_index is not None
            and self.mastery_is_action is not None
            and i == self.mastery_die_index
            and is_action == self.mastery_is_action
        ):
            text_color = "blue"

        return rect_color, text_color

    def draw_dice(self, dice, x, y, dice_size, label, cancelled_dice, remaining_dice, is_action):
        """Draw dice on canvas with appropriate colors and click bindings.
        
        Args:
            dice: List of dice values to draw
            x, y: Starting position for drawing
            dice_size: Size of each die in pixels
            label: Label for the dice group
            cancelled_dice: List of cancelled dice values
            remaining_dice: List of remaining dice values
            is_action: Whether these are action dice
            
        Returns:
            Updated y position for next element
        """
        self.dice_canvas.create_text(x, y, text=label, anchor="nw", font=('Helvetica', 14, 'bold'))
        y += 35
        highest_remaining_die = max(remaining_dice, default=0)
        cancelled_count = {die: cancelled_dice.count(die) for die in set(cancelled_dice)}
        
        if is_action:
            self.action_dice_tags = []  # Reset tags for Action Dice

        for i, die in enumerate(dice):
            rect_color, text_color = self._determine_die_color(
                die, i, is_action, cancelled_count, highest_remaining_die, remaining_dice
            )

            # Set up tags for interaction
            if is_action:
                tag = f"action_die_{i}"
                self.action_dice_tags.append(tag)
            else:
                tag = f"danger_die_{i}"
            tags = (tag,)

            # Draw dice
            self.dice_canvas.create_rectangle(x, y, x + dice_size, y + dice_size, fill=rect_color, tags=tags)
            self.dice_canvas.create_text(x + dice_size // 2, y + dice_size // 2, text=str(die), fill=text_color, font=('Helvetica', 16, 'bold'), tags=tags)

            # Bind click for mastery if not used
            if not self.mastery_used:
                self.dice_canvas.tag_bind(tag, '<Button-1>', lambda event, idx=i, is_act=is_action: self.on_die_click(idx, is_act))

            x += dice_size + 5

        return y + dice_size + 20  # Make sure this is outside the for-loop!


    def roll_and_process(self):
        """Roll dice and process results with visual display."""
        # Unbind previous canvas tags before clearing
        for tag in self.action_dice_tags:
            self.dice_canvas.tag_unbind(tag, '<Button-1>')
        
        self.dice_canvas.delete("all")
        try:
            num_action_dice = int(self.action_dice_entry.get())
            if not (0 <= num_action_dice <= self.MAX_DICE):
                raise ValueError(f"Action Dice must be between 0 and {self.MAX_DICE}.")
            num_danger_dice = int(self.danger_dice_entry.get())
            if not (0 <= num_danger_dice <= self.MAX_DICE):
                raise ValueError(f"Danger Dice must be between 0 and {self.MAX_DICE}.")
        except ValueError as e:
            error_msg = str(e) if str(e).startswith(("Action", "Danger")) else "Invalid input: Use numbers 0-10."
            self.dice_result_label.config(text=error_msg)
            return

        if num_action_dice == 0 and num_danger_dice == 0:
            self.dice_result_label.config(text="No dice to roll!")
            return

        # Reset mastery state
        self.mastery_used = False
        self.action_dice_tags = []
        self.mastery_die_index = None
        self.mastery_is_action = None
        self.mastery_die_value = None

        # Roll dice
        action_dice = roll_dice(num_action_dice)
        danger_dice = roll_dice(num_danger_dice)
        
        # Process the dice (sorts and cancels)
        action_dice_sorted, danger_dice_sorted, cancelled_dice, remaining_action_dice = process_results(action_dice.copy(), danger_dice.copy())
        
        # Calculate uncancelled Danger Dice
        remaining_danger_dice = danger_dice.copy()
        for action_die in action_dice:
            if action_die in remaining_danger_dice:
                remaining_danger_dice.remove(action_die)
        
        # Count uncancelled 6s for Pressure
        pressure_increase = remaining_danger_dice.count(6)
        
        # Store sorted dice values for display and rerolling
        self.action_dice_values = action_dice_sorted.copy()
        self.danger_dice_values = danger_dice_sorted.copy()
        
        result = determine_result(remaining_action_dice)
        if pressure_increase > 0:
            result = f"{result}; Pressure +{pressure_increase}"

        self.dice_result_label.config(text=result)
        x, y = 10, 10
        y = self.draw_dice(action_dice_sorted, x, y, self.DICE_SIZE, "Action Dice", cancelled_dice, remaining_action_dice, True)
        y = self.draw_dice(danger_dice_sorted, x, y, self.DICE_SIZE, "Danger Dice", cancelled_dice, [], False)
        self.dice_canvas.config(height=y)
        for _ in range(6):
            self.dice_canvas.update()
            time.sleep(0.02)
        self.fate_output.insert(tk.END, f"Dice Result: {result}\n")
        if pressure_increase > 0:
            self.fate_output.insert(tk.END, f"Pressure: +{pressure_increase}\n")
        self.fate_output.insert(tk.END, "\n")
        self.fate_output.see(tk.END)

        # If there are no action dice, disable mastery
        if num_action_dice == 0:
            self.mastery_used = True

    # Themes Methods
    def btn_generate_themes(self):
        """Generate themes based on the current order in the listbox."""
        themes = [self.themes_listbox.get(i) for i in range(self.themes_listbox.size())]
        weights = [40, 30, 20, 8, 2]  # Default weights (highest for first theme, lowest for last)
        results = generate_themes(themes, weights)
        self.themes_output.delete(1.0, tk.END)
        for result in results:
            self.themes_output.insert(tk.END, result + "\n\n")
        self.themes_output.see(tk.END)

    # Fate & Oracles Methods
    def btn_roll_fate(self):
        chaos_factor = int(self.chaos_factor_var.get())
        likelihood = self.likelihood_var.get()
        result, roll = check_fate_chart(chaos_factor, likelihood)
        self.fate_output.insert(tk.END, f"Fate Result: {result} (Roll: {roll})\n\n")
        self.fate_output.see(tk.END)

    def btn_roll_interaction(self):
        result = get_une_interaction(self.relationship_var.get(), self.demeanor_var.get())
        self.fate_output.insert(tk.END, result + "\n\n")
        self.fate_output.see(tk.END)

    def btn_action_oracle(self):
        result = generate_action_oracle()
        self.fate_output.insert(tk.END, result + "\n\n")
        self.fate_output.see(tk.END)

    def btn_create_npc(self):
        result = generate_npc()
        self.fate_output.insert(tk.END, result + "\n\n")
        self.fate_output.see(tk.END)

    # Characters & Threads Methods
    def btn_choose_character(self):
        result = select_from_list(self.data_manager, 'characters')
        self.chars_output.insert(tk.END, result + "\n\n")
        self.chars_output.see(tk.END)

    def btn_choose_thread(self):
        result = select_from_list(self.data_manager, 'threads')
        self.chars_output.insert(tk.END, result + "\n\n")
        self.chars_output.see(tk.END)

    def update_listbox(self, listbox_widget, data_type):
        entries = sorted(get_general_data(self.data_manager, data_type))
        listbox_widget.delete(0, tk.END)
        for index, entry in enumerate(entries, start=1):
            listbox_widget.insert(tk.END, f"{index}. {entry}")

    def on_listbox_select(self, event, entry_widget):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            value = widget.get(selection[0]).split('. ', 1)[-1]
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, value)
            # Ensure the entry remains editable
            entry_widget.config(state='normal')

    def add_update_entry(self, data_type, entry_widget, listbox_widget):
        new_entry = entry_widget.get().strip()
        if not new_entry:
            self.update_status(f"Cannot add empty {data_type}.")
            return
        success = add_to_general_data(self.data_manager, data_type, new_entry)
        if success:
            self.update_listbox(listbox_widget, data_type)
            self.save_current_data_silently()
            self.update_status(f"Updated {data_type}: {new_entry}")
        else:
            current_entries = get_general_data(self.data_manager, data_type)
            if len(current_entries) >= self.MAX_ITEMS:
                self.update_status(f"Limit reached: Cannot have more than {self.MAX_ITEMS} {data_type}.")
            elif current_entries.count(new_entry) >= self.MAX_DUPLICATES:
                self.update_status(f"Limit reached: Cannot have more than {self.MAX_DUPLICATES} '{new_entry}' {data_type}.")

    def delete_entry(self, data_type, listbox_widget):
        selection_index = listbox_widget.curselection()
        if selection_index:
            selected_text = listbox_widget.get(selection_index).split('. ', 1)[-1]
            remove_from_general_data(self.data_manager, data_type, selected_text)
            self.update_listbox(listbox_widget, data_type)
            self.save_current_data_silently()
            self.update_status(f"Deleted {data_type}: {selected_text}")

    def save_current_data_silently(self):
        if self.file_path and save_campaign(self.data_manager, self.file_path):
            pass
        else:
            self.update_status("Warning: No file loaded. Please save as a new file.")

    def load_campaign(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        lists_dir = os.path.join(script_dir, "..", "data", "lists")
        file_path = filedialog.askopenfilename(
            defaultextension=".json", 
            filetypes=[("JSON files", "*.json")],
            initialdir=lists_dir
        )
        if file_path and load_campaign(self.data_manager, file_path):
            self.file_path = file_path
            self.save_last_file_path(file_path)  # Remember this file
            self.update_listbox(self.chars_listbox, 'characters')
            self.update_listbox(self.threads_listbox, 'threads')
            self.update_status(f"Campaign loaded from {file_path}")
        else:
            if file_path:  # Only show error if user selected a file
                messagebox.showerror("Error", "Failed to load campaign data.")

    def save_campaign(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        lists_dir = os.path.join(script_dir, "..", "data", "lists")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", 
            filetypes=[("JSON files", "*.json")],
            initialdir=lists_dir
        )
        if file_path and save_campaign(self.data_manager, file_path):
            self.file_path = file_path
            self.save_last_file_path(file_path)  # Remember this file
            self.update_status(f"Campaign saved to {file_path}")
            messagebox.showinfo("Success", "Campaign saved to new location or updated existing file!")
        else:
            if file_path:  # Only show error if user selected a file
                messagebox.showerror("Error", "Failed to save campaign data.")
