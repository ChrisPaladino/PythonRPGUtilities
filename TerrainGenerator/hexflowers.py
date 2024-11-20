import tkinter as tk
from tkinter import ttk
import random
import math

class HexflowerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hexflower Map Generator")
        self.root.geometry("1000x600")

        self.setup_canvases()
        
        self.season_var = tk.StringVar(value="Spring")
        self.season_dropdown = ttk.Combobox(root, 
                                            textvariable=self.season_var, 
                                            values=["Spring", "Summer", "Autumn", "Winter"],
                                            state="readonly")
        self.season_dropdown.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.season_dropdown.bind('<<ComboboxSelected>>', self.update_weather_map)

        self.roll_button = tk.Button(root, text="Roll 2d6", command=self.roll_and_move)
        self.roll_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.hex_size = 30
        self.current_hex_weather = 0
        self.current_hex_terrain = 0
        self.weather_positions = self.create_hexflower()
        self.terrain_positions = self.create_hexflower()
        self.draw_hexflower(self.canvas_weather, self.weather_positions, "weather")
        self.draw_hexflower(self.canvas_terrain, self.terrain_positions, "terrain")

    def setup_canvases(self):
        self.canvas_weather = tk.Canvas(self.root, width=450, height=600, bg="white")
        self.canvas_weather.grid(row=0, column=0, padx=10, pady=10)
        self.canvas_terrain = tk.Canvas(self.root, width=450, height=600, bg="white")
        self.canvas_terrain.grid(row=0, column=1, padx=10, pady=10)

    def create_hexflower(self):
        positions = []
        start_x, start_y = 200, 300  # Adjusted starting position for better fit
        hex_height = self.hex_size * math.sqrt(3)  # Height of a hex
        hex_width = self.hex_size * 2

        # Center hex
        positions.append((start_x, start_y))

        # First ring
        for i in range(6):
            x = start_x + hex_width * math.cos(math.radians(i * 60))
            y = start_y + hex_width * math.sin(math.radians(i * 60))
            positions.append((x, y))

        # Second ring
        for i in range(12):
            angle = math.radians((i * 30) % 360)
            if i % 2 == 0:  # Even indices for larger radii hexes
                radius = self.hex_size * 4
            else:  # Odd indices for smaller radii hexes
                radius = self.hex_size * 3.464  # Adjusted to fit the column layout
            x = start_x + radius * math.cos(angle)
            y = start_y + radius * math.sin(angle)
            positions.append((x, y))

        return positions

    def draw_hexflower(self, canvas, positions, type_map):
        for index, pos in enumerate(positions):
            fill_color = "light blue" if index == getattr(self, f"current_hex_{type_map}") else "white"
            self.draw_hex(canvas, pos, fill_color, index)

    def draw_hex(self, canvas, pos, fill, index):
        x, y = pos
        points = self.calculate_hex_points(x, y)
        canvas.create_polygon(points, outline='black', fill=fill, width=2)
        canvas.create_text(x, y, text=str(index), font=("Arial", 10))

    def calculate_hex_points(self, x, y):
        points = []
        for angle in range(0, 360, 60):
            angle_rad = math.radians(angle)
            points.extend([x + self.hex_size * math.cos(angle_rad),
                           y + self.hex_size * math.sin(angle_rad)])
        return points

    def roll_and_move(self):
        roll = sum(random.randint(1, 6) for _ in range(2))
        direction = self.get_direction(roll)
        print(f"Rolled: {roll}, Direction: {direction}")
        
        self.update_hex_position("weather", direction)
        self.update_hex_position("terrain", direction)
        
        self.draw_hexflower(self.canvas_weather, self.weather_positions, "weather")
        self.draw_hexflower(self.canvas_terrain, self.terrain_positions, "terrain")

    def update_hex_position(self, type_map, direction):
        current_index = getattr(self, f"current_hex_{type_map}")
        
        # Placeholder for movement logic
        # This will need to be adjusted based on your specific hexflower layout
        movement_map = {
            "North": -6, "South": 6, 
            "Upper Right": -5 if current_index % 6 != 5 else 1, 
            "Upper Left": -1, 
            "Lower Right": 1, 
            "Lower Left": 5 if current_index % 6 != 0 else -1
        }
        
        if direction in movement_map:
            current_index = (current_index + movement_map[direction]) % 19

        setattr(self, f"current_hex_{type_map}", current_index)

    def update_weather_map(self, *args):
        print(f"Current season: {self.season_var.get()}")

    def get_direction(self, roll):
        return {
            2: "Upper Right", 3: "Upper Right",
            4: "Lower Right", 5: "Lower Right",
            6: "South", 7: "South",
            8: "Lower Left", 9: "Lower Left",
            10: "Upper Left", 11: "Upper Left",
            12: "North"
        }.get(roll, "Stay (Center)")

if __name__ == "__main__":
    root = tk.Tk()
    app = HexflowerApp(root)
    root.mainloop()