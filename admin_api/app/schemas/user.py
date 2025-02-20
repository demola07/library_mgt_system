from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List
from .book import BookBorrowed

class UserBase(BaseModel):
    email: EmailStr
    firstname: str
    lastname: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserWithBorrowedBooks(User):
    borrowed_books: List[BookBorrowed] = []

    class Config:
        from_attributes = True
