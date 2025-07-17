import tkinter as tk
from tkinter import ttk
from oracles import yesno

# Stub functions for each oracle
def interpretive_oracle():
    open_oracle_window("Interpretive Oracle (d66)", "Roll d66 and interpret.")

def yes_no_oracle():
    def run_yes_no():
        try:
            power = int(power_entry.get())
        except ValueError:
            result_var.set("Enter a valid number for Power.")
            return
        result = yesno.yes_no_oracle(power)
        result_var.set(f"Result: {result}")

    oracle_win = tk.Toplevel(root)
    oracle_win.title("Yes/No Oracle")

    ttk.Label(oracle_win, text="Power Modifier:").grid(column=0, row=0, padx=10, pady=10)
    power_entry = ttk.Entry(oracle_win)
    power_entry.grid(column=1, row=0, padx=10, pady=10)

    roll_button = ttk.Button(oracle_win, text="Roll", command=run_yes_no)
    roll_button.grid(column=0, row=1, columnspan=2, padx=10, pady=10)

    result_var = tk.StringVar()
    result_label = ttk.Label(oracle_win, textvariable=result_var, font=("Arial", 14))
    result_label.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

def conflict_oracle():
    open_oracle_window("Conflict Oracle", "Roll d66 between 1 and 7 times.")

def profile_builder_oracle():
    open_oracle_window("Profile Builder Oracle", "Build a 5-step profile.")

def challenge_action_oracle():
    open_oracle_window("Challenge Action Oracle", "Select a Role and roll.")

def consequence_oracle():
    open_oracle_window("Consequence Oracle", "Roll d66 + d6 for consequences.")

def revelations_oracle():
    open_oracle_window("Revelations Oracle", "Roll d66 for revelation.")

def open_oracle_window(title, message):
    oracle_win = tk.Toplevel(root)
    oracle_win.title(title)
    ttk.Label(oracle_win, text=message, font=("Arial", 12)).pack(padx=20, pady=20)

# Main application window
root = tk.Tk()
root.title("Legends in the Mist: Oracles")

# Create grid of oracle buttons
oracle_names = [
    ("Interpretive", interpretive_oracle),
    ("Yes/No", yes_no_oracle),
    ("Conflict", conflict_oracle),
    ("Profile Builder", profile_builder_oracle),
    ("Challenge Action", challenge_action_oracle),
    ("Consequence", consequence_oracle),
    ("Revelations", revelations_oracle),
]

# Style
style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=10)

# Place buttons in grid
for idx, (name, command) in enumerate(oracle_names):
    row = idx // 2
    col = idx % 2
    btn = ttk.Button(root, text=name, command=command)
    btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

# Make the grid responsive
for i in range(4):  # up to 4 rows
    root.grid_rowconfigure(i, weight=1)
for j in range(2):  # 2 columns
    root.grid_columnconfigure(j, weight=1)

root.mainloop()
