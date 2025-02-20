from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from ..models.book import Book, Publisher, Category

def get_book(db: Session, book_id: int) -> Optional[Book]:
    return db.query(Book).filter(Book.id == book_id).first()

def get_books(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    publisher: Optional[Publisher] = None,
    category: Optional[Category] = None,
    available_only: bool = False
) -> List[Book]:
    query = db.query(Book)
    
    # Apply filters
    if publisher:
        query = query.filter(Book.publisher == publisher)
    if category:
        query = query.filter(Book.category == category)
    if available_only:
        query = query.filter(Book.available == True)
    
    return query.offset(skip).limit(limit).all()

def update_book_availability(db: Session, book_id: int, available: bool, return_date=None):
    db_book = get_book(db, book_id)
    if db_book:
        db_book.available = available
        db_book.return_date = return_date
        db.commit()
        db.refresh(db_book)
    return db_book
