import tkinter as tk
import random

# Hex types and their corresponding colors
HEX_TYPES = {
    "Grassland": "lightgreen",
    "Wasteland": "tan",
    "Hills": "khaki",
    "Swamp": "darkgreen",
    "Forest": "green",
    "Mountain": "gray",
    "Water": "blue",
}

class Hex:
    def __init__(self, x, y, hex_type=None):
        self.x = x
        self.y = y
        self.hex_type = hex_type or random.choice(list(HEX_TYPES.keys()))

class TerrainGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()

        self.hexes = {}  # Store hexes keyed by (x, y)
        self.hex_size = 40  # Radius of each hex
        self.current_hex = (0, 0)

        # Generate the first hex
        self.add_hex(0, 0)

        # Bind keys for navigation
        self.root.bind("<Up>", lambda e: self.move(0, -1))
        self.root.bind("<Down>", lambda e: self.move(0, 1))
        self.root.bind("<Left>", lambda e: self.move(-1, 0))
        self.root.bind("<Right>", lambda e: self.move(1, 0))

    def add_hex(self, x, y):
        if (x, y) in self.hexes:
            return

        # Generate a new hex
        hex_type = random.choice(list(HEX_TYPES.keys()))
        new_hex = Hex(x, y, hex_type)
        self.hexes[(x, y)] = new_hex

        # Draw it on the canvas
        self.draw_hex(new_hex)

    def draw_hex(self, hex_obj):
        x, y = hex_obj.x, hex_obj.y
        size = self.hex_size
        px, py = self.hex_to_pixel(x, y)

        # Calculate points for the hexagon
        points = self.hex_points(px, py, size)

        # Draw hexagon
        self.canvas.create_polygon(points, fill=HEX_TYPES[hex_obj.hex_type], outline="black")

        # Add text label for terrain type
        self.canvas.create_text(px, py, text=hex_obj.hex_type, fill="black", font=("Arial", 8))

    def hex_points(self, cx, cy, size):
        """Calculate the points for a hexagon centered at (cx, cy)."""
        points = []
        for i in range(6):
            angle = 2 * 3.14159 / 6 * i  # Divide circle into 6 parts for hex points
            x = cx + size * math.cos(angle)
            y = cy + size * math.sin(angle)
            points.extend([x, y])
        return points

    def hex_to_pixel(self, x, y):
        """Convert hex grid coordinates to canvas pixel coordinates."""
        size = self.hex_size
        px = size * 3/2 * x
        py = size * (3**0.5) * (y + 0.5 * (x % 2))
        return px + 400, py + 300  # Center the grid in the window

    def move(self, dx, dy):
        """Move to a new hex."""
        new_x = self.current_hex[0] + dx
        new_y = self.current_hex[1] + dy

        self.current_hex = (new_x, new_y)
        self.add_hex(new_x, new_y)

if __name__ == "__main__":
    import math
    root = tk.Tk()
    app = TerrainGeneratorApp(root)
    root.mainloop()
