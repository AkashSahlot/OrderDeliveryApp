from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from enum import Enum

class MenuCategory(str, Enum):
    APPETIZER = "appetizer"
    MAIN_COURSE = "main_course"
    DESSERT = "dessert"
    BEVERAGE = "beverage"

class MenuItem(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    price: float
    is_available: bool = True
    image_url: Optional[HttpUrl] = None

class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float
    category: MenuCategory
    is_available: bool = True
    image_url: Optional[HttpUrl] = None

class Restaurant(BaseModel):
    id: Optional[str] = None
    name: str
    address: str
    contact_info: str
    image_url: Optional[HttpUrl] = None
    cuisine_type: str
    menu_items: Optional[List[MenuItem]] = []

class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_info: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    cuisine_type: Optional[str] = None 