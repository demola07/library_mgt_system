from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    publisher: str
    category: str

class BookCreate(BookBase):
    pass

class BooksCreate(BaseModel):
    """Schema for creating multiple books at once."""
    books: list[BookCreate]

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

class UnavailableBook(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    publisher: str
    category: str
    available: bool
    borrow_date: Optional[date] = None
    return_date: Optional[date] = None

    class Config:
        from_attributes = True

class BookBorrowed(BookBase):
    """Schema for a borrowed book with its availability information"""
    id: int
    borrow_date: date
    return_date: date
    available: Optional[bool] = None

    class Config:
        from_attributes = True
