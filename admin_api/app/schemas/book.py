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

class UnavailableBook(BookBase):
    """Schema for books that are currently borrowed"""
    id: int
    borrower_name: str
    borrower_email: str
    return_date: date

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
