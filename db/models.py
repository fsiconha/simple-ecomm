from dataclasses import dataclass, field
from typing import Dict, Optional

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
    items: Dict[int, int] = field(default_factory=dict)

@dataclass
class Order:
    id: Optional[int]
    created_at: str
    user_id: int
    products: str  # JSON string containing products and quantities
