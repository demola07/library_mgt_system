from pydantic import BaseModel
from datetime import date

class BorrowBase(BaseModel):
    book_id: int
    days: int  # Number of days to borrow the book

class BorrowCreate(BorrowBase):
    user_id: int

class Borrow(BorrowBase):
    id: int
    borrow_date: date
    return_date: date
    
    class Config:
        from_attributes = True
