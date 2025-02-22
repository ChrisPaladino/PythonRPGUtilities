import tkinter as tk
from tkinter import ttk
import random
import time

def determine_result(remaining_action_dice):
    if not remaining_action_dice:
        return "BOTCH"
    highest = max(remaining_action_dice)
    if highest == 6:
        boons = remaining_action_dice.count(6) - 1
        return f"Success with {boons} BOON(s)" if boons > 0 else "Success"
    if highest in (4, 5):
        return "Partial Success"
    return "BOTCH" if highest == 1 else "Failure"

def adjust_dice(entry, delta):
    try:
        current_value = int(entry.get())
    except ValueError:
        current_value = 0
    new_value = max(0, min(10, current_value + delta))
    entry.delete(0, tk.END)
    entry.insert(0, str(new_value))

def clear_dice():
    action_dice_entry.delete(0, tk.END)
    action_dice_entry.insert(0, "1")
    danger_dice_entry.delete(0, tk.END)
    danger_dice_entry.insert(0, "0")
    result_label.config(text="")
    canvas.delete("all")

def draw_dice(canvas, dice, x, y, dice_size, label, cancelled_dice, remaining_dice, is_action):
    canvas.create_text(x, y, text=label, anchor="nw", font=('Helvetica', 14, 'bold'), fill="#E0E0E0")
    y += 35
    highest_remaining_die = max(remaining_dice, default=0)
    cancelled_count = {die: cancelled_dice.count(die) for die in set(cancelled_dice)}

    for i, die in enumerate(dice):
        rect_color = "#404040"  # Dark gray default
        text_color = "#E0E0E0"  # Light gray text
        if die in cancelled_count and cancelled_count[die] > 0:
            rect_color = "#D32F2F"  # Muted red for cancelled
            text_color = "white"
            cancelled_count[die] -= 1
        elif is_action and die == highest_remaining_die and die in remaining_dice:
            rect_color = "#388E3C"  # Muted green for highest
            text_color = "white"

        rect = canvas.create_rectangle(x, y, x + dice_size, y + dice_size, fill=rect_color, outline="#606060")
        text = canvas.create_text(x + dice_size // 2, y + dice_size // 2, text=str(die), fill=text_color, font=('Helvetica', dice_size // 3, 'bold'))
        x += dice_size + 5
    
    # Subtle fade-in
    for alpha in range(0, 6):  # Reduced steps for faster effect
        canvas.update()
        time.sleep(0.02)
    
    return y + dice_size + 20

def process_results(action_dice, danger_dice):
    cancelled_dice = []
    action_dice.sort(reverse=True)
    danger_dice.sort(reverse=True)
    remaining_action_dice = action_dice.copy()
    for danger_die in danger_dice:
        if danger_die in remaining_action_dice:
            remaining_action_dice.remove(danger_die)
            cancelled_dice.append(danger_die)
    return action_dice, danger_dice, cancelled_dice, remaining_action_dice

def roll_and_process():
    canvas.delete("all")
    try:
        num_action_dice = int(action_dice_entry.get())
        if not (0 <= num_action_dice <= 10):
            raise ValueError("Action Dice must be between 0 and 10.")
        num_danger_dice = int(danger_dice_entry.get())
        if not (0 <= num_danger_dice <= 10):
            raise ValueError("Danger Dice must be between 0 and 10.")
    except ValueError as e:
        error_msg = str(e) if str(e).startswith(("Action", "Danger")) else "Invalid input: Use numbers 0-10."
        result_label.config(text=error_msg, foreground="#D32F2F")
        return

    if num_action_dice == 0 and num_danger_dice == 0:
        result_label.config(text="No dice to roll!", foreground="#D32F2F")
        return

    action_dice = roll_dice(num_action_dice)
    danger_dice = roll_dice(num_danger_dice)
    action_dice_sorted, danger_dice_sorted, cancelled_dice, remaining_action_dice = process_results(action_dice.copy(), danger_dice.copy())
    result = determine_result(remaining_action_dice)

    result_label.config(text=result, foreground="#E0E0E0")
    x, y = 10, 10
    y = draw_dice(canvas, action_dice_sorted, x, y, 30, "Action Dice", cancelled_dice, remaining_action_dice, True)
    y = draw_dice(canvas, danger_dice_sorted, x, y, 30, "Danger Dice", cancelled_dice, [], False)
    canvas.config(scrollregion=(0, 0, canvas.winfo_width(), y))

def roll_dice(n):
    return [random.randint(1, 6) for _ in range(n)]

# Main application setup
root = tk.Tk()
root.title("Cityscape Dice Roller")
root.geometry("400x500")
root.configure(bg="#212121")  # Dark gray background

# Style Configuration
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Helvetica", 12), background="#212121", foreground="#E0E0E0")
style.configure("TButton", font=("Helvetica", 12), background="#424242", foreground="#E0E0E0")  # Static background, no hover or active states
style.map("TButton", background=[], foreground=[])  # Explicitly clear any mapped states
style.configure("TFrame", background="#424242")  # Darken input frame
style.configure("TEntry", fieldbackground="#424242", background="#424242", foreground="#E0E0E0")  # Darken entry fields
style.configure("TLabelframe", background="#212121", foreground="#E0E0E0")  # Darken label frame
style.configure("TLabelframe.Label", background="#212121", foreground="#E0E0E0")

# Input and Controls Frame
input_frame = ttk.Frame(root)
input_frame.grid(row=0, column=0, columnspan=2, pady=15, padx=10, sticky="ew")

action_dice_label = ttk.Label(input_frame, text="Action Dice:")
action_dice_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

action_dice_entry = ttk.Entry(input_frame, width=4)
action_dice_entry.insert(0, "1")
action_dice_entry.grid(row=0, column=1, padx=5, pady=5)

action_dice_plus = ttk.Button(input_frame, text="+", width=2, command=lambda: adjust_dice(action_dice_entry, 1))
action_dice_plus.grid(row=0, column=2, padx=2)
action_dice_minus = ttk.Button(input_frame, text="-", width=2, command=lambda: adjust_dice(action_dice_entry, -1))
action_dice_minus.grid(row=0, column=3, padx=2)

danger_dice_label = ttk.Label(input_frame, text="Danger Dice:")
danger_dice_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

danger_dice_entry = ttk.Entry(input_frame, width=4)
danger_dice_entry.insert(0, "0")
danger_dice_entry.grid(row=1, column=1, padx=5, pady=5)

danger_dice_plus = ttk.Button(input_frame, text="+", width=2, command=lambda: adjust_dice(danger_dice_entry, 1))
danger_dice_plus.grid(row=1, column=2, padx=2)
danger_dice_minus = ttk.Button(input_frame, text="-", width=2, command=lambda: adjust_dice(danger_dice_entry, -1))
danger_dice_minus.grid(row=1, column=3, padx=2)

roll_button = ttk.Button(input_frame, text="Roll Dice", command=roll_and_process)
roll_button.grid(row=0, column=4, padx=10, pady=5)

clear_button = ttk.Button(input_frame, text="Clear", command=clear_dice)
clear_button.grid(row=1, column=4, padx=10, pady=5)

result_label = ttk.Label(root, text="", font=("Helvetica", 16, "bold"), background="#212121", foreground="#E0E0E0")
result_label.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="w")

# Canvas with Scrollbar
canvas_frame = ttk.LabelFrame(root, text="Dice Results", labelanchor="n")
canvas_frame.grid(row=2, column=0, columnspan=2, pady=5, padx=10, sticky="nsew")

scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

canvas = tk.Canvas(canvas_frame, bg="#2D2D2D", yscrollcommand=scrollbar.set)
canvas.pack(fill="both", expand=True, padx=5, pady=5)
scrollbar.config(command=canvas.yview)

# Make layout responsive
root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=1)
canvas_frame.columnconfigure(0, weight=1)
canvas_frame.rowconfigure(0, weight=1)

root.mainloop()