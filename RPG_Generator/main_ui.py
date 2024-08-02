import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from npc_logic import (generate_themes, generate_npc, get_une_interaction, select_from_list, generate_action_oracle,
                       add_to_general_data, remove_from_general_data, get_general_data, check_the_fates_dice,
                       load_campaign, save_campaign, data_manager, initialize_data)

# Only allow one of each window open
manage_data_window_open = None
roll_fate_window_open = None
manage_themes_window_open = None
selected_file_path = initialize_data()
global_file_path = None

# Initialize main window
root = tk.Tk()
root.title("RPG Generator")

# Initialize global variables for relationship and demeanor
relationship_var = tk.StringVar()
demeanor_var = tk.StringVar()
themes_listbox = None  # Global declaration for the themes listbox

def update_listbox(listbox_widget, data_type):
    entries = get_general_data(data_type)
    listbox_widget.delete(0, tk.END)
    for index, entry in enumerate(sorted(entries), start=1):
        if entry != "Choose character" and entry != "Choose thread":
            listbox_widget.insert(tk.END, f"{index}. {entry}")

def btn_roll_fate():
    global roll_fate_window_open

    if roll_fate_window_open is not None:
        roll_fate_window_open.focus_set()
        roll_fate_window_open.lift()
        return
    
    roll_fate_window = tk.Toplevel()
    roll_fate_window.title("Check The Fates")
    roll_fate_window.geometry("230x95")
    roll_fate_window.resizable(False, False)

    roll_fate_window_open = roll_fate_window
    roll_fate_window.bind('<Destroy>', lambda e: on_window_close('roll_fate'))

    tk.Label(roll_fate_window, text="Chaos Factor:").grid(row=0, column=0)
    chaos_factor_var = tk.StringVar(value="5")
    chaos_factor_options = [str(i) for i in range(1, 10)]
    chaos_factor_dropdown = ttk.Combobox(roll_fate_window, textvariable=chaos_factor_var, values=chaos_factor_options, state="readonly")
    chaos_factor_dropdown.grid(row=0, column=1)

    tk.Label(roll_fate_window, text="Likelihood:").grid(row=1, column=0)
    likelihood_var = tk.StringVar(value="50/50")
    likelihood_options = ["Certain", "Nearly Certain", "Very Likely", "Likely", "50/50", "Unlikely", "Very Unlikely", "Nearly Impossible", "Impossible"]
    likelihood_dropdown = ttk.Combobox(roll_fate_window, textvariable=likelihood_var, values=likelihood_options, state="readonly")
    likelihood_dropdown.grid(row=1, column=1)

    result_label = tk.Label(roll_fate_window, text="Result details will appear here")
    result_label.grid(row=3, column=0, columnspan=2)

    def btn_check_the_fates():
        chaos_factor = int(chaos_factor_var.get())
        likelihood = likelihood_var.get()
        result, dice1, dice2, total_roll = check_the_fates_dice(chaos_factor, likelihood)
        result_text = result
        result_label.config(text=result_text)
        
    check_fates_button = tk.Button(roll_fate_window, text="Check The Fates", command=btn_check_the_fates)
    check_fates_button.grid(row=2, column=0, columnspan=2)

def btn_roll_interaction():
    relationship = relationship_var.get()
    demeanor = demeanor_var.get()
    result = get_une_interaction(relationship, demeanor)
    output_text.insert(tk.END, result + "\n\n")
    output_text.see(tk.END)

def btn_manage_lists():
    global manage_data_window_open
    global global_file_path

    if manage_data_window_open is not None:
        manage_data_window_open.focus_set()
        manage_data_window_open.lift()       
        return

    list_manage_window = tk.Toplevel()
    list_manage_window.title("Manage Data")
    list_manage_window.geometry("600x525") 

    manage_data_window_open = list_manage_window
    list_manage_window.bind('<Destroy>', lambda e: on_window_close('manage_data'))

    characters_frame = tk.Frame(list_manage_window)
    threads_frame = tk.Frame(list_manage_window)

    list_manage_window.grid_columnconfigure(0, weight=1)
    list_manage_window.grid_columnconfigure(1, weight=1)
    list_manage_window.grid_rowconfigure(0, weight=1)

    characters_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    threads_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    characters_frame.grid_rowconfigure(1, weight=1)
    characters_frame.grid_columnconfigure(0, weight=1)
    threads_frame.grid_rowconfigure(1, weight=1)
    threads_frame.grid_columnconfigure(0, weight=1)

    entry_character = tk.Entry(characters_frame, width=50)
    entry_character.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
   
    lst_characters = tk.Listbox(characters_frame, selectmode=tk.SINGLE, height=15, width=50)
    lst_characters.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    entry_thread = tk.Entry(threads_frame, width=50)
    entry_thread.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    
    lst_threads = tk.Listbox(threads_frame, selectmode=tk.SINGLE, height=15, width=50)
    lst_threads.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def update_listboxes():
        update_listbox(lst_characters, 'characters')
        update_listbox(lst_threads, 'threads')

    def load_campaign_data():
        global global_file_path
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            loaded_data = load_campaign(file_path)
            if loaded_data:
                global_file_path = file_path  # Update the global file path
                update_listboxes()
                print(f"Campaign loaded successfully from {file_path}")
            else:
                messagebox.showerror("Error", "Failed to load campaign data.")

    def save_campaign_data():
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            success = save_campaign(file_path)
            if success:
                messagebox.showinfo("Success", "Campaign saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save campaign data.")

    load_campaign_button = tk.Button(list_manage_window, text="Load Campaign", command=load_campaign_data)
    load_campaign_button.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

    save_campaign_button = tk.Button(list_manage_window, text="Save Campaign", command=save_campaign_data)
    save_campaign_button.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

    update_listboxes()

    def on_listbox_select(event, entry_widget):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            value = widget.get(index).split('. ', 1)[-1]
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, value)

    lst_characters.bind('<<ListboxSelect>>', lambda event: on_listbox_select(event, entry_character))
    lst_threads.bind('<<ListboxSelect>>', lambda event: on_listbox_select(event, entry_thread))

    tk.Button(characters_frame, text="Add/Update Character", command=lambda: add_update_entry('characters', entry_character, lst_characters)).grid(row=2, column=0, sticky="ew")
    tk.Button(threads_frame, text="Add/Update Thread", command=lambda: add_update_entry('threads', entry_thread, lst_threads)).grid(row=2, column=0, sticky="ew")
    tk.Button(characters_frame, text="Delete Character", command=lambda: delete_entry('characters', lst_characters)).grid(row=3, column=0, sticky="ew")
    tk.Button(threads_frame, text="Delete Thread", command=lambda: delete_entry('threads', lst_threads)).grid(row=3, column=0, sticky="ew")

def add_update_entry(data_type, entry_widget, listbox_widget):
    new_entry = entry_widget.get().strip()
    if not new_entry:
        return

    current_entries = get_general_data(data_type)
    print(f"Current number of {data_type}: {len(current_entries)}")
    print(f"Current entries: {current_entries}")

    success = add_to_general_data(data_type, new_entry)
    
    if success:
        update_listbox(listbox_widget, data_type)
        print(f"Updated data: {data_manager.data}")  # Debug print
        save_current_data()
    else:
        if len(current_entries) >= 25:
            messagebox.showinfo("List Full", "The list can only contain up to 25 entries.")
        elif current_entries.count(new_entry) >= 3:
            messagebox.showinfo("Limit Reached", "Each entry can only appear up to 3 times.")

def delete_entry(data_type, listbox_widget):
    selection_index = listbox_widget.curselection()
    if selection_index:
        selected_text = listbox_widget.get(selection_index).split('. ', 1)[-1]
        remove_from_general_data(data_type, selected_text)
        update_listbox(listbox_widget, data_type)
        save_current_data()

def save_current_data(file_path=None):
    global global_file_path
    if file_path is None:
        file_path = global_file_path
    if file_path:
        success = save_campaign(file_path)
        if success:
            print(f"Campaign saved successfully to {file_path}")
        else:
            print("Failed to save campaign data.")
    else:
        print("No file currently loaded. Unable to save.")

def on_window_close(window_name):
    global manage_data_window_open, roll_fate_window_open, manage_themes_window_open

    if window_name == 'manage_data':
        manage_data_window_open = None
    elif window_name == 'roll_fate':
        roll_fate_window_open = None
    elif window_name == 'manage_themes':
        manage_themes_window_open = None

def btn_manage_themes():
    global manage_themes_window_open
    global themes_listbox

    if manage_themes_window_open is not None:
        manage_themes_window_open.focus_set()
        manage_themes_window_open.lift()
        return

    theme_window = tk.Toplevel()
    theme_window.title("Manage Themes")
    theme_window.resizable(False, False)

    manage_themes_window_open = theme_window
    theme_window.bind('<Destroy>', lambda e: on_window_close('manage_themes'))

    left_frame = tk.Frame(theme_window)
    left_frame.grid(row=0, column=0, padx=5, pady=5)

    middle_frame = tk.Frame(theme_window)
    middle_frame.grid(row=0, column=1, padx=5, pady=5)

    right_frame = tk.Frame(theme_window)
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
        themes_listbox.delete(0, tk.END)
        for i in range(lb_selected_themes.size()):
            themes_listbox.insert(tk.END, lb_selected_themes.get(i))
        theme_window.destroy()

    add_button = tk.Button(middle_frame, text="Add >", command=add_theme)
    add_button.grid(row=0, column=0, pady=5)
    remove_button = tk.Button(middle_frame, text="< Remove", command=remove_theme)
    remove_button.grid(row=1, column=0, pady=5)
    confirm_button = tk.Button(middle_frame, text="Confirm", command=confirm_selection)
    confirm_button.grid(row=2, column=0, pady=5)

    lb_current_themes.bind("<Double-Button-1>", lambda _: add_theme())
    lb_selected_themes.bind("<Double-Button-1>", lambda _: remove_theme())

    for i in range(themes_listbox.size()):
        lb_current_themes.insert(tk.END, themes_listbox.get(i))

def btn_action_oracle():
    oracle_text = generate_action_oracle()
    output_text.insert(tk.END, oracle_text + "\n\n")
    output_text.see(tk.END)

def btn_create_npc():
    npc_description = generate_npc()
    output_text.insert(tk.END, npc_description + "\n\n")
    output_text.see(tk.END)

def btn_choose_character():
    selected_character = select_from_list('characters')
    output_text.insert(tk.END, selected_character + "\n\n")
    output_text.see(tk.END)

def btn_generate_themes():
    themes = [themes_listbox.get(i) for i in range(themes_listbox.size())]
    weights = [40, 30, 20, 8, 2]
    
    theme_results = generate_themes(themes, weights)
    
    for theme_result in theme_results:
        output_text.insert(tk.END, theme_result + "\n\n")
    output_text.see(tk.END)

def btn_choose_thread():
    selected_thread = select_from_list('threads')
    output_text.insert(tk.END, selected_thread + "\n\n")
    output_text.see(tk.END)

def btn_clear_output():
    output_text.delete(1.0, tk.END)

def setup_top_frame(root):
    top_frame = tk.Frame(root, height=125)
    top_frame.grid(row=0, column=0, sticky="nsew")
    top_frame.grid_propagate(False)

    for i in range(4):
        top_frame.columnconfigure(i, weight=1)

    setup_column1(top_frame)
    setup_column2(top_frame)
    setup_column3(top_frame)
    setup_column4(top_frame)

    return top_frame

def setup_bottom_frame(root):
    bottom_frame = tk.Frame(root)
    bottom_frame.grid(row=1, column=0, sticky="nsew")
    bottom_frame.grid_columnconfigure(0, weight=1)
    bottom_frame.grid_rowconfigure(0, weight=1)

    output_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD)
    output_text.pack(fill=tk.BOTH, expand=True)

    return output_text

def setup_column1(parent):
    col_frame = tk.Frame(parent)
    col_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

    tk.Button(col_frame, text="Create NPC", command=btn_create_npc).grid(row=0, column=0, sticky="ew")
    tk.Button(col_frame, text="Roll Interaction", command=btn_roll_interaction).grid(row=1, column=0, sticky="ew")

    relationship_combobox = ttk.Combobox(col_frame, textvariable=relationship_var, state='readonly', values=["loved", "friendly", "peaceful", "neutral", "distrustful", "hostile", "hated"])
    relationship_combobox.grid(row=2, column=0, sticky="ew")
    relationship_combobox.set("neutral")

    demeanor_combobox = ttk.Combobox(col_frame, textvariable=demeanor_var, state='readonly', values=["scheming", "insane", "friendly", "hostile", "inquisitive", "knowing", "mysterious", "prejudiced"])
    demeanor_combobox.grid(row=3, column=0, sticky="ew")
    demeanor_combobox.set("friendly")

def setup_column2(parent):
    col_frame = tk.Frame(parent)
    col_frame.grid(row=0, column=1, sticky="nw", padx=10, pady=10)

    tk.Button(col_frame, text="Manage Data", command=btn_manage_lists).grid(row=0, column=0, sticky="ew")
    tk.Button(col_frame, text="Choose Character", command=btn_choose_character).grid(row=1, column=0, sticky="ew")
    tk.Button(col_frame, text="Choose Thread", command=btn_choose_thread).grid(row=2, column=0, sticky="ew")
    tk.Button(col_frame, text="Roll Fate", command=btn_roll_fate).grid(row=3, column=0, sticky="ew")

def setup_column3(parent):
    global themes_listbox
    col_frame = tk.Frame(parent)
    col_frame.grid(row=0, column=2, sticky="nw", padx=10, pady=10)

    themes_listbox = tk.Listbox(col_frame, height=5)
    themes_listbox.grid(row=0, column=0, sticky="ew")

    for theme in ["action", "mystery", "personal", "social", "tension"]:
        themes_listbox.insert(tk.END, theme)

def setup_column4(parent):
    col_frame = tk.Frame(parent)
    col_frame.grid(row=0, column=3, sticky="nw", padx=10, pady=10)

    tk.Button(col_frame, text="Action Oracle", command=btn_action_oracle).grid(row=0, column=0, sticky="ew")
    tk.Button(col_frame, text="Manage Themes", command=btn_manage_themes).grid(row=1, column=0, sticky="ew")
    tk.Button(col_frame, text="Generate Themes", command=btn_generate_themes).grid(row=2, column=0, sticky="ew")
    tk.Button(col_frame, text="Clear Output", command=btn_clear_output).grid(row=3, column=0, sticky="ew")

# Configure main window layout
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=1)

# Set up frames and widgets
top_frame = setup_top_frame(root)
output_text = setup_bottom_frame(root)

def show_startup_message():
    global global_file_path
    if selected_file_path:
        if data_manager.data.get('characters') or data_manager.data.get('threads'):
            print(f"Data loaded successfully from {selected_file_path}")
            global_file_path = selected_file_path  # Set the global file path
        else:
            print(f"File selected ({selected_file_path}), but no valid data found. Starting with empty lists.")
    else:
        print("No file selected. Starting with empty lists.")

root.after(100, show_startup_message)
root.mainloop()