from datetime import datetime

from sqlalchemy.orm import backref
from flaskapp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    items = db.relationship("Item", backref='items')
    products = db.relationship("Product", backref="products", lazy=True)



    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}')"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_file = db.Column(db.String, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Item('{self.name}', '{self.type}', '{self.price}', '{self.image_file}')"

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    components = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_file = db.Column(db.String, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Product('{self.name}', '{self.type}', '{self.price}')"

class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    item_pk = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"Product('{self.name}', '{self.quantity}')"
    
    



