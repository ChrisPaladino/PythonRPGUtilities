import tkinter as tk
from tkinter import ttk
from rpgcompanion_logic import RPGCompanionLogic  # Importing logic module

class RPGCompanionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RPG Dice Roller")
        self.create_widgets()

    def create_widgets(self):
        """Creates the GUI elements."""
        # Main Frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=("N", "W", "E", "S"))

        # Title Label
        self.title_label = ttk.Label(self.main_frame, text="RPG Dice Roller", font=("Arial", 16))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=5)

        # Dice Buttons Frame
        self.dice_frame = ttk.LabelFrame(self.main_frame, text="Dice Rolls", padding="10")
        self.dice_frame.grid(row=1, column=0, sticky="W", pady=5)

        # Dice Buttons
        dice_types = ["d4", "d6", "d8", "d10", "d12", "d20", "d100"]
        for idx, dice in enumerate(dice_types):
            button = ttk.Button(self.dice_frame, text=dice, command=lambda d=dice: self.roll_dice(d))
            button.grid(row=idx // 3, column=idx % 3, padx=5, pady=5)

        # Custom Input Frame
        self.custom_frame = ttk.LabelFrame(self.main_frame, text="Custom Roll", padding="10")
        self.custom_frame.grid(row=1, column=1, sticky="E", pady=5)

        self.custom_entry = ttk.Entry(self.custom_frame, width=20)
        self.custom_entry.grid(row=0, column=0, padx=5, pady=5)

        self.custom_button = ttk.Button(
            self.custom_frame, text="Roll", command=self.roll_custom
        )
        self.custom_button.grid(row=0, column=1, padx=5, pady=5)

        # Output Frame
        self.output_frame = ttk.LabelFrame(self.main_frame, text="Results", padding="10")
        self.output_frame.grid(row=2, column=0, columnspan=2, sticky=("W", "E"), pady=5)

        self.output_text = tk.Text(self.output_frame, height=10, wrap="word", state="disabled")
        self.output_text.grid(row=0, column=0, sticky=("W", "E"))

        # Clear and Copy Buttons
        self.action_frame = ttk.Frame(self.output_frame)
        self.action_frame.grid(row=1, column=0, sticky="E", pady=5)

        self.clear_button = ttk.Button(
            self.action_frame, text="Clear", command=self.clear_output
        )
        self.clear_button.grid(row=0, column=0, padx=5)

        self.copy_button = ttk.Button(
            self.action_frame, text="Copy", command=self.copy_output
        )
        self.copy_button.grid(row=0, column=1, padx=5)

    def roll_dice(self, dice):
        """Handles dice button clicks."""
        result = RPGCompanionLogic.roll_standard_dice(dice)
        self.display_output(f"Rolled {dice}: {result}\n")

    def roll_custom(self):
        """Handles custom roll input."""
        formula = self.custom_entry.get()
        result = RPGCompanionLogic.roll_custom_formula(formula)
        self.display_output(f"Rolled {formula}: {result}\n")

    def display_output(self, message):
        """Displays output in the text box."""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", message)
        self.output_text.configure(state="disabled")

    def clear_output(self):
        """Clears the text box output."""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")

    def copy_output(self):
        """Copies the text box output to the clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get("1.0", "end").strip())
        self.root.update()  # Now it stays on the clipboard

def main():
    root = tk.Tk()
    app = RPGCompanionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
