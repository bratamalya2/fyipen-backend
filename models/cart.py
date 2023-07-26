from pydantic import BaseModel
from typing import List

from .users import User
from .cartItem import CartItem

class Cart(BaseModel):
    user: User
    items: List[CartItem]