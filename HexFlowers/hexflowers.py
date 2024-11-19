import tkinter as tk
from tkinter import ttk
import random

class HexflowerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hexflower Map Generator")
        
        # Create frames for weather and terrain hexmaps
        self.weather_frame = tk.Frame(root)
        self.weather_frame.grid(row=0, column=0, padx=10, pady=10)
        
        self.terrain_frame = tk.Frame(root)
        self.terrain_frame.grid(row=0, column=1, padx=10, pady=10)

        # Dropdown for seasons
        self.season_var = tk.StringVar(value="Spring")
        self.season_dropdown = ttk.Combobox(self.weather_frame, textvariable=self.season_var, values=["Spring", "Summer", "Autumn", "Winter"])
        self.season_dropdown.grid(row=0, column=0, padx=5, pady=5)

        # Create hexmap grids
        self.weather_hexmap = self.create_hexmap(self.weather_frame)
        self.terrain_hexmap = self.create_hexmap(self.terrain_frame)

        # Buttons for rolling dice and setting cell
        self.roll_button = tk.Button(root, text="Roll 2d6", command=self.roll_dice)
        self.roll_button.grid(row=1, column=0, padx=5, pady=5)

        self.set_cell_button = tk.Button(root, text="Set Cell", command=self.set_cell)
        self.set_cell_button.grid(row=1, column=1, padx=5, pady=5)

    def create_hexmap(self, frame):
        hexmap = []
        for row in range(5):
            hex_row = []
            for col in range(5):
                cell = tk.Label(frame, text="", width=10, height=5, borderwidth=2, relief="groove")
                cell.grid(row=row, column=col, padx=2, pady=2)
                hex_row.append(cell)
            hexmap.append(hex_row)
        return hexmap

    def roll_dice(self):
        roll = random.randint(1, 6) + random.randint(1, 6)
        direction = self.get_direction(roll)
        print(f"Rolled: {roll}, Direction: {direction}")

    def get_direction(self, roll):
        directions = {
            12: "North",
            2: "Upper Right", 3: "Upper Right",
            4: "Lower Right", 5: "Lower Right",
            6: "South",
            8: "Lower Left", 9: "Lower Left",
            10: "Upper Left", 11: "Upper Left"
        }
        return directions.get(roll, "Invalid Roll")

    def set_cell(self):
        # Placeholder function to manually set the current cell
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = HexflowerApp(root)
    root.mainloop()