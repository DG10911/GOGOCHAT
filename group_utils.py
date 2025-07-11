# group_utils.py
import json
import os

GROUP_FILE = 'groups.json'

if not os.path.exists(GROUP_FILE):
    with open(GROUP_FILE, 'w') as f:
        json.dump({}, f)

def load_group_data():
    with open(GROUP_FILE, 'r') as f:
        return json.load(f)

def save_group_data(data):
    with open(GROUP_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_group_code(code, group_name):
    data = load_group_data()
    data[code] = group_name
    save_group_data(data)

def get_group_name_from_code(code):
    data = load_group_data()
    return data.get(code)