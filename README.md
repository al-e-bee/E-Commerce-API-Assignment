# Flask-SQLAlchemy & Flask-Marshmallow E-Commerce API

A RESTful API built with Python, Flask, SQLAlchemy, and Marshmallow to manage users, products, and multi-item orders in an e-commerce platform.

---

## Features

- **Object-Relational Mapping (ORM):** Uses Flask-SQLAlchemy for seamless MySQL database operations.
- **Serialization & Validation:** Uses Flask-Marshmallow and Marshmallow AutoSchema to serialize model outputs and validate incoming JSON payloads.
- **Many-to-Many Relationships:** Manages order-product relationships using a dedicated association table (`order_product`).
- **Complete CRUD Operations:** Full capabilities for managing Users, Products, and Orders.
- **Defensive Error & Edge-Case Handling:** Protects against missing IDs (404), duplicate item additions (400), and invalid schema payloads.

---

## Tech Stack

- **Language:** Python 3.x
- **Framework:** Flask
- **ORM & Database:** Flask-SQLAlchemy, MySQL (`mysql-connector-python`)
- **Serialization:** Flask-Marshmallow, `marshmallow-sqlalchemy`

---

## API Endpoints Summary

| Category     | Method   | Endpoint                                         | Description                           |
| :----------- | :------- | :----------------------------------------------- | :------------------------------------ |
| **Users**    | `POST`   | `/users`                                         | Create a new user                     |
|              | `GET`    | `/users`                                         | Get all users                         |
|              | `GET`    | `/users/<id>`                                    | Get single user by ID                 |
|              | `PUT`    | `/users/<id>`                                    | Update user information               |
|              | `DELETE` | `/users/<id>`                                    | Delete user and cascade delete orders |
| **Products** | `POST`   | `/products`                                      | Create a new product                  |
|              | `GET`    | `/products`                                      | Get all products                      |
|              | `GET`    | `/products/<id>`                                 | Get single product by ID              |
|              | `PUT`    | `/products/<id>`                                 | Update product details                |
|              | `DELETE` | `/products/<id>`                                 | Delete product                        |
| **Orders**   | `POST`   | `/orders`                                        | Create an order for a user            |
|              | `GET`    | `/orders/user/<user_id>`                         | Get all orders belonging to a user    |
|              | `GET`    | `/orders/<order_id>/products`                    | Get all products inside an order      |
|              | `PUT`    | `/orders/<order_id>/add_product/<product_id>`    | Add a product to an order             |
|              | `DELETE` | `/orders/<order_id>/remove_product/<product_id>` | Remove a product from an order        |

---

## Design Decisions & Edge Case Handling

- **Cascade Deletion:** Configured `cascade='all, delete-orphan'` on `User.user_orders` so deleting a user safely cleans up associated orders without causing foreign key constraint failures.
- **Duplicate Prevention:** Before appending a product to an order, the system checks if `product in order.products` to prevent duplicate row creation.
- **Safe Relationship Management:** Removing a product from an order uses `.remove()` on the association relationship rather than deleting the base `Product` record from the database.

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/al-e-bee/E-Commerce-API-Assignment
   ```
2. Install dependencies: `pip install Flask Flask-SQLAlchemy Flask-Marshmallow marshmallow-sqlalchemy mysql-connector-python`

3. Run the script: `python app.py`
