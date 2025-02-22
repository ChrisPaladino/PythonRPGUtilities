import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import time
from logic import (generate_themes, generate_npc, get_une_interaction, select_from_list,
                  generate_action_oracle, check_the_fates_dice, determine_result,
                  process_results, roll_dice)
from data_manager import add_to_general_data, remove_from_general_data, get_general_data, load_campaign, save_campaign
import os

class RPGApp:
    def __init__(self, root, data_manager):
        self.root = root
        self.root.title("RPG Generator")
        self.data_manager = data_manager
        self.file_path = None
        self.windows = {'manage_data': None, 'manage_themes': None}
        self.relationship_var = tk.StringVar(value="neutral")
        self.demeanor_var = tk.StringVar(value="friendly")
        self.themes_listbox = None

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
        else:
            self.update_status("No file selected. Starting with empty lists.")
        self.update_all_lists()

    def update_status(self, message):
        self.status_label.config(text=message)

    def prompt_initial_file(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        lists_dir = os.path.join(script_dir, "data", "lists")
        os.makedirs(lists_dir, exist_ok=True)
        return filedialog.askopenfilename(
            title="Select default JSON file",
            initialdir=lists_dir,
            filetypes=[("JSON files", "*.json")]
        )

    def update_all_lists(self):
        if self.themes_listbox:
            self.themes_listbox.delete(0, tk.END)
            for theme in ["action", "mystery", "personal", "social", "tension"]:
                self.themes_listbox.insert(tk.END, theme)

    def setup_themes_tab(self):
        control_frame = tk.Frame(self.themes_tab)
        control_frame.pack(pady=10, padx=10, fill="x")

        tk.Button(control_frame, text="Manage Themes", command=self.btn_manage_themes).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="Generate Themes", command=self.btn_generate_themes).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(control_frame, text="Clear Output", command=lambda: self.themes_output.delete(1.0, tk.END)).grid(row=0, column=2, padx=5, pady=5)

        self.themes_listbox = tk.Listbox(self.themes_tab, height=5)
        self.themes_listbox.pack(pady=10, padx=10, fill="x")

        self.themes_output = scrolledtext.ScrolledText(self.themes_tab, wrap=tk.WORD, height=20, width=70)
        self.themes_output.pack(fill="both", expand=True, padx=10, pady=10)

        self.update_all_lists()

    def setup_fate_tab(self):
        control_frame = tk.Frame(self.fate_tab)
        control_frame.pack(pady=10, padx=10, fill="x")

        # Dice Rolling Section
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

        self.dice_canvas = tk.Canvas(self.fate_tab, height=0)  # Initially collapsed
        self.dice_canvas.pack(fill="x", padx=10, pady=5)

        # Fate Section
        fate_frame = tk.LabelFrame(self.fate_tab, text="Fate Check")
        fate_frame.pack(pady=5, padx=10, fill="x")

        tk.Label(fate_frame, text="Chaos Factor:").grid(row=0, column=0, padx=5, pady=5)
        self.chaos_factor_var = tk.StringVar(value="5")
        ttk.Combobox(fate_frame, textvariable=self.chaos_factor_var, values=[str(i) for i in range(1, 10)], state="readonly").grid(row=0, column=1, padx=5, pady=5)

        tk.Label(fate_frame, text="Likelihood:").grid(row=0, column=2, padx=5, pady=5)
        self.likelihood_var = tk.StringVar(value="50/50")
        ttk.Combobox(fate_frame, textvariable=self.likelihood_var, values=["Certain", "Nearly Certain", "Very Likely", "Likely", "50/50", "Unlikely", "Very Unlikely", "Nearly Impossible", "Impossible"], state="readonly").grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(fate_frame, text="Roll Fate", command=self.btn_roll_fate).grid(row=0, column=4, padx=10, pady=5)

        # Interaction Section
        interaction_frame = tk.LabelFrame(self.fate_tab, text="NPC Interaction")
        interaction_frame.pack(pady=5, padx=10, fill="x")

        ttk.Combobox(interaction_frame, textvariable=self.relationship_var, state='readonly', 
                     values=["loved", "friendly", "peaceful", "neutral", "distrustful", "hostile", "hated"]).grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(interaction_frame, textvariable=self.demeanor_var, state='readonly', 
                     values=["scheming", "insane", "friendly", "hostile", "inquisitive", "knowing", "mysterious", "prejudiced"]).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(interaction_frame, text="Roll Interaction", command=self.btn_roll_interaction).grid(row=0, column=2, padx=10, pady=5)

        # Other Buttons
        other_frame = tk.Frame(self.fate_tab)
        other_frame.pack(pady=5, padx=10, fill="x")
        tk.Button(other_frame, text="Action Oracle", command=self.btn_action_oracle).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(other_frame, text="Create NPC", command=self.btn_create_npc).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(other_frame, text="Clear Output", command=lambda: self.fate_output.delete(1.0, tk.END)).grid(row=0, column=2, padx=5, pady=5)

        self.fate_output = scrolledtext.ScrolledText(self.fate_tab, wrap=tk.WORD, height=15, width=70)
        self.fate_output.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_chars_tab(self):
        control_frame = tk.Frame(self.chars_tab)
        control_frame.pack(pady=10, padx=10, fill="x")

        tk.Button(control_frame, text="Manage Data", command=self.btn_manage_lists).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="Choose Character", command=self.btn_choose_character).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(control_frame, text="Choose Thread", command=self.btn_choose_thread).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(control_frame, text="New Character:").grid(row=1, column=0, padx=5, pady=5)
        self.char_entry = ttk.Entry(control_frame, width=20)
        self.char_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="Add", command=lambda: self.add_item("characters")).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(control_frame, text="New Thread:").grid(row=2, column=0, padx=5, pady=5)
        self.thread_entry = ttk.Entry(control_frame, width=20)
        self.thread_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="Add", command=lambda: self.add_item("threads")).grid(row=2, column=2, padx=5, pady=5)

        self.chars_output = scrolledtext.ScrolledText(self.chars_tab, wrap=tk.WORD, height=20, width=70)
        self.chars_output.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_campaign_display()

    # Dice Methods
    def adjust_dice(self, entry, delta):
        try:
            current_value = int(entry.get())
        except ValueError:
            current_value = 0
        new_value = max(0, min(10, current_value + delta))
        entry.delete(0, tk.END)
        entry.insert(0, str(new_value))

    def clear_dice(self):
        self.action_dice_entry.delete(0, tk.END)
        self.action_dice_entry.insert(0, "1")
        self.danger_dice_entry.delete(0, tk.END)
        self.danger_dice_entry.insert(0, "0")
        self.dice_result_label.config(text="")
        self.dice_canvas.delete("all")
        self.dice_canvas.config(height=0)  # Collapse on clear

    def draw_dice(self, dice, x, y, dice_size, label, cancelled_dice, remaining_dice, is_action):
        self.dice_canvas.create_text(x, y, text=label, anchor="nw", font=('Helvetica', 14, 'bold'))
        y += 35
        highest_remaining_die = max(remaining_dice, default=0)
        cancelled_count = {die: cancelled_dice.count(die) for die in set(cancelled_dice)}

        for die in dice:
            rect_color = "grey"
            text_color = "black"
            if die in cancelled_count and cancelled_count[die] > 0:
                rect_color = "#D32F2F"  # Red for cancelled
                text_color = "white"
                cancelled_count[die] -= 1
            elif is_action and die == highest_remaining_die and die in remaining_dice:
                rect_color = "#388E3C"  # Green for highest remaining
                text_color = "white"

            self.dice_canvas.create_rectangle(x, y, x + dice_size, y + dice_size, fill=rect_color, outline="black")
            self.dice_canvas.create_text(x + dice_size // 2, y + dice_size // 2, text=str(die), fill=text_color, font=('Helvetica', dice_size // 3, 'bold'))
            x += dice_size + 5
        
        return y + dice_size + 20

    def roll_and_process(self):
        self.dice_canvas.delete("all")
        try:
            num_action_dice = int(self.action_dice_entry.get())
            if not (0 <= num_action_dice <= 10):
                raise ValueError("Action Dice must be between 0 and 10.")
            num_danger_dice = int(self.danger_dice_entry.get())
            if not (0 <= num_danger_dice <= 10):
                raise ValueError("Danger Dice must be between 0 and 10.")
        except ValueError as e:
            error_msg = str(e) if str(e).startswith(("Action", "Danger")) else "Invalid input: Use numbers 0-10."
            self.dice_result_label.config(text=error_msg)
            return

        if num_action_dice == 0 and num_danger_dice == 0:
            self.dice_result_label.config(text="No dice to roll!")
            return

        action_dice = roll_dice(num_action_dice)
        danger_dice = roll_dice(num_danger_dice)
        action_dice_sorted, danger_dice_sorted, cancelled_dice, remaining_action_dice = process_results(action_dice.copy(), danger_dice.copy())
        result = determine_result(remaining_action_dice)

        self.dice_result_label.config(text=result)
        x, y = 10, 10
        y = self.draw_dice(action_dice_sorted, x, y, 30, "Action Dice", cancelled_dice, remaining_action_dice, True)
        y = self.draw_dice(danger_dice_sorted, x, y, 30, "Danger Dice", cancelled_dice, [], False)
        self.dice_canvas.config(height=y)  # Expand to show results
        for _ in range(6):
            self.dice_canvas.update()
            time.sleep(0.02)
        self.fate_output.insert(tk.END, f"Dice Result: {result}\n\n")
        self.fate_output.see(tk.END)

    # Themes Methods
    def btn_manage_themes(self):
        if self.windows['manage_themes']:
            self.windows['manage_themes'].focus_set()
            self.windows['manage_themes'].lift()
            return
        window = tk.Toplevel(self.root)
        window.title("Manage Themes")
        window.resizable(False, False)
        self.windows['manage_themes'] = window
        window.bind('<Destroy>', lambda e: self.on_window_close('manage_themes'))

        left_frame = tk.Frame(window)
        middle_frame = tk.Frame(window)
        right_frame = tk.Frame(window)
        left_frame.grid(row=0, column=0, padx=5, pady=5)
        middle_frame.grid(row=0, column=1, padx=5, pady=5)
        right_frame.grid(row=0, column=2, padx=5, pady=5)

        lb_current_themes = tk.Listbox(left_frame, height=5)
        lb_current_themes.grid(row=0, column=0, sticky="nsew")
        lb_selected_themes = tk.Listbox(right_frame, height=5)
        lb_selected_themes.grid(row=0, column=0, sticky="nsew")

        def add_theme():
            selected = lb_current_themes.curselection()
            if selected:
                theme = lb_current_themes.get(selected)
                lb_current_themes.delete(selected)
                lb_selected_themes.insert(tk.END, theme)

        def remove_theme():
            selected = lb_selected_themes.curselection()
            if selected:
                theme = lb_selected_themes.get(selected)
                lb_selected_themes.delete(selected)
                lb_current_themes.insert(tk.END, theme)

        def confirm_selection():
            if lb_selected_themes.size() != 5:
                messagebox.showerror("Error", "You must select exactly 5 unique themes.")
                return
            self.themes_listbox.delete(0, tk.END)
            for i in range(lb_selected_themes.size()):
                self.themes_listbox.insert(tk.END, lb_selected_themes.get(i))
            window.destroy()

        tk.Button(middle_frame, text="Add >", command=add_theme).grid(row=0, column=0, pady=5)
        tk.Button(middle_frame, text="< Remove", command=remove_theme).grid(row=1, column=0, pady=5)
        tk.Button(middle_frame, text="Confirm", command=confirm_selection).grid(row=2, column=0, pady=5)
        lb_current_themes.bind("<Double-Button-1>", lambda _: add_theme())
        lb_selected_themes.bind("<Double-Button-1>", lambda _: remove_theme())

        for i in range(self.themes_listbox.size()):
            lb_current_themes.insert(tk.END, self.themes_listbox.get(i))

    def btn_generate_themes(self):
        themes = [self.themes_listbox.get(i) for i in range(self.themes_listbox.size())]
        weights = [40, 30, 20, 8, 2]
        results = generate_themes(themes, weights)
        self.themes_output.delete(1.0, tk.END)
        for result in results:
            self.themes_output.insert(tk.END, result + "\n\n")
        self.themes_output.see(tk.END)

    # Fate & Oracles Methods
    def btn_roll_fate(self):
        chaos_factor = int(self.chaos_factor_var.get())
        likelihood = self.likelihood_var.get()
        result, _, _, _ = check_the_fates_dice(chaos_factor, likelihood)
        self.fate_output.insert(tk.END, f"Fate Result: {result}\n\n")
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
    def btn_manage_lists(self):
        if self.windows['manage_data']:
            self.windows['manage_data'].focus_set()
            self.windows['manage_data'].lift()
            return
        window = tk.Toplevel(self.root)
        window.title("Manage Data")
        window.geometry("600x525")
        window.resizable(True, True)
        self.windows['manage_data'] = window
        window.bind('<Destroy>', lambda e: self.on_window_close('manage_data'))

        main_frame = tk.Frame(window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        characters_frame = tk.Frame(main_frame)
        threads_frame = tk.Frame(main_frame)
        characters_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        threads_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        characters_frame.grid_columnconfigure(0, weight=1)
        characters_frame.grid_rowconfigure(1, weight=1)
        threads_frame.grid_columnconfigure(0, weight=1)
        threads_frame.grid_rowconfigure(1, weight=1)

        entry_character = tk.Entry(characters_frame)
        entry_character.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        lst_characters = tk.Listbox(characters_frame, selectmode=tk.SINGLE)
        lst_characters.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        tk.Button(characters_frame, text="Add/Update Character", command=lambda: self.add_update_entry('characters', entry_character, lst_characters)).grid(row=2, column=0, sticky="ew", pady=2)
        tk.Button(characters_frame, text="Delete Character", command=lambda: self.delete_entry('characters', lst_characters)).grid(row=3, column=0, sticky="ew", pady=2)

        entry_thread = tk.Entry(threads_frame)
        entry_thread.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        lst_threads = tk.Listbox(threads_frame, selectmode=tk.SINGLE)
        lst_threads.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        tk.Button(threads_frame, text="Add/Update Thread", command=lambda: self.add_update_entry('threads', entry_thread, lst_threads)).grid(row=2, column=0, sticky="ew", pady=2)
        tk.Button(threads_frame, text="Delete Thread", command=lambda: self.delete_entry('threads', lst_threads)).grid(row=3, column=0, sticky="ew", pady=2)

        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        tk.Button(button_frame, text="Load Campaign", command=self.load_campaign).grid(row=0, column=0, sticky="ew", padx=5)
        tk.Button(button_frame, text="Save Campaign", command=self.save_campaign).grid(row=0, column=1, sticky="ew", padx=5)

        self.update_listbox(lst_characters, 'characters')
        self.update_listbox(lst_threads, 'threads')

        lst_characters.bind('<<ListboxSelect>>', lambda event: self.on_listbox_select(event, entry_character))
        lst_threads.bind('<<ListboxSelect>>', lambda event: self.on_listbox_select(event, entry_thread))

    def btn_choose_character(self):
        result = select_from_list(self.data_manager, 'characters')
        self.chars_output.insert(tk.END, result + "\n\n")
        self.chars_output.see(tk.END)

    def btn_choose_thread(self):
        result = select_from_list(self.data_manager, 'threads')
        self.chars_output.insert(tk.END, result + "\n\n")
        self.chars_output.see(tk.END)

    # Utility Methods
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
            self.update_campaign_display()
        else:
            current_entries = get_general_data(self.data_manager, data_type)
            if len(current_entries) >= 25:
                messagebox.showinfo("Limit Reached", f"You can have no more than 25 {data_type}.")
            elif current_entries.count(new_entry) >= 3:
                messagebox.showinfo("Limit Reached", f"You can have no more than 3 '{new_entry}' {data_type}.")

    def delete_entry(self, data_type, listbox_widget):
        selection_index = listbox_widget.curselection()
        if selection_index:
            selected_text = listbox_widget.get(selection_index).split('. ', 1)[-1]
            remove_from_general_data(self.data_manager, data_type, selected_text)
            self.update_listbox(listbox_widget, data_type)
            self.save_current_data_silently()
            self.update_status(f"Deleted {data_type}: {selected_text}")
            self.update_campaign_display()

    def save_current_data_silently(self):
        if self.file_path and save_campaign(self.data_manager, self.file_path):
            pass
        else:
            self.update_status("Warning: No file loaded. Please save as a new file.")

    def load_campaign(self):
        lists_dir = os.path.join(os.path.dirname(__file__), "data", "lists")
        file_path = filedialog.askopenfilename(
            defaultextension=".json", 
            filetypes=[("JSON files", "*.json")],
            initialdir=lists_dir
        )
        if file_path and load_campaign(self.data_manager, file_path):
            self.file_path = file_path
            self.update_campaign_display()
            self.update_status(f"Campaign loaded from {file_path}")
        else:
            messagebox.showerror("Error", "Failed to load campaign data.")

    def save_campaign(self):
        lists_dir = os.path.join(os.path.dirname(__file__), "data", "lists")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", 
            filetypes=[("JSON files", "*.json")],
            initialdir=lists_dir
        )
        if file_path and save_campaign(self.data_manager, file_path):
            self.file_path = file_path
            self.update_status(f"Campaign saved to {file_path}")
            messagebox.showinfo("Success", "Campaign saved successfully!")

    def add_item(self, data_type):
        entry = self.char_entry if data_type == "characters" else self.thread_entry
        item = entry.get()
        if add_to_general_data(self.data_manager, data_type, item):
            entry.delete(0, tk.END)
            self.update_campaign_display()

    def update_campaign_display(self):
        self.chars_output.delete(1.0, tk.END)
        chars = "\n".join(self.data_manager.get_items("characters"))
        threads = "\n".join(self.data_manager.get_items("threads"))
        self.chars_output.insert(tk.END, f"Characters:\n{chars}\n\nThreads:\n{threads}")

    def on_window_close(self, window_name):
        self.windows[window_name] = None