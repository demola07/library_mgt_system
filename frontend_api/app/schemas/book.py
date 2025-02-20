from pydantic import BaseModel
from datetime import date
from typing import Optional
from ..models.book import Category, Publisher

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    publisher: Publisher
    category: Category

class Book(BookBase):
    id: int
    available: bool
    return_date: Optional[date] = None

    class Config:
        from_attributes = True

class BookList(BaseModel):
    id: int
    title: str
    author: str
    publisher: Publisher
    category: Category
    available: bool

    class Config:
        from_attributes = True
