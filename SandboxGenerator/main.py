import tkinter as tk
import random
import math

def roll_dice(sides):
    return random.randint(1, sides)

def generate_biome(is_starting_hex=False, previous_hex=None):
    """Generates a biome based on the rules."""
    roll = roll_dice(10)
    print(f"Dice roll: {roll}")  # Debug output

    if is_starting_hex:
        if roll in [1, 2, 3, 4]:
            return "Grassland"
        elif roll in [5, 6]:
            return "Forest"
        elif roll in [7, 8]:
            return "Hills"
        elif roll == 9:
            return "Marsh"
        else:
            return "Mountains"
    else:
        if roll in [1, 2, 3, 4, 5]:
            return previous_hex  # Same as previous hex
        elif roll == 6:
            return "Grassland"
        elif roll == 7:
            return "Forest"
        elif roll == 8:
            return "Hills"
        elif roll == 9:
            return "Marsh"
        else:
            return "Mountains"

def generate_extended_hex_map():
    """Generates a full extended hex map based on snowflake expansion."""
    hexes = {}

    def set_biome(x, y, previous_hex=None):
        if (x, y) not in hexes:
            hexes[(x, y)] = generate_biome(is_starting_hex=False, previous_hex=previous_hex)

    # Starting hex
    print("Generating starting hex:")
    hexes[(0, 0)] = generate_biome(is_starting_hex=True)
    print(f"Starting hex biome: {hexes[(0, 0)]}")

    # First layer (6 hexes around the starting hex)
    directions = [
        (0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)  # Clockwise directions
    ]

    for dx, dy in directions:
        set_biome(dx, dy, previous_hex=hexes[(0, 0)])

    # Second layer (12 hexes)
    second_layer_directions = [
        (-1, -2), (0, -2), (1, -2), (2, -1), (2, 0), (2, 1),
        (1, 2), (0, 2), (-1, 2), (-2, 1), (-2, 0), (-2, -1)
    ]

    for dx, dy in second_layer_directions:
        neighbors = [(dx + d[0], dy + d[1]) for d in directions if (dx + d[0], dy + d[1]) in hexes]
        if neighbors:
            previous_hex = random.choice([hexes[neighbor] for neighbor in neighbors])
            set_biome(dx, dy, previous_hex=previous_hex)
        else:
            print(f"No neighbors found for hex ({dx}, {dy}), defaulting to 'Grassland'.")
            set_biome(dx, dy, previous_hex="Grassland")

    return hexes

def get_biome_color(biome):
    """Returns the color associated with a biome."""
    colors = {
        "Grassland": "lightgreen",
        "Forest": "darkgreen",
        "Hills": "brown",
        "Marsh": "#6b4423",  # Murky dark green/brown
        "Mountains": "grey"
    }
    return colors.get(biome, "lightblue")

def create_hex(canvas, x, y, text, fill="lightblue"):
    """Creates a hexagon shape on the canvas with flat tops."""
    size = 30  # Size of the hexagon
    dx = size * math.sqrt(3) / 2
    points = [
        x - size / 2, y - dx,
        x + size / 2, y - dx,
        x + size, y,
        x + size / 2, y + dx,
        x - size / 2, y + dx,
        x - size, y
    ]
    canvas.create_polygon(points, fill=fill, outline="black")
    canvas.create_text(x, y, text=text, font=("Arial", 8, "bold"))

def display_map():
    """Displays the hex map in a tkinter canvas."""
    hex_map = generate_extended_hex_map()
    canvas.delete("all")

    # Offset multipliers for positioning hexes
    offset_x, offset_y = 300, 300
    hex_size = 30
    for (dx, dy), biome in hex_map.items():
        x = offset_x + dx * (hex_size * 3 / 2)
        y = offset_y + dy * (hex_size * math.sqrt(3))
        create_hex(canvas, x, y, biome, fill=get_biome_color(biome))

# Tkinter setup
root = tk.Tk()
root.title("Extended Biome Hex Map Generator")

canvas = tk.Canvas(root, width=700, height=700, bg="white")
canvas.pack(pady=20, padx=20)

# Generate Button
try:
    generate_button = tk.Button(root, text="Generate Extended Hex Map", command=display_map)
    generate_button.pack()
except Exception as e:
    print(f"An error occurred: {e}")

root.mainloop()
