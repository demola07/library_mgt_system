from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from ...core.database import get_db
from ...schemas.borrow import Borrow, BorrowCreate
from ...services import borrow_service, book_service

router = APIRouter()

@router.post("/{user_id}/borrow/{book_id}", response_model=Borrow)
def borrow_book(
    user_id: int,
    book_id: int,
    days: int,
    db: Session = Depends(get_db)
):
    """
    Borrow a book for a specified number of days.
    """
    # Check if book is available
    book = book_service.get_book(db, book_id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.available:
        raise HTTPException(
            status_code=400,
            detail=f"Book is not available. Will be available after {book.return_date}"
        )
    
    # Create borrow record
    borrow_data = BorrowCreate(
        user_id=user_id,
        book_id=book_id,
        days=days
    )
    
    return borrow_service.create_borrow_record(db=db, borrow=borrow_data)
