import json
import random
import os
import math
import tkinter as tk
from tkinter import filedialog

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

class DataManager:
    def __init__(self):
        self.data = {"characters": [], "threads": []}

    def add_item(self, data_type, item):
        if data_type not in self.data:
            self.data[data_type] = []
        if item not in ["Choose character", "Choose thread"]:
            if len(self.data[data_type]) < 25:
                if item not in self.data[data_type]:
                    self.data[data_type].append(item)
                    self.data[data_type].sort()  # Sort after adding
                return True
        return False

    def get_items(self, data_type):
        return sorted(self.data.get(data_type, []))  # Return sorted list

    def load_from_file(self, file_path):
        if file_path:
            loaded_data = load_json_data(file_path)
            if loaded_data:
                self.data.clear()
                self.data.update(loaded_data)
            else:
                print(f"Error loading data from {file_path}. Starting with empty data.")
        else:
            print("No file path provided. Starting with empty data.")

    def remove_item(self, data_type, item):
        if data_type in self.data and item in self.data[data_type]:
            self.data[data_type].remove(item)
            # No need to sort here as it's already sorted

    def save_to_file(self, file_path):
        sorted_data = {
            "characters": sorted(self.data["characters"]),
            "threads": sorted(self.data["threads"])
        }
        return save_json_data(file_path, sorted_data)

data_manager = DataManager()

def load_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {file_path} file not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}.")
        return None

def save_json_data(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)  # Remove sort_keys=True
        print(f"Data successfully saved to {file_path}.")
        return True
    except IOError as e:
        print(f"Error saving JSON to {file_path}: {e}")
        return False

def initialize_data():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set the default directory to the 'data' subfolder
    default_dir = os.path.join(script_dir, 'data')

    # Create the 'data' directory if it doesn't exist
    if not os.path.exists(default_dir):
        os.makedirs(default_dir)

    # Open file dialog with default directory set
    file_path = filedialog.askopenfilename(
        title="Select default JSON file",
        initialdir=default_dir,
        filetypes=[("JSON files", "*.json")]
    )

    if file_path:
        data_manager.load_from_file(file_path)
    else:
        print("No file selected. Starting with empty data.")
    root.destroy()
    return file_path

def get_general_data(data_type):
    return data_manager.get_items(data_type)

def add_to_general_data(data_type, item):
    if data_type not in data_manager.data:
        data_manager.data[data_type] = []
    if item not in ["Choose character", "Choose thread"]:
        if len(data_manager.data[data_type]) < 25:
            if data_manager.data[data_type].count(item) < 3:
                data_manager.data[data_type].append(item)
                data_manager.data[data_type].sort()  # Sort after adding
                return True
    return False    

def remove_from_general_data(data_type, item):
    data_manager.remove_item(data_type, item)

def load_campaign(file_path):
    data_manager.load_from_file(file_path)
    return data_manager.data

def save_campaign(file_path):
    return data_manager.save_to_file(file_path)

def get_plot_point(theme, d100_roll):
    if plot_points is None or theme not in plot_points:
        return None, "Plot point data not found."
    
    for key, value in plot_points[theme].items():
        range_parts = key.split('-')
        range_start = int(range_parts[0])
        range_end = int(range_parts[-1])
        if range_start <= d100_roll <= range_end:
            return theme, value
    return None, "Plot point not found for the given roll."

def get_une_interaction(npc_relationship, npc_demeanor):
    if npc_data is None:
        return "Error loading NPC data."

    d100_roll = random.randint(1, 100)
    npc_mood = None
    for key, value in npc_data['npcMood'][npc_relationship].items():
        range_start, range_end = map(int, key.split('-'))
        if range_start <= d100_roll <= range_end:
            npc_mood = value
            break

    npc_bearing = random.choice(npc_data['npcBearing'][npc_demeanor])
    npc_focus = random.choice(npc_data['npcFocus'])

    result = (f"The {npc_relationship} NPC is {npc_mood}. "
              f"They are {npc_demeanor}, and speak of {npc_bearing} "
              f"regarding the PC's {npc_focus}.")
    return result

def generate_themes(themes_listbox, weights):
    weighted_theme_selection = random.choices(themes_listbox, weights, k=5)
    
    theme_results = []
    for theme in weighted_theme_selection:
        d100_roll = random.randint(1, 100)
        _, plot_point = get_plot_point(theme, d100_roll)
        theme_results.append(f"Theme: {theme.capitalize()}, Plot Point: {plot_point}")
    
    return theme_results

def generate_npc_age():
    age_categories = ["child", "adolescent", "young adult", "adult", "middle-aged", "senior"]
    weights = [4, 8, 25, 30, 20, 13]
    age_category = random.choices(age_categories, weights, k=1)[0]
    age_distribution = {
        "child": (0, 12),
        "adolescent": (13, 17),
        "young adult": (18, 24),
        "adult": (25, 44),
        "middle-aged": (45, 64),
        "senior": (65, 100)
    }
    min_age, max_age = age_distribution[age_category]
    npc_age = random.randint(min_age, max_age)
    return npc_age, age_category

def generate_npc():
    if npc_data is None:
        return "Error loading NPC data."

    sex = random.choice(['male', 'female'])
    modifier = random.choice(npc_data['modifiers'])
    noun = random.choice(npc_data['nouns'])
    motivationverb1 = random.choice(npc_data['motivationVerbs'])
    motivationnoun1 = random.choice(npc_data['motivationNouns'])
    motivationverb2 = random.choice(npc_data['motivationVerbs'])
    motivationnoun2 = random.choice(npc_data['motivationNouns'])
    npc_name = generate_name()
    npc_age, age_category = generate_npc_age()

    return f"NPC: {npc_name}, the {sex}, {age_category} ({npc_age}), {modifier} {noun}, wants to {motivationverb1} {motivationnoun1}, and {motivationverb2} {motivationnoun2}."

def generate_name():
    if npc_data is None:
        return "Error loading NPC data."

    first, last = random.sample(npc_data['names'], 2)
    return f"{first} {last}"

def check_the_fates_dice(chaos_factor, likelihood):
    likelihood_modifiers = {
        "Certain": +5,
        "Nearly Certain": +4,
        "Very Likely": +2,
        "Likely": +1,
        "50/50": 0,
        "Unlikely": -1,
        "Very Unlikely": -2,
        "Nearly Impossible": -4,
        "Impossible": -5,
    }


# Low chaos (my default) modifiers    
    chaos_factor_modifiers = {
        9: +2,
        8: +1,
        7: +1,
        6: 0,
        5: 0,
        4: 0,
        3: -1,
        2: -1,
        1: -2,
    }

# Regular chaos fate chart
#    chaos_factor_modifiers = {
#        9: +5,
#        8: +4,
#        7: +2,
#        6: +1,
#        5: 0,
#        4: -1,
#        3: -2,
#        2: -4,
#        1: -5,
#    }

    dice1 = random.randint(1, 10)
    dice2 = random.randint(1, 10)
    
    total_modifier = likelihood_modifiers[likelihood] + chaos_factor_modifiers[chaos_factor]
    total_roll = dice1 + dice2 + total_modifier
    
    if dice1 == dice2 and dice1 <= chaos_factor:
        result = "Random Event"
    elif total_roll >= 18:
        result = "Exceptional YES"
    elif total_roll >= 11:
        result = "Yes"
    elif total_roll <= 4:
        result = "Exceptional NO"
    else:
        result = "No"
    
    return result, dice1, dice2, total_roll

def select_from_list(data_type):    
    items = get_general_data(data_type)
    if not items:
        return "No items available"

    # Number of actual items
    count = len(items)
    
    # Determine the placeholder text depending on the data type
    placeholder = "Choose character" if data_type == 'characters' else "Choose thread"
    
    # Round up count to the next multiple of 5 but cap at 25 (since we never store more than 25)
    # For example, if count=19 => next multiple of 5 is 20 => total_slots=20
    total_slots = (math.ceil(count / 5.0) * 5)
    if total_slots > 25:
        total_slots = 25

    # Pad with placeholders until we have total_slots entries
    while len(items) < total_slots:
        items.append(placeholder)

    # Roll one integer in [0, total_slots-1]
    roll = random.randint(0, total_slots - 1)
    
    return items[roll]

def generate_action_oracle():
    if action_oracle_data is None:
        return "Error loading action oracle data."

    action1 = random.choice(action_oracle_data['action1'])
    action2 = random.choice(action_oracle_data['action2'])
    return f"Action Oracle: {action1} {action2}"

# Load initial data
npc_data = load_json_data('data/npc_data.json')
plot_points = load_json_data('data/plot_points.json')
action_oracle_data = load_json_data('data/action_oracle.json')