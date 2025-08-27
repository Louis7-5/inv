import customtkinter as ctk
from tkinter import messagebox, Toplevel
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

def create_user(username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists."
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except Exception as e:
        return False, str(e)

def on_login():
    username = entry_username.get()
    password = entry_password.get() 
    if check_login(username, password):
        root.destroy()
        subprocess.Popen([sys.executable, "dashboard.py"])
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def open_create_account():
    root.destroy()  # Close the login window

    popup = ctk.CTk()  # Use CTk as the main window for create account
    popup.title("Create Account")
    popup.geometry("350x250")
    popup.resizable(True, True)
    try:
        popup.state('zoomed')  # Maximize window (Windows)
    except Exception:
        popup.attributes('-zoomed', True)  # Maximize window (Linux/Mac)

    ctk.CTkLabel(popup, text="Create New Account", font=("Consolas", 16, "bold")).pack(pady=(20, 10))
    ctk.CTkLabel(popup, text="Username:").pack(pady=(10, 2))
    new_username = ctk.CTkEntry(popup, width=180)
    new_username.pack()
    ctk.CTkLabel(popup, text="Password:").pack(pady=(10, 2))
    new_password = ctk.CTkEntry(popup, show="*", width=180)
    new_password.pack()
    ctk.CTkLabel(popup, text="Confirm Password:").pack(pady=(10, 2))
    confirm_password = ctk.CTkEntry(popup, show="*", width=180)
    confirm_password.pack()

    def submit():
        u = new_username.get()
        p = new_password.get()
        cp = confirm_password.get()
        if not u or not p:
            messagebox.showerror("Error", "All fields are required.", parent=popup)
            return
        if p != cp:
            messagebox.showerror("Error", "Passwords do not match.", parent=popup)
            return
        ok, msg = create_user(u, p)
        if ok:
            messagebox.showinfo("Success", msg, parent=popup)
            popup.destroy()
            # Re-open login window after successful registration
            subprocess.Popen([sys.executable, "signin.py"])
        else:
            messagebox.showerror("Error", msg, parent=popup)

    ctk.CTkButton(popup, text="Sign Up", command=submit, fg_color="#20bfa9", corner_radius=20, width=120).pack(pady=20)

    popup.mainloop()

root = ctk.CTk()
root.title("Login")
root.geometry("600x350")
root.resizable(True, True)  # Allow maximize

# Main container
main_frame = ctk.CTkFrame(root, fg_color="#f5f5f5")
main_frame.pack(fill="both", expand=True)

# Left panel (Welcome)
left_frame = ctk.CTkFrame(main_frame, width=220, fg_color="#20bfa9", corner_radius=0)
left_frame.pack(side="left", fill="y")
left_frame.pack_propagate(False)
ctk.CTkLabel(left_frame, text="Welcome Back!", font=("Consolas", 20, "bold"), text_color="#fff").pack(pady=(60, 10))
ctk.CTkLabel(left_frame, text="To keep connected with us please\nlogin with your personal info.", font=("Consolas", 12), text_color="#fff", justify="center").pack(pady=(0, 30))
ctk.CTkButton(left_frame, text="Sign In", fg_color="#fff", text_color="#20bfa9", hover_color="#e0f7f4", corner_radius=20, width=120).pack()

# Right panel (Login form)
right_frame = ctk.CTkFrame(main_frame, fg_color="#f5f5f5")
right_frame.pack(side="left", fill="both", expand=True, padx=(0, 0))
ctk.CTkLabel(right_frame, text="Sign In to Account", font=("Consolas", 18, "bold"), text_color="#20bfa9").pack(pady=(40, 10))

ctk.CTkLabel(right_frame, text="Username:", font=("Consolas", 12)).pack(pady=(10, 2))
entry_username = ctk.CTkEntry(right_frame, width=200)
entry_username.pack()

ctk.CTkLabel(right_frame, text="Password:", font=("Consolas", 12)).pack(pady=(15, 2))
entry_password = ctk.CTkEntry(right_frame, show="*", width=200)
entry_password.pack()

login_button = ctk.CTkButton(right_frame, text="Login", command=on_login, fg_color="#20bfa9", corner_radius=20, width=120)
login_button.pack(pady=(30, 10))

ctk.CTkButton(right_frame, text="Create Account", command=open_create_account, fg_color="#fff", text_color="#20bfa9", border_width=2, border_color="#20bfa9", corner_radius=20, width=120).pack()

root.mainloop()