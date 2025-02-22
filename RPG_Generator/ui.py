import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from logic import (generate_themes, generate_npc, get_une_interaction, select_from_list,
                  generate_action_oracle, check_the_fates_dice)
from data_manager import add_to_general_data, remove_from_general_data, get_general_data, load_campaign, save_campaign
import os

class RPGApp:
    def __init__(self, root, data_manager):
        self.root = root
        self.root.title("RPG Generator")
        self.data_manager = data_manager
        self.file_path = None
        self.windows = {'manage_data': None, 'roll_fate': None, 'manage_themes': None}
        
        # Initialize variables
        self.relationship_var = tk.StringVar(value="neutral")
        self.demeanor_var = tk.StringVar(value="friendly")
        self.themes_listbox = None
        
        # Add a status label at the bottom of the main window
        self.status_label = tk.Label(self.root, text="", anchor="w")
        self.status_label.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        # Set up UI
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.top_frame = self.setup_top_frame()
        self.output_text = self.setup_bottom_frame()
        
        # Load initial data and update UI
        self.file_path = self.prompt_initial_file()
        print(f"Initial file path: {self.file_path}")  # Debug: Check file path
        if self.file_path:
            if self.data_manager.load_from_file(self.file_path):
                print(f"Loaded data: {self.data_manager.data}")  # Debug: Check loaded data
                self.update_status(f"Data loaded from {self.file_path}")
                self.update_all_lists()
            else:
                print("Failed to load data from file")  # Debug: Loading failure
                self.update_status("Failed to load data. Starting with empty lists.")
                self.update_all_lists()
        else:
            print("No file selected")  # Debug: No file selected
            self.update_status("No file selected. Starting with empty lists.")
            self.update_all_lists()

    def update_status(self, message):
        self.status_label.config(text=message)

    def prompt_initial_file(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        lists_dir = os.path.join(script_dir, "data", "lists")
        os.makedirs(lists_dir, exist_ok=True)  # Ensure directory exists
        return filedialog.askopenfilename(
            title="Select default JSON file",
            initialdir=lists_dir,
            filetypes=[("JSON files", "*.json")]
        )

    def update_all_lists(self):
        # Update any listboxes or UI components that depend on data
        if hasattr(self, 'themes_listbox'):
            print("Updating themes listbox")  # Debug: Check themes update
            self.themes_listbox.delete(0, tk.END)
            for theme in ["action", "mystery", "personal", "social", "tension"]:
                self.themes_listbox.insert(tk.END, theme)
        print(f"Characters data: {get_general_data(self.data_manager, 'characters')}")  # Debug: Check characters
        print(f"Threads data: {get_general_data(self.data_manager, 'threads')}")  # Debug: Check threads

    def setup_top_frame(self):
        top_frame = tk.Frame(self.root, height=125)
        top_frame.grid(row=0, column=0, sticky="nsew")
        top_frame.grid_propagate(False)
        for i in range(4):
            top_frame.columnconfigure(i, weight=1)
        self.setup_column1(top_frame)
        self.setup_column2(top_frame)
        self.setup_column3(top_frame)
        self.setup_column4(top_frame)
        return top_frame

    def setup_bottom_frame(self):
        bottom_frame = tk.Frame(self.root)
        bottom_frame.grid(row=1, column=0, sticky="nsew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(0, weight=1)
        output_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD)  # Fixed to bottom_frame
        output_text.pack(fill=tk.BOTH, expand=True)
        return output_text

    def setup_column1(self, parent):
        col_frame = tk.Frame(parent)
        col_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        tk.Button(col_frame, text="Create NPC", command=self.btn_create_npc).grid(row=0, column=0, sticky="ew")
        tk.Button(col_frame, text="Roll Interaction", command=self.btn_roll_interaction).grid(row=1, column=0, sticky="ew")
        ttk.Combobox(col_frame, textvariable=self.relationship_var, state='readonly', 
                     values=["loved", "friendly", "peaceful", "neutral", "distrustful", "hostile", "hated"]).grid(row=2, column=0, sticky="ew")
        ttk.Combobox(col_frame, textvariable=self.demeanor_var, state='readonly', 
                     values=["scheming", "insane", "friendly", "hostile", "inquisitive", "knowing", "mysterious", "prejudiced"]).grid(row=3, column=0, sticky="ew")

    def setup_column2(self, parent):
        col_frame = tk.Frame(parent)
        col_frame.grid(row=0, column=1, sticky="nw", padx=10, pady=10)
        tk.Button(col_frame, text="Manage Data", command=self.btn_manage_lists).grid(row=0, column=0, sticky="ew")
        tk.Button(col_frame, text="Choose Character", command=self.btn_choose_character).grid(row=1, column=0, sticky="ew")
        tk.Button(col_frame, text="Choose Thread", command=self.btn_choose_thread).grid(row=2, column=0, sticky="ew")
        tk.Button(col_frame, text="Roll Fate", command=self.btn_roll_fate).grid(row=3, column=0, sticky="ew")

    def setup_column3(self, parent):
        col_frame = tk.Frame(parent)
        col_frame.grid(row=0, column=2, sticky="nw", padx=10, pady=10)
        self.themes_listbox = tk.Listbox(col_frame, height=5)
        self.themes_listbox.grid(row=0, column=0, sticky="ew")

    def setup_column4(self, parent):
        col_frame = tk.Frame(parent)
        col_frame.grid(row=0, column=3, sticky="nw", padx=10, pady=10)
        tk.Button(col_frame, text="Action Oracle", command=self.btn_action_oracle).grid(row=0, column=0, sticky="ew")
        tk.Button(col_frame, text="Manage Themes", command=self.btn_manage_themes).grid(row=1, column=0, sticky="ew")
        tk.Button(col_frame, text="Generate Themes", command=self.btn_generate_themes).grid(row=2, column=0, sticky="ew")
        tk.Button(col_frame, text="Clear Output", command=self.btn_clear_output).grid(row=3, column=0, sticky="ew")

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
        window.geometry("600x525")  # Default size, but will be resizable
        window.resizable(True, True)  # Allow resizing
        self.windows['manage_data'] = window
        window.bind('<Destroy>', lambda e: self.on_window_close('manage_data'))

        # Main frame to hold everything, with padding
        main_frame = tk.Frame(window, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Use a grid layout for the main frame
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)  # Allow the content to expand vertically

        # Frames for characters and threads
        characters_frame = tk.Frame(main_frame)
        threads_frame = tk.Frame(main_frame)
        characters_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        threads_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Configure frames to expand
        characters_frame.grid_columnconfigure(0, weight=1)
        characters_frame.grid_rowconfigure(1, weight=1)  # Listbox expands vertically
        threads_frame.grid_columnconfigure(0, weight=1)
        threads_frame.grid_rowconfigure(1, weight=1)  # Listbox expands vertically

        # Character Section
        entry_character = tk.Entry(characters_frame)
        entry_character.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        lst_characters = tk.Listbox(characters_frame, selectmode=tk.SINGLE)
        lst_characters.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        tk.Button(characters_frame, text="Add/Update Character", command=lambda: self.add_update_entry('characters', entry_character, lst_characters)).grid(row=2, column=0, sticky="ew", pady=2)
        tk.Button(characters_frame, text="Delete Character", command=lambda: self.delete_entry('characters', lst_characters)).grid(row=3, column=0, sticky="ew", pady=2)

        # Thread Section
        entry_thread = tk.Entry(threads_frame)
        entry_thread.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        lst_threads = tk.Listbox(threads_frame, selectmode=tk.SINGLE)
        lst_threads.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        tk.Button(threads_frame, text="Add/Update Thread", command=lambda: self.add_update_entry('threads', entry_thread, lst_threads)).grid(row=2, column=0, sticky="ew", pady=2)
        tk.Button(threads_frame, text="Delete Thread", command=lambda: self.delete_entry('threads', lst_threads)).grid(row=3, column=0, sticky="ew", pady=2)

        # Campaign buttons at the bottom
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        def load_campaign_data():
            lists_dir = os.path.join(os.path.dirname(__file__), "data", "lists")
            file_path = filedialog.askopenfilename(
                defaultextension=".json", 
                filetypes=[("JSON files", "*.json")],
                initialdir=lists_dir
            )
            if file_path and load_campaign(self.data_manager, file_path):
                self.file_path = file_path
                self.update_listbox(lst_characters, 'characters')
                self.update_listbox(lst_threads, 'threads')
                messagebox.showinfo("Success", f"Campaign loaded from {file_path}")
            else:
                messagebox.showerror("Error", "Failed to load campaign data.")

        def save_campaign_data():
            lists_dir = os.path.join(os.path.dirname(__file__), "data", "lists")
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json", 
                filetypes=[("JSON files", "*.json")],
                initialdir=lists_dir
            )
            if file_path and save_campaign(self.data_manager, file_path):
                self.file_path = file_path
                messagebox.showinfo("Success", "Campaign saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save campaign data.")

        tk.Button(button_frame, text="Load Campaign", command=load_campaign_data).grid(row=0, column=0, sticky="ew", padx=5)
        tk.Button(button_frame, text="Save Campaign", command=save_campaign_data).grid(row=0, column=1, sticky="ew", padx=5)

        # Update listboxes immediately after creating the window
        def update_listboxes():
            print(f"Updating listboxes - Characters: {get_general_data(self.data_manager, 'characters')}, Threads: {get_general_data(self.data_manager, 'threads')}")  # Debug: Check data before updating
            self.update_listbox(lst_characters, 'characters')
            self.update_listbox(lst_threads, 'threads')

        update_listboxes()

        # Bind listbox selections
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
        print(f"Updating {data_type} listbox with: {entries}")  # Debug: Check entries
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
            self.save_current_data_silently()  # Use silent save for automatic saves
            self.update_status(f"Updated {data_type}: {new_entry}")
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
            self.save_current_data_silently()  # Use silent save for automatic saves
            self.update_status(f"Deleted {data_type}: {selected_text}")

    def save_current_data_silently(self):
        # Silent save without message boxes
        if self.file_path and save_campaign(self.data_manager, self.file_path):
            pass  # No message box, just save quietly
        else:
            self.update_status("Warning: No file loaded. Please save as a new file.")

    def save_current_data(self):
        # Manual save with message boxes (used only for "Save Campaign" button)
        if self.file_path and save_campaign(self.data_manager, self.file_path):
            messagebox.showinfo("Success", f"Campaign saved to {self.file_path}")
        else:
            messagebox.showwarning("Warning", "No file loaded. Please save as a new file.")

    def on_window_close(self, window_name):
        self.windows[window_name] = None