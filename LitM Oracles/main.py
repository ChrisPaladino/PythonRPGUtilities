import tkinter as tk
from tkinter import ttk
import json
import os

from utils.dice import roll_d66, roll_2d6

# Load Oracle Data
base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, "data", "interpretive.json"), "r") as f:
    interpretive_data = json.load(f)

with open(os.path.join(base_dir, "data", "conflict.json"), "r") as f:
    conflict_data = json.load(f)


# --- Utility Functions ---
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


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
        results = []
        for category in interpretive_data.keys():
            result_text = roll_category(interpretive_data, category)
            results.append(result_text)

        # Display results
        result_textbox.config(state="normal")
        result_textbox.delete("1.0", tk.END)
        result_textbox.insert(tk.END, "\n\n".join(results))
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
        font=("Courier", 10),
        yscrollcommand=scrollbar.set,
        state="disabled"
    )
    result_textbox.pack(fill="both", expand=True)
    scrollbar.config(command=result_textbox.yview)


def show_conflict(frame):
    clear_frame(frame)

    def roll_and_display():
        results = []
        for category in conflict_data.keys():
            result_text = roll_category(conflict_data, category)
            results.append(result_text)

        # Display results
        result_textbox.config(state="normal")
        result_textbox.delete("1.0", tk.END)
        result_textbox.insert(tk.END, "\n\n".join(results))
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
        font=("Courier", 10),
        yscrollcommand=scrollbar.set,
        state="disabled"
    )
    result_textbox.pack(fill="both", expand=True)
    scrollbar.config(command=result_textbox.yview)


def show_yesno(frame):
    clear_frame(frame)

    def roll_and_display():
        try:
            power = int(power_entry.get())
        except ValueError:
            result_var.set("Enter a valid integer for Power.")
            return

        roll = roll_2d6() + power
        if roll <= 2:
            result = "Extreme No"
        elif 3 <= roll <= 6:
            result = "No"
        elif 7 <= roll <= 9:
            result = "Complicated (Yes with caveat or No with complication)"
        elif 10 <= roll <= 11:
            result = "Yes"
        else:
            result = "Extreme Yes"

        result_var.set(f"You rolled: {roll} → {result}")

    ttk.Label(frame, text="Yes/No Oracle", font=("Arial", 14)).pack(pady=10)

    ttk.Label(frame, text="Power Modifier:").pack(pady=5)
    power_entry = ttk.Entry(frame)
    power_entry.insert(0, "0")  # Default to 0
    power_entry.pack(pady=5)

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
root = tk.Tk()
root.title("Legends in the Mist: Oracles")
root.geometry("900x600")

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
    ("Profile Builder", lambda f: show_placeholder(f, "Profile Builder")),
    ("Challenge Action", lambda f: show_placeholder(f, "Challenge Action")),
    ("Consequence", lambda f: show_placeholder(f, "Consequence")),
    ("Revelations", lambda f: show_placeholder(f, "Revelations")),
]

for name, command in oracle_buttons:
    btn = ttk.Button(menu_frame, text=name, command=lambda c=command: c(content_frame))
    btn.pack(fill="x", pady=5)

# Start with Interpretive Oracle by default
show_interpretive(content_frame)

root.mainloop()
