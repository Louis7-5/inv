import customtkinter
from db_connection import get_connection
import tkinter.ttk as ttk

class MetricsFrame(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        customtkinter.CTkLabel(self, text="Metrics Page", font=("Consolas", 16)).pack(pady=20)
        # Add metrics widgets here

class InventoryFrame(customtkinter.CTkFrame):
    def __init__(self, parent, conn, refresh_callback):
        super().__init__(parent)
        self.conn = conn
        self.refresh_callback = refresh_callback

        # Table for items
        self.items_table = customtkinter.CTkTextbox(self, width=600, height=300, font=("Consolas", 12))
        self.items_table.pack(padx=20, pady=10, fill="both", expand=True)
        self.items_table.configure(state="disabled")

        btn_frame = customtkinter.CTkFrame(self)
        btn_frame.pack(pady=10)

        customtkinter.CTkButton(btn_frame, text="Refresh", command=self.refresh_items).pack(side="left", padx=5)
        customtkinter.CTkButton(btn_frame, text="Add Item", command=self.open_add_item_window).pack(side="left", padx=5)
        customtkinter.CTkButton(btn_frame, text="Remove Item", command=self.open_remove_item_window).pack(side="left", padx=5)

        self.refresh_items()

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

class SuppliersFrame(customtkinter.CTkFrame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn

        customtkinter.CTkLabel(self, text="Suppliers Page", font=("Consolas", 16)).pack(pady=20)

        # Table for suppliers using ttk.Treeview
        columns = ("id", "name", "address", "contacts", "date", "supplies")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

        btn_frame = customtkinter.CTkFrame(self)
        btn_frame.pack(pady=10)

        customtkinter.CTkButton(btn_frame, text="Refresh", command=self.refresh_suppliers).pack(side="left", padx=5)
        customtkinter.CTkButton(btn_frame, text="Add Supplier", command=self.open_add_supplier_window).pack(side="left", padx=5)
        customtkinter.CTkButton(btn_frame, text="Remove Supplier", command=self.open_remove_supplier_window).pack(side="left", padx=5)

        self.refresh_suppliers()

    def refresh_suppliers(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, address, contacts, date, supplies FROM suppliers")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def open_add_supplier_window(self):
        win = customtkinter.CTkToplevel(self)
        win.title("Add Supplier")
        win.geometry("350x400")

        labels = ["Supplier ID:", "Name:", "Address:", "Contacts:", "Date (YYYY-MM-DD):", "Supplies:"]
        entries = []
        for label in labels:
            customtkinter.CTkLabel(win, text=label).pack(pady=5)
            entry = customtkinter.CTkEntry(win)
            entry.pack(pady=5)
            entries.append(entry)

        def add_supplier():
            try:
                id = entries[0].get()
                name = entries[1].get()
                address = entries[2].get()
                contacts = entries[3].get()
                date = entries[4].get()
                supplies = entries[5].get()
            except Exception:
                return
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO suppliers (id, name, address, contacts, date, supplies)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=%s, address=%s, contacts=%s, date=%s, supplies=%s
            """, (id, name, address, contacts, date, supplies, name, address, contacts, date, supplies))
            self.conn.commit()
            win.destroy()
            self.refresh_suppliers()

        customtkinter.CTkButton(win, text="Add", command=add_supplier).pack(pady=20)

    def open_remove_supplier_window(self):
        win = customtkinter.CTkToplevel(self)
        win.title("Remove Supplier")
        win.geometry("300x150")

        customtkinter.CTkLabel(win, text="Supplier ID:").pack(pady=5)
        id_entry = customtkinter.CTkEntry(win)
        id_entry.pack(pady=5)

        def remove_supplier():
            id = id_entry.get()
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM suppliers WHERE id = %s", (id,))
            self.conn.commit()
            win.destroy()
            self.refresh_suppliers()

        customtkinter.CTkButton(win, text="Remove", command=remove_supplier).pack(pady=20)

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

        self.metrics_btn = customtkinter.CTkButton(self.nav_frame, text="Metrics", command=lambda: self.show_frame("metrics"))
        self.metrics_btn.grid(row=1, column=0, padx=20, pady=10)

        self.inventory_btn = customtkinter.CTkButton(self.nav_frame, text="Inventory", command=lambda: self.show_frame("inventory"))
        self.inventory_btn.grid(row=2, column=0, padx=20, pady=10)

        self.suppliers_btn = customtkinter.CTkButton(self.nav_frame, text="Suppliers", command=lambda: self.show_frame("suppliers"))
        self.suppliers_btn.grid(row=3, column=0, padx=20, pady=10)

        # Main frame
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Page frames
        self.frames = {}
        self.frames["metrics"] = MetricsFrame(self.main_frame)
        self.frames["inventory"] = InventoryFrame(self.main_frame, self.conn, self.show_frame)
        self.frames["suppliers"] = SuppliersFrame(self.main_frame, self.conn)

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
            frame.grid_remove()

        self.show_frame("metrics")

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.grid_remove()
        self.frames[name].grid()

if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()
