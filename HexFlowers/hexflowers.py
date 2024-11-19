import tkinter as tk
from tkinter import ttk
import random
import math

class HexflowerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hexflower Map Generator")

        # Create a canvas for hexflower
        self.canvas = tk.Canvas(root, width=400, height=400)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        # Create dropdown for seasons
        self.season_var = tk.StringVar(value="Spring")
        self.season_dropdown = ttk.Combobox(root, textvariable=self.season_var, values=["Spring", "Summer", "Autumn", "Winter"])
        self.season_dropdown.grid(row=1, column=0, padx=5, pady=5)

        # Draw hexflower
        self.hex_size = 30
        self.hex_positions = self.create_hexflower()
        self.draw_hexflower()

        # Roll button
        self.roll_button = tk.Button(root, text="Roll 2d6", command=self.roll_dice)
        self.roll_button.grid(row=2, column=0, padx=5, pady=5)

    def create_hexflower(self):
        positions = []
        for q in range(-2, 3):
            for r in range(-2, 3):
                if abs(q + r) <= 2:  # Hexflower condition
                    x = self.hex_size * 3/2 * q
                    y = self.hex_size * math.sqrt(3) * (r + q/2)
                    positions.append((x + 200, y + 200))  # Centering the hexflower
        return positions

    def draw_hexflower(self):
        for pos in self.hex_positions:
            self.draw_hex(pos)

    def draw_hex(self, pos):
        x, y = pos
        points = [
            x + self.hex_size * math.cos(math.radians(angle))
            for angle in range(0, 360, 60)
        ]
        points += [
            y + self.hex_size * math.sin(math.radians(angle))
            for angle in range(0, 360, 60)
        ]
        self.canvas.create_polygon(points, outline='black', fill='', width=2)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = HexflowerApp(root)
    root.mainloop()