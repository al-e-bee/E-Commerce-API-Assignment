from __future__ import annotations
import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped
from sqlalchemy import ForeignKey, Table, Column, String, Integer, select, DateTime, func, Float
from marshmallow import ValidationError
from typing import List, Optional
import os

# Initialize app
app = Flask(__name__)

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:*D3tr01t26!*@localhost/ecommerce_api'

# Create Base Model
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

# Association Table
order_product = Table(
    'order_product',
    Base.metadata,
    Column('order_id', ForeignKey('orders.id'), primary_key=True),
    Column('product_id', ForeignKey('products.id'), primary_key=True)
)

# Models
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # One-to-Many Relationship: User to Orders
    user_orders: Mapped[List['Order']] = relationship(back_populates='user', cascade='all, delete-orphan')
    
class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    
    # Many-to-Many: Orders to User
    user: Mapped['User'] = relationship(back_populates='user_orders')
    products: Mapped[List['Product']] = relationship(secondary=order_product,back_populates='product_in_orders')
    
class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    # Relationship: Product to Order
    product_in_orders: Mapped[List['Order']] = relationship(secondary=order_product,back_populates='products')
    
# User Schema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        
# Order Schema
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True
        
# Product Schema
class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

        
# Initialize Schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

#===========================
# IMPLEMENT CRUD ENDPOINTS
#===========================

# ----USER ENDPOINTS--------
# Create a user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_user = User(name=user_data['name'], address=user_data['address'], email=user_data['email'])
    db.session.add(new_user)
    db.session.commit()
    
    return user_schema.jsonify(new_user), 201

# Retrieve All Users
@app.route('/users', methods=['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()
    
    return users_schema.jsonify(users), 200

# Retrieve a SINGLE User by ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)
    return user_schema.jsonify(user), 200

# Update User
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id) 
    
    if not user:
        return jsonify({"message": 'Invalid user id'}), 400
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    user.name = user_data['name']
    user.address = user_data['address']
    user.email = user_data['email']
    
    db.session.commit()
    return user_schema.jsonify(user), 200

# Delete a User
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({'message': 'Invalid user id'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'Successfully deleted user {id}'}), 200

#-----PRODUCT ENDPOINTS------
# Create a Product
@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'], )
    db.session.add(new_product)
    db.session.commit()
    
    return user_schema.jsonify(new_product), 201

# Retrieve All Products
@app.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()
    
    return products_schema.jsonify(products), 200

# Retrieve a SINGLE Product by ID
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = db.session.get(Product, id)
    return product_schema.jsonify(product), 200

# Update Product
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({'message': 'Invalid product id'}), 400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    
    db.session.commit()
    return product_schema.jsonify(product), 200

# Delete Product
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Product, id)
    
    if not product:
        return jsonify({'message': 'Invalid product id'}), 400
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': f'Successfully deleted product {id}'}), 200

#----ORDER ENDPOINTS----
# Create an Order
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Order(
        user_id = order_data['user_id']
    )
    
    if 'order_date' in order_data and order_data['order_date']:
        new_order.order_date = order_data['order_date']
    
    db.session.add(new_order)
    db.session.commit()
    
    return order_schema.jsonify(new_order), 201

# Add a product to an order (prevent duplicates)
@app.route('/orders/<order_id>/add_product/<product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)
    
    if not order or not product:
        return jsonify({'message': 'Order or Product not found.'}), 404
    
    if product in order.products:
        return jsonify({'message': f'Product "{product.product_name}" is already in order #{order.id}'}), 400
    
    order.products.append(product)
    db.session.commit()
    return jsonify({'message': f'Sucessfully added {product.product_name} to order #{order_id}!'}), 200

# Remove a Product from an Order
@app.route('/orders/<order_id>/remove_product/<product_id>', methods=['DELETE'])
def delete_product_from_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)
    
    if not order or not product:
        return jsonify({'message': 'Order or Product not found.'}), 404
    
    if product not in order.products:
        return jsonify({'message': f'Product "{product.product_name}" is not part of order #{order_id}.'}), 400
    
    order.products.remove(product)
    db.session.commit()
    return jsonify({'message': f'Successfully removed product "{product.product_name}" from order #{order.id}!'}), 200

# Get all Orders for a User
@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_all_orders_for_user(user_id):

    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if not user.user_orders:
        return jsonify({'message': 'No orders found for this user.'}), 200
    
    return orders_schema.jsonify(user.user_orders), 200
    
# Get all Products for an Order
@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_all_products_in_order(order_id):
    
    order = db.session.get(Order, order_id)
    
    if not order:
        return jsonify({'message': 'Order not found.'}), 404
    
    if not order.products:
        return jsonify({'message': f'Order #{order_id} has no products.'}), 200
    
    return products_schema.jsonify(order.products), 200