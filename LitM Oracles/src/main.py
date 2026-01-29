import tkinter as tk
from tkinter import ttk
import json
import os
import random

# Load Oracle Data
base_dir = os.path.dirname(os.path.abspath(__file__))

interpretive_data = {}
conflict_data = {}
revelations_data = {}
challenge_action_data = {}
consequence_data = {}


def load_json_file(filename):
    data_path = os.path.join(base_dir, "data", filename)
    try:
        with open(data_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Data file not found: {data_path}")
    except json.JSONDecodeError:
        print(f"Data file is malformed JSON: {data_path}")
    return None


def load_oracle_data():
    global interpretive_data, conflict_data, revelations_data, challenge_action_data, consequence_data

    interpretive_data = load_json_file("interpretive.json") or {}
    conflict_data = load_json_file("conflict.json") or {}
    revelations_data = load_json_file("revelations.json") or {}
    challenge_action_data = load_json_file("challenge_action.json") or {}
    consequence_data = load_json_file("consequence.json") or {}

# --- Utility Functions ---
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def display_missing_data(text_widget, dataset_name):
    text_widget.config(state="normal")
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, f"{dataset_name} data is unavailable.")
    text_widget.config(state="disabled")


def roll_category(data, category_name, depth=0):
    """Rolls a d66 for a given category and fully resolves 'Roll Again Twice' entries recursively."""
    if depth > 10:  # prevent infinite recursion
        return f"{category_name}: (Too many rerolls, check data)"

    roll = roll_d66()
    key = f"{roll:02d}"
    result = data[category_name].get(key, "(No entry)")

    if "Roll again twice" in result:
        # Roll twice recursively and combine results
        result1 = roll_category(data, category_name, depth + 1)
        result2 = roll_category(data, category_name, depth + 1)
        return f"{category_name} (Rolled {key}, Rerolled):\n{result1}\n{result2}"
    else:
        return f"{category_name} (Rolled {key}):\n{result}"


# --- Oracle Panels ---
def show_interpretive(frame):
    clear_frame(frame)

    def roll_and_display():
        if not interpretive_data:
            display_missing_data(result_textbox, "Interpretive oracle")
            return
        results = []
        for category in interpretive_data.keys():
            result_text = roll_category(interpretive_data, category)
            results.append(result_text)

        # Display results
        result_textbox.config(state="normal")
        result_textbox.delete("1.0", tk.END)
        for result in results:
            insert_colored_text(result_textbox, result)
            result_textbox.insert(tk.END, "\n\n")

        result_textbox.config(state="disabled")

    ttk.Label(frame, text="Interpretive Oracle", font=("Arial", 14)).pack(pady=10)

    roll_button = ttk.Button(frame, text="Roll Interpretive Oracle", command=roll_and_display)
    roll_button.pack(pady=10)

    # Scrollable text box
    result_frame = ttk.Frame(frame)
    result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(result_frame)
    scrollbar.pack(side="right", fill="y")

    result_textbox = tk.Text(
        result_frame,
        wrap="word",
        font=("Arial", 10),
        yscrollcommand=scrollbar.set,
        state="disabled"
    )
    result_textbox.pack(fill="both", expand=True)
    scrollbar.config(command=result_textbox.yview)

def insert_colored_text(text_widget, content):
    """Inserts text into a Tkinter Text widget with background colors for tag/status/limit and bold for role."""
    # Define tags and their styles
    text_widget.tag_configure("status", background="#90EE90", foreground="black")  # light green bg
    text_widget.tag_configure("tag", background="yellow", foreground="black")
    text_widget.tag_configure("limit", background="#FFB6B6", foreground="black")  # light red bg
    text_widget.tag_configure("role", font=("Arial", 10, "bold"))

    idx = 0
    while idx < len(content):
        if content.startswith("[status]", idx):
            end = content.find("[/status]", idx)
            if end != -1:
                status_text = content[idx+8:end]
                text_widget.insert(tk.END, status_text, "status")
                idx = end + 9
                continue
        elif content.startswith("[tag]", idx):
            end = content.find("[/tag]", idx)
            if end != -1:
                tag_text = content[idx+5:end]
                text_widget.insert(tk.END, tag_text, "tag")
                idx = end + 6
                continue
        elif content.startswith("[limit]", idx):
            end = content.find("[/limit]", idx)
            if end != -1:
                limit_text = content[idx+7:end]
                text_widget.insert(tk.END, limit_text, "limit")
                idx = end + 8
                continue
        elif content.startswith("[role]", idx):
            end = content.find("[/role]", idx)
            if end != -1:
                role_text = content[idx+6:end]
                text_widget.insert(tk.END, role_text, "role")
                idx = end + 7
                continue
        else:
            text_widget.insert(tk.END, content[idx])
            idx += 1

def show_consequence(frame):
    clear_frame(frame)

    def roll_and_display():
        if not consequence_data:
            display_missing_data(result_textbox, "Consequence oracle")
            return
        roll_d66_value = roll_d66()
        roll_d6_value = roll_d6()

        # Find which range the d66 roll falls into
        result_text = None
        for roll_range, entry in consequence_data.items():
            low, high = map(int, roll_range.split("-"))
            if low <= roll_d66_value <= high:
                consequence = entry["Consequence"]
                specific = entry["Specific"].get(str(roll_d6_value), "(No specific consequence)")
                result_text = (
                    f"Consequence Oracle (Rolled {roll_d66_value} → {roll_range}):\n\n"
                    f"{consequence}\n\n"
                    f"Specific Consequence (Rolled {roll_d6_value}):\n{specific}"
                )
                break
        if not result_text:
            result_text = f"(No entry found for roll {roll_d66_value})"

        # Display results
        result_textbox.config(state="normal")
        result_textbox.delete("1.0", tk.END)
        insert_colored_text(result_textbox, result_text)  # Use our color/bold tagging
        result_textbox.config(state="disabled")

    ttk.Label(frame, text="Consequence Oracle", font=("Arial", 14)).pack(pady=10)

    roll_button = ttk.Button(frame, text="Roll Consequence Oracle", command=roll_and_display)
    roll_button.pack(pady=10)

    # Scrollable text box
    result_frame = ttk.Frame(frame)
    result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(result_frame)
    scrollbar.pack(side="right", fill="y")

    result_textbox = tk.Text(
        result_frame,
        wrap="word",
        font=("Arial", 10),
        yscrollcommand=scrollbar.set,
        state="disabled"
    )
    result_textbox.pack(fill="both", expand=True)
    scrollbar.config(command=result_textbox.yview)

def show_conflict(frame):
    clear_frame(frame)

    def roll_and_display():
        if not conflict_data:
            display_missing_data(result_textbox, "Conflict oracle")
            return
        results = []
        for category in conflict_data.keys():
            result_text = roll_category(conflict_data, category)
            results.append(result_text)

        # Display results
        result_textbox.config(state="normal")
        result_textbox.delete("1.0", tk.END)
        for result in results:
            insert_colored_text(result_textbox, result)
            result_textbox.insert(tk.END, "\n\n")

        result_textbox.config(state="disabled")

    ttk.Label(frame, text="Conflict Oracle", font=("Arial", 14)).pack(pady=10)

    roll_button = ttk.Button(frame, text="Roll Conflict Oracle", command=roll_and_display)
    roll_button.pack(pady=10)

    # Scrollable text box
    result_frame = ttk.Frame(frame)
    result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(result_frame)
    scrollbar.pack(side="right", fill="y")

    result_textbox = tk.Text(
        result_frame,
        wrap="word",
        font=("Arial", 10),
        yscrollcommand=scrollbar.set,
        state="disabled"
    )
    result_textbox.pack(fill="both", expand=True)
    scrollbar.config(command=result_textbox.yview)

def roll_d6():
    return random.randint(1, 6)

def roll_d66():
    tens = random.randint(1, 6) * 10
    ones = random.randint(1, 6)
    return tens + ones

def roll_2d6():
    return random.randint(1, 6) + random.randint(1, 6)

def roll_challenge_action(role_override=None):
    """Rolls a challenge action. Randomly picks a role unless overridden."""
    if not challenge_action_data:
        return (role_override or "Unknown", None, "?", "Challenge action data is unavailable.")
    if role_override:
        # User picked a role, find matching JSON key
        json_keys = challenge_action_data.keys()
        role_lookup = next((k for k in json_keys if k.replace("[role]", "").replace("[/role]", "") == role_override), None)
        if role_lookup is None:
            return (role_override, None, "?", f"(Role '{role_override}' not found in challenge_action.json)")
    else:
        # Randomly pick JSON key directly
        role_lookup = random.choice(list(challenge_action_data.keys()))

    # Clean name for display
    display_role = role_lookup.replace("[role]", "").replace("[/role]", "")

    role_data = challenge_action_data[role_lookup]
    roll = str(roll_d6())

    if isinstance(role_data, dict):
        for sub_category, outcomes in role_data.items():
            if isinstance(outcomes, dict) and roll in outcomes:
                return (display_role, sub_category, roll, outcomes[roll])
        if roll in role_data:
            return (display_role, None, roll, role_data[roll])
    else:
        if roll in role_data:
            return (display_role, None, roll, role_data[roll])

    return (display_role, None, roll, "(No entry for this roll)")

def show_profile_builder(frame):
    clear_frame(frame)

    def build_profile():
        if not challenge_action_data:
            display_missing_data(result_textbox, "Profile builder")
            return
        # STEP 1: Role selection
        selected_role = role_var.get()
        role_override = None if selected_role == "Random" else selected_role

        # STEP 2: Challenge Rating (either dropdown or random)
        selected_cr = cr_var.get()
        if selected_cr == "Random":
            challenge_rating = random.randint(1, 5)
            cr_text = f"Step 2: Challenge Rating (Rolled {challenge_rating}) → {challenge_rating}"
        else:
            challenge_rating = int(selected_cr)
            cr_text = f"Step 2: Challenge Rating → {challenge_rating}"
        results = [cr_text]

        # STEP 3: Limits
        hard = challenge_rating + 1
        medium = challenge_rating
        easy = challenge_rating - 1 if challenge_rating - 1 > 0 else None
        limits = [f"Hard: {hard}", f"Medium: {medium}"]
        if easy:
            limits.append(f"Easy: {easy}")
        results.append("Step 3: Limits\n" + "\n".join(limits))

        # STEP 4: Tags & Statuses
        results.append(f"Step 4: Tags & Statuses\nTags: {challenge_rating}\nStatuses: {challenge_rating}")

        # STEP 5: Threats & Consequences — show ALL powers, not one roll
        if role_override:
            role_key = next(
                (k for k in challenge_action_data.keys()
                 if k.replace("[role]", "").replace("[/role]", "") == role_override),
                None
            )
        else:
            role_key = random.choice(list(challenge_action_data.keys()))
            role_override = role_key.replace("[role]", "").replace("[/role]", "")

        role_data = challenge_action_data[role_key]
        step5_lines = [f"Step 5: Threats & Consequences\nRole: {role_override}\n"]

        # if dict has subcategories (like Charge), group them
        if isinstance(role_data, dict) and all(isinstance(v, dict) for v in role_data.values()):
            for sub_name, sub_entries in role_data.items():
                step5_lines.append(f"\n{sub_name.capitalize()} — Threats & Consequences")
                for roll_num in sorted(sub_entries.keys(), key=lambda x: int(x)):
                    step5_lines.append(f"{roll_num}. {sub_entries[roll_num]}")
        else:
            # flat list of 1–6
            step5_lines.append(f"\n{role_override} — Threats & Consequences")
            for roll_num in sorted(role_data.keys(), key=lambda x: int(x)):
                step5_lines.append(f"{roll_num}. {role_data[roll_num]}")

        results.append("\n".join(step5_lines))

        # Display results
        result_textbox.config(state="normal")
        result_textbox.delete("1.0", tk.END)
        for result in results:
            insert_colored_text(result_textbox, result)
            result_textbox.insert(tk.END, "\n\n")
        result_textbox.config(state="disabled")

    # --- UI ELEMENTS ---
    ttk.Label(frame, text="Profile Builder", font=("Arial", 14)).pack(pady=10)

    # Role dropdown
    ttk.Label(frame, text="Select Role (or leave Random):").pack(pady=5)
    role_var = tk.StringVar()
    role_dropdown = ttk.Combobox(frame, textvariable=role_var, state="readonly")
    clean_roles = [r.replace("[role]", "").replace("[/role]", "") for r in challenge_action_data.keys()]
    role_dropdown["values"] = ["Random"] + clean_roles
    role_dropdown.current(0)
    role_dropdown.pack(pady=5)

    # Challenge Rating dropdown
    ttk.Label(frame, text="Select Challenge Rating (or Random):").pack(pady=5)
    cr_var = tk.StringVar()
    cr_dropdown = ttk.Combobox(frame, textvariable=cr_var, state="readonly")
    cr_dropdown["values"] = ["Random", "1", "2", "3", "4", "5"]
    cr_dropdown.current(0)
    cr_dropdown.pack(pady=5)

    # Build button
    ttk.Button(frame, text="Build Profile", command=build_profile).pack(pady=10)

    # Scrollable output area
    result_frame = ttk.Frame(frame)
    result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(result_frame)
    scrollbar.pack(side="right", fill="y")

    result_textbox = tk.Text(
        result_frame,
        wrap="word",
        font=("Arial", 10),
        yscrollcommand=scrollbar.set,
        state="disabled"
    )
    result_textbox.pack(fill="both", expand=True)
    scrollbar.config(command=result_textbox.yview)

def show_revelations(frame):
    clear_frame(frame)

    def roll_and_display():
        if not revelations_data:
            display_missing_data(result_textbox, "Revelations oracle")
            return
        roll = roll_d66()
        # Find which range the roll falls into
        result_text = None
        for roll_range, acts in revelations_data.items():
            low, high = map(int, roll_range.split("-"))
            if low <= roll <= high:
                result_text = (
                    f"Revelations Oracle (Rolled {roll} → {roll_range}):\n\n"
                    f"Act I: {acts['Act I']}\n\n"
                    f"Act II: {acts['Act II']}\n\n"
                    f"Act III: {acts['Act III']}"
                )
                break
        if not result_text:
            result_text = f"(No entry found for roll {roll})"

        # Display results
        result_textbox.config(state="normal")
        result_textbox.delete("1.0", tk.END)
        insert_colored_text(result_textbox, result_text)  # supports color/bold tags
        result_textbox.config(state="disabled")

    ttk.Label(frame, text="Revelations Oracle", font=("Arial", 14)).pack(pady=10)

    roll_button = ttk.Button(frame, text="Roll Revelations Oracle", command=roll_and_display)
    roll_button.pack(pady=10)

    # Scrollable text box
    result_frame = ttk.Frame(frame)
    result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(result_frame)
    scrollbar.pack(side="right", fill="y")

    result_textbox = tk.Text(
        result_frame,
        wrap="word",
        font=("Arial", 10),
        yscrollcommand=scrollbar.set,
        state="disabled"
    )
    result_textbox.pack(fill="both", expand=True)
    scrollbar.config(command=result_textbox.yview)

def show_yesno(frame):
    clear_frame(frame)

    def roll_and_display():
        try:
            power = int(power_var.get())
        except ValueError:
            result_var.set("Select a valid Power Modifier.")
            return

        base_roll = roll_2d6()
        total = base_roll + power
        modifier_str = f"+{power}" if power >= 0 else f"{power}"  # format +2 or -3

        if total <= 2:
            result = "Extreme No"
        elif 3 <= total <= 6:
            result = "No"
        elif 7 <= total <= 9:
            result = "Complicated (Yes with caveat or No with complication)"
        elif 10 <= total <= 11:
            result = "Yes"
        else:
            result = "Extreme Yes"

        result_var.set(f"You rolled: {total} ({base_roll}{modifier_str}) →  {result}")

    ttk.Label(frame, text="Yes/No Oracle", font=("Arial", 14)).pack(pady=10)

    ttk.Label(frame, text="Power Modifier:").pack(pady=5)
    power_var = tk.StringVar(value="0")
    power_dropdown = ttk.Combobox(
        frame,
        textvariable=power_var,
        values=[str(i) for i in range(-4, 5)],  # -4 to +4
        state="readonly"
    )
    power_dropdown.pack(pady=5)

    roll_button = ttk.Button(frame, text="Roll 2d6 + Power", command=roll_and_display)
    roll_button.pack(pady=10)

    result_var = tk.StringVar()
    result_label = ttk.Label(frame, textvariable=result_var, wraplength=600)
    result_label.pack(pady=10)

def show_placeholder(frame, name):
    clear_frame(frame)
    ttk.Label(frame, text=f"{name} Oracle", font=("Arial", 14)).pack(pady=10)
    ttk.Label(frame, text="(Placeholder for future implementation)").pack(pady=5)


# --- Main App Window ---
if __name__ == "__main__":
    load_oracle_data()

    root = tk.Tk()
    root.title("Legends in the Mist: Oracles")
    root.geometry("900x600")
    root.minsize(800, 500)

    # Layout: menu left, content right
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    menu_frame = ttk.Frame(root, padding=10)
    menu_frame.grid(row=0, column=0, sticky="ns")

    content_frame = ttk.Frame(root, padding=10, relief="sunken")
    content_frame.grid(row=0, column=1, sticky="nsew")

    # Oracle buttons
    oracle_buttons = [
        ("Interpretive", show_interpretive),
        ("Yes/No", show_yesno),
        ("Conflict", show_conflict),
        ("Profile Builder", show_profile_builder),
        ("Consequence", show_consequence),
        ("Revelations", show_revelations),
    ]

    for name, command in oracle_buttons:
        btn = ttk.Button(menu_frame, text=name, command=lambda c=command: c(content_frame))
        btn.pack(fill="x", pady=5)

    # Start with Interpretive Oracle by default
    show_interpretive(content_frame)

    root.mainloop()
