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
        products: list[tuple[int, int]],
        db_path: Optional[str] = None
    ) -> Cart:
    """
    Adds products to the user's shopping cart.
    
    This function checks if a cart already exists for the user.
    - If so, it loads the existing items (stored as JSON) and updates the quantities.
    - If not, it creates a new cart record for the user.
    
    :param user: The user adding products to the cart.
    :param products: A list of tuples where each tuple is (product_id, product_quantity).
    :param db_path: Optional path to the SQLite database.

    :return: A Cart object with a cart_id and an items dictionary mapping product_id to product_quantity.
    """
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    # Check if the user already has a cart.
    cursor.execute("SELECT id, items FROM carts WHERE user_id = ?", (user.id,))
    row = cursor.fetchone()
    if row:
        cart_id = row["id"]
        existing_items = json.loads(row["items"]) if row["items"] else {}
    else:
        # Create a new cart with an empty items dictionary.
        empty_items_json = json.dumps({})
        cursor.execute(
            "INSERT INTO carts (user_id, items) VALUES (?, ?)",
            (user.id, empty_items_json)
        )
        cart_id = cursor.lastrowid
        existing_items = {}

    # Process each product.
    for product_id, product_quantity in products:
        # Verify that the product exists.
        product = get_product_by_id(product_id, db_path)
        if not product:
            raise OrderServiceError("Product not found")
        
        # Update the items dictionary.
        if product_id in existing_items:
            existing_items[product_id] += product_quantity
        else:
            existing_items[product_id] = product_quantity
    
    # Update the cart row with the new items JSON.
    new_items_json = json.dumps(existing_items)
    cursor.execute("UPDATE carts SET items = ? WHERE id = ?", (new_items_json, cart_id))
    conn.commit()
    conn.close()

    return Cart(id=cart_id, user_id=user.id, items=existing_items)

def view_cart(
        cart: Cart, user: User, db_path: Optional[str] = None
    ) -> list[dict]:
    """
    Retrieves the user's current cart items.
    
    :param cart: Cart object (with attribute cart_id) to identify the cart row.
    :param user: The user whose cart is being viewed.
    :param db_path: Optional database path.

    :return: List of dictionaries with 'product_id' and 'product_quantity'
    """
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT items FROM carts WHERE user_id = ? AND id = ?",
        (user.id, cart.id)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return []
    # The items column contains a JSON string, e.g., '{"101": 3, "102": 1}'
    items_dict = json.loads(row["items"])

    return [
        {"product_id": int(pid), "product_quantity": qty} for pid, qty in items_dict.items()
    ]

def clean_cart(
        cart: Cart,
        user: User,
        db_path: Optional[str] = None
    ) -> None:
    """
    Clean the user's cart.

    :param user: The user owner of the cart
    """
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM carts WHERE user_id = ? AND id = ?",
        (user.id, cart.id)
    )
    conn.commit()
    conn.close()

def place_order(
        cart: Cart,
        user: User,
        db_path: Optional[str] = None
    ) -> Order:
    """
    Places an order based on the user's current cart. The order record will include the cart's products as a JSON string.

    :param user: The user placing the order.
    :param db_path: Optional database path.

    :return: Order object with associated serialized products.
    """
    # Retrieve the cart items (expected to be a list of dictionaries with product_id and product_quantity)
    cart_items = view_cart(cart, user, db_path)
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
    conn.commit()
    conn.close()
    # Clear the user's cart after placing the order.
    clean_cart(cart, user, db_path)

    return Order(
        id=order_id,
        user_id=user.id,
        created_at=created_at,
        products=products_json
    )
