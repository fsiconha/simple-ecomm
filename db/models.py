from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int]
    username: str
    password: str  # This is stored as a hash.
    role: str      # "admin" or "regular"

@dataclass
class Product:
    id: Optional[int]
    name: str
    description: str
    price: float

@dataclass
class Cart:
    id: Optional[int]
    user_id: int
    product_id: int
    product_quantity: int

@dataclass
class Order:
    id: Optional[int]
    created_at: str
    user_id: int
    cart_it: int
