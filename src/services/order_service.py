import json
import sqlite3
from typing import List, Optional
from datetime import datetime
from db.database import get_db_connection
from db.models import Cart, Order, User
from src.services.product_service import get_product_by_id

class OrderServiceError(Exception):
    pass

def add_to_cart(
        user: User,
        product_id: int,
        product_quantity: int = 1,
        db_path: Optional[str] = None
    ) -> Cart:
    """
    Adds a product to the user's cart.

    :param user: The user adding to cart
    :param product_id: ID of the product to add
    :param product_quantity: Quantity to add

    :return: Cart object
    """
    # Verify that the product exists
    product = get_product_by_id(product_id, db_path)
    if not product:
        raise OrderServiceError("Product not found")
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    # Check if the product is already in the cart
    cursor.execute(
        "SELECT * FROM carts WHERE user_id = ? AND product_id = ?",
        (user.id, product_id)
    )
    row = cursor.fetchone()
    if row:
        new_quantity = row["product_quantity"] + product_quantity
        cursor.execute(
            "UPDATE carts SET product_quantity = ? WHERE id = ?",
            (new_quantity, row["id"])
        )
        cart_id = row["id"]
    else:
        cursor.execute(
            "INSERT INTO carts (user_id, product_id, product_quantity) VALUES (?, ?, ?)",
            (user.id, product_id, product_quantity)
        )
        cart_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return Cart(
        id=cart_id, user_id=user.id, product_id=product_id, product_quantity=product_quantity
    )

def view_cart(user: User, db_path: Optional[str] = None) -> list[dict]:
    """
    Retrieves the user's current cart items.

    :param user: The user whose cart is being viewed

    :return: List of dictionaries with 'product_id' and 'product_quantity'
    """
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT product_id, product_quantity FROM carts WHERE user_id = ?",
        (user.id,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            'product_id': row["product_id"],
            'product_quantity': row["product_quantity"]
        }
        for row in rows
    ]

def place_order(user: User, db_path: Optional[str] = None) -> Order:
    """
    Places an order based on the user's current cart. The order record will include the cart's products as a JSON string.

    :param user: The user placing the order.
    :param db_path: Optional database path.

    :return: Order object with associated cart_id and serialized products.
    """
    # Retrieve the cart items (expected to be a list of dictionaries with product_id and product_quantity)
    cart_items = view_cart(user, db_path)
    if not cart_items:
        raise OrderServiceError("Cart is empty")
    # Serialize the cart items into a JSON string.
    products_json = json.dumps(cart_items)

    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    # Insert the order record, including the products JSON.
    cursor.execute(
        "INSERT INTO orders (user_id, created_at, products) VALUES (?, ?, ?)",
        (user.id, created_at, products_json)
    )
    order_id = cursor.lastrowid
    # Clear the user's cart after placing the order.
    cursor.execute("DELETE FROM carts WHERE user_id = ?", (user.id,))
    conn.commit()
    conn.close()

    return Order(
        id=order_id,
        user_id=user.id,
        created_at=created_at,
        products=products_json
    )
