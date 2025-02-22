import json
import os

class DataManager:
    def __init__(self):
        self.data = {"characters": [], "threads": []}

    def add_item(self, data_type, item):
        item = item.strip()
        if not item or item in ["Choose character", "Choose thread"]:
            return False
        if data_type not in self.data:
            self.data[data_type] = []
        if len(self.data[data_type]) < 25 and self.data[data_type].count(item) < 3:
            self.data[data_type].append(item)
            self.data[data_type].sort()
            return True
        return False

    def get_items(self, data_type):
        return sorted(self.data.get(data_type, []))

    def remove_item(self, data_type, item):
        if data_type in self.data and item in self.data[data_type]:
            self.data[data_type].remove(item)

    def load_from_file(self, file_path):
        if not file_path:
            return False
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                loaded_data = json.load(file)
                self.data.clear()
                self.data.update(loaded_data)
                return True
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(f"Error loading {file_path}: {e}")
            return False

    def save_to_file(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump({k: sorted(v) for k, v in self.data.items()}, file, indent=4)
                return True
        except IOError as e:
            print(f"Error saving {file_path}: {e}")
            return False

# Remove the global data_manager instance
# data_manager = DataManager()

# Update functions to accept a data_manager parameter
def add_to_general_data(data_manager, data_type, item):
    return data_manager.add_item(data_type, item)

def remove_from_general_data(data_manager, data_type, item):
    data_manager.remove_item(data_type, item)

def get_general_data(data_manager, data_type):
    return data_manager.get_items(data_type)

def load_campaign(data_manager, file_path):
    return data_manager.load_from_file(file_path)

def save_campaign(data_manager, file_path):
    return data_manager.save_to_file(file_path)

def load_json_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"Error loading {file_path}: {e}")
        return None