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
        self.free_reroll = False
        self.rolls = []
        self.successes = {}
        self.initial_successes = {}
        self.reroll_enabled = False
        self.reroll_used = False

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

        # Reroll Button
        self.reroll_button = tk.Button(self.root, text="Re-roll", command=self.reroll_dice, state="disabled")
        self.reroll_button.grid(row=3, column=2, columnspan=2)

        # Dice Display
        tk.Label(self.root, text="Dice Rolls:").grid(row=4, column=0, sticky="w")
        self.dice_canvas = tk.Canvas(self.root, width=300, height=50, bg="white")
        self.dice_canvas.grid(row=4, column=1, columnspan=3, pady=10)

        # Results Display
        self.results_display = tk.Text(self.root, height=10, width=50, state="disabled")
        self.results_display.grid(row=5, column=0, columnspan=4, pady=10)

    def increment_dice(self):
        if self.dice_count < 9:
            self.dice_count += 1
            self.dice_display.config(text=str(self.dice_count))

    def decrement_dice(self):
        if self.dice_count > 2:
            self.dice_count -= 1
            self.dice_display.config(text=str(self.dice_count))

    def roll_dice(self):
        self.reroll_used = False
        self.rolls = [random.randint(1, 6) for _ in range(self.dice_count)]
        self.rolls.sort(reverse=True)
        roll_counts = {side: self.rolls.count(side) for side in set(self.rolls)}

        self.calculate_successes(roll_counts)
        self.initial_successes = self.successes.copy()

        self.reroll_enabled = any(count >= 2 for count in roll_counts.values()) or self.free_reroll
        self.reroll_button.config(state="normal" if self.reroll_enabled else "disabled")

        self.display_dice(roll_counts)
        self.display_results()

    def reroll_dice(self):
        if not self.reroll_enabled or self.reroll_used:
            return

        roll_counts = {side: self.rolls.count(side) for side in set(self.rolls)}

        if not any(count >= 2 for count in roll_counts.values()) and not self.free_reroll:
            return  # No reroll allowed without successes unless it's a free reroll

        non_success_rolls = [roll for roll in self.rolls if roll_counts[roll] < 2]
        new_rolls = [random.randint(1, 6) for _ in range(len(non_success_rolls))]

        for i in range(len(self.rolls)):
            if roll_counts[self.rolls[i]] < 2:
                self.rolls[i] = new_rolls.pop(0)

        self.rolls.sort(reverse=True)
        roll_counts = {side: self.rolls.count(side) for side in set(self.rolls)}

        self.calculate_successes(roll_counts)

        # Determine improvement
        improved = self.check_improvement()
        if not improved and not self.free_reroll:
            self.downgrade_success()

        self.reroll_enabled = False
        self.reroll_used = True
        self.reroll_button.config(state="disabled")

        self.display_dice(roll_counts)
        self.display_results()

    def calculate_successes(self, roll_counts):
        self.successes = {
            "BASIC": 0,
            "CRITICAL": 0,
            "EXTREME": 0,
            "IMPOSSIBLE": 0,
            "JACKPOT": 0,
        }

        for count in roll_counts.values():
            if count >= 6:
                self.successes["JACKPOT"] += 1
            elif count == 5:
                self.successes["IMPOSSIBLE"] += 1
            elif count == 4:
                self.successes["EXTREME"] += 1
            elif count == 3:
                self.successes["CRITICAL"] += 1
            elif count == 2:
                self.successes["BASIC"] += 1

    def check_improvement(self):
        for level in ["JACKPOT", "IMPOSSIBLE", "EXTREME", "CRITICAL", "BASIC"]:
            if self.successes[level] > self.initial_successes.get(level, 0):
                return True
        return False

    def downgrade_success(self):
        for level in ["BASIC", "CRITICAL", "EXTREME", "IMPOSSIBLE", "JACKPOT"]:
            if self.successes[level] > 0:
                self.successes[level] -= 1
                break

    def display_dice(self, roll_counts):
        self.dice_canvas.delete("all")
        for i, roll in enumerate(self.rolls):
            x = i * 30 + 10
            color = "lightblue"
            if roll_counts[roll] >= 2:
                color = "green"
            self.dice_canvas.create_rectangle(x, 10, x + 20, 30, fill=color)
            self.dice_canvas.create_text(x + 10, 20, text=str(roll))

    def display_results(self):
        self.results_display.config(state="normal")
        self.results_display.delete(1.0, tk.END)

        self.results_display.insert(tk.END, f"Rolls: {self.rolls}\n")
        for level, count in self.successes.items():
            self.results_display.insert(tk.END, f"{level} Successes: {count}\n")

        difficulty = self.difficulty_menu.get()
        needed_success = {"BASIC": "BASIC", "CRITICAL": "CRITICAL", "EXTREME": "EXTREME", "IMPOSSIBLE": "IMPOSSIBLE"}[difficulty]

        success_required = 2 if self.double_difficulty.get() else 1
        passed = self.successes[needed_success] >= success_required

        self.results_display.insert(tk.END, f"\nNeeded Successes: {success_required} ({needed_success})\n")

        if passed:
            self.results_display.insert(tk.END, "\nResult: You passed the roll!\n")
        else:
            self.results_display.insert(tk.END, "\nResult: You failed the roll.\n")

        self.results_display.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = DiceRollerApp(root)
    root.mainloop()
