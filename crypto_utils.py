from cryptography.fernet import Fernet

# Fixed key for both server and client
key = b'CC6ZcJz3zMcKFWuI5G0h4E8aJHinVQLDazYzIRssV1E='
cipher = Fernet(key)

def encrypt(message):
    return cipher.encrypt(message.encode())

def decrypt(token):
    return cipher.decrypt(token).decode()