from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from ..models.book import Category, Publisher

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    publisher: Publisher
    category: Category

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    pass

class Book(BookBase):
    id: int
    available: bool
    return_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BookBorrowed(BaseModel):
    id: int
    title: str
    borrower_name: str
    borrower_email: str
    borrow_date: date
    return_date: date

    class Config:
        from_attributes = True
