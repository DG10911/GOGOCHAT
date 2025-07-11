# group_codes.py

import json
import os

GROUP_CODES_FILE = "group_codes.json"

# Ensure file exists
if not os.path.exists(GROUP_CODES_FILE):
    with open(GROUP_CODES_FILE, "w") as f:
        json.dump({}, f)

def save_code(code, group_name):
    codes = load_codes()
    codes[code] = group_name
    with open(GROUP_CODES_FILE, "w") as f:
        json.dump(codes, f, indent=4)

def get_group_by_code(code):
    codes = load_codes()
    return codes.get(code)

def load_codes():
    with open(GROUP_CODES_FILE, "r") as f:
        return json.load(f)