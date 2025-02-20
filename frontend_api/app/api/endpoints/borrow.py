from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from ...core.database import get_db
from ...schemas.borrow import Borrow, BorrowCreate
from ...services import borrow_service, book_service

router = APIRouter()

@router.post("/{user_id}/borrow/{book_id}",
    response_model=Borrow,
    summary="Borrow a book"
)
def borrow_book(
    user_id: int = Path(..., description="User ID"),
    book_id: int = Path(..., description="Book ID"),
    days: int = Query(..., ge=1, le=30, description="Number of days to borrow"),
    db: Session = Depends(get_db)
):
    """Borrow a book for a specified number of days."""
    # Check if book exists and is available
    book = book_service.get_book(db, book_id=book_id)
    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )
    
    # Create borrow record
    borrow_data = BorrowCreate(
        user_id=user_id,
        book_id=book_id,
        days=days
    )
    
    return borrow_service.create_borrow_record(db=db, borrow=borrow_data)
