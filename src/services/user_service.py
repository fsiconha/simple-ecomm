import sqlite3
import hashlib
from typing import Optional
from db.database import get_db_connection
from src.models import User

class UserServiceError(Exception):
    pass

def hash_password(password: str) -> str:
    """Hashes the password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(
        username: str,
        password: str,
        role: str = "regular",
        db_path: Optional[str] = None
    ) -> User:
    """
    Registers a new user.
    :param username: Username
    :param password: Plain text password
    :param role: Role of the user (admin or regular)
    
    :return: User object
    """
    hashed = hash_password(password)
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return User(id=user_id, username=username, password=hashed, role=role)
    except sqlite3.IntegrityError:
        raise UserServiceError("Username already exists")
    finally:
        conn.close()

def login_user(
        username: str,
        password: str,
        db_path: Optional[str] = None
    ) -> User:
    """
    Authenticates a user.
    :param username: Username
    :param password: Plain text password
    :return: User object if authenticated
    """
    hashed = hash_password(password)
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row["password"] == hashed:
        return User(
            id=row["id"],
            username=row["username"],
            password=row["password"],
            role=row["role"]
        )
    else:
        raise UserServiceError("Invalid username or password")

def get_user_by_id(
        user_id: int,
        db_path: Optional[str] = None
    ) -> Optional[User]:
    conn = get_db_connection(db_path) if db_path else get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(
            id=row["id"],
            username=row["username"],
            password=row["password"],
            role=row["role"]
        )

    return None
