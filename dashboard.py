import customtkinter
from db_connection import get_connection

class DashboardApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Dashboard")
        self.geometry("800x500")
        self.conn = get_connection()

        # Layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Navigation frame
        self.nav_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="ns")
        self.nav_frame.grid_rowconfigure(4, weight=1)

        self.title_label = customtkinter.CTkLabel(self.nav_frame, text="Inventory", font=customtkinter.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20)

        self.refresh_btn = customtkinter.CTkButton(self.nav_frame, text="Refresh", command=self.refresh_items)
        self.refresh_btn.grid(row=1, column=0, padx=20, pady=10)

        self.add_btn = customtkinter.CTkButton(self.nav_frame, text="Add Item", command=self.open_add_item_window)
        self.add_btn.grid(row=2, column=0, padx=20, pady=10)

        self.remove_btn = customtkinter.CTkButton(self.nav_frame, text="Remove Item", command=self.open_remove_item_window)
        self.remove_btn.grid(row=3, column=0, padx=20, pady=10)

        # Main frame
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Table for items
        self.items_table = customtkinter.CTkTextbox(self.main_frame, width=600, height=400, font=("Consolas", 12))
        self.items_table.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.items_table.configure(state="disabled")

        self.refresh_items()

    # Refresh items from the database and display in the table
    def refresh_items(self):
        self.items_table.configure(state="normal")
        self.items_table.delete("1.0", "end")
        cursor = self.conn.cursor()
        cursor.execute("SELECT item_id, name, quantity, price FROM items")
        rows = cursor.fetchall()
        self.items_table.insert("end", f"{'ID':<10}{'Name':<20}{'Qty':<10}{'Price':<10}\n")
        self.items_table.insert("end", "-"*50 + "\n")
        for row in rows:
            self.items_table.insert("end", f"{row[0]:<10}{row[1]:<20}{row[2]:<10}{row[3]:<10.2f}\n")
        self.items_table.configure(state="disabled")

    # add item window
    def open_add_item_window(self):
        win = customtkinter.CTkToplevel(self)
        win.title("Add Item")
        win.geometry("300x300")

        customtkinter.CTkLabel(win, text="Item ID:").pack(pady=5)
        id_entry = customtkinter.CTkEntry(win)
        id_entry.pack(pady=5)

        customtkinter.CTkLabel(win, text="Name:").pack(pady=5)
        name_entry = customtkinter.CTkEntry(win)
        name_entry.pack(pady=5)

        customtkinter.CTkLabel(win, text="Quantity:").pack(pady=5)
        qty_entry = customtkinter.CTkEntry(win)
        qty_entry.pack(pady=5)

        customtkinter.CTkLabel(win, text="Price:").pack(pady=5)
        price_entry = customtkinter.CTkEntry(win)
        price_entry.pack(pady=5)

        def add_item():
            item_id = id_entry.get()
            name = name_entry.get()
            try:
                quantity = int(qty_entry.get())
                price = float(price_entry.get())
            except ValueError:
                return
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO items (item_id, name, quantity, price)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=%s, quantity=%s, price=%s
            """, (item_id, name, quantity, price, name, quantity, price))
            self.conn.commit()
            win.destroy()
            self.refresh_items()

        customtkinter.CTkButton(win, text="Add", command=add_item).pack(pady=20)

    # remove item window
    def open_remove_item_window(self):
        win = customtkinter.CTkToplevel(self)
        win.title("Remove Item")
        win.geometry("300x150")

        customtkinter.CTkLabel(win, text="Item ID:").pack(pady=5)
        id_entry = customtkinter.CTkEntry(win)
        id_entry.pack(pady=5)

        customtkinter.CTkLabel(win, text="Quantity to Remove:").pack(pady=5)
        qty_entry = customtkinter.CTkEntry(win)
        qty_entry.pack(pady=5)

        def remove_item():
            item_id = id_entry.get()
            try:
                quantity = int(qty_entry.get())
            except ValueError:
                return
            cursor = self.conn.cursor()
            cursor.execute("SELECT quantity FROM items WHERE item_id = %s", (item_id,))
            result = cursor.fetchone()
            if result:
                new_qty = result[0] - quantity
                if new_qty <= 0:
                    cursor.execute("DELETE FROM items WHERE item_id = %s", (item_id,))
                else:
                    cursor.execute("UPDATE items SET quantity = %s WHERE item_id = %s", (new_qty, item_id))
                self.conn.commit()
            win.destroy()
            self.refresh_items()

        customtkinter.CTkButton(win, text="Remove", command=remove_item).pack(pady=20)

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()
