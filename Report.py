import customtkinter as ctk
from tkinter import ttk, messagebox
import datetime
from db_connection import get_connection

class ReportApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Reports")
        self.geometry("900x600")
        self.conn = get_connection()

        # Title
        ctk.CTkLabel(self, text="Inventory Management Reports", font=("Consolas", 22, "bold")).pack(pady=20)

        # Date Range Selection
        date_frame = ctk.CTkFrame(self)
        date_frame.pack(pady=10)
        ctk.CTkLabel(date_frame, text="Start Date:").pack(side="left", padx=5)
        self.start_entry = ctk.CTkEntry(date_frame, width=120)
        self.start_entry.pack(side="left", padx=5)
        ctk.CTkLabel(date_frame, text="End Date:").pack(side="left", padx=5)
        self.end_entry = ctk.CTkEntry(date_frame, width=120)
        self.end_entry.pack(side="left", padx=5)
        today = datetime.date.today()
        week_ago = today - datetime.timedelta(days=7)
        self.start_entry.insert(0, week_ago.strftime("%Y-%m-%d"))
        self.end_entry.insert(0, today.strftime("%Y-%m-%d"))
        ctk.CTkButton(date_frame, text="Generate Report", command=self.generate_report).pack(side="left", padx=10)

        # Tabs for Summary and Detailed
        tabview = ctk.CTkTabview(self, width=850, height=450)
        tabview.pack(pady=20, expand=True, fill="both")
        self.summary_tab = tabview.add("Summary Report")
        self.detailed_tab = tabview.add("Detailed Report")

        # Summary Table
        self.summary_tree = ttk.Treeview(self.summary_tab, columns=("Metric", "Value"), show="headings", height=15)
        self.summary_tree.heading("Metric", text="Metric")
        self.summary_tree.heading("Value", text="Value")
        self.summary_tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Detailed Table
        self.detailed_tree = ttk.Treeview(self.detailed_tab, columns=("Date", "Product", "Type", "Qty", "Price", "Amount"), show="headings", height=15)
        for col in ("Date", "Product", "Type", "Qty", "Price", "Amount"):
            self.detailed_tree.heading(col, text=col)
        self.detailed_tree.pack(expand=True, fill="both", padx=10, pady=10)

    def generate_report(self):
        start_date = self.start_entry.get()
        end_date = self.end_entry.get()
        try:
            cursor = self.conn.cursor()

            # Summary Report
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN type='Purchase' THEN quantity*price ELSE 0 END) AS Total_Purchase,
                    SUM(CASE WHEN type='Sale' THEN quantity*price ELSE 0 END) AS Total_Sale,
                    SUM(CASE WHEN type='Sale' THEN quantity*price ELSE 0 END) - 
                    SUM(CASE WHEN type='Purchase' THEN quantity*price ELSE 0 END) AS Profit,
                    SUM(CASE WHEN type='Purchase' THEN quantity ELSE 0 END) AS Total_Purchased_Qty,
                    SUM(CASE WHEN type='Sale' THEN quantity ELSE 0 END) AS Total_Sold_Qty
                FROM transactions
                WHERE date BETWEEN %s AND %s
            """, (start_date, end_date))
            summary = cursor.fetchone()

            self.summary_tree.delete(*self.summary_tree.get_children())
            metrics = [
                ("Total Purchase Amount", summary[0] or 0),
                ("Total Sale Amount", summary[1] or 0),
                ("Profit", summary[2] or 0),
                ("Total Purchased Quantity", summary[3] or 0),
                ("Total Sold Quantity", summary[4] or 0),
            ]
            for metric, value in metrics:
                self.summary_tree.insert("", "end", values=(metric, f"{value:,.2f}" if isinstance(value, (float, int)) else value))

            # Detailed Report
            cursor.execute("""
                SELECT date, product, type, quantity, price, quantity*price as amount
                FROM transactions
                WHERE date BETWEEN %s AND %s
                ORDER BY date DESC
            """, (start_date, end_date))
            rows = cursor.fetchall()
            self.detailed_tree.delete(*self.detailed_tree.get_children())
            for row in rows:
                self.detailed_tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{e}")

if __name__ == "__main__":
    app = ReportApp()
    app.mainloop()