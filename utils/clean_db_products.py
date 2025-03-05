from typing import Optional
from db.database import get_db_connection

def clean_products(db_path: Optional[str] = None) -> None:
    """
    Deletes all products registered in the database.

    :param db_path: Optional path to the SQLite database.
    """
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products")
    conn.commit()
    conn.close()
