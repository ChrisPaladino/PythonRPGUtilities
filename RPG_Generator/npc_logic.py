import json
import random
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

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

def add_to_general_data(data_type, item):
    if len(general_data[data_type]) < 25 and general_data[data_type].count(item) < 3:
        general_data[data_type].append(item)
        save_json_data('data/data.json', general_data)
        return True
    return False

def remove_from_general_data(data_type, item):
    if item in general_data[data_type]:
        general_data[data_type].remove(item)
        save_json_data('data/data.json', general_data)

def get_general_data(data_type):
    return general_data.get(data_type, [])

def save_json_data(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {file_path}.")
    except IOError as e:
        print(f"Error saving JSON to {file_path}: {e}")

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
    # Mapping of likelihood to its modifier value
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

    # Chaos Factor modifiers
    chaos_factor_modifiers = {
        9: +5,
        8: +4,
        7: +2,
        6: +1,
        5: 0,
        4: -1,
        3: -2,
        2: -4,
        1: -5,
    }

    dice1 = random.randint(1, 10)
    dice2 = random.randint(1, 10)
    
    # Apply both modifiers to the roll
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
    if general_data is None:
        return "Error loading data."
    items = list(general_data.get(data_type, []))
    items += ["Choose character" if data_type == 'characters' else "Choose thread"] * (25 - len(items))
    chosen_item = random.choice(items)
    items.clear()
    return f"{chosen_item}"

def generate_action_oracle():
    if action_oracle_data is None:
        return "Error loading action oracle data."

    action1 = random.choice(action_oracle_data['action1'])
    action2 = random.choice(action_oracle_data['action2'])
    return f"Action Oracle: {action1} {action2}"

npc_data = load_json_data('data/npc_data.json')
plot_points = load_json_data('data/plot_points.json')
action_oracle_data = load_json_data('data/action_oracle.json')
general_data = load_json_data('data/data.json')