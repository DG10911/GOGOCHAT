import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext, filedialog
import threading
import time
from datetime import datetime
from auth import login_user, signup_user
from protocol_utils import send_message, recv_message
import socket
import os
import subprocess
import platform

HOST = '127.0.0.1'
PORT = 12345

client = None
username = ""
downloads_dir = "downloads"
os.makedirs(downloads_dir, exist_ok=True)

def connect_to_server():
    global client
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        send_message(client, username)
        return True
    except Exception as e:
        messagebox.showerror("Connection Failed", f"Could not connect to server: {e}")
        return False

def welcome_screen():
    root = tk.Tk()
    root.title("Welcome to GoGo Chat")
    root.geometry("300x200")

    tk.Label(root, text="Welcome to GoGo Chat!", font=("Arial", 16)).pack(pady=20)
    tk.Button(root, text="Login", command=lambda: [root.destroy(), login_screen()]).pack(pady=5)
    tk.Button(root, text="Signup", command=lambda: [root.destroy(), signup_screen()]).pack(pady=5)
    root.mainloop()

def login_screen():
    win = tk.Tk()
    win.title("Login")
    win.geometry("300x200")

    tk.Label(win, text="Username").pack()
    user_entry = tk.Entry(win)
    user_entry.pack()

    tk.Label(win, text="Password").pack()
    pass_entry = tk.Entry(win, show="*")
    pass_entry.pack()

    def try_login():
        global username
        u = user_entry.get().strip()
        p = pass_entry.get().strip()
        if login_user(u, p):
            username = u
            win.destroy()
            if connect_to_server():
                home_screen()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    tk.Button(win, text="Login", command=try_login).pack(pady=10)
    tk.Button(win, text="Back", command=lambda: [win.destroy(), welcome_screen()]).pack()
    win.mainloop()

def signup_screen():
    win = tk.Tk()
    win.title("Signup")
    win.geometry("300x200")

    tk.Label(win, text="Username").pack()
    user_entry = tk.Entry(win)
    user_entry.pack()

    tk.Label(win, text="Password").pack()
    pass_entry = tk.Entry(win, show="*")
    pass_entry.pack()

    def try_signup():
        u = user_entry.get().strip()
        p = pass_entry.get().strip()
        if signup_user(u, p):
            messagebox.showinfo("Account Created", "Now login with your credentials.")
            win.destroy()
            login_screen()
        else:
            messagebox.showerror("Signup Failed", "Username may already exist.")

    tk.Button(win, text="Signup", command=try_signup).pack(pady=10)
    tk.Button(win, text="Back", command=lambda: [win.destroy(), welcome_screen()]).pack()
    win.mainloop()

def home_screen():
    home = tk.Tk()
    home.title("GoGo Chat Home")
    home.geometry("350x300")

    tk.Label(home, text=f"👤 {username}", font=("Arial", 14)).pack(pady=5)

    def start_private_chat():
        target = simpledialog.askstring("Private Chat", "Enter username to chat:")
        if target:
            open_chat_window(target)

    def logout():
        home.destroy()
        client.close()
        welcome_screen()

    tk.Button(home, text="1-to-1 Chat", width=25, command=start_private_chat).pack(pady=5)
    tk.Button(home, text="Logout", width=25, command=logout).pack(pady=20)
    home.mainloop()

def emoji_picker(entry_field):
    emoji_win = tk.Toplevel()
    emoji_win.title("Choose Emoji 😊")
    emoji_win.configure(bg="#1e1e2e")

    emoji_list = ['😊', '😂', '❤️', '🔥', '👍', '👌', '🎉', '😭', '😡', '💬', '🙌', '🤯', '😎']

    for em in emoji_list:
        tk.Button(
            emoji_win,
            text=em,
            font=("Arial", 16),
            width=3,
            command=lambda e=em: [entry_field.insert(tk.END, e), emoji_win.destroy()],
            bg="#2c2c3a",
            fg="white"
        ).pack(side=tk.LEFT, padx=4, pady=8)

def open_file(filepath):
    try:
        if platform.system() == "Darwin":  # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == "Windows":
            os.startfile(filepath)
        else:
            subprocess.call(('xdg-open', filepath))
    except Exception as e:
        messagebox.showerror("Error", f"Could not open file: {e}")

def open_chat_window(target_user):
    win = tk.Toplevel()
    win.title(f"Chat with {target_user}")
    win.geometry("600x500")
    win.configure(bg="#1e1e2e")

    top = tk.Frame(win, bg="#1e1e2e")
    top.pack(fill=tk.X)
    tk.Button(top, text="Back", command=win.destroy, bg="#444", fg="white").pack(side=tk.LEFT, padx=10)
    tk.Label(top, text=f"Chat with {target_user}", bg="#1e1e2e", fg="white", font=("Arial", 14)).pack()

    chat_area = scrolledtext.ScrolledText(win, wrap=tk.WORD, bg="#2c2c3a", fg="white", font=("Arial", 12))
    chat_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    chat_area.config(state='disabled')

    typing_label = tk.Label(win, text="", fg="lightgreen", bg="#1e1e2e")
    typing_label.pack()

    bottom = tk.Frame(win, bg="#1e1e2e")
    bottom.pack(fill=tk.X)

    entry = tk.Entry(bottom, font=("Arial", 12), width=40, bg="#2c2c3a", fg="white")
    entry.pack(side=tk.LEFT, padx=(10, 2))

    def display_message(sender, text, incoming=True):
        timestamp = datetime.now().strftime("%H:%M")
        ticks = "✓✓" if incoming else "✓"
        chat_area.config(state='normal')
        chat_area.insert(tk.END, f"{sender} ({timestamp}) {ticks}: {text}\n")
        chat_area.config(state='disabled')
        chat_area.see(tk.END)

    def notify_typing(event=None):
        send_message(client, f"TYPING:{target_user}")

    def send_file():
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)

        send_message(client, f"FILEUPLOAD:{target_user}")
        send_message(client, f"{filename}|{filesize}")

        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                client.sendall(chunk)

        display_message("You", f"📎 Sent file: {filename}", incoming=False)

    def handle_send():
        msg = entry.get().strip()
        if msg:
            send_message(client, f"1TO1:{target_user}:{msg}")
            display_message("You", msg, incoming=False)
            entry.delete(0, tk.END)

    entry.bind("<Key>", notify_typing)
    entry.bind("<Return>", lambda e: handle_send())

    tk.Button(bottom, text="📎", command=send_file, bg="#444", fg="white").pack(side=tk.LEFT, padx=3)
    tk.Button(bottom, text="😊", command=lambda: emoji_picker(entry), bg="#444", fg="white").pack(side=tk.LEFT)
    tk.Button(bottom, text="➔", command=handle_send, bg="red", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

    def receive():
        while True:
            try:
                msg = recv_message(client)

                if msg.startswith("TYPING:"):
                    _, typist = msg.split(":", 1)
                    typing_label.config(text=f"{typist}")
                    win.after(3000, lambda: typing_label.config(text=""))

                elif msg.startswith("MSG:"):
                    _, sender, text = msg.split(":", 2)
                    if sender == target_user:
                        display_message(sender, text)

                elif msg.startswith("FILE:"):
                    _, sender, filename, fsize = msg.split(":", 3)
                    file_info = recv_message(client)
                    fname, fsize = file_info.split("|")
                    fsize = int(fsize)

                    save_path = os.path.join(downloads_dir, fname)
                    with open(save_path, "wb") as f:
                        received = 0
                        while received < fsize:
                            chunk = client.recv(min(4096, fsize - received))
                            if not chunk:
                                break
                            f.write(chunk)
                            received += len(chunk)

                    display_message(sender, f"📎 Received file: {fname} (click to open)")
                    chat_area.tag_config(fname, foreground="cyan", underline=1)
                    chat_area.tag_bind(fname, "<Button-1>", lambda e, path=save_path: open_file(path))
                    chat_area.config(state='normal')
                    chat_area.insert(tk.END, f"\n")
                    start = chat_area.index("end-2l")
                    chat_area.insert(tk.END, f"{fname}\n", fname)
                    chat_area.config(state='disabled')

            except Exception as e:
                print(f"[RECEIVE ERROR] {e}")
                break

    threading.Thread(target=receive, daemon=True).start()

if __name__ == "__main__":
    welcome_screen()