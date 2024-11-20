import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

# Dynamically locate the data folder relative to the script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_FOLDER, "terrain_data.json")

class TerrainGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Terrain Generator")
        
        # Ensure data folder exists
        os.makedirs(DATA_FOLDER, exist_ok=True)
        
        # Terrain data
        self.terrain_data = self.load_terrain_data()
        self.current_terrain = tk.StringVar(value="Plains")
        
        # GUI setup
        self.setup_ui()
    
    def setup_ui(self):
        # Dropdown for current terrain
        ttk.Label(self.root, text="Current Terrain:").pack(pady=5)
        self.terrain_menu = ttk.Combobox(self.root, textvariable=self.current_terrain, state="readonly")
        self.update_terrain_menu()
        self.terrain_menu.pack(pady=5)
        
        # Buttons
        ttk.Button(self.root, text="Generate Next", command=self.generate_next).pack(pady=5)
        ttk.Button(self.root, text="Manage Terrains", command=self.manage_terrains).pack(pady=5)
        
        # Terrain results text box
        self.results_text = tk.Text(self.root, wrap=tk.WORD, height=15, width=50)
        self.results_text.pack(pady=10)
        self.results_text.config(state=tk.DISABLED)  # Make it read-only
    
    def load_terrain_data(self):
        if not os.path.exists(DATA_FILE):
            print("No terrain data loaded in: ", DATA_FILE)
            return {"Plains": {"Plains": 40, "Hills": 30, "Forest": 20}}  # Default data
        try:
            with open(DATA_FILE, "r") as file:
                data = json.load(file)
                return data
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Error reading terrain data: {e}")
            return {}
    
    def save_terrain_data(self):
        with open(DATA_FILE, "w") as file:
            json.dump(self.terrain_data, file, indent=4)
    
    def update_terrain_menu(self):
        self.terrain_menu['values'] = list(self.terrain_data.keys())
    
    def generate_next(self):
        current = self.current_terrain.get()
        if current not in self.terrain_data:
            messagebox.showerror("Error", "Invalid current terrain!")
            return
        
        weights = self.terrain_data[current]
        next_terrain = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
        self.current_terrain.set(next_terrain)
        self.log_terrain(next_terrain)
    
    def log_terrain(self, terrain):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, f"{terrain}\n")
        self.results_text.see(tk.END)  # Auto-scroll to the end
        self.results_text.config(state=tk.DISABLED)
    
    def manage_terrains(self):
        ManageTerrainDialog(self)


class ManageTerrainDialog:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("Manage Terrains")
        
        self.selected_terrain = tk.StringVar()
        self.weight_vars = {}
        
        # Dropdown to select terrain
        ttk.Label(self.window, text="Select Terrain to Edit:").pack(pady=5)
        self.terrain_menu = ttk.Combobox(self.window, textvariable=self.selected_terrain, state="readonly")
        self.terrain_menu['values'] = list(self.parent.terrain_data.keys())
        self.terrain_menu.pack(pady=5)
        self.terrain_menu.bind("<<ComboboxSelected>>", self.load_weights)
        
        # Frame for weights
        self.weights_frame = ttk.LabelFrame(self.window, text="Terrain Weights")
        self.weights_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Buttons
        ttk.Button(self.window, text="Add New Terrain", command=self.add_terrain).pack(pady=5)
        ttk.Button(self.window, text="Save and Close", command=self.save_and_close).pack(pady=5)
    
    def load_weights(self, event=None):
        terrain = self.selected_terrain.get()
        if not terrain:
            return
        
        # Clear previous weight widgets
        for widget in self.weights_frame.winfo_children():
            widget.destroy()
        
        # Load weights
        self.weight_vars = {}
        terrain_weights = self.parent.terrain_data.get(terrain, {})
        all_terrains = set(self.parent.terrain_data.keys())
        
        for related_terrain in sorted(all_terrains):
            ttk.Label(self.weights_frame, text=f"{related_terrain}:").pack(anchor=tk.W, padx=10, pady=2)
            weight_var = tk.IntVar(value=terrain_weights.get(related_terrain, 0))
            self.weight_vars[related_terrain] = weight_var
            ttk.Entry(self.weights_frame, textvariable=weight_var).pack(anchor=tk.W, padx=20)
    
    def save_weights(self):
        terrain = self.selected_terrain.get()
        if not terrain:
            return
        
        self.parent.terrain_data[terrain] = {
            related: weight_var.get()
            for related, weight_var in self.weight_vars.items()
        }
    
    def add_terrain(self):
        new_terrain = tk.simpledialog.askstring("New Terrain", "Enter the name of the new terrain:")
        if not new_terrain or new_terrain in self.parent.terrain_data:
            messagebox.showerror("Error", "Invalid or duplicate terrain name!")
            return
        
        # Add new terrain with default weights
        self.parent.terrain_data[new_terrain] = {key: 0 for key in self.parent.terrain_data.keys()}
        for terrain in self.parent.terrain_data.keys():
            self.parent.terrain_data[terrain][new_terrain] = 0
        
        self.parent.save_terrain_data()
        self.parent.update_terrain_menu()
        self.terrain_menu['values'] = list(self.parent.terrain_data.keys())
    
    def save_and_close(self):
        self.save_weights()
        self.parent.save_terrain_data()
        self.parent.update_terrain_menu()
        self.window.destroy()


# Main loop
if __name__ == "__main__":
    root = tk.Tk()
    app = TerrainGenerator(root)
    root.mainloop()
