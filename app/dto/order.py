from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PLACED = "PLACED"
    PREPARING = "PREPARING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"

class OrderItem(BaseModel):
    menu_item_id: str
    name: str
    quantity: int
    price: float

class Order(BaseModel):
    id: Optional[str] = None
    user_id: str
    restaurant_id: str
    items: List[OrderItem]
    total: float
    delivery_address: str
    status: OrderStatus = OrderStatus.PLACED
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None