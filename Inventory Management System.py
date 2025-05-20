# Import required libraries
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sys

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models (Class Diagram implementation)
class Product(db.Model):
    """Product model representing items in inventory"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50))
    price = db.Column(db.Float)
    barcode = db.Column(db.String(50), unique=True)
    items = db.relationship('InventoryItem', backref='product', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'barcode': self.barcode
        }

class Inventory(db.Model):
    """Inventory location model"""
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    items = db.relationship('InventoryItem', backref='inventory', lazy=True)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'inventory_id': self.inventory_id,
            'quantity': self.quantity,
            'last_updated': self.last_updated
        }
# Initialize the database
with app.app_context():
    db.create_all()     