import customtkinter
from db_connection import get_connection
import tkinter.ttk as ttk
import datetime
import threading

class MetricsFrame(customtkinter.CTkFrame):
    def __init__(self, parent, conn, show_inventory_callback):
        super().__init__(parent)
        self.conn = conn
        self.show_inventory_callback = show_inventory_callback

        # Title with background color
        title_frame = customtkinter.CTkFrame(self, fg_color="#226622")
        title_frame.pack(fill="x")
        customtkinter.CTkLabel(
            title_frame, text="Inventory Management System",
            font=("Consolas", 20, "bold"), text_color="#fff", bg_color="#226622"
        ).pack(pady=10)

        # Date Range Frame with current dates and rounded corners
        date_frame = customtkinter.CTkFrame(self, fg_color="#f5f5f5", corner_radius=12)
        date_frame.pack(fill="x", padx=20, pady=(10, 10))
        today = datetime.date.today()
        week_ago = today - datetime.timedelta(days=7)
        customtkinter.CTkLabel(date_frame, text="Start Date").pack(side="left", padx=5)
        self.start_entry = customtkinter.CTkEntry(date_frame, width=100)
        self.start_entry.insert(0, week_ago.strftime("%Y-%m-%d"))
        self.start_entry.pack(side="left", padx=5)
        customtkinter.CTkLabel(date_frame, text="End Date").pack(side="left", padx=5)
        self.end_entry = customtkinter.CTkEntry(date_frame, width=100)
        self.end_entry.insert(0, today.strftime("%Y-%m-%d"))
        self.end_entry.pack(side="left", padx=5)
        customtkinter.CTkButton(date_frame, text="Refresh", command=self.refresh_metrics, fg_color="#20bfa9", corner_radius=10).pack(side="left", padx=10)
        customtkinter.CTkButton(date_frame, text="Product Master", command=self.show_inventory_callback, fg_color="#4B0082", corner_radius=10).pack(side="right", padx=5)
        customtkinter.CTkButton(date_frame, text="Save", command=self.save_metrics, fg_color="#8B0000", corner_radius=10).pack(side="right", padx=5)

        # Metrics Cards Frame with border, clickable, and flash animation
        self.cards_frame = customtkinter.CTkFrame(self, fg_color="#f5f5f5")
        self.cards_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.card_labels = []
        self.card_frames = []
        card_data = [
            ("Purchase", "16368.51", "#8B0000"),
            ("Sale", "7740.35", "#BDB76B"),
            ("Profit", "2319.98", "#228B22"),
            ("Inventory Qty.", "572", "#4B0082"),
            ("Inventory Amt.", "15688.50", "#2F4F4F"),
        ]
        for idx, (label, value, color) in enumerate(card_data):
            card = customtkinter.CTkFrame(
                self.cards_frame, fg_color=color, width=120, height=60, corner_radius=15, border_width=3, border_color="#fff"
            )
            card.pack(side="left", padx=10, pady=8, fill="y", expand=True)
            value_label = customtkinter.CTkLabel(card, text=value, font=("Consolas", 18, "bold"), text_color="#fff")
            value_label.pack(pady=(10, 0))
            customtkinter.CTkLabel(card, text=label, font=("Consolas", 12), text_color="#fff").pack(pady=(0, 10))
            self.card_labels.append(value_label)
            self.card_frames.append(card)
            card.bind("<Button-1>", lambda e, i=idx: self.flash_card(i))

        # Main Content Frame (1 column, no graphs)
        main_frame = customtkinter.CTkFrame(self, fg_color="#f8f8fa")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Product Transactions (only Product ID, no Sale/Purchase)
        trans_frame = customtkinter.CTkFrame(main_frame, fg_color="#f5f5f5", corner_radius=12)
        trans_frame.pack(fill="both", expand=True, padx=10, pady=10)
        customtkinter.CTkLabel(trans_frame, text="Product Transactions: Add/Update", font=("Consolas", 14, "bold"), text_color="#226622").pack(pady=5)
        form_frame = customtkinter.CTkFrame(trans_frame, fg_color="#e9f7f6", corner_radius=10)
        form_frame.pack(fill="x", padx=5, pady=5)

        # Product ID search and dropdown (searchable, picks from inventory)
        customtkinter.CTkLabel(form_frame, text="Product ID").grid(row=0, column=0, padx=2, pady=2)
        self.product_search = customtkinter.CTkEntry(form_frame, width=80)
        self.product_search.grid(row=0, column=1, padx=2, pady=2)
        self.product_search.bind("<KeyRelease>", self.update_product_combo)
        self.product_combo = customtkinter.CTkComboBox(form_frame, width=120, values=self.get_product_id_list())
        self.product_combo.grid(row=0, column=2, padx=2, pady=2)

        customtkinter.CTkLabel(form_frame, text="Qty.").grid(row=0, column=3, padx=2, pady=2)
        self.qty_entry = customtkinter.CTkEntry(form_frame, width=40)
        self.qty_entry.grid(row=0, column=4, padx=2, pady=2)
        customtkinter.CTkLabel(form_frame, text="Date").grid(row=0, column=5, padx=2, pady=2)
        self.date_entry = customtkinter.CTkEntry(form_frame, width=80)
        self.date_entry.insert(0, today.strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=6, padx=2, pady=2)
        customtkinter.CTkLabel(form_frame, text="Rate").grid(row=1, column=0, padx=2, pady=2)
        self.rate_entry = customtkinter.CTkEntry(form_frame, width=40)
        self.rate_entry.grid(row=1, column=1, padx=2, pady=2)
        customtkinter.CTkButton(form_frame, text="Add", width=60, fg_color="#228B22", command=self.add_transaction, corner_radius=10).grid(row=1, column=2, padx=2, pady=2)
        customtkinter.CTkButton(form_frame, text="Update", width=60, fg_color="#BDB76B", command=self.update_transaction, corner_radius=10).grid(row=1, column=3, padx=2, pady=2)

        # Show Transactions
        filter_frame = customtkinter.CTkFrame(trans_frame, fg_color="#f5f5f5")
        filter_frame.pack(fill="x", padx=5, pady=5)
        customtkinter.CTkLabel(filter_frame, text="Show Transactions:").pack(side="left", padx=2)
        self.trans_filter = customtkinter.StringVar(value="ALL")
        all_radio = customtkinter.CTkRadioButton(filter_frame, text="ALL", variable=self.trans_filter, value="ALL", command=self.refresh_transactions)
        all_radio.pack(side="left", padx=2)
        customtkinter.CTkButton(filter_frame, text="Extract", width=60, fg_color="#20bfa9", command=self.extract_transactions, corner_radius=10).pack(side="left", padx=10)

        # Transactions Table
        self.trans_table = customtkinter.CTkTextbox(trans_frame, width=300, height=200, font=("Consolas", 11))
        self.trans_table.pack(fill="both", expand=True, padx=5, pady=5)
        self.refresh_transactions()

    def flash_card(self, idx):
        card = self.card_frames[idx]
        orig_color = card._fg_color
        flash_color = "#FFD700"  # Gold
        def do_flash():
            card.configure(fg_color=flash_color)
            card.after(150, lambda: card.configure(fg_color=orig_color))
        threading.Thread(target=do_flash).start()
        # You can add more actions here, e.g., show a messagebox or open a detail window

    def refresh_metrics(self):
        # Dummy: update card values, you can fetch from DB here
        values = ["16368.51", "7740.35", "2319.98", "572", "15688.50"]
        for lbl, val in zip(self.card_labels, values):
            lbl.configure(text=val)
        self.plot_stock_graph(self.winfo_children()[2].winfo_children()[0])  # update graph
        self.refresh_transactions()

    def save_metrics(self):
        import tkinter.messagebox as mb
        mb.showinfo("Save", "Metrics saved (dummy action).")

    def get_product_id_list(self, search=""):
        cursor = self.conn.cursor()
        if search:
            cursor.execute("SELECT item_id FROM items WHERE item_id LIKE %s", (f"%{search}%",))
        else:
            cursor.execute("SELECT item_id FROM items")
        products = [str(row[0]) for row in cursor.fetchall()]
        return products if products else ["No Products"]

    def update_product_combo(self, event=None):
        search = self.product_search.get()
        products = self.get_product_id_list(search)
        self.product_combo.configure(values=products)
        if products:
            self.product_combo.set(products[0])

    def refresh_transactions(self):
        self.trans_table.configure(state="normal")
        self.trans_table.delete("1.0", "end")
        self.trans_table.insert("end", f"{'Product ID':<12}{'Quantity':<8}{'Price':<8}{'Amount':<10}{'Date':<12}\n")
        self.trans_table.insert("end", "-"*50 + "\n")
        # Example: dummy data, you can fetch from DB
        for i in range(1, 10):
            product_id = f"P{i:03d}"
            qty = 10 + i
            price = 20.0 + i
            amount = qty * price
            self.trans_table.insert("end", f"{product_id:<12}{qty:<8}{price:<8.2f}{amount:<10.2f}{datetime.date.today().strftime('%Y-%m-%d')}\n")
        self.trans_table.configure(state="disabled")

    def extract_transactions(self):
        import tkinter.messagebox as mb
        mb.showinfo("Extract", "Transactions extracted (dummy action).")

    def add_transaction(self):
        import tkinter.messagebox as mb
        mb.showinfo("Add", "Transaction added (dummy action).")

    def update_transaction(self):
        import tkinter.messagebox as mb
        mb.showinfo("Update", "Transaction updated (dummy action).")

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

class LogoutFrame(customtkinter.CTkFrame):
    def __init__(self, parent, logout_callback):
        super().__init__(parent)
        customtkinter.CTkLabel(self, text="Are you sure you want to logout?", font=("Consolas", 16)).pack(pady=30)
        btn_frame = customtkinter.CTkFrame(self)
        btn_frame.pack(pady=10)
        customtkinter.CTkButton(btn_frame, text="Logout", command=logout_callback).pack(side="left", padx=10)

class MetricsDashboard(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management Dashboard")
        self.geometry("900x600")
        self.conn = get_connection()

        # Navigation
        nav_frame = customtkinter.CTkFrame(self)
        nav_frame.pack(side="left", fill="y", padx=10, pady=10)

        content_frame = customtkinter.CTkFrame(self)
        content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.frames = {}

        def show_frame(name):
            for f in self.frames.values():
                f.pack_forget()
            self.frames[name].pack(fill="both", expand=True)

        btn_metrics = customtkinter.CTkButton(nav_frame, text="Metrics", command=lambda: show_frame("metrics"))
        btn_metrics.pack(pady=10, fill="x")
        btn_inventory = customtkinter.CTkButton(nav_frame, text="Inventory", command=lambda: show_frame("inventory"))
        btn_inventory.pack(pady=10, fill="x")
        btn_suppliers = customtkinter.CTkButton(nav_frame, text="Suppliers", command=lambda: show_frame("suppliers"))
        btn_suppliers.pack(pady=10, fill="x")
        btn_reports = customtkinter.CTkButton(nav_frame, text="Reports", command=lambda: show_frame("reports"))
        btn_reports.pack(pady=10, fill="x")
        btn_logout = customtkinter.CTkButton(nav_frame, text="Logout", command=lambda: show_frame("logout"))
        btn_logout.pack(pady=10, fill="x")

        self.frames["metrics"] = MetricsFrame(
            content_frame,
            self.conn,
            lambda: [self.frames["inventory"].refresh_items(), show_frame("inventory")]
        )
        self.frames["inventory"] = InventoryFrame(content_frame, self.conn, lambda: self.frames["inventory"].refresh_items())
        self.frames["suppliers"] = SuppliersFrame(content_frame, self.conn)
        self.frames["reports"] = ReportFrame(content_frame, self.conn)  # <-- Add this line

        import sys
        import subprocess
        def logout():
            self.destroy()
            subprocess.Popen([sys.executable, "signin.py"])

        self.frames["logout"] = LogoutFrame(content_frame, logout)

        show_frame("metrics")

class ReportFrame(customtkinter.CTkFrame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn

        customtkinter.CTkLabel(self, text="Inventory Reports", font=("Consolas", 18, "bold")).pack(pady=20)

        # Tabs for Summary and Detailed
        tabview = customtkinter.CTkTabview(self, width=800, height=400)
        tabview.pack(pady=10, expand=True, fill="both")
        self.summary_tab = tabview.add("Summary Report")
        self.detailed_tab = tabview.add("Detailed Report")

        # Summary Frame
        summary_frame = customtkinter.CTkFrame(self.summary_tab)
        summary_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.summary_table = customtkinter.CTkTextbox(summary_frame, width=700, height=300, font=("Consolas", 12))
        self.summary_table.pack(fill="both", expand=True)
        self.summary_table.configure(state="disabled")
        customtkinter.CTkButton(summary_frame, text="Refresh Summary", command=self.refresh_summary).pack(pady=10)

        # Detailed Frame
        detailed_frame = customtkinter.CTkFrame(self.detailed_tab)
        detailed_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.detailed_table = customtkinter.CTkTextbox(detailed_frame, width=700, height=300, font=("Consolas", 12))
        self.detailed_table.pack(fill="both", expand=True)
        self.detailed_table.configure(state="disabled")
        customtkinter.CTkButton(detailed_frame, text="Refresh Detailed", command=self.refresh_detailed).pack(pady=10)

        self.refresh_summary()
        self.refresh_detailed()

    def refresh_summary(self):
        self.summary_table.configure(state="normal")
        self.summary_table.delete("1.0", "end")
        cursor = self.conn.cursor()
        # Inventory summary: total value, total quantity, number of products
        cursor.execute("SELECT COUNT(*), SUM(quantity), SUM(quantity * price) FROM items")
        count, total_qty, total_value = cursor.fetchone()
        metrics = [
            ("Number of Products", count or 0),
            ("Total Inventory Quantity", total_qty or 0),
            ("Total Inventory Value", total_value or 0),
        ]
        self.summary_table.insert("end", f"{'Metric':<30}{'Value':>20}\n")
        self.summary_table.insert("end", "-"*50 + "\n")
        for metric, value in metrics:
            if isinstance(value, float):
                self.summary_table.insert("end", f"{metric:<30}{value:>20,.2f}\n")
            else:
                self.summary_table.insert("end", f"{metric:<30}{value:>20}\n")
        self.summary_table.configure(state="disabled")

    def refresh_detailed(self):
        self.detailed_table.configure(state="normal")
        self.detailed_table.delete("1.0", "end")
        cursor = self.conn.cursor()
        cursor.execute("SELECT item_id, name, quantity, price, quantity*price as value FROM items ORDER BY name")
        rows = cursor.fetchall()
        self.detailed_table.insert("end", f"{'ID':<8}{'Name':<25}{'Qty':<10}{'Price':<12}{'Value':<15}\n")
        self.detailed_table.insert("end", "-"*70 + "\n")
        for row in rows:
            self.detailed_table.insert("end", f"{row[0]:<8}{row[1]:<25}{row[2]:<10}{row[3]:<12.2f}{row[4]:<15.2f}\n")
        self.detailed_table.configure(state="disabled")

if __name__ == "__main__":
    app = MetricsDashboard()
    app.mainloop()
