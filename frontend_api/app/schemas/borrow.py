from pydantic import BaseModel
from datetime import date

class BorrowBase(BaseModel):
    book_id: int

class BorrowCreate(BorrowBase):
    user_id: int
    days: int  # Used only for calculation

class Borrow(BorrowBase):
    id: int
    user_id: int  # Added this since we want to return it
    borrow_date: date
    return_date: date
    
    class Config:
        from_attributes = True
