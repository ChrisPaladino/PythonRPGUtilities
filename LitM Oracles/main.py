import tkinter as tk
from tkinter import ttk
from oracles import yesno

def run_yes_no():
    try:
        power = int(power_entry.get())
    except ValueError:
        result_var.set("Enter a valid number for Power.")
        return

    result = yesno.yes_no_oracle(power)
    result_var.set(f"Result: {result}")

# Create the main window
root = tk.Tk()
root.title("Legends in the Mist Oracles")

# Grid Layout
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Power Input
ttk.Label(root, text="Power Modifier:").grid(column=0, row=0, padx=10, pady=10)
power_entry = ttk.Entry(root)
power_entry.grid(column=1, row=0, padx=10, pady=10)

# Button
roll_button = ttk.Button(root, text="Roll Yes/No Oracle", command=run_yes_no)
roll_button.grid(column=0, row=1, columnspan=2, padx=10, pady=10)

# Result Label
result_var = tk.StringVar()
result_label = ttk.Label(root, textvariable=result_var, font=("Arial", 14))
result_label.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

root.mainloop()
