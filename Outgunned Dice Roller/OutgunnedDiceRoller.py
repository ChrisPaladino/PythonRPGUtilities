import tkinter as tk
from tkinter import ttk
import random

class DiceRollerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Outgunned Dice Roller")

        # Initial values
        self.dice_count = 2
        self.difficulty = "CRITICAL"
        self.double_difficulty = tk.BooleanVar()

        # Layout
        self.create_widgets()

    def create_widgets(self):
        # Dice Count Section
        tk.Label(self.root, text="Number of Dice (2-9):").grid(row=0, column=0, sticky="w")
        self.dice_display = tk.Label(self.root, text=str(self.dice_count))
        self.dice_display.grid(row=0, column=1)

        tk.Button(self.root, text="+", command=self.increment_dice).grid(row=0, column=2)
        tk.Button(self.root, text="-", command=self.decrement_dice).grid(row=0, column=3)

        # Difficulty Section
        tk.Label(self.root, text="Select Difficulty:").grid(row=1, column=0, sticky="w")
        self.difficulty_menu = ttk.Combobox(self.root, values=["BASIC", "CRITICAL", "EXTREME", "IMPOSSIBLE"], state="readonly")
        self.difficulty_menu.set(self.difficulty)
        self.difficulty_menu.grid(row=1, column=1, columnspan=2)

        # Double Difficulty Checkbox
        self.double_difficulty_checkbox = tk.Checkbutton(self.root, text="Double Difficulty", variable=self.double_difficulty)
        self.double_difficulty_checkbox.grid(row=2, column=0, columnspan=2, sticky="w")

        # Roll Button
        self.roll_button = tk.Button(self.root, text="Roll Dice", command=self.roll_dice)
        self.roll_button.grid(row=3, column=0, columnspan=2)

        # Results Display
        self.results_display = tk.Text(self.root, height=10, width=50, state="disabled")
        self.results_display.grid(row=4, column=0, columnspan=4, pady=10)

    def increment_dice(self):
        if self.dice_count < 9:
            self.dice_count += 1
            self.dice_display.config(text=str(self.dice_count))

    def decrement_dice(self):
        if self.dice_count > 2:
            self.dice_count -= 1
            self.dice_display.config(text=str(self.dice_count))

    def roll_dice(self):
        # Roll the dice
        rolls = [random.randint(1, 6) for _ in range(self.dice_count)]
        roll_counts = {side: rolls.count(side) for side in set(rolls)}

        # Calculate successes
        successes = {
            "BASIC": 0,
            "CRITICAL": 0,
            "EXTREME": 0,
            "IMPOSSIBLE": 0,
            "JACKPOT": 0,
        }

        for count in roll_counts.values():
            if count >= 6:
                successes["JACKPOT"] += 1
            elif count == 5:
                successes["IMPOSSIBLE"] += 1
            elif count == 4:
                successes["EXTREME"] += 1
            elif count == 3:
                successes["CRITICAL"] += 1
            elif count == 2:
                successes["BASIC"] += 1

        # Display results
        self.display_results(rolls, successes)

    def display_results(self, rolls, successes):
        # Clear previous results
        self.results_display.config(state="normal")
        self.results_display.delete(1.0, tk.END)

        # Show rolls
        self.results_display.insert(tk.END, f"Rolls: {rolls}\n")

        # Show successes
        for level, count in successes.items():
            self.results_display.insert(tk.END, f"{level} Successes: {count}\n")

        # Evaluate outcome
        difficulty = self.difficulty_menu.get()
        needed_success = {"BASIC": "BASIC", "CRITICAL": "CRITICAL", "EXTREME": "EXTREME", "IMPOSSIBLE": "IMPOSSIBLE"}[difficulty]

        if self.double_difficulty.get():
            success_required = 2
        else:
            success_required = 1

        passed = successes[needed_success] >= success_required

        if passed:
            self.results_display.insert(tk.END, "\nResult: You passed the roll!")
        else:
            self.results_display.insert(tk.END, "\nResult: You failed the roll.")

        self.results_display.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = DiceRollerApp(root)
    root.mainloop()
