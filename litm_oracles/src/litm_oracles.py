import tkinter as tk
from tkinter import ttk
import json
import random
from pathlib import Path

# Load Oracle Data
base_dir = Path(__file__).resolve().parent

interpretive_data = {}
conflict_data = {}
revelations_data = {}
challenge_action_data = {}
consequence_data = {}


def load_json_file(filename):
    data_path = base_dir.parent / "data" / filename
    try:
        with data_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Data file not found: {data_path}")
    except json.JSONDecodeError as exc:
        print(f"Data file is malformed JSON: {data_path} ({exc})")
    except OSError as exc:
        print(f"Failed to read data file: {data_path} ({exc})")
    return None


def load_oracle_data():
    global interpretive_data, conflict_data, revelations_data, challenge_action_data, consequence_data

    interpretive_data = load_json_file("interpretive.json") or {}
    conflict_data = load_json_file("conflict.json") or {}
    revelations_data = load_json_file("revelations.json") or {}
    challenge_action_data = load_json_file("challenge_action.json") or {}
    consequence_data = load_json_file("consequence.json") or {}


def create_results_textbox(frame):
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

    return result_textbox


def set_text_content(text_widget, content, use_colored=True):
    text_widget.config(state="normal")
    text_widget.delete("1.0", tk.END)

    if use_colored:
        insert_colored_text(text_widget, content)
    else:
        text_widget.insert(tk.END, content)

    text_widget.config(state="disabled")


def set_text_results(text_widget, results):
    text_widget.config(state="normal")
    text_widget.delete("1.0", tk.END)

    for result in results:
        insert_colored_text(text_widget, result)
        text_widget.insert(tk.END, "\n\n")

    text_widget.config(state="disabled")


def clean_role_name(role_key):
    return role_key.replace("[role]", "").replace("[/role]", "")


def get_role_key_by_name(role_name):
    return next((k for k in challenge_action_data.keys() if clean_role_name(k) == role_name), None)


def get_clean_roles():
    return [clean_role_name(role_key) for role_key in challenge_action_data.keys()]


def get_random_role_key():
    return random.choice(list(challenge_action_data.keys()))


def parse_roll_range(roll_range):
    return map(int, roll_range.split("-"))


def sorted_roll_keys(entries):
    return sorted(entries.keys(), key=lambda key: int(key))


def has_subcategory_roll_tables(role_data):
    return isinstance(role_data, dict) and all(isinstance(v, dict) for v in role_data.values())


def append_role_entries(step5_lines, title, entries):
    step5_lines.append(f"\n{title}")
    for roll_num in sorted_roll_keys(entries):
        step5_lines.append(f"{roll_num}. {entries[roll_num]}")


def render_profile_step5(role_name, role_data):
    step5_lines = [f"Step 5: Threats & Consequences\nRole: {role_name}\n"]

    if has_subcategory_roll_tables(role_data):
        for sub_name, sub_entries in role_data.items():
            append_role_entries(step5_lines, f"{sub_name.capitalize()} — Threats & Consequences", sub_entries)
    else:
        append_role_entries(step5_lines, f"{role_name} — Threats & Consequences", role_data)

    return "\n".join(step5_lines)


def format_consequence_result(roll_d66_value, roll_range, consequence, roll_d6_value, specific):
    return (
        f"Consequence Oracle (Rolled {roll_d66_value} → {roll_range}):\n\n"
        f"{consequence}\n\n"
        f"Specific Consequence (Rolled {roll_d6_value}):\n{specific}"
    )


def find_consequence_result(roll_d66_value, roll_d6_value):
    for roll_range, entry in consequence_data.items():
        low, high = parse_roll_range(roll_range)
        if low <= roll_d66_value <= high:
            consequence = entry["Consequence"]
            specific = entry["Specific"].get(str(roll_d6_value), "(No specific consequence)")
            return format_consequence_result(roll_d66_value, roll_range, consequence, roll_d6_value, specific)

    return f"(No entry found for roll {roll_d66_value})"


def format_revelations_result(roll, roll_range, acts):
    return (
        f"Revelations Oracle (Rolled {roll} → {roll_range}):\n\n"
        f"Act I: {acts['Act I']}\n\n"
        f"Act II: {acts['Act II']}\n\n"
        f"Act III: {acts['Act III']}"
    )


def find_revelation_result(roll):
    for roll_range, acts in revelations_data.items():
        low, high = parse_roll_range(roll_range)
        if low <= roll <= high:
            return format_revelations_result(roll, roll_range, acts)

    return f"(No entry found for roll {roll})"


def get_yesno_outcome(total):
    if total <= 2:
        return "Extreme No"
    if 3 <= total <= 6:
        return "No"
    if 7 <= total <= 9:
        return "Complicated (Yes with caveat or No with complication)"
    if 10 <= total <= 11:
        return "Yes"
    return "Extreme Yes"


def format_yesno_result(total, base_roll, power, result):
    modifier_str = f"+{power}" if power >= 0 else f"{power}"
    return f"You rolled: {total} ({base_roll}{modifier_str}) →  {result}"


def select_profile_role(selected_role):
    if selected_role == "Random":
        role_key = get_random_role_key()
        return role_key, clean_role_name(role_key)

    role_key = get_role_key_by_name(selected_role)
    return role_key, selected_role


def select_challenge_rating(selected_cr):
    if selected_cr == "Random":
        challenge_rating = random.randint(1, 5)
        cr_text = f"Step 2: Challenge Rating (Rolled {challenge_rating}) → {challenge_rating}"
    else:
        challenge_rating = int(selected_cr)
        cr_text = f"Step 2: Challenge Rating → {challenge_rating}"

    return challenge_rating, cr_text


def build_limits_text(challenge_rating):
    hard = challenge_rating + 1
    medium = challenge_rating
    easy = challenge_rating - 1 if challenge_rating - 1 > 0 else None

    limits = [f"Hard: {hard}", f"Medium: {medium}"]
    if easy:
        limits.append(f"Easy: {easy}")

    return "Step 3: Limits\n" + "\n".join(limits)


def build_tags_statuses_text(challenge_rating):
    return f"Step 4: Tags & Statuses\nTags: {challenge_rating}\nStatuses: {challenge_rating}"


def build_oracle_category_results(data):
    return [roll_category(data, category) for category in data.keys()]

# --- Utility Functions ---
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def display_missing_data(text_widget, dataset_name):
    set_text_content(text_widget, f"{dataset_name} data is unavailable.", use_colored=False)


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
        results = build_oracle_category_results(interpretive_data)
        set_text_results(result_textbox, results)

    ttk.Label(frame, text="Interpretive Oracle", font=("Arial", 14)).pack(pady=10)

    roll_button = ttk.Button(frame, text="Roll Interpretive Oracle", command=roll_and_display)
    roll_button.pack(pady=10)

    result_textbox = create_results_textbox(frame)

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

        result_text = find_consequence_result(roll_d66_value, roll_d6_value)
        set_text_content(result_textbox, result_text)

    ttk.Label(frame, text="Consequence Oracle", font=("Arial", 14)).pack(pady=10)

    roll_button = ttk.Button(frame, text="Roll Consequence Oracle", command=roll_and_display)
    roll_button.pack(pady=10)

    result_textbox = create_results_textbox(frame)

def show_conflict(frame):
    clear_frame(frame)

    def roll_and_display():
        if not conflict_data:
            display_missing_data(result_textbox, "Conflict oracle")
            return
        results = build_oracle_category_results(conflict_data)
        set_text_results(result_textbox, results)

    ttk.Label(frame, text="Conflict Oracle", font=("Arial", 14)).pack(pady=10)

    roll_button = ttk.Button(frame, text="Roll Conflict Oracle", command=roll_and_display)
    roll_button.pack(pady=10)

    result_textbox = create_results_textbox(frame)

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
        role_lookup = get_role_key_by_name(role_override)
        if role_lookup is None:
            return (role_override, None, "?", f"(Role '{role_override}' not found in challenge_action.json)")
    else:
        # Randomly pick JSON key directly
        role_lookup = get_random_role_key()

    # Clean name for display
    display_role = clean_role_name(role_lookup)

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
        role_key, role_name = select_profile_role(selected_role)

        # STEP 2: Challenge Rating (either dropdown or random)
        selected_cr = cr_var.get()
        challenge_rating, cr_text = select_challenge_rating(selected_cr)
        results = [cr_text]

        # STEP 3: Limits
        results.append(build_limits_text(challenge_rating))

        # STEP 4: Tags & Statuses
        results.append(build_tags_statuses_text(challenge_rating))

        # STEP 5: Threats & Consequences — show ALL powers, not one roll
        role_data = challenge_action_data[role_key]
        results.append(render_profile_step5(role_name, role_data))

        set_text_results(result_textbox, results)

    # --- UI ELEMENTS ---
    ttk.Label(frame, text="Profile Builder", font=("Arial", 14)).pack(pady=10)

    # Role dropdown
    ttk.Label(frame, text="Select Role (or leave Random):").pack(pady=5)
    role_var = tk.StringVar()
    role_dropdown = ttk.Combobox(frame, textvariable=role_var, state="readonly")
    clean_roles = get_clean_roles()
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

    result_textbox = create_results_textbox(frame)

def show_revelations(frame):
    clear_frame(frame)

    def roll_and_display():
        if not revelations_data:
            display_missing_data(result_textbox, "Revelations oracle")
            return
        roll = roll_d66()
        result_text = find_revelation_result(roll)
        set_text_content(result_textbox, result_text)

    ttk.Label(frame, text="Revelations Oracle", font=("Arial", 14)).pack(pady=10)

    roll_button = ttk.Button(frame, text="Roll Revelations Oracle", command=roll_and_display)
    roll_button.pack(pady=10)

    result_textbox = create_results_textbox(frame)

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
        result = get_yesno_outcome(total)
        result_var.set(format_yesno_result(total, base_roll, power, result))

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
