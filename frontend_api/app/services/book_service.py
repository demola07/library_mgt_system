from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from ..models.book import Book, Publisher, Category
from ..schemas.book import BookCreate

def get_book(db: Session, book_id: int) -> Optional[Book]:
    """Get a book by its ID.
    
    Args:
        db: Database session
        book_id: ID of the book to retrieve
    
    Returns:
        Book if found and available, None otherwise
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    
    # Return None for both non-existent and unavailable books
    if not book or not book.available:
        return None
        
    return book

def get_books(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    publisher: Optional[Publisher] = None,
    category: Optional[Category] = None,
    available_only: bool = True
) -> List[Book]:
    """Get books with optional filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        publisher: Filter by publisher
        category: Filter by category
        available_only: Only return available books
    
    Returns:
        List of books matching the criteria
    """
    query = db.query(Book)
    
    # Apply filters
    if publisher:
        query = query.filter(Book.publisher == publisher)
    if category:
        query = query.filter(Book.category == category)
    if available_only:
        query = query.filter(Book.available == True)
    
    return query.offset(skip).limit(limit).all()

def update_book_availability(db: Session, book_id: int, available: bool, return_date=None) -> Optional[Book]:
    """Update a book's availability status.
    
    Args:
        db: Database session
        book_id: ID of the book to update
        available: New availability status
        return_date: Expected return date if book is borrowed
    
    Returns:
        Updated book if found, None otherwise
    """
    db_book = get_book(db, book_id)
    if db_book:
        db_book.available = available
        db_book.return_date = return_date
        db.commit()
        db.refresh(db_book)
    return db_book

def create_book(db: Session, book: BookCreate) -> Book:
    """Create a new book (used for synchronization with Admin API).
    
    Args:
        db: Database session
        book: Book data from Admin API
    
    Returns:
        Created book instance
    """
    db_book = Book(**book.model_dump(), available=True)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int) -> bool:
    """Delete a book (used for synchronization with Admin API).
    
    Args:
        db: Database session
        book_id: ID of the book to delete
    
    Returns:
        True if book was deleted, False if not found
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        db.delete(book)
        db.commit()
        return True
    return False
