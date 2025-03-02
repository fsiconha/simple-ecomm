import sqlite3
from typing import List, Optional
from db.database import get_db_connection
from db.models import Product, User

class ProductServiceError(Exception):
    pass

def add_product(
        admin_user: User,
        name: str,
        description: str,
        price: float,
        db_path: Optional[str] = None
    ) -> Product:
    """
    Adds a new product. Only admins can add products.

    :param admin_user: The user attempting the operation
    :param name: Product name
    :param description: Product description
    :param price: Product price

    :return: Product object
    """
    if admin_user.role != "admin":
        raise ProductServiceError("Unauthorized: Only admins can add products")
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
        (name, description, price)
    )
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()

    return Product(
        id=product_id, name=name, description=description, price=price
    )

def edit_product(
        admin_user: User,
        product_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        db_path: Optional[str] = None
    ) -> Product:
    """
    Edits an existing product. Only admins can edit products.

    :param admin_user: The user attempting the operation
    :param product_id: ID of the product to edit

    :return: Updated Product object
    """
    if admin_user.role != "admin":
        raise ProductServiceError("Unauthorized: Only admins can edit products")
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    # Fetch current product details
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ProductServiceError("Product not found")
    new_name = name if name is not None else row["name"]
    new_description = (
        description if description is not None else row["description"]
    )
    new_price = price if price is not None else row["price"]
    cursor.execute(
        "UPDATE products SET name = ?, description = ?, price = ? WHERE id = ?",
        (new_name, new_description, new_price, product_id)
    )
    conn.commit()
    conn.close()

    return Product(
        id=product_id, name=new_name, description=new_description, price=new_price
    )

def delete_product(
        admin_user: User,
        product_id: int,
        db_path: Optional[str] = None
    ) -> None:
    """
    Deletes a product. Only admins can delete products.

    :param admin_user: The user attempting the operation
    :param product_id: ID of the product to delete
    """
    if admin_user.role != "admin":
        raise ProductServiceError("Unauthorized: Only admins can delete products")
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise ProductServiceError("Product not found")
    conn.commit()
    conn.close()

def get_product_by_id(
        product_id: int,
        db_path: Optional[str] = None
    ) -> Optional[Product]:
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Product(
            id=row["id"], name=row["name"], description=row["description"], price=row["price"]
        )
    return None

def get_all_products(db_path: Optional[str] = None) -> List[Product]:
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()

    return [Product(id=row["id"], name=row["name"], description=row["description"], price=row["price"]) for row in rows]
