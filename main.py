import mysql.connector
from mysql.connector import Error
from db_connection import get_connection

class Item:
    def __init__(self, item_id, name, quantity, price, category=None):
        self.item_id = item_id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.category = category

class Inventory:
    def __init__(self):
        self.items = {}
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="inventory_db"
        )
        # self.create_table()
        self.load_items()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                item_id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                quantity INT,
                price FLOAT
            )
        """)
        self.conn.commit()

    def load_items(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT item_id, name, quantity, price FROM items")
        for row in cursor.fetchall():
            item = Item(row[0], row[1], row[2], row[3], None)
            self.items[item.item_id] = item
            print(f"ID: {item.item_id}, Name: {item.name}, Quantity: {item.quantity}, Price: {item.price}")

    def add_item(self, item):
        self.items[item.item_id] = item
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO items (item_id, name, quantity, price)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name=%s, quantity=%s, price=%s
        """, (item.item_id, item.name, item.quantity, item.price, item.name, item.quantity, item.price))
        self.conn.commit()

    def remove_item(self, item_id, quantity):
        if item_id in self.items:
            self.items[item_id].quantity -= quantity
            cursor = self.conn.cursor()
            if self.items[item_id].quantity <= 0:
                del self.items[item_id]
                cursor.execute("DELETE FROM items WHERE item_id = %s", (item_id,))
            else:
                cursor.execute("UPDATE items SET quantity = %s WHERE item_id = %s",
                               (self.items[item_id].quantity, item_id))
            self.conn.commit()

    def display_inventory(self):
        if not self.items:
            print("Inventory is empty.")
        for item in self.items.values():
            print(f"ID: {item.item_id}, Name: {item.name}, Quantity: {item.quantity}, Price: {item.price}")

    def get_inventory_value(self):
        return sum(item.quantity * item.price for item in self.items.values())

def fetch_items():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        items = cursor.fetchall()
        conn.close()
        return items
    except Exception as e:
        print("Database Error:", e)
        return []

def main():
    inventory = Inventory()

    while True:
        print("\nInventory Management System")
        print("1. Add Product")
        print("2. Remove Product")
        print("3. Update Product")
        print("4. Display Inventory")
        print("5. Get Inventory Value")
        print("6. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            item_id = input("Enter item ID: ")
            name = input("Enter item name: ")
            quantity = int(input("Enter item quantity: "))
            price = float(input("Enter item price: "))
            item = Item(item_id, name, quantity, price)
            inventory.add_item(item)
            print(f"Added {name} to inventory.")
        elif choice == '2':
            item_id = input("Enter item ID to remove: ")
            quantity = int(input("Enter quantity to remove: "))
            inventory.remove_item(item_id, quantity)
            print(f"Removed {quantity} of {item_id} from inventory.")
        elif choice == '3':
            item_id = input("Enter item ID to update: ")
            if item_id in inventory.items:
                name = input("Enter new item name (leave blank to keep current): ")
                quantity = input("Enter new item quantity (leave blank to keep current): ")
                price = input("Enter new item price (leave blank to keep current): ")

                if name:
                    inventory.items[item_id].name = name
                if quantity:
                    inventory.items[item_id].quantity = int(quantity)
                if price:
                    inventory.items[item_id].price = float(price)

                print(f"Updated {item_id} in inventory.")
            else:
                print(f"Item with ID {item_id} not found.")
        elif choice == '4':
            inventory.load_items()
        elif choice == '5':
            value = inventory.get_inventory_value()
            print(f"Total Inventory Value: ${value:.2f}")
        elif choice == '6':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")  
if __name__ == "__main__":
    main()
