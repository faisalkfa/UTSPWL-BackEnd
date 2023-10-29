from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Index, Text, LargeBinary
from sqlalchemy.orm import relationship
from .meta import Base, DBSession
from datetime import datetime
import base64

class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)

Index('my_index', MyModel.name, unique=True, mysql_length=255)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(length=255), unique=True, nullable=False)
    password = Column(String(length=255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Add other columns as needed, such as name, email, etc.

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(length=255), nullable=False)
    description = Column(String(length=255), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    image_blob = Column(LargeBinary(length=(2**32)-1))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, price, stock, description, image):
        self.name = name
        self.price = price
        self.stock = stock
        self.description = description
        self.image_blob = image

    def to_dict(self):
        image_base64 = base64.b64encode(self.image_blob).decode("utf-8") if self.image_blob else None

        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'description': self.description,
            'image': image_base64
        }

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='transactions')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Add other columns as needed, such as transaction time, total price, etc.
    transaction_details = relationship('TransactionDetail', back_populates='transaction')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            # Add other transaction-related fields as needed
        }

    def calculate_total(self):
        total = 0
        for detail in self.transaction_details:
            total += detail.calculate_subtotal()
        return total

User.transactions = relationship('Transaction', order_by=Transaction.id, back_populates='user')

class TransactionDetail(Base):
    __tablename__ = 'transaction_details'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    transaction = relationship('Transaction', back_populates='transaction_details')
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product = relationship('Product', backref='transactions')
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            
        }
    
    def calculate_subtotal(self):
        return self.product.price * self.quantity
    

class ShoppingCart(Base):
    __tablename__ = 'shopping_carts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='shopping_cart')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Add other columns as needed, such as cart creation time, etc.
    cart_items = relationship('ShoppingCartItem', back_populates='cart')

User.shopping_cart = relationship('ShoppingCart', uselist=False, back_populates='user')

class ShoppingCartItem(Base):
    __tablename__ = 'shopping_cart_items'
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('shopping_carts.id'), nullable=False)
    cart = relationship('ShoppingCart', back_populates='cart_items')
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product = relationship('Product', backref='shopping_carts')
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    



# class History(Base):
#     __tablename__ = 'histories'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     user = relationship('User', back_populates='histories')
#     action = Column(String(length=255), nullable=False)
#     # Kolom lain seperti deskripsi perubahan, waktu perubahan, dll.

# User.histories = relationship('History', order_by=History.id, back_populates='user')