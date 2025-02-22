import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import time
from logic import (generate_themes, generate_npc, get_une_interaction, select_from_list,
                  generate_action_oracle, check_the_fates_dice, determine_result,
                  process_results, roll_dice, draw_dice)
from data_manager import add_to_general_data, remove_from_general_data, get_general_data, load_campaign, save_campaign
import os

class RPGApp:
    def __init__(self, root, data_manager):
        self.root = root
        self.root.title("RPG Generator")
        self.data_manager = data_manager
        self.file_path = None
        self.windows = {'manage_data': None, 'roll_fate': None, 'manage_themes': None}
        self.relationship_var = tk.StringVar(value="neutral")
        self.demeanor_var = tk.StringVar(value="friendly")
        self.themes_listbox = None

        self.root.geometry("600x700")
        self.root.configure(bg="#212121")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Tabbed Interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Dice Roller Tab
        self.dice_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dice_tab, text="Dice Roller")
        self.setup_dice_tab()

        # Generators Tab
        self.gen_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.gen_tab, text="Generators")
        self.setup_gen_tab()

        # Campaign Tab
        self.campaign_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.campaign_tab, text="Campaign")
        self.setup_campaign_tab()

        # Status Label
        self.status_label = tk.Label(self.root, text="", anchor="w", bg="#212121", fg="#E0E0E0")
        self.status_label.pack(fill="x", padx=10, pady=5)

        # Initial File Prompt
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

    def setup_dice_tab(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Helvetica", 12), background="#212121", foreground="#E0E0E0")
        style.configure("TButton", font=("Helvetica", 12), background="#424242", foreground="#E0E0E0")
        style.map("TButton", background=[], foreground=[])
        style.configure("TFrame", background="#424242")
        style.configure("TEntry", fieldbackground="#424242", foreground="#E0E0E0")
        style.configure("TLabelframe", background="#212121", foreground="#E0E0E0")
        style.configure("TLabelframe.Label", background="#212121", foreground="#E0E0E0")

        input_frame = ttk.Frame(self.dice_tab)
        input_frame.grid(row=0, column=0, pady=15, padx=10, sticky="ew")

        ttk.Label(input_frame, text="Action Dice:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.action_dice_entry = ttk.Entry(input_frame, width=4)
        self.action_dice_entry.insert(0, "1")
        self.action_dice_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="+", width=2, command=lambda: self.adjust_dice(self.action_dice_entry, 1)).grid(row=0, column=2, padx=2)
        ttk.Button(input_frame, text="-", width=2, command=lambda: self.adjust_dice(self.action_dice_entry, -1)).grid(row=0, column=3, padx=2)

        ttk.Label(input_frame, text="Danger Dice:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.danger_dice_entry = ttk.Entry(input_frame, width=4)
        self.danger_dice_entry.insert(0, "0")
        self.danger_dice_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="+", width=2, command=lambda: self.adjust_dice(self.danger_dice_entry, 1)).grid(row=1, column=2, padx=2)
        ttk.Button(input_frame, text="-", width=2, command=lambda: self.adjust_dice(self.danger_dice_entry, -1)).grid(row=1, column=3, padx=2)

        ttk.Button(input_frame, text="Roll Dice", command=self.roll_and_process).grid(row=0, column=4, padx=10, pady=5)
        ttk.Button(input_frame, text="Clear", command=self.clear_dice).grid(row=1, column=4, padx=10, pady=5)

        self.dice_result_label = ttk.Label(self.dice_tab, text="", font=("Helvetica", 16, "bold"), background="#212121", foreground="#E0E0E0")
        self.dice_result_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        canvas_frame = ttk.LabelFrame(self.dice_tab, text="Dice Results", labelanchor="n")
        canvas_frame.grid(row=2, column=0, pady=5, padx=10, sticky="nsew")
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.dice_canvas = tk.Canvas(canvas_frame, bg="#2D2D2D", yscrollcommand=scrollbar.set)
        self.dice_canvas.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.dice_canvas.yview)

        self.dice_tab.columnconfigure(0, weight=1)
        self.dice_tab.rowconfigure(2, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

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
            self.dice_result_label.config(text=error_msg, foreground="#D32F2F")
            return

        if num_action_dice == 0 and num_danger_dice == 0:
            self.dice_result_label.config(text="No dice to roll!", foreground="#D32F2F")
            return

        action_dice = roll_dice(num_action_dice)
        danger_dice = roll_dice(num_danger_dice)
        action_dice_sorted, danger_dice_sorted, cancelled_dice, remaining_action_dice = process_results(action_dice.copy(), danger_dice.copy())
        result = determine_result(remaining_action_dice)

        self.dice_result_label.config(text=result, foreground="#E0E0E0")
        x, y = 10, 10
        y = draw_dice(self.dice_canvas, action_dice_sorted, x, y, 30, "Action Dice", cancelled_dice, remaining_action_dice, True)
        y = draw_dice(self.dice_canvas, danger_dice_sorted, x, y, 30, "Danger Dice", cancelled_dice, [], False)
        self.dice_canvas.config(scrollregion=(0, 0, self.dice_canvas.winfo_width(), y))
        for _ in range(6):
            self.dice_canvas.update()
            time.sleep(0.02)

    def setup_gen_tab(self):
        top_frame = tk.Frame(self.gen_tab, height=125, bg="#212121")
        top_frame.grid(row=0, column=0, sticky="nsew")
        top_frame.grid_propagate(False)
        for i in range(4):
            top_frame.columnconfigure(i, weight=1)
        self.setup_column1(top_frame)
        self.setup_column2(top_frame)
        self.setup_column3(top_frame)
        self.setup_column4(top_frame)

        bottom_frame = tk.Frame(self.gen_tab, bg="#212121")
        bottom_frame.grid(row=1, column=0, sticky="nsew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(0, weight=1)
        self.output_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD, bg="#2D2D2D", fg="#E0E0E0")
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.gen_tab.columnconfigure(0, weight=1)
        self.gen_tab.rowconfigure(1, weight=1)

    def setup_column1(self, parent):
        col_frame = tk.Frame(parent, bg="#212121")
        col_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        tk.Button(col_frame, text="Create NPC", command=self.btn_create_npc, bg="#424242", fg="#E0E0E0").grid(row=0, column=0, sticky="ew")
        tk.Button(col_frame, text="Roll Interaction", command=self.btn_roll_interaction, bg="#424242", fg="#E0E0E0").grid(row=1, column=0, sticky="ew")
        ttk.Combobox(col_frame, textvariable=self.relationship_var, state='readonly', 
                     values=["loved", "friendly", "peaceful", "neutral", "distrustful", "hostile", "hated"]).grid(row=2, column=0, sticky="ew")
        ttk.Combobox(col_frame, textvariable=self.demeanor_var, state='readonly', 
                     values=["scheming", "insane", "friendly", "hostile", "inquisitive", "knowing", "mysterious", "prejudiced"]).grid(row=3, column=0, sticky="ew")

    def setup_column2(self, parent):
        col_frame = tk.Frame(parent, bg="#212121")
        col_frame.grid(row=0, column=1, sticky="nw", padx=10, pady=10)
        tk.Button(col_frame, text="Manage Data", command=self.btn_manage_lists, bg="#424242", fg="#E0E0E0").grid(row=0, column=0, sticky="ew")
        tk.Button(col_frame, text="Choose Character", command=self.btn_choose_character, bg="#424242", fg="#E0E0E0").grid(row=1, column=0, sticky="ew")
        tk.Button(col_frame, text="Choose Thread", command=self.btn_choose_thread, bg="#424242", fg="#E0E0E0").grid(row=2, column=0, sticky="ew")
        tk.Button(col_frame, text="Roll Fate", command=self.btn_roll_fate, bg="#424242", fg="#E0E0E0").grid(row=3, column=0, sticky="ew")

    def setup_column3(self, parent):
        col_frame = tk.Frame(parent, bg="#212121")
        col_frame.grid(row=0, column=2, sticky="nw", padx=10, pady=10)
        self.themes_listbox = tk.Listbox(col_frame, height=5, bg="#2D2D2D", fg="#E0E0E0")
        self.themes_listbox.grid(row=0, column=0, sticky="ew")

    def setup_column4(self, parent):
        col_frame = tk.Frame(parent, bg="#212121")
        col_frame.grid(row=0, column=3, sticky="nw", padx=10, pady=10)
        tk.Button(col_frame, text="Action Oracle", command=self.btn_action_oracle, bg="#424242", fg="#E0E0E0").grid(row=0, column=0, sticky="ew")
        tk.Button(col_frame, text="Manage Themes", command=self.btn_manage_themes, bg="#424242", fg="#E0E0E0").grid(row=1, column=0, sticky="ew")
        tk.Button(col_frame, text="Generate Themes", command=self.btn_generate_themes, bg="#424242", fg="#E0E0E0").grid(row=2, column=0, sticky="ew")
        tk.Button(col_frame, text="Clear Output", command=self.btn_clear_output, bg="#424242", fg="#E0E0E0").grid(row=3, column=0, sticky="ew")

    def setup_campaign_tab(self):
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12), background="#212121", foreground="#E0E0E0")
        style.configure("TButton", font=("Helvetica", 12), background="#424242", foreground="#E0E0E0")
        style.configure("TEntry", fieldbackground="#424242", foreground="#E0E0E0")

        control_frame = tk.Frame(self.campaign_tab, bg="#212121")
        control_frame.pack(pady=10, padx=10, fill="x")

        ttk.Button(control_frame, text="Load Campaign", command=self.load_campaign).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="Save Campaign", command=self.save_campaign).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(control_frame, text="New Character:").grid(row=1, column=0, padx=5, pady=5)
        self.char_entry = ttk.Entry(control_frame, width=20)
        self.char_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="Add", command=lambda: self.add_item("characters")).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(control_frame, text="New Thread:").grid(row=2, column=0, padx=5, pady=5)
        self.thread_entry = ttk.Entry(control_frame, width=20)
        self.thread_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="Add", command=lambda: self.add_item("threads")).grid(row=2, column=2, padx=5, pady=5)

        self.campaign_text = scrolledtext.ScrolledText(self.campaign_tab, height=20, width=70, bg="#2D2D2D", fg="#E0E0E0", font=("Helvetica", 12))
        self.campaign_text.pack(pady=10, padx=10, fill="both", expand=True)
        self.update_campaign_display()

    # Generator Methods (unchanged except for output handling)
    def btn_roll_fate(self):
        if self.windows['roll_fate']:
            self.windows['roll_fate'].focus_set()
            self.windows['roll_fate'].lift()
            return
        window = tk.Toplevel(self.root)
        window.title("Check The Fates")
        window.geometry("230x95")
        window.resizable(False, False)
        self.windows['roll_fate'] = window
        window.bind('<Destroy>', lambda e: self.on_window_close('roll_fate'))

        tk.Label(window, text="Chaos Factor:").grid(row=0, column=0)
        chaos_factor_var = tk.StringVar(value="5")
        ttk.Combobox(window, textvariable=chaos_factor_var, values=[str(i) for i in range(1, 10)], state="readonly").grid(row=0, column=1)
        tk.Label(window, text="Likelihood:").grid(row=1, column=0)
        likelihood_var = tk.StringVar(value="50/50")
        ttk.Combobox(window, textvariable=likelihood_var, values=["Certain", "Nearly Certain", "Very Likely", "Likely", "50/50", "Unlikely", "Very Unlikely", "Nearly Impossible", "Impossible"], state="readonly").grid(row=1, column=1)
        result_label = tk.Label(window, text="Result details will appear here")
        result_label.grid(row=3, column=0, columnspan=2)

        def check_fates():
            chaos_factor = int(chaos_factor_var.get())
            likelihood = likelihood_var.get()
            result, _, _, _ = check_the_fates_dice(chaos_factor, likelihood)
            result_label.config(text=result)
            self.output_text.insert(tk.END, f"Fate Result: {result}\n\n")
            self.output_text.see(tk.END)
        tk.Button(window, text="Check The Fates", command=check_fates).grid(row=2, column=0, columnspan=2)

    def btn_roll_interaction(self):
        result = get_une_interaction(self.relationship_var.get(), self.demeanor_var.get())
        self.output_text.insert(tk.END, result + "\n\n")
        self.output_text.see(tk.END)

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
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        tk.Button(button_frame, text="Load Campaign", command=self.load_campaign).grid(row=0, column=0, sticky="ew", padx=5)
        tk.Button(button_frame, text="Save Campaign", command=self.save_campaign).grid(row=0, column=1, sticky="ew", padx=5)

        self.update_listbox(lst_characters, 'characters')
        self.update_listbox(lst_threads, 'threads')

        lst_characters.bind('<<ListboxSelect>>', lambda event: self.on_listbox_select(event, entry_character))
        lst_threads.bind('<<ListboxSelect>>', lambda event: self.on_listbox_select(event, entry_thread))

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

    def btn_action_oracle(self):
        result = generate_action_oracle()
        self.output_text.insert(tk.END, result + "\n\n")
        self.output_text.see(tk.END)

    def btn_create_npc(self):
        result = generate_npc()
        self.output_text.insert(tk.END, result + "\n\n")
        self.output_text.see(tk.END)

    def btn_choose_character(self):
        result = select_from_list(self.data_manager, 'characters')
        self.output_text.insert(tk.END, result + "\n\n")
        self.output_text.see(tk.END)

    def btn_generate_themes(self):
        themes = [self.themes_listbox.get(i) for i in range(self.themes_listbox.size())]
        weights = [40, 30, 20, 8, 2]
        results = generate_themes(themes, weights)
        for result in results:
            self.output_text.insert(tk.END, result + "\n\n")
        self.output_text.see(tk.END)

    def btn_choose_thread(self):
        result = select_from_list(self.data_manager, 'threads')
        self.output_text.insert(tk.END, result + "\n\n")
        self.output_text.see(tk.END)

    def btn_clear_output(self):
        self.output_text.delete(1.0, tk.END)

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

    def save_current_data(self):
        if self.file_path and save_campaign(self.data_manager, self.file_path):
            messagebox.showinfo("Success", f"Campaign saved to {self.file_path}")
        else:
            messagebox.showwarning("Warning", "No file loaded. Please save as a new file.")

    def on_window_close(self, window_name):
        self.windows[window_name] = None

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
        self.campaign_text.delete(1.0, tk.END)
        chars = "\n".join(self.data_manager.get_items("characters"))
        threads = "\n".join(self.data_manager.get_items("threads"))
        self.campaign_text.insert(tk.END, f"Characters:\n{chars}\n\nThreads:\n{threads}")