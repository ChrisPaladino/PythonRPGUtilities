import tkinter as tk
from tkinter import ttk
from rpgcompanion_logic import RPGCompanionLogic  # Importing logic module

# GUI Module (rpgcompanion_gui.py)
class RPGCompanionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RPG Dice Roller")
        self.dice_mode = tk.StringVar(value="Standard")
        self.cortex_dice_pool = []  # Stores the Cortex dice pool
        self.create_widgets()

    def create_widgets(self):
        """Creates the GUI elements."""
        # Main Frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=("N", "W", "E", "S"))

        # Mode Selection
        self.mode_frame = ttk.LabelFrame(self.main_frame, text="Dice Mode", padding="10")
        self.mode_frame.grid(row=0, column=0, sticky=("W", "E"))

        for mode in ["Standard", "Cortex", "Starforged"]:
            ttk.Radiobutton(
                self.mode_frame,
                text=mode,
                variable=self.dice_mode,
                value=mode,
                command=self.update_mode,
            ).pack(side="left", padx=5, pady=5)

        # Standard Dice Section
        self.standard_frame = ttk.LabelFrame(self.main_frame, text="Standard Dice", padding="10")
        self.standard_frame.grid(row=1, column=0, sticky="W", pady=5)

        for dice in ["d4", "d6", "d8", "d10", "d12", "d20", "d100"]:
            ttk.Button(self.standard_frame, text=dice, command=lambda d=dice: self.roll_standard_dice(d)).pack(
                side="left", padx=5, pady=5
            )

        # Cortex Dice Section
        self.cortex_frame = ttk.LabelFrame(self.main_frame, text="Cortex Dice", padding="10")
        self.cortex_frame.grid(row=2, column=0, sticky=("W", "E"), pady=5)

        self.cortex_pool_label = ttk.Label(self.cortex_frame, text="Dice Pool:")
        self.cortex_pool_label.grid(row=0, column=0, sticky="W")

        self.cortex_pool_display = ttk.Label(self.cortex_frame, text="", width=50)
        self.cortex_pool_display.grid(row=0, column=1, sticky="W")

        self.cortex_dice_buttons = ttk.Frame(self.cortex_frame)
        self.cortex_dice_buttons.grid(row=1, column=0, columnspan=2)

        for dice in ["d4", "d6", "d8", "d10", "d12"]:
            btn = ttk.Button(
                self.cortex_dice_buttons,
                text=f"Add {dice}",
                command=lambda d=dice: self.add_to_cortex_pool(d),
            )
            btn.pack(side="left", padx=5, pady=5)

        self.cortex_roll_button = ttk.Button(self.cortex_frame, text="Roll Pool", command=self.roll_cortex_pool)
        self.cortex_roll_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Custom Formula Section
        self.custom_frame = ttk.LabelFrame(self.main_frame, text="Custom Formula", padding="10")
        self.custom_frame.grid(row=3, column=0, sticky=("W", "E"), pady=5)

        self.custom_entry = ttk.Entry(self.custom_frame, width=30)
        self.custom_entry.grid(row=0, column=0, padx=5, pady=5)

        self.custom_roll_button = ttk.Button(self.custom_frame, text="Roll", command=self.roll_custom_formula)
        self.custom_roll_button.grid(row=0, column=1, padx=5, pady=5)

        # Output Frame
        self.output_frame = ttk.LabelFrame(self.main_frame, text="Results", padding="10")
        self.output_frame.grid(row=4, column=0, sticky=("W", "E"), pady=5)

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

        self.update_mode()

    def update_mode(self):
        """Updates visible frames based on the selected mode."""
        mode = self.dice_mode.get()
        self.standard_frame.grid_remove()
        self.cortex_frame.grid_remove()

        if mode == "Standard":
            self.standard_frame.grid()
        elif mode == "Cortex":
            self.cortex_frame.grid()

    def roll_standard_dice(self, dice):
        """Handles standard dice rolls."""
        result = RPGCompanionLogic.roll_standard_dice(dice)
        self.display_output(f"Rolled {dice}: {result}\n")

    def roll_custom_formula(self):
        """Handles custom formula input and rolling."""
        formula = self.custom_entry.get()
        result = RPGCompanionLogic.roll_custom_formula(formula)
        # Add "Rolled" prefix here
        self.display_output(f"Rolled {formula}: {result}\n")

    def add_to_cortex_pool(self, dice):
        """Adds a die to the Cortex dice pool."""
        self.cortex_dice_pool.append(dice)
        self.update_cortex_pool_display()

    def update_cortex_pool_display(self):
        """Updates the display of the Cortex dice pool."""
        self.cortex_pool_display.config(text=", ".join(self.cortex_dice_pool))

    def roll_cortex_pool(self):
        """Rolls the Cortex dice pool and handles the results."""
        results = RPGCompanionLogic.roll_cortex_pool(self.cortex_dice_pool)

        # Display results with die sizes
        result_str = "Cortex Roll: " + ", ".join(f"{die}: {value}" for die, value in results["rolls"])
        self.display_output(f"{result_str}\n")

        # Handle hitches
        if results["hitches"]:
            hitches_str = ", ".join(f"{die}: {value}" for die, value in results["hitches"])
            self.display_output(f"Hitches (cannot be used): {hitches_str}\n")

        # Valid results for selection
        valid_str = ", ".join(f"{die}: {value}" for die, value in results["valid"])
        self.display_output(f"Valid Results: {valid_str}\n")

        if len(results["valid"]) >= 2:
            total = sum(value for _, value in results["valid"][:2])
            effect_die = results["valid"][2][0] if len(results["valid"]) > 2 else "d4"
            self.display_output(f"Total: {total}, Effect Die: {effect_die}\n")
        else:
            self.display_output("Not enough valid dice for a total and effect die.\n")

        self.cortex_dice_pool.clear()
        self.update_cortex_pool_display()

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

# Main Entry Point
def main():
    root = tk.Tk()
    app = RPGCompanionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()