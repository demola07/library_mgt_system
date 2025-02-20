from sqlalchemy.orm import Session
from datetime import date, timedelta
from ..models.borrow import BorrowRecord
from ..schemas.borrow import BorrowCreate
from . import book_service

def create_borrow_record(db: Session, borrow: BorrowCreate):
    # Calculate return date
    return_date = date.today() + timedelta(days=borrow.days)
    
    # Create borrow record
    db_borrow = BorrowRecord(
        user_id=borrow.user_id,
        book_id=borrow.book_id,
        borrow_date=date.today(),
        return_date=return_date
    )
    
    # Update book availability
    book_service.update_book_availability(
        db=db,
        book_id=borrow.book_id,
        available=False,
        return_date=return_date
    )
    
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    return db_borrow
