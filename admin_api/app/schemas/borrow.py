from pydantic import BaseModel
from datetime import date

class BorrowCreate(BaseModel):
    """Schema for creating a new borrow record"""
    user_id: int
    book_id: int
    return_date: date

class Borrow(BorrowCreate):
    """Schema for a borrow record with additional fields"""
    id: int
    borrow_date: date

    class Config:
        from_attributes = True

class BookBorrowed(BaseModel):
    """Schema for a borrowed book with complete details and borrow information"""
    id: int
    title: str
    author: str
    isbn: str
    publisher: str
    category: str
    borrow_date: date
    return_date: date

    class Config:
        from_attributes = True 