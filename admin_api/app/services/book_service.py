from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.book import Book
from ..schemas.book import BookCreate, BookUpdate
from ..core.redis import publish_book_update


def create_book(db: Session, book: BookCreate) -> Book:
    """Create a new book in the catalogue.
    
    Args:
        db: Database session injected by FastAPI dependency system
        book: Book data validated by Pydantic
    
    Returns:
        The created book instance
    """
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    # Publish to Redis for frontend service
    publish_book_update(book.model_dump(), 'create')
    
    return db_book


def delete_book(db: Session, book_id: int) -> bool:
    """Delete a book from the catalogue.
    
    Args:
        db: Database session injected by FastAPI dependency system
        book_id: ID of the book to delete
    
    Returns:
        True if book was deleted, False if book was not found
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        # Publish to Redis for frontend service
        publish_book_update({'id': book_id}, 'delete')
        
        db.delete(book)
        db.commit()
        return True
    return False


def get_book(db: Session, book_id: int) -> Optional[Book]:
    """Get a book by its ID.
    
    Args:
        db: Database session injected by FastAPI dependency system
        book_id: ID of the book to retrieve
    
    Returns:
        Book instance if found, None otherwise
    """
    return db.query(Book).filter(Book.id == book_id).first()


def get_unavailable_books(db: Session, skip: int = 0, limit: int = 100) -> List[Book]:
    """Get all books that are currently borrowed.
    
    Args:
        db: Database session injected by FastAPI dependency system
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
    
    Returns:
        List of books that are currently unavailable
    """
    return (
        db.query(Book)
        .filter(Book.available == False)
        .offset(skip)
        .limit(limit)
        .all()
    )
