import tkinter as tk
import random
import math

# -------------------------------------------------
#                BIOME TABLES
# -------------------------------------------------
def roll_dice(sides=10):
    return random.randint(1, sides)

def generate_starting_biome():
    """Center hex (#1)."""
    roll = roll_dice(10)
    if 1 <= roll <= 4:
        return "Grassland"
    elif 5 <= roll <= 6:
        return "Forest"
    elif 7 <= roll <= 8:
        return "Hills"
    elif roll == 9:
        return "Marsh"
    else:  # 10
        return "Mountains"

def generate_next_biome(previous_biome):
    """Neighbor hexes (roll 1d10, referencing parent's biome)."""
    roll = roll_dice(10)
    if 1 <= roll <= 5:
        return previous_biome
    elif roll == 6:
        return "Grassland"
    elif roll == 7:
        return "Forest"
    elif roll == 8:
        return "Hills"
    elif roll == 9:
        return "Marsh"
    else:  # 10
        return "Mountains"

def get_biome_color(biome):
    """Assign a color for each biome."""
    return {
        "Grassland":  "lightgreen",
        "Forest":     "darkgreen",
        "Hills":      "brown",
        "Marsh":      "#6b4423",
        "Mountains":  "grey"
    }.get(biome, "lightblue")

# -------------------------------------------------
#        FLAT-TOP COORDINATES & NEIGHBORS
# -------------------------------------------------
#
# We want #2 above #1, sharing a *flat* edge at the top.
# In a standard flat‐topped axial system, the 6 neighbors
# (clockwise, starting from top) can be:
#
#   #2  (0, -1)
#   #3  (1, -1)
#   #4  (1, 0)
#   #5  (0, 1)
#   #6  (-1, 1)
#   #7  (-1, 0)
#
FLAT_TOP_NEIGHBORS = [
    (0, -1),   # top
    (1, -1),   # top-right
    (1, 0),    # bottom-right
    (0, 1),    # bottom
    (-1, 1),   # bottom-left
    (-1, 0)    # top-left
]

def axial_distance(q1, r1, q2, r2):
    """Hex distance in axial coords."""
    return (abs(q1 - q2) 
          + abs(r1 - r2) 
          + abs((q1 + r1) - (q2 + r2))) // 2

def ring_coordinates(radius):
    """
    Return all axial coords at exactly `radius` from (0,0),
    in clockwise order starting from the 'top' (0, -radius).
    
    For a flat‐topped layout, one common approach is:
      directions = [(1,0),(1,1),(0,1),(-1,0),(-1,-1),(0,-1)]
    """
    if radius == 0:
        return [(0,0)]
    q, r = 0, -radius
    results = []
    directions = [
        (1, 0),
        (1, 1),
        (0, 1),
        (-1, 0),
        (-1, -1),
        (0, -1),
    ]
    for (dq, dr) in directions:
        for _ in range(radius):
            results.append((q, r))
            q += dq
            r += dr
    return results

def find_parent(q, r, hexmap):
    """
    For a hex at distance d=2, find its neighbor at distance d-1=1.
    That neighbor is the 'parent' for biome rolls.
    """
    d = axial_distance(0, 0, q, r)
    for (dq, dr) in FLAT_TOP_NEIGHBORS:
        nq, nr = q + dq, r + dr
        if (nq, nr) in hexmap:
            if axial_distance(0, 0, nq, nr) == d - 1:
                return (nq, nr)
    return None

def generate_hex_map_19():
    """
    Builds a '19-hex snowflake':
      - Center (#1)
      - Ring 1 (#2..#7)
      - Ring 2 (#8..#19)
    All using the 'flat‐topped' orientation & numbering
    in a clockwise loop starting from top.
    """
    hexmap = {}

    # Center => #1
    center_biome = generate_starting_biome()
    hexmap[(0, 0)] = {
        "biome": center_biome,
        "number": 1
    }

    # Ring 1 => #2..#7
    ring1 = ring_coordinates(1)  # 6 coords
    for i, (q, r) in enumerate(ring1):
        parent_biome = hexmap[(0, 0)]["biome"]
        new_biome = generate_next_biome(parent_biome)
        hexmap[(q, r)] = {
            "biome": new_biome,
            "number": i+2
        }

    # Ring 2 => #8..#19
    ring2 = ring_coordinates(2)  # 12 coords
    for i, (q, r) in enumerate(ring2):
        parent_coord = find_parent(q, r, hexmap)
        if parent_coord:
            parent_biome = hexmap[parent_coord]["biome"]
        else:
            parent_biome = center_biome
        new_biome = generate_next_biome(parent_biome)
        hexmap[(q, r)] = {
            "biome": new_biome,
            "number": i+8
        }

    return hexmap

# -------------------------------------------------
#       DRAWING A FLAT-TOPPED HEX
# -------------------------------------------------
def create_flat_topped_hex(canvas, cx, cy, size=30, fill="lightblue", outline="black", text=""):
    """
    Draw corners at angles: 0°, 60°, 120°, 180°, 240°, 300° 
    so that the top edge is fully horizontal.
    """
    points = []
    for angle_deg in [0, 60, 120, 180, 240, 300]:
        rad = math.radians(angle_deg)
        x = cx + size * math.cos(rad)
        y = cy + size * math.sin(rad)
        points.extend((x, y))

    # Draw the hex polygon
    canvas.create_polygon(points, fill=fill, outline=outline)

    # Optionally label the center
    if text:
        canvas.create_text(cx, cy, text=text, font=("Arial", 9, "bold"))

def axial_to_pixel_flat(q, r, size=30, offset_x=300, offset_y=300):
    """
    Convert 'flat-topped' axial coords (q,r) to pixel coords.
    The standard formula (Red Blob Games):
      x = offset_x + (3/2 * q * size)
      y = offset_y + (sqrt(3) * (r + q/2) * size)
    => ensures that (0, -1) is *directly above* (0,0) 
       with a shared horizontal edge, not a corner.
    """
    x = offset_x + (1.5 * q * size)
    y = offset_y + (math.sqrt(3) * (r + q/2.0) * size)
    return x, y

def draw_hex_map(canvas):
    """Clears & redraws the 19‐hex map with flat‐topped hexes and no gaps."""
    canvas.delete("all")
    hexmap = generate_hex_map_19()
    hex_size = 30

    for (q, r), data in hexmap.items():
        biome  = data["biome"]
        number = data["number"]
        px, py = axial_to_pixel_flat(q, r, hex_size, 300, 300)

        create_flat_topped_hex(
            canvas, px, py, size=hex_size,
            fill=get_biome_color(biome),
            text=f"{number}\n{biome}"
        )

# -------------------------------------------------
#               MAIN GUI
# -------------------------------------------------
def main():
    root = tk.Tk()
    root.title("19-Hex Snowflake (Flat-Topped)")

    btn = tk.Button(root, text="Generate Hex Map",
                    command=lambda: draw_hex_map(canvas))
    btn.pack(pady=10)

    canvas = tk.Canvas(root, width=700, height=700, bg="white")
    canvas.pack(padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
