import customtkinter as ctk
from tkinter import messagebox
import subprocess
import sys
from db_connection import get_connection

def check_login(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return False

def on_login():
    username = entry_username.get()
    password = entry_password.get() 
    if check_login(username, password):
        root.destroy()
        subprocess.Popen([sys.executable, "main.py"])  # Changed from dashboard.py to main.py
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# UI setup
root = ctk.CTk()
root.title("Login")
root.geometry("400x350")

label_username = ctk.CTkLabel(root, text="Username:")
label_username.pack(pady=(59, 25))
entry_username = ctk.CTkEntry(root)
entry_username.pack()

label_password = ctk.CTkLabel(root, text="Password:")
label_password.pack(pady=(30, 25))
entry_password = ctk.CTkEntry(root, show="*")
entry_password.pack()

login_button = ctk.CTkButton(root, text="Login", command=on_login)
login_button.pack(pady=40)

root.mainloop()