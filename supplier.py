from datetime import datetime
import tkinter as tk

class Supplier:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.created_at = datetime.now()

    def show_info(self):
        print(f"Supplier Name: {self.name}")
        print(f"Balance: {self.balance}")
        print(f"Date Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

def show_dashboard(supplier):
    dashboard = tk.Toplevel()  # Open a new window
    dashboard.title("Supplier Dashboard")

    # Create frames for organization
    info_frame = tk.Frame(dashboard, padx=10, pady=10, relief=tk.RIDGE, borderwidth=2)
    info_frame.pack(padx=10, pady=10, fill='both', expand=True)

    tk.Label(info_frame, text=f"Supplier Name: {supplier.name}", font=("Arial", 12)).pack(pady=5)
    tk.Label(info_frame, text=f"Balance: {supplier.balance}", font=("Arial", 12)).pack(pady=5)
    tk.Label(info_frame, text=f"Date Created: {supplier.created_at.strftime('%Y-%m-%d %H:%M:%S')}", font=("Arial", 12)).pack(pady=5)

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    supplier = Supplier("Acme Corp", 1500.75)
    show_dashboard(supplier)

    root.mainloop()

# Example usage:
if __name__ == "__main__":
    main()