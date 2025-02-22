import random
import math
import os
from data_manager import load_json_data

script_dir = os.path.dirname(os.path.abspath(__file__))
npc_data = load_json_data(os.path.join(script_dir, "data", "npc_data.json"))
plot_points = load_json_data(os.path.join(script_dir, "data", "plot_points.json"))
action_oracle_data = load_json_data(os.path.join(script_dir, "data", "action_oracle.json"))

# Dice Rolling Logic
def determine_result(remaining_action_dice):
    if not remaining_action_dice:
        return "BOTCH"
    highest = max(remaining_action_dice)
    if highest == 6:
        boons = remaining_action_dice.count(6) - 1
        return f"Success with {boons} BOON(s)" if boons > 0 else "Success"
    if highest in (4, 5):
        return "Partial Success"
    return "BOTCH" if highest == 1 else "Failure"

def process_results(action_dice, danger_dice):
    cancelled_dice = []
    action_dice.sort(reverse=True)
    danger_dice.sort(reverse=True)
    remaining_action_dice = action_dice.copy()
    for danger_die in danger_dice:
        if danger_die in remaining_action_dice:
            remaining_action_dice.remove(danger_die)
            cancelled_dice.append(danger_die)
    return action_dice, danger_dice, cancelled_dice, remaining_action_dice

def roll_dice(n):
    return [random.randint(1, 6) for _ in range(n)]

# Generator Logic
def get_une_interaction(npc_relationship, npc_demeanor):
    if npc_data is None:
        return "Error loading NPC data."
    d100_roll = random.randint(1, 100)  # Percentile roll (01-100)
    npc_mood = None
    for key, value in npc_data['npcMood'][npc_relationship].items():
        range_start, range_end = map(int, key.split('-'))
        if range_start <= d100_roll <= range_end:
            npc_mood = value
            break
    npc_bearing = random.choice(npc_data['npcBearing'][npc_demeanor])
    npc_focus = random.choice(npc_data['npcFocus'])
    return (f"The {npc_relationship} NPC is {npc_mood}. "
            f"They are {npc_demeanor}, and speak of {npc_bearing} "
            f"regarding the PC's {npc_focus}.")

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
        "child": (0, 12), "adolescent": (13, 17), "young adult": (18, 24),
        "adult": (25, 44), "middle-aged": (45, 64), "senior": (65, 100)
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

# New Fate Chart Logic (Normal-Chaos, using 1d100, corrected ranges)
def check_fate_chart(chaos_factor, likelihood):
    # Define the Fate Chart ranges for Normal-Chaos (Chaos Factor 1-9, percentile 01-100)
    fate_chart = {
        "Certain": {
            1: {"Exceptional Yes": range(1, 11), "Yes": range(11, 51), "No": range(51, 92), "Exceptional No": range(92, 101)},
            2: {"Exceptional Yes": range(1, 14), "Yes": range(14, 66), "No": range(66, 95), "Exceptional No": range(95, 101)},
            3: {"Exceptional Yes": range(1, 16), "Yes": range(16, 76), "No": range(76, 97), "Exceptional No": range(97, 101)},
            4: {"Exceptional Yes": range(1, 18), "Yes": range(18, 86), "No": range(86, 99), "Exceptional No": range(99, 101)},
            5: {"Exceptional Yes": range(1, 19), "Yes": range(19, 91), "No": range(91, 100), "Exceptional No": range(100, 101)},
            6: {"Exceptional Yes": range(1, 20), "Yes": range(20, 96), "No": range(96, 101), "Exceptional No": []},
            7: {"Exceptional Yes": range(1, 21), "Yes": range(21, 100), "No": [], "Exceptional No": []},  # X means impossible
            8: {"Exceptional Yes": range(1, 21), "Yes": range(21, 100), "No": [], "Exceptional No": []},  # X means impossible
            9: {"Exceptional Yes": range(1, 21), "Yes": range(21, 100), "No": [], "Exceptional No": []}  # X means impossible
        },
        "Nearly Certain": {
            1: {"Exceptional Yes": range(1, 8), "Yes": range(8, 36), "No": range(36, 89), "Exceptional No": range(89, 101)},
            2: {"Exceptional Yes": range(1, 11), "Yes": range(11, 51), "No": range(51, 92), "Exceptional No": range(92, 101)},
            3: {"Exceptional Yes": range(1, 14), "Yes": range(14, 66), "No": range(66, 95), "Exceptional No": range(95, 101)},
            4: {"Exceptional Yes": range(1, 16), "Yes": range(16, 76), "No": range(76, 97), "Exceptional No": range(97, 101)},
            5: {"Exceptional Yes": range(1, 18), "Yes": range(18, 86), "No": range(86, 99), "Exceptional No": range(99, 101)},
            6: {"Exceptional Yes": range(1, 19), "Yes": range(19, 91), "No": range(91, 100), "Exceptional No": range(100, 101)},
            7: {"Exceptional Yes": range(1, 20), "Yes": range(20, 96), "No": range(96, 101), "Exceptional No": []},
            8: {"Exceptional Yes": range(1, 21), "Yes": range(21, 100), "No": [], "Exceptional No": []},  # X means impossible
            9: {"Exceptional Yes": range(1, 21), "Yes": range(21, 100), "No": [], "Exceptional No": []}  # X means impossible
        },
        "Very Likely": {
            1: {"Exceptional Yes": range(1, 6), "Yes": range(6, 26), "No": range(26, 87), "Exceptional No": range(87, 101)},
            2: {"Exceptional Yes": range(1, 8), "Yes": range(8, 36), "No": range(36, 89), "Exceptional No": range(89, 101)},
            3: {"Exceptional Yes": range(1, 11), "Yes": range(11, 51), "No": range(51, 92), "Exceptional No": range(92, 101)},
            4: {"Exceptional Yes": range(1, 14), "Yes": range(14, 66), "No": range(66, 95), "Exceptional No": range(95, 101)},
            5: {"Exceptional Yes": range(1, 16), "Yes": range(16, 76), "No": range(76, 97), "Exceptional No": range(97, 101)},
            6: {"Exceptional Yes": range(1, 18), "Yes": range(18, 86), "No": range(86, 99), "Exceptional No": range(99, 101)},
            7: {"Exceptional Yes": range(1, 19), "Yes": range(19, 91), "No": range(91, 100), "Exceptional No": range(100, 101)},
            8: {"Exceptional Yes": range(1, 20), "Yes": range(20, 96), "No": range(96, 101), "Exceptional No": []},
            9: {"Exceptional Yes": range(1, 21), "Yes": range(21, 100), "No": [], "Exceptional No": []}  # X means impossible
        },
        "Likely": {
            1: {"Exceptional Yes": range(1, 4), "Yes": range(4, 16), "No": range(16, 85), "Exceptional No": range(85, 101)},
            2: {"Exceptional Yes": range(1, 6), "Yes": range(6, 26), "No": range(26, 87), "Exceptional No": range(87, 101)},
            3: {"Exceptional Yes": range(1, 8), "Yes": range(8, 36), "No": range(36, 89), "Exceptional No": range(89, 101)},
            4: {"Exceptional Yes": range(1, 11), "Yes": range(11, 51), "No": range(51, 92), "Exceptional No": range(92, 101)},
            5: {"Exceptional Yes": range(1, 14), "Yes": range(14, 66), "No": range(66, 95), "Exceptional No": range(95, 101)},
            6: {"Exceptional Yes": range(1, 16), "Yes": range(16, 76), "No": range(76, 97), "Exceptional No": range(97, 101)},
            7: {"Exceptional Yes": range(1, 18), "Yes": range(18, 86), "No": range(86, 99), "Exceptional No": range(99, 101)},
            8: {"Exceptional Yes": range(1, 19), "Yes": range(19, 91), "No": range(91, 100), "Exceptional No": range(100, 101)},
            9: {"Exceptional Yes": range(1, 20), "Yes": range(20, 96), "No": range(96, 101), "Exceptional No": []}
        },
        "50/50": {
            1: {"Exceptional Yes": range(1, 3), "Yes": range(3, 11), "No": range(11, 83), "Exceptional No": range(83, 101)},
            2: {"Exceptional Yes": range(1, 4), "Yes": range(4, 16), "No": range(16, 85), "Exceptional No": range(85, 101)},
            3: {"Exceptional Yes": range(1, 6), "Yes": range(6, 26), "No": range(26, 87), "Exceptional No": range(87, 101)},
            4: {"Exceptional Yes": range(1, 8), "Yes": range(8, 36), "No": range(36, 89), "Exceptional No": range(89, 101)},
            5: {"Exceptional Yes": range(1, 11), "Yes": range(11, 51), "No": range(51, 92), "Exceptional No": range(92, 101)},
            6: {"Exceptional Yes": range(1, 14), "Yes": range(14, 66), "No": range(66, 95), "Exceptional No": range(95, 101)},
            7: {"Exceptional Yes": range(1, 16), "Yes": range(16, 76), "No": range(76, 97), "Exceptional No": range(97, 101)},
            8: {"Exceptional Yes": range(1, 18), "Yes": range(18, 86), "No": range(86, 99), "Exceptional No": range(99, 101)},
            9: {"Exceptional Yes": range(1, 19), "Yes": range(19, 91), "No": range(91, 100), "Exceptional No": range(100, 101)}
        },
        "Unlikely": {
            1: {"Exceptional Yes": [], "Yes": range(1, 2), "No": range(2, 6), "Exceptional No": range(6, 101)},  # X means impossible
            2: {"Exceptional Yes": [], "Yes": range(1, 3), "No": range(3, 11), "Exceptional No": range(11, 101)},
            3: {"Exceptional Yes": [], "Yes": range(1, 4), "No": range(4, 16), "Exceptional No": range(16, 101)},
            4: {"Exceptional Yes": [], "Yes": range(1, 6), "No": range(6, 26), "Exceptional No": range(26, 101)},
            5: {"Exceptional Yes": [], "Yes": range(1, 8), "No": range(8, 36), "Exceptional No": range(36, 101)},
            6: {"Exceptional Yes": [], "Yes": range(1, 11), "No": range(11, 51), "Exceptional No": range(51, 101)},
            7: {"Exceptional Yes": [], "Yes": range(1, 14), "No": range(14, 66), "Exceptional No": range(66, 101)},
            8: {"Exceptional Yes": [], "Yes": range(1, 16), "No": range(16, 76), "Exceptional No": range(76, 101)},
            9: {"Exceptional Yes": [], "Yes": range(1, 18), "No": range(18, 86), "Exceptional No": range(86, 101)}
        },
        "Very Unlikely": {
            1: {"Exceptional Yes": [], "Yes": [], "No": range(1, 81), "Exceptional No": range(81, 101)},  # X means impossible
            2: {"Exceptional Yes": [], "Yes": range(1, 2), "No": range(2, 6), "Exceptional No": range(6, 101)},
            3: {"Exceptional Yes": [], "Yes": range(1, 3), "No": range(3, 11), "Exceptional No": range(11, 101)},
            4: {"Exceptional Yes": [], "Yes": range(1, 4), "No": range(4, 16), "Exceptional No": range(16, 101)},
            5: {"Exceptional Yes": [], "Yes": range(1, 6), "No": range(6, 26), "Exceptional No": range(26, 101)},
            6: {"Exceptional Yes": [], "Yes": range(1, 8), "No": range(8, 36), "Exceptional No": range(36, 101)},
            7: {"Exceptional Yes": [], "Yes": range(1, 11), "No": range(11, 51), "Exceptional No": range(51, 101)},
            8: {"Exceptional Yes": [], "Yes": range(1, 14), "No": range(14, 66), "Exceptional No": range(66, 101)},
            9: {"Exceptional Yes": [], "Yes": range(1, 16), "No": range(16, 76), "Exceptional No": range(76, 101)}
        },
        "Nearly Impossible": {
            1: {"Exceptional Yes": [], "Yes": [], "No": range(1, 81), "Exceptional No": range(81, 101)},  # X means impossible
            2: {"Exceptional Yes": [], "Yes": [], "No": range(1, 81), "Exceptional No": range(81, 101)},  # X means impossible
            3: {"Exceptional Yes": [], "Yes": range(1, 2), "No": range(2, 6), "Exceptional No": range(6, 101)},
            4: {"Exceptional Yes": [], "Yes": range(1, 3), "No": range(3, 11), "Exceptional No": range(11, 101)},
            5: {"Exceptional Yes": [], "Yes": range(1, 4), "No": range(4, 16), "Exceptional No": range(16, 101)},
            6: {"Exceptional Yes": [], "Yes": range(1, 6), "No": range(6, 26), "Exceptional No": range(26, 101)},
            7: {"Exceptional Yes": [], "Yes": range(1, 8), "No": range(8, 36), "Exceptional No": range(36, 101)},
            8: {"Exceptional Yes": [], "Yes": range(1, 11), "No": range(11, 51), "Exceptional No": range(51, 101)},
            9: {"Exceptional Yes": [], "Yes": range(1, 14), "No": range(14, 66), "Exceptional No": range(66, 101)}
        },
        "Impossible": {
            1: {"Exceptional Yes": [], "Yes": range(1, 2), "No": range(2, 82), "Exceptional No": range(82, 101)},  # X 1 81
            2: {"Exceptional Yes": [], "Yes": [], "No": range(1, 81), "Exceptional No": range(81, 101)},  # X 1 81
            3: {"Exceptional Yes": [], "Yes": [], "No": range(1, 81), "Exceptional No": range(81, 101)},  # X 1 81
            4: {"Exceptional Yes": [], "Yes": range(1, 2), "No": range(2, 6), "Exceptional No": range(6, 101)},
            5: {"Exceptional Yes": [], "Yes": range(1, 3), "No": range(3, 11), "Exceptional No": range(11, 101)},
            6: {"Exceptional Yes": [], "Yes": range(1, 4), "No": range(4, 16), "Exceptional No": range(16, 101)},
            7: {"Exceptional Yes": [], "Yes": range(1, 6), "No": range(6, 26), "Exceptional No": range(26, 101)},
            8: {"Exceptional Yes": [], "Yes": range(1, 8), "No": range(8, 36), "Exceptional No": range(36, 101)},
            9: {"Exceptional Yes": [], "Yes": range(1, 11), "No": range(11, 51), "Exceptional No": range(51, 101)}
        }
    }

    # Roll percentile dice (01-100) using a single d100
    roll = random.randint(1, 100)  # Direct 1d100 roll (1-100, treating 0 as 100)
    chaos_factor = min(max(chaos_factor, 1), 9)  # Ensure chaos_factor is between 1 and 9

    # Check for Random Event (simplified for 1d100: rolls that are multiples of 11 up to Chaos Factor * 11)
    # For Chaos 9, check rolls 11, 22, 33, 44, 55, 66, 77, 88, 99
    # Scale by Chaos Factor: only check rolls up to Chaos Factor * 11
    if roll in [i * 11 for i in range(1, chaos_factor + 1) if i * 11 <= 99]:
        return "Random Event", roll, None, None

    # Determine result based on likelihood and chaos factor
    ranges = fate_chart[likelihood][chaos_factor]
    if roll in ranges["Exceptional Yes"]:
        return "Exceptional YES", roll, None, None
    elif roll in ranges["Yes"]:
        return "Yes", roll, None, None
    elif roll in ranges["No"]:
        return "No", roll, None, None
    elif ranges["Exceptional No"]:  # Only check if Exceptional No exists (not empty)
        return "Exceptional NO", roll, None, None
    else:
        return "Impossible", roll, None, None  # Fallback for "X" cases

def select_from_list(data_manager, data_type):
    from data_manager import get_general_data
    items = get_general_data(data_manager, data_type)
    if not items:
        return "No items available"
    count = len(items)
    placeholder = "Choose character" if data_type == 'characters' else "Choose thread"
    total_slots = min((math.ceil(count / 5.0) * 5), 25)
    while len(items) < total_slots:
        items.append(placeholder)
    roll = random.randint(0, total_slots - 1)
    return items[roll]

def generate_action_oracle():
    if action_oracle_data is None:
        return "Error loading action oracle data."
    action1 = random.choice(action_oracle_data['action1'])
    action2 = random.choice(action_oracle_data['action2'])
    return f"Action Oracle: {action1} {action2}"

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

def generate_npc_age():
    age_categories = ["child", "adolescent", "young adult", "adult", "middle-aged", "senior"]
    weights = [4, 8, 25, 30, 20, 13]
    age_category = random.choices(age_categories, weights, k=1)[0]
    age_distribution = {
        "child": (0, 12), "adolescent": (13, 17), "young adult": (18, 24),
        "adult": (25, 44), "middle-aged": (45, 64), "senior": (65, 100)
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

def generate_themes(themes_listbox, weights):
    weighted_theme_selection = random.choices(themes_listbox, weights, k=5)
    theme_results = []
    for theme in weighted_theme_selection:
        d100_roll = random.randint(1, 100)
        _, plot_point = get_plot_point(theme, d100_roll)
        theme_results.append(f"Theme: {theme.capitalize()}, Plot Point: {plot_point}")
    return theme_results