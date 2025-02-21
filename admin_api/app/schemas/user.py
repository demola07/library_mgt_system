from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .book import BookBorrowed

class UserBase(BaseModel):
    """Base schema for user data"""
    email: str
    firstname: str
    lastname: str

class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserWithBorrowedBooksResponse(UserResponse):
    """Schema for user response with their borrowed books"""
    borrowed_books: List[BookBorrowed]

    class Config:
        from_attributes = True
