import sqlite3
import os
from models.menu_item import MenuItem
from models.order import Order
from models.restaurant import Restaurant
from models.user import Manager, Customer

DATABASE_FILE = "snappfood.db"


def get_connection():
    return sqlite3.connect(DATABASE_FILE)


def _load_order_items(cursor, order):
    cursor.execute("""
        SELECT name, price, item_type, is_available, image
        FROM order_items WHERE order_id = ?
    """, (order.order_id,))
    for item_row in cursor.fetchall():
        item = MenuItem(item_row[0], item_row[1], item_row[2],
                        bool(item_row[3]), item_row[4])
        order.items.append(item)


def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     TEXT PRIMARY KEY,
            first_name  TEXT NOT NULL,
            last_name   TEXT NOT NULL,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            role        TEXT NOT NULL,
            restaurant  TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            name             TEXT PRIMARY KEY,
            manager_username TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant  TEXT NOT NULL,
            name        TEXT NOT NULL,
            price       INTEGER NOT NULL,
            item_type   TEXT NOT NULL,
            is_available INTEGER NOT NULL DEFAULT 1,
            image       TEXT,
            FOREIGN KEY (restaurant) REFERENCES restaurants(name)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id    TEXT PRIMARY KEY,
            customer    TEXT NOT NULL,
            restaurant  TEXT NOT NULL,
            time        TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    TEXT NOT NULL,
            name        TEXT NOT NULL,
            price       INTEGER NOT NULL,
            item_type   TEXT NOT NULL,
            is_available INTEGER NOT NULL DEFAULT 1,
            image       TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    """)

    conn.commit()
    conn.close()


def save_data(platform):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM order_items")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM menu_items")
    cursor.execute("DELETE FROM restaurants")
    cursor.execute("DELETE FROM users")

    for user in platform.users:
        restaurant_name = None
        if hasattr(user, 'restaurant') and user.restaurant:
            restaurant_name = user.restaurant.name
        cursor.execute("""
            INSERT INTO users (user_id, first_name, last_name, username, password, role, restaurant)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user.user_id, user.first_name, user.last_name,
              user.username, user.password, user.role, restaurant_name))

    for restaurant in platform.restaurants:
        cursor.execute("""
            INSERT INTO restaurants (name, manager_username) VALUES (?, ?)
        """, (restaurant.name, restaurant.manager_username))

        for item in restaurant.menu:
            cursor.execute("""
                INSERT INTO menu_items (restaurant, name, price, item_type, is_available, image)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (restaurant.name, item.name, item.price,
                  item.item_type, int(item.is_available), item.image))

        for order in restaurant.orders:
            cursor.execute("""
                INSERT OR IGNORE INTO orders (order_id, customer, restaurant, time)
                VALUES (?, ?, ?, ?)
            """, (order.order_id, order.customer, order.restaurant, order.time))

            for item in order.items:
                cursor.execute("""
                    INSERT INTO order_items (order_id, name, price, item_type, is_available, image)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (order.order_id, item.name, item.price,
                      item.item_type, int(item.is_available), item.image))

    for user in platform.users:
        if user.role == "customer":
            for order in user.order_history:
                cursor.execute("""
                    INSERT OR IGNORE INTO orders (order_id, customer, restaurant, time)
                    VALUES (?, ?, ?, ?)
                """, (order.order_id, order.customer, order.restaurant, order.time))

    conn.commit()
    conn.close()
    print("  Data saved.")


def load_data(platform):
    if not os.path.exists(DATABASE_FILE):
        return

    conn = get_connection()
    cursor = conn.cursor()

    platform.users.clear()
    platform.restaurants.clear()

    cursor.execute("SELECT name, manager_username FROM restaurants")
    for row in cursor.fetchall():
        restaurant = Restaurant(row[0], row[1])

        cursor.execute("""
            SELECT name, price, item_type, is_available, image
            FROM menu_items WHERE restaurant = ?
        """, (restaurant.name,))
        for item_row in cursor.fetchall():
            item = MenuItem(item_row[0], item_row[1], item_row[2],
                            bool(item_row[3]), item_row[4])
            restaurant.menu.append(item)

        cursor.execute("""
            SELECT order_id, customer, restaurant, time
            FROM orders WHERE restaurant = ?
        """, (restaurant.name,))
        for order_row in cursor.fetchall():
            order = Order(order_row[0], order_row[1], order_row[2])
            order.time = order_row[3]
            _load_order_items(cursor, order) 
            restaurant.orders.append(order)

        platform.restaurants.append(restaurant)

    cursor.execute("SELECT user_id, first_name, last_name, username, password, role FROM users")
    for row in cursor.fetchall():
        user_id, first_name, last_name, username, password, role = row
        if role == "manager":
            user = Manager(first_name, last_name, username, password)
            user.user_id = user_id
            for restaurant in platform.restaurants:
                if restaurant.manager_username == username:
                    user.restaurant = restaurant
        else:
            user = Customer(first_name, last_name, username, password)
            user.user_id = user_id
            cursor.execute("""
                SELECT order_id, customer, restaurant, time
                FROM orders WHERE customer = ?
            """, (username,))
            for order_row in cursor.fetchall():
                order = Order(order_row[0], order_row[1], order_row[2])
                order.time = order_row[3]
                _load_order_items(cursor, order) 
                user.order_history.append(order)

        platform.users.append(user)

    conn.close()


def get_next_order_number():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    conn.close()
    return count + 1