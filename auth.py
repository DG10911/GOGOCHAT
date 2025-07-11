import os

USER_DB = "users.txt"

def load_users():
    users = {}
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            for line in f:
                username, password = line.strip().split(":")
                users[username] = password
    return users

def login_user(username, password):
    users = load_users()
    return username in users and users[username] == password

def signup_user(username, password):
    users = load_users()
    if username in users:
        return False  # Username already taken
    with open(USER_DB, "a") as f:
        f.write(f"{username}:{password}\n")
    return True