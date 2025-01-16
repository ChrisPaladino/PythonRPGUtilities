import tkinter as tk
from tkinter import ttk
import random

def determine_result(remaining_action_dice):
    if not remaining_action_dice:
        return "BOTCH"
    else:
        highest_action_die = max(remaining_action_dice)
        if highest_action_die == 6:
            boons = remaining_action_dice.count(6) - 1
            if boons > 0:
                return f"Success with {boons} BOON(s)"
            else:
                return "Success"
        elif highest_action_die in (4, 5):
            return "Partial Success"
        else:
            return "Failure"

def adjust_dice(entry, delta):
    try:
        current_value = int(entry.get())
    except ValueError:
        current_value = 0
    new_value = max(0, min(20, current_value + delta))
    entry.delete(0, tk.END)
    entry.insert(0, str(new_value))

def draw_dice(canvas, dice, x, y, dice_size, label, cancelled_dice, remaining_dice, is_action):
    # Draw a label for the dice frame
    canvas.create_text(
        x, y, text=label, anchor="nw", font=('Helvetica', 12), fill="black"
    )
    y += 30  # Add vertical spacing below the label

    highest_remaining_die = max(remaining_dice, default=0)
    cancelled_count = {die: cancelled_dice.count(die) for die in set(cancelled_dice)}

    for i, die in enumerate(dice):
        rect_color = "white"
        text_color = "black"
        if die in cancelled_count and cancelled_count[die] > 0:
            rect_color = "red"
            text_color = "white"
            cancelled_count[die] -= 1
        elif is_action and die == highest_remaining_die:
            rect_color = "green"
            text_color = "white"
            highest_remaining_die = -1

        canvas.create_rectangle(
            x, y, x + dice_size, y + dice_size,
            fill=rect_color, outline="black"
        )
        canvas.create_text(
            x + dice_size // 2, y + dice_size // 2,
            text=str(die), fill=text_color, font=('Helvetica', dice_size // 3)
        )
        x += dice_size + 5  # Move right for the next dice
    return y + dice_size + 20  # Add spacing after the row

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
        num_danger_dice = int(danger_dice_entry.get())
        if not (0 <= num_action_dice <= 20 and 0 <= num_danger_dice <= 20):
            raise ValueError
    except (ValueError, TypeError):
        result_label.config(text="Invalid input: Enter a number between 0 and 20 for each dice type.", foreground="red")
        return

    action_dice = roll_dice(num_action_dice)
    danger_dice = roll_dice(num_danger_dice)
    action_dice_sorted, danger_dice_sorted, cancelled_dice, remaining_action_dice = process_results(action_dice.copy(), danger_dice.copy())
    result = determine_result(remaining_action_dice)

    result_label.config(text=result, foreground="blue")

    # Draw Action and Danger Dice
    x = 10
    y = 10
    y = draw_dice(canvas, action_dice_sorted, x, y, 25, "Action Dice", cancelled_dice, remaining_action_dice, True)
    draw_dice(canvas, danger_dice_sorted, x, y, 25, "Danger Dice", cancelled_dice, [], False)

def roll_dice(n):
    return [random.randint(1, 6) for _ in range(n)]

# Main application setup
root = tk.Tk()
root.title("Action Story Dice Roller")
root.geometry("350x350")

# Style Configuration
style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 12))
style.configure("TButton", font=("Helvetica", 12))

# Input and Controls Frame
input_frame = ttk.Frame(root)
input_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

# Action Dice Input
action_dice_label = ttk.Label(input_frame, text="Action Dice:")
action_dice_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

action_dice_entry = ttk.Entry(input_frame, width=4)
action_dice_entry.insert(0, "1")  # Default value
action_dice_entry.grid(row=0, column=1, padx=5, pady=5)

action_dice_plus = ttk.Button(input_frame, text="+", width=2, command=lambda: adjust_dice(action_dice_entry, 1))
action_dice_plus.grid(row=0, column=2, padx=2)

action_dice_minus = ttk.Button(input_frame, text="-", width=2, command=lambda: adjust_dice(action_dice_entry, -1))
action_dice_minus.grid(row=0, column=3, padx=2)

# Danger Dice Input
danger_dice_label = ttk.Label(input_frame, text="Danger Dice:")
danger_dice_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

danger_dice_entry = ttk.Entry(input_frame, width=4)
danger_dice_entry.insert(0, "0")  # Default value
danger_dice_entry.grid(row=1, column=1, padx=5, pady=5)

danger_dice_plus = ttk.Button(input_frame, text="+", width=2, command=lambda: adjust_dice(danger_dice_entry, 1))
danger_dice_plus.grid(row=1, column=2, padx=2)

danger_dice_minus = ttk.Button(input_frame, text="-", width=2, command=lambda: adjust_dice(danger_dice_entry, -1))
danger_dice_minus.grid(row=1, column=3, padx=2)

# Roll Dice Button
roll_button = ttk.Button(input_frame, text="Roll Dice", command=roll_and_process)
roll_button.grid(row=0, column=4, rowspan=2, padx=5, pady=5, sticky="ns")

# Result Label
result_label = ttk.Label(root, text="", font=("Helvetica", 14))
result_label.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky="w")

# Canvas for dice display
canvas_frame = ttk.LabelFrame(root, text="Dice Results")
canvas_frame.grid(row=2, column=0, columnspan=2, pady=5, padx=10, sticky="nsew")

canvas = tk.Canvas(canvas_frame, bg="#f5f5f5")  # Light gray background for clarity
canvas.pack(fill="both", expand=True, padx=5, pady=5)

# Configure resizing behavior
root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=1)

root.mainloop()