import json
import hashlib
from datetime import datetime
import os

# File path for users.json
USERS_FILE = 'users.json'

# Create users.json if it doesn't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({"users": []}, f, indent=4)

# Load users from JSON
def load_users():
    with open(USERS_FILE, 'r',encoding='utf-8') as f:
        return json.load(f)

# Save users to JSON
def save_users(data):
    with open(USERS_FILE, 'w',encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# Hash the password using MD5
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Add a new user
def add_user():
    username = input("Enter username: ").strip()
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()

    users_data = load_users()

    # Check if username already exists
    for user in users_data['users']:
        if user['username'] == username:
            print("❌ Username already exists.")
            return

    new_user = {
        "username": username,
        "password": hash_password(password),
        "email": email,
        "created_at": datetime.now().isoformat(),
        "is_active": True,
        "last_login": None
    }

    users_data['users'].append(new_user)
    save_users(users_data)
    print("✅ User registered successfully.")

# Run the program
add_user()