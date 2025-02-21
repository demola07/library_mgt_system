from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookBase(BaseModel):
    """Base schema for book data"""
    title: str
    author: str
    isbn: str
    publisher: str
    category: str

class BookCreate(BookBase):
    """Schema for creating a new book"""
    pass

class BookResponse(BookBase):
    """Schema for book response"""
    id: int
    available: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BookList(BookResponse):
    """Schema for book list response"""
    pass

class BookDetail(BookResponse):
    """Schema for detailed book response"""
    pass
