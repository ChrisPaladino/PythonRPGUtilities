import tkinter as tk
import random
import math
from collections import deque

# -----------------------------------------------------
#                  BIOME LOGIC
# -----------------------------------------------------
def roll_dice(sides=10):
    return random.randint(1, sides)

def generate_starting_biome():
    roll = roll_dice(10)
    if 1 <= roll <= 4:
        return "Grassland"
    elif 5 <= roll <= 6:
        return "Forest"
    elif 7 <= roll <= 8:
        return "Hills"
    elif roll == 9:
        return "Marsh"
    else:
        return "Mountains"

def generate_next_biome(previous_biome):
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
    else:
        return "Mountains"

def get_biome_color(biome):
    return {
        "Grassland":  "lightgreen",
        "Forest":     "darkgreen",
        "Hills":      "brown",
        "Marsh":      "#6b4423",
        "Mountains":  "grey"
    }.get(biome, "lightblue")

# -----------------------------------------------------
#             FLAT-TOP NEIGHBORS & DISTANCE
# -----------------------------------------------------
FLAT_TOP_NEIGHBORS = [
    (0, -1),
    (1, -1),
    (1, 0),
    (0, 1),
    (-1, 1),
    (-1, 0)
]

def axial_distance(q1, r1, q2, r2):
    return (abs(q1 - q2)
          + abs(r1 - r2)
          + abs((q1 + r1) - (q2 + r2))) // 2

# -----------------------------------------------------
#   BFS TO FIND RING=1 and RING=2 COORDS
# -----------------------------------------------------
def bfs_up_to_radius_2():
    """
    Perform a BFS from (0,0) outward up to distance=2.
    Returns a dict: {(q,r): distance}, distance in {0,1,2}.
    """
    from collections import deque

    center = (0, 0)
    queue = deque([center])
    visited = {center: 0}  # (0,0) => dist=0

    while queue:
        q, r = queue.popleft()
        dist = visited[(q, r)]
        if dist < 2:
            for (dq, dr) in FLAT_TOP_NEIGHBORS:
                nq, nr = q + dq, r + dr
                if (nq, nr) not in visited:
                    visited[(nq, nr)] = dist + 1
                    queue.append((nq, nr))

    return visited

# -----------------------------------------------------
#   SORTING RINGS (CLOCKWISE, STARTING "TOP")
# -----------------------------------------------------

def axial_to_pixel_flat(q, r, size=1):
    """Convert axial (q,r) to pixel, for 'flat-topped' layout."""
    x = 1.5 * q * size
    y = math.sqrt(3) * (r + q/2) * size
    return (x, y)

def angle_for_clockwise_top(q, r):
    """
    Returns an angle so that:
      - (0, -1) => near angle=0
      - angles increase clockwise
      - top is first
    We'll do a standard trick: angle = atan2( px, -py ), 
    so top => (px=0, py<0) => angle=0, 
    and going right => px>0 => angle>0, etc. 
    """
    (px, py) = axial_to_pixel_flat(q, r, size=10)
    # top => py < 0 => we want angle=0 => so angle=atan2(px, -py)
    return math.atan2(px, -py)

def sort_ring_clockwise(coords):
    """Sort given coords in a clockwise order, top first, using angle_for_clockwise_top()."""
    return sorted(coords, key=lambda c: angle_for_clockwise_top(*c))

def rotate_list_until_first_is(coords, desired_coord):
    """
    Rotate 'coords' so that 'desired_coord' is at index 0.
    If 'desired_coord' not in coords, no rotation is done.
    """
    if desired_coord not in coords:
        return coords
    i = coords.index(desired_coord)
    return coords[i:] + coords[:i]

# -----------------------------------------------------
#  BUILD THE 19-HEX SNOWFLAKE
# -----------------------------------------------------
def generate_hex_map_19():
    """
    1) BFS => visited with distance=0..2
    2) center => #1
       ring1 => #2..#7
       ring2 => #8..#19
    3) We'll forcibly rotate ring1 so (0,-1) is first => #2,
       and ring2 so (0,-2) is first => #8.
    """
    visited = bfs_up_to_radius_2()  # dict of {(q,r): dist}
    center_coords = [c for c,d in visited.items() if d == 0]  # just (0,0)
    ring1_coords = [c for c,d in visited.items() if d == 1]
    ring2_coords = [c for c,d in visited.items() if d == 2]

    # 1) The center => #1
    hexmap = {}
    center_coord = center_coords[0]  # (0,0)
    center_biome = generate_starting_biome()
    hexmap[center_coord] = {"biome": center_biome, "number": 1}

    # 2) ring1 => #2..#7
    ring1_sorted = sort_ring_clockwise(ring1_coords)
    # Force (0,-1) to be the first => #2
    ring1_sorted = rotate_list_until_first_is(ring1_sorted, (0, -1))
    for i, c in enumerate(ring1_sorted):
        parent_biome = center_biome
        biome = generate_next_biome(parent_biome)
        hexmap[c] = {"biome": biome, "number": i + 2}

    # 3) ring2 => #8..#19
    ring2_sorted = sort_ring_clockwise(ring2_coords)
    # Force (0,-2) to be the first => #8
    ring2_sorted = rotate_list_until_first_is(ring2_sorted, (0, -2))
    for i, c in enumerate(ring2_sorted):
        # find parent => ring1 neighbor
        for (dq, dr) in FLAT_TOP_NEIGHBORS:
            neigh = (c[0]+dq, c[1]+dr)
            if neigh in hexmap and 2 <= hexmap[neigh]["number"] <= 7:
                p_biome = hexmap[neigh]["biome"]
                break
        else:
            p_biome = center_biome
        biome = generate_next_biome(p_biome)
        hexmap[c] = {"biome": biome, "number": i + 8}

    return hexmap

# -----------------------------------------------------
#    DRAWING (with debug)
# -----------------------------------------------------
def debug_draw_flat_topped_hex(canvas, q, r, size=30, offset_x=300, offset_y=300,
                               fill="lightblue", outline="black", text=""):
    px = offset_x + (1.5 * q * size)
    py = offset_y + (math.sqrt(3)*(r + q/2.0)*size)

    print(f"Hex (q={q}, r={r}), #={text}, center=({px:.1f},{py:.1f})")
    corners = []
    for angle_deg in [0, 60, 120, 180, 240, 300]:
        rad = math.radians(angle_deg)
        cx = px + size * math.cos(rad)
        cy = py + size * math.sin(rad)
        corners.extend((cx, cy))

    # Print corners for debugging
    for i in range(0, len(corners), 2):
        print(f"   corner {i//2}: ({corners[i]:.1f}, {corners[i+1]:.1f})")
    print("-"*60)

    canvas.create_polygon(corners, fill=fill, outline=outline)
    if text:
        canvas.create_text(px, py, text=text, font=("Arial", 9, "bold"))

def draw_hex_map(canvas):
    canvas.delete("all")
    hexmap = generate_hex_map_19()
    hex_size = 30

    print("\n=== BFS-based FLAT-top map (with forced #2 top in ring1, #8 top in ring2) ===")
    # Sort final display by "number" so we see #1..#19 in ascending order
    items = sorted(hexmap.items(), key=lambda kv: kv[1]["number"])
    for (q, r), data in items:
        biome = data["biome"]
        number = data["number"]
        fill_color = get_biome_color(biome)
        text_label = f"{number}\n{biome}"

        debug_draw_flat_topped_hex(
            canvas, q, r,
            size=hex_size,
            fill=fill_color,
            text=text_label
        )
    print("=== Done ===\n")

def main():
    root = tk.Tk()
    root.title("19-Hex BFS Snowflake (FLAT-TOP, forced top #2 and #8)")

    btn = tk.Button(root, text="Generate Hex Map",
                    command=lambda: draw_hex_map(canvas))
    btn.pack(pady=5)

    canvas = tk.Canvas(root, width=700, height=700, bg="white")
    canvas.pack(padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
