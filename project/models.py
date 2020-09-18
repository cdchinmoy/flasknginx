from project import db
from sqlalchemy.orm import relationship
import uuid

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.name

    def check_username_exist(username):
        user = User.query.filter_by(username=username).first()
        if user:
            return user
        else:
            return False

    def check_email_exist(email):
        user = User.query.filter_by(email=email).first()
        if user:
            return user
        else:
            return False        


class Seller(db.Model):
    __tablename__ = 'seller'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self):
        return '<Seller %r>' % self.name

    def check_username_exist(username):
        seller = Seller.query.filter_by(username=username).first()
        if seller:
            return seller
        else:
            return False

    def check_email_exist(email):
        seller = Seller.query.filter_by(email=email).first()
        if seller:
            return seller
        else:
            return False        
    


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(200), nullable=False)
    product_price = db.Column(db.String(10), nullable=False)
    product_desc = db.Column(db.String(500), nullable=False)
    sellers = relationship('Seller', secondary="seller_product", backref="products")

    def __init__(self, product_name, product_price, product_desc):
        self.product_name = product_name
        self.product_price = product_price
        self.product_desc = product_desc

    def __repr__(self):
        return '<Product %r>' % self.product_name

seller_product_table = db.Table('seller_product',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('seller_id', db.Integer, db.ForeignKey('seller.id'))
)        
