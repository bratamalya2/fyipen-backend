from pydantic import BaseModel

from .book import Book

class CartItem(BaseModel):
    item: Book
    qty: int